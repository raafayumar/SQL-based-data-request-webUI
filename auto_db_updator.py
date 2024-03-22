import os
import time
import mysql.connector
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from table_2_updator_module import table_two
import threading
import pandas as pd
import sys
from datetime import datetime


class MyHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.connect_to_database()
        self.create_database_and_table()
        self.created_count = 0  # Initialize count for created files
        self.updated_count = 0  # Initialize count for updated files
        self.deleted_count = 0  # Initialize count for deleted files
        self.deletion_set = set()
        self.processed_combinations = set()
        self.reset_timer = None

    def create_database_and_table(self):
        # Create the database if it doesn't exist
        create_db_sql = "CREATE DATABASE IF NOT EXISTS incabin_db"
        self.execute_sql(create_db_sql, ())

        # Switch to the incabin_db database
        use_db_sql = "USE incabin_db"
        self.execute_sql(use_db_sql, ())

        # Create the data_path table if it doesn't exist
        create_table_sql = (
            "CREATE TABLE IF NOT EXISTS data_path ("
            "sl_no INT AUTO_INCREMENT PRIMARY KEY,"
            "Absolute_Path VARCHAR(255),"
            "Task VARCHAR(255),"
            "Sensor VARCHAR(255),"
            "Date VARCHAR(255),"
            "Time_Stamp VARCHAR(255),"
            "Subject_Name VARCHAR(255),"
            "Ph_No VARCHAR(255),"
            "Unique_subjects VARCHAR(255),"
            "Location VARCHAR(255),"
            "Gender VARCHAR(255),"
            "Age VARCHAR(255),"
            "Spectacles VARCHAR(255),"
            "Lux_Values VARCHAR(255),"
            "Traffic_Data VARCHAR(255),"
            "Run_No VARCHAR(255),"
            "Frame_No VARCHAR(255),"
            "Extension VARCHAR(255),"
            "txt_exist INT"
            ")"
        )
        self.execute_sql(create_table_sql, ())

    def connect_to_database(self):
        # Connect to MySQL server
        self.db_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Incabin@123",
            pool_size=10,  # Adjust the pool size as needed
            pool_name="mypool",
            pool_reset_session=True
        )
        self.db_cursor = self.db_connection.cursor()

        # Create or use the database and table
        self.create_database_and_table()

    def connect_to_mysql(self):
        try:
            # print(datetime.now(), file=sys.stdout)
            # Check if the connection is active or if it's None
            if self.db_connection is None or not self.db_connection.is_connected():
                self.db_connection = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="Incabin@123",
                    pool_size=10,  # Adjust the pool size as needed
                    pool_name="mypool",
                    pool_reset_session=True
                )

                print(datetime.now(), 'Connected to MySQL database', file=sys.stdout)

            self.db_cursor = self.db_connection.cursor()

        except mysql.connector.Error as e:
            print(datetime.now(), f"Error: {e}", file=sys.stdout)

    def close_database_connection(self):
        if self.db_connection is not None and self.db_connection.is_connected():
            self.db_cursor.close()
            self.db_connection.close()
            self.db_connection = None
            print(datetime.now(), 'Table 1 updated successfully', file=sys.stdout)

    def execute_sql(self, sql, values):
        self.db_cursor.execute(sql, values)
        self.db_connection.commit()

    def on_created(self, event):
        if not event.is_directory:
            self.connect_to_mysql()
            self.extract_and_save_info(event.src_path)
            self.update_database()
            self.created_count += 1  # Increment count for created files
            print(datetime.now(), f"Files created: {self.created_count}", file=sys.stdout)

            # Cancel the existing timer if it's already running
            if self.reset_timer and self.reset_timer.is_alive():
                self.reset_timer.cancel()

            # Check for a period of inactivity before resetting the count
            reset_delay_seconds = 10  # Adjust this value based on your requirements
            self.reset_timer = threading.Timer(reset_delay_seconds, self.reset_created_count)
            self.reset_timer.start()

    def reset_created_count(self):
        print(datetime.now(), "Updating Table 2, Please wait...", file=sys.stdout)
        self.close_database_connection()
        self.created_count = 0
        self.deleted_count = 0
        self.created_count = 0
        print(datetime.now(), table_two(), file=sys.stdout)

    def on_deleted(self, event):
        if not event.is_directory:
            self.connect_to_mysql()
            file_path = event.src_path
            path_separator = os.path.sep
            components = file_path.split(path_separator)

            # Extract information from the file name
            file_name = components[-1]
            file_name_parts = file_name.split('_')
            deletion_pair = (
                components[components.index('datafolder') + 1],
                components[components.index('datafolder') + 2],
                components[components.index('datafolder') + 3],
                '',  # Placeholder for Timestamp
                file_name_parts[1][:2],  # Take first two characters of Name
                file_name_parts[2][-4:],  # Take last four digits of Contact_No
                file_name_parts[3],
                file_name_parts[4],
                int(file_name_parts[5]),
                file_name_parts[6],
                int(file_name_parts[9]),  # Convert Run to int
                ''  # Placeholder for Comments
                ''
                ''
            )
            # Add the deletion pair to the set
            self.deletion_set.add(deletion_pair)

            # Check if any change has occurred in the deletion set
            if self.deletion_set != self.processed_combinations:
                # Start deletion process if there's any change in the set
                threading.Thread(target=self.delete_from_csv, args=(r'/home/incabin/DATA/AutoVault/metadata/metadata.csv', deletion_pair)).start()
                self.processed_combinations = self.deletion_set.copy()
                print(datetime.now(), "Deletions initiated.", file=sys.stdout)

            self.delete_from_database(event.src_path)
            self.deleted_count += 1  # Increment count for deleted files
            print(datetime.now(), f"Files deleted: {self.deleted_count}", file=sys.stdout)

            # Cancel the existing timer if it's already running
            if self.reset_timer and self.reset_timer.is_alive():
                self.reset_timer.cancel()

            # Check for a period of inactivity before resetting the count
            reset_delay_seconds = 10  # Adjust this value based on your requirements
            self.reset_timer = threading.Timer(reset_delay_seconds, self.reset_created_count)
            self.reset_timer.start()

    def delete_from_csv(self, csv_file, deletion_pair):
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file)

        name_index = 4
        contact_index = 5
        df['Contact_No'] = df['Contact_No'].astype(str)
        df['Name'] = df['Name'].astype(str)
        # Filter the DataFrame based on the deletion_pair and Run value
        mask = (
                (df['Task'] == deletion_pair[0]) &
                (df['Sensor'] == deletion_pair[1]) &
                (df['Date'] == deletion_pair[2]) &
                (df['Name'].str.startswith(deletion_pair[name_index])) &
                (df['Contact_No'].str.endswith(deletion_pair[contact_index])) &
                (df['Location'] == deletion_pair[6]) &
                (df['Gender'] == deletion_pair[7]) &
                (df['Age'] == deletion_pair[8]) &
                (df['Spectacles'] == deletion_pair[9]) &
                (df['Run'] == deletion_pair[10])  # Include only rows with the specified Run value
        )
        # Delete the selected row(s)
        df = df[~mask]

        # Write the updated data back to the same CSV file
        df.to_csv(csv_file, index=False)

        # Clear the deletion set after processing
        self.deletion_set.clear()

    def extract_and_save_info(self, file_path):
        # Extract information from the file path
        path_separator = os.path.sep
        components = file_path.split(path_separator)

        # Extract information from the file name
        file_name = components[-1]
        file_name_parts = file_name.split('_')

        # Create a dictionary with extracted information
        entry = {'absolute path': file_path, 'task': components[components.index('datafolder') + 1],
                 'sensor': components[components.index('datafolder') + 2],
                 'date': components[components.index('datafolder') + 3],
                 'time stamp': '', 'subject name': '', 'ph no': '', 'Unique_subjects': '', 'location': '', 'gender': '', 'age': '',
                 'spectacles': '', 'lux values': '', 'traffic data': '', 'run no': '', 'frame no': '', 'extension': '', 'txt_exist': ''}

        if file_name_parts:
            entry['time stamp'] = file_name_parts[0]
            entry['subject name'] = file_name_parts[1] if len(file_name_parts) >= 2 else ''
            entry['ph no'] = file_name_parts[2] if len(file_name_parts) >= 3 else ''
            entry['Unique_subjects'] = file_name_parts[1] + file_name_parts[2]
            entry['location'] = file_name_parts[3] if len(file_name_parts) >= 4 else ''
            entry['gender'] = file_name_parts[4] if len(file_name_parts) >= 5 else ''
            entry['age'] = file_name_parts[5] if len(file_name_parts) >= 6 else ''
            entry['spectacles'] = file_name_parts[6] if len(file_name_parts) >= 7 else ''
            entry['lux values'] = file_name_parts[7] if len(file_name_parts) >= 8 else ''
            entry['traffic data'] = file_name_parts[8] if len(file_name_parts) >= 9 else ''
            entry['run no'] = file_name_parts[9] if len(file_name_parts) >= 10 else ''
            entry['frame no'], entry['extension'] = os.path.splitext(file_name_parts[-1])

        if os.path.splitext(file_path)[0] != '.txt':
            txt_file_path = file_path.replace(entry['extension'], ".txt")
            entry['txt_exist'] = 1 if os.path.exists(txt_file_path) else 0

        # Save the entry to the MySQL database
        sql = ("INSERT INTO incabin_db.data_path (`sl_no`, `Absolute_Path`, `Task`, `Sensor`, `Date`, `Time_Stamp`, "
               "`Subject_Name`, `Ph_No`,`Unique_subjects`, `Location`, `Gender`, `Age`, `Spectacles`, `Lux_Values`, "
               "`Traffic_Data`, `Run_No`, `Frame_No`, `Extension`, `txt_exist`) "
               "VALUES (NULL, %(absolute path)s, %(task)s, %(sensor)s, %(date)s, %(time stamp)s, "
               "%(subject name)s, %(ph no)s,  %(Unique_subjects)s, %(location)s, %(gender)s, %(age)s, %(spectacles)s, "
               "%(lux values)s, %(traffic data)s, %(run no)s, %(frame no)s, %(extension)s, %(txt_exist)s)")
        self.execute_sql(sql, entry)

    def update_database(self):
        # Retrieve the last serial number from the MySQL database
        select_sql = "SELECT MAX(sl_no) FROM incabin_db.data_path"
        self.db_cursor.execute(select_sql)
        last_serial_number = self.db_cursor.fetchone()[0]

        # Retrieve all entries with serial numbers greater than the last
        select_sql = "SELECT * FROM incabin_db.data_path WHERE sl_no > %s"
        self.db_cursor.execute(select_sql, (last_serial_number,))
        new_entries = self.db_cursor.fetchall()

        # Insert new entries into the MySQL database
        insert_sql = (
            "INSERT INTO incabin_db.data_path "
            "(Absolute_Path, Task, Sensor, Date, Time_Stamp, Subject_Name, Ph_No, Unique_subjects, Location, Gender, Age, "
            "Spectacles, Lux_Values, Traffic_Data, Run_No, Frame_No, Extension, txt_exist) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        for entry in new_entries:
            self.db_cursor.execute(insert_sql, entry[1:])
            self.updated_count += 1  # Increment count for updated files

    def delete_from_database(self, file_path):
        # Delete the entry from the database based on the file path
        delete_sql = "DELETE FROM incabin_db.data_path WHERE Absolute_Path = %s"
        self.execute_sql(delete_sql, (file_path,))


if __name__ == "__main__":
    path_to_watch = r'/home/incabin/DATA/AutoVault/datafolder'

    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path_to_watch, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(0.01)
    except KeyboardInterrupt:
        observer.stop()
