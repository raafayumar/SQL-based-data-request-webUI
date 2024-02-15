import os
import mysql.connector
import time
from tqdm import tqdm

# Path to the folder
folder_path = r'/home/incabin/DATA/AutoVault/datafolder'
folder_name = 'datafolder'

operating_system = os.name
if operating_system == 'nt':  # Windows
    path_separator = '\\'
else:  # Linux or other Unix-like systems
    path_separator = '/'


# Function to get all files recursively in a directory
def get_all_file_paths(directory):
    print("getting files...")
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            file_paths.append(os.path.join(root, filename))
    return file_paths


# Function to establish a MySQL connection with connection pooling
def connect_to_database():
    print("connecting...")
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Incabin@123",
        connect_timeout=120,
        pool_size=10,  # Adjust the pool size as needed
        pool_name="mypool",
        pool_reset_session=True
    )
    return connection


# Function to create the "data" database if not exists
def create_database(cursor):
    print("creating db")
    cursor.execute("DROP DATABASE IF EXISTS incabin_db")
    cursor.execute("CREATE DATABASE IF NOT EXISTS incabin_db")
    cursor.execute("USE incabin_db")


# Function to create the "data_path" table if not exists
def create_data_path_table(cursor):
    print("creating table")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_path (
            `sl_no` INT AUTO_INCREMENT PRIMARY KEY,
            `Absolute_path` VARCHAR(255),  -- Add the new column for whole_path
            `Path` VARCHAR(255),
            `Task` VARCHAR(255),
            `Sensor` VARCHAR(255),
            `Date` VARCHAR(255),
            `Time_Stamp` VARCHAR(255),
            `Subject_Name` VARCHAR(255),
            `Ph_No` VARCHAR(255),
            `Unique_subjects` VARCHAR(255),
            `Location` VARCHAR(255),
            `Gender` VARCHAR(255),
            `Age` VARCHAR(255),
            `Spectacles` VARCHAR(255),
            `Lux_Values` VARCHAR(255),
            `Traffic_Data` VARCHAR(255),
            `Run_No` VARCHAR(255),
            `Frame_No` VARCHAR(255),
            `Extension` VARCHAR(255)
        )
    """)


# Function to create the "data_vis" table if not exists
def create_data_vis_table(cursor):
    print("creating table 2")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_vis (
            `condition_` VARCHAR(255),
            `row_count` INT
        )
    """)


# Function to insert data into the "data_path" table with reconnection logic
def insert_data_into_data_path_table(connection, cursor, data):
    print('creating table 1 columns')
    st_tim_d1 = time.time()
    sql = ("INSERT INTO data_path (`sl_no`, `Absolute_Path`, `Path`, `Task`, `Sensor`, `Date`, `Time_Stamp`, "
           "`Subject_Name`, `Ph_No`, Unique_subjects, `Location`, `Gender`, `Age`, `Spectacles`, `Lux_Values`, `Traffic_Data`, `Run_No`, "
           "`Frame_No`, `Extension`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

    chunk_size = 100  # Adjust the chunk size as needed

    for i in range(0, len(data), chunk_size):
        chunk_data = data[i:i + chunk_size]
        try:
            cursor.executemany(sql, chunk_data)
            connection.commit()
            end_time_d1 = time.time()
            t_d1 = end_time_d1 - st_tim_d1
            print(t_d1)
        except mysql.connector.errors.OperationalError as e:
            if e.errno == mysql.connector.errorcode.CR_SERVER_LOST:
                print("Reconnecting to the database...")
                connection.reconnect(attempts=3, delay=5)
                cursor = connection.cursor()
                cursor.executemany(sql, chunk_data)
                connection.commit()
            else:
                raise e


# Record the start time
start_execution_time = time.perf_counter()

# Retrieve all file paths
file_paths = get_all_file_paths(folder_path)

# Connect to MySQL database
connection = connect_to_database()
cursor = connection.cursor()

# Create database and table if not exists
create_database(cursor)
create_data_path_table(cursor)
create_data_vis_table(cursor)  # Create the data_vis table

# Prepare data for insertion into the "data_path" table
data = []
for path in tqdm(file_paths, desc="fetching files", unit='file'):
    components = path.split(path_separator)
    # print(path)
    # Check if 'folder_name' is in the split path and return its index
    index = components.index(folder_name)

    whole_path_column = path  # Set whole_path to the full file path
    task_column = components[index + 1]
    sensor_column = components[index + 2]
    date_column = components[index + 3]
    file_name = components[-1]
    file_name_parts = file_name.split('_')

    # Extract information from the file name parts
    time_stamp_column = subject_name_column = ph_no_column = Unique_subjects= location_column = gender_column = age_column = spectacles_column = lux_values_column = traffic_data_column = run_no_column = frame_no_column = extension_column = ''

    if len(file_name_parts) >= 1:
        time_stamp_column = file_name_parts[0]
    if len(file_name_parts) >= 2:
        subject_name_column = file_name_parts[1]
    if len(file_name_parts) >= 3:
        ph_no_column = file_name_parts[2]
    if len(file_name_parts) >= 4:
        location_column = file_name_parts[3]
    if len(file_name_parts) >= 5:
        gender_column = file_name_parts[4]
    if len(file_name_parts) >= 6:
        age_column = file_name_parts[5]
    if len(file_name_parts) >= 7:
        spectacles_column = file_name_parts[6]
    if len(file_name_parts) >= 8:
        lux_values_column = file_name_parts[7]
    if len(file_name_parts) >= 9:
        traffic_data_column = file_name_parts[8]
    if len(file_name_parts) >= 10:
        run_no_column = file_name_parts[9]
    if len(file_name_parts) >= 11:
        frame_no_column, extension_column = os.path.splitext(file_name_parts[10])
    # print(file_name_parts)
    Unique_subjects = file_name_parts[1] + file_name_parts[2]
    # print(len(Unique_subjects))

    data.append((
        None, whole_path_column, path_separator.join(components[:index+1]), task_column, sensor_column, date_column, time_stamp_column,
        subject_name_column, ph_no_column, Unique_subjects, location_column,
        gender_column, age_column, spectacles_column, lux_values_column, traffic_data_column, run_no_column,
        frame_no_column, extension_column
    ))

# Insert data into the "data_path" table
insert_data_into_data_path_table(connection, cursor, data)

# Close the cursor and connection
cursor.close()
connection.close()

# Connect to the database and execute the query for data_vis
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Incabin@123',
    'database': 'incabin_db'
}

# Define the SQL query for data_vis
sql_query_data_vis = r"""
    INSERT INTO incabin_db.data_vis (condition_, row_count)
SELECT condition_, SUM(row_count) AS row_count
FROM (
    SELECT 
        task AS condition_,
        COUNT(*) AS row_count
    FROM incabin_db.data_path
    WHERE task REGEXP '\\bSeat_belt\\b|\\bHands_on_off_steering\\b|\\bGaze_detection\\b|\\bDriver_face\\b|\\bDriver_pose\\b|\\bDriver_vitals\\b|\\bOccupant_vitals\\b|\\bGesture_recognition\\b|\\bOccupant\\b|\\bBreathing\\b'
    AND extension <> '.txt'
    GROUP BY task

    UNION ALL

    SELECT 
        sensor AS condition_,
        COUNT(*) AS row_count
    FROM incabin_db.data_path
    WHERE sensor REGEXP '\\bFlir\\b|\\bAzure_IR\\b|\\bAzure_RGB\\b|\\bAzure_Depth\\b|\\bGopro\\b|\\bToF\\b|\\bTI-Radar\\b|\\bVayyar\\b|\\bIntel_rgb\\b'
    AND extension <> '.txt'
    GROUP BY sensor

    UNION ALL

    SELECT 
        location AS condition_,
        COUNT(*) AS row_count
    FROM incabin_db.data_path
    WHERE location REGEXP '\\bla\\b|\\bpa\\b|\\bcc\\b|\\bco\\b'
    AND extension <> '.txt'
    GROUP BY location

    UNION ALL

    SELECT 
        gender AS condition_,
        COUNT(*) AS row_count
    FROM incabin_db.data_path
    WHERE gender REGEXP '\\bm\\b|\\bf\\b|\\bt\\b'
    AND extension <> '.txt'
    GROUP BY gender

    UNION ALL

    SELECT 
    age_group AS condition_,
    SUM(row_count) AS row_count
    FROM (
    SELECT 
        CASE 
            WHEN age BETWEEN 10 AND 20 THEN 'Age_10_to_20'
            WHEN age BETWEEN 21 AND 30 THEN 'Age_21_to_30'
            WHEN age BETWEEN 31 AND 40 THEN 'Age_31_to_40'
            WHEN age BETWEEN 41 AND 50 THEN 'Age_41_to_50'
            WHEN age BETWEEN 51 AND 60 THEN 'Age_51_to_60'
            WHEN age BETWEEN 61 AND 70 THEN 'Age_61_to_70'
            WHEN age BETWEEN 71 AND 80 THEN 'Age_71_to_80'
            WHEN age BETWEEN 81 AND 90 THEN 'Age_81_to_90'
            WHEN age BETWEEN 91 AND 100 THEN 'Age_91_to_100'
        END AS age_group,
        COUNT(DISTINCT Unique_subjects) AS row_count
    FROM 
        incabin_db.data_path
    WHERE 
        age BETWEEN 0 AND 100
    GROUP BY 
        age_group
    ) AS AgeGroups
        WHERE
        age_group IS NOT NULL
        GROUP BY 
        age_group

    UNION ALL

    SELECT 
        spectacles AS condition_,
        COUNT(*) AS row_count
    FROM incabin_db.data_path
    WHERE spectacles REGEXP '\\bwg\\b|\\bng\\b|\\bsg\\b'
    AND extension <> '.txt' 
    GROUP BY spectacles

    UNION ALL

    SELECT 
        extension AS condition_,
        COUNT(*) AS row_count
    FROM incabin_db.data_path
    WHERE extension REGEXP '\\bnpy\\b|\\bjpeg\\b|\\bpng\\b|\\bmp4\\b|\\bcsv\\b|\\bpcl\\b|\\btxt\\b'
    GROUP BY extension

    UNION ALL

    SELECT 
        CASE 
            WHEN lux_values BETWEEN 00000 AND 00050 THEN 'Low_Ambience'
            WHEN lux_values BETWEEN 00051 AND 00700 THEN 'Moderate_Ambience'
            WHEN lux_values BETWEEN 00701 AND 99999 THEN 'Intense_Ambience'
        END AS condition_,
        COUNT(*) AS row_count
    FROM incabin_db.data_path
    WHERE lux_values BETWEEN 00000 AND 99999
    AND extension <> '.txt'
    GROUP BY condition_

    UNION ALL

    SELECT 
        'Unique_Subjects' AS condition_,
        COUNT(DISTINCT Unique_subjects) AS row_count
    FROM incabin_db.data_path
) AS subquery
GROUP BY condition_
 ON DUPLICATE KEY UPDATE row_count = VALUES(row_count);
"""

# Connect to the database and execute the query
try:
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute(sql_query_data_vis)
    connection.commit()
    print("Query executed successfully for data_vis.")
except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    cursor.close()
    connection.close()
    print("Connection closed.")

# Record the end time and calculate the execution time
end_execution_time = time.perf_counter()
execution_time = end_execution_time - start_execution_time
print(f"Execution time: {execution_time} seconds")
