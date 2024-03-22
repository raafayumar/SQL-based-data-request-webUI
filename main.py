import os
from flask import Flask, render_template, request, send_file, session, redirect, url_for, jsonify
import shutil
import tempfile
import mysql.connector
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys

path_to_data = r'/home/incabin/DATA/AutoVault/datafolder'

app = Flask(__name__)
app.secret_key = 'a5e537855c5534969268116424a49312e8f725f6879e626bbedf7dfed9e90abb'

# Global vars
abs_filepath = []
progress = 0
total_files = 0
done = 0

# Database connection configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Incabin@123",
    database="incabin_db",
    pool_size=10,  # Adjust the pool size as needed
    pool_name="mypool",
    pool_reset_session=True
)


# Function to check if the user is logged in
def is_logged_in():
    return 'username' in session


# Function to execute custom SQL query
def execute_custom_query(query, cursor):
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0] if result else None


# Function to fetch data from the database and generate the pie chart for tasks
def generate_task_pie_chart(cursor):
    task_queries = [
        "Seat_belt",
        "Hands_on_off_steering",
        "Gaze_detection",
        "Driver_face",
        "Driver_pose",
        "Driver_vitals",
        "Occupant_vitals",
        "Gesture_recognition",
        "Occupant",
        "Breathing"
    ]

    task_results = {}

    for task in task_queries:
        query = f"SELECT row_count FROM `incabin_db`.`data_vis` WHERE condition_ = '{task}';"  # Updated table name
        result = execute_custom_query(query, cursor)
        task_results[task] = result

    # Create a DataFrame for the pie chart
    df_task = pd.DataFrame(list(task_results.items()), columns=['Task', 'Files Detected'])

    # Create a Plotly pie chart for tasks
    fig_task = px.pie(df_task, names='Task', values='Files Detected', title='<b>Tasks</b>')
    fig_task.update_layout(title_x=0.5)

    # Save the plot to HTML file
    chart_html_task = fig_task.to_html(full_html=False)

    return chart_html_task


# Function to fetch data from the database and generate the pie chart for sensors
def generate_sensor_pie_chart(cursor):
    sensor_queries = [
        "Flir",
        "Azure_IR",
        "Azure_RGB",
        "Azure_Depth",
        "Gopro",
        "ToF",
        "TI-Radar",
        "Vayyar",
        "Intel_rgb"
    ]

    sensor_results = {}
    for sensor in sensor_queries:
        query = f"SELECT row_count FROM `incabin_db`.`data_vis` WHERE condition_ = '{sensor}';"  # Updated table name
        result = execute_custom_query(query, cursor)
        sensor_results[sensor] = result

    # Create a DataFrame for the pie chart
    df_sensor = pd.DataFrame(list(sensor_results.items()), columns=['Sensor', 'Files Detected'])

    # Create a Plotly pie chart for sensors
    fig_sensor = px.pie(df_sensor, names='Sensor', values='Files Detected',
                        title='<b>Sensors</b>')
    fig_sensor.update_layout(title_x=0.5)

    # Save the plot to HTML file
    chart_html_sensor = fig_sensor.to_html(full_html=False)

    return chart_html_sensor


# Function to fetch data from the database and generate the pie chart for locations
def generate_location_pie_chart(cursor):
    # Short and long forms for location
    location_mapping = {"pa": "Parking", "la": "lab", "co": "city outskirts", "cc": "city (Inside Banglore)"}
    location_results = {}

    for short_form, long_form in location_mapping.items():
        query = f"SELECT row_count FROM `incabin_db`.`data_vis` WHERE condition_ = '{short_form}';"  # Updated table name
        result = execute_custom_query(query, cursor)
        location_results[long_form] = result

    # Create a DataFrame for the pie chart
    df_location = pd.DataFrame(list(location_results.items()), columns=['location', 'Files Detected'])

    # Create a Plotly pie chart for locations
    fig_location = px.pie(df_location, names='location', values='Files Detected',
                          title='<b>Location</b>')
    fig_location.update_layout(title_x=0.5)

    # Save the plot to HTML file
    chart_html_location = fig_location.to_html(full_html=False)

    return chart_html_location


# Function to fetch data from the database and generate the pie chart for spectacles
def generate_spectacles_pie_chart(cursor):
    # Short and long forms for spectacles
    spectacles_mapping = {"sg": "Sun glasses", "ng": "Without glasses", "wg": "With glasses"}
    spectacles_results = {}

    for short_form, long_form in spectacles_mapping.items():
        query = f"SELECT row_count FROM `incabin_db`.`data_vis` WHERE condition_ = '{short_form}';"  # Updated table name
        result = execute_custom_query(query, cursor)
        spectacles_results[long_form] = result

    # Create a DataFrame for the pie chart
    df_spectacles = pd.DataFrame(list(spectacles_results.items()), columns=['Spectacles', 'Files Detected'])

    # Create a Plotly pie chart for spectacles
    fig_spectacles = px.pie(df_spectacles, names='Spectacles', values='Files Detected',
                            title='<b>Spectacles</b>')
    fig_spectacles.update_layout(title_x=0.5)

    # Save the plot to HTML file
    chart_html_spectacles = fig_spectacles.to_html(full_html=False)

    return chart_html_spectacles


# Function to fetch data from the database and generate the pie chart for gender
def generate_gender_pie_chart(cursor):
    # Short and long forms for gender
    gender_mapping = {"m": "Male", "f": "Female", "t": "Transgender"}
    gender_results = {}

    for short_form, long_form in gender_mapping.items():
        query = f"SELECT row_count FROM `incabin_db`.`data_vis` WHERE condition_ = '{short_form}';"  # Updated table name
        result = execute_custom_query(query, cursor)
        gender_results[long_form] = result

    # Create a DataFrame for the pie chart
    df_gender = pd.DataFrame(list(gender_results.items()), columns=['Gender', 'Files Detected'])

    # Create a Plotly pie chart for genders
    fig_gender = px.pie(df_gender, names='Gender', values='Files Detected',
                        title='<b>Gender</b>')
    fig_gender.update_layout(title_x=0.5)

    # Save the plot to HTML file
    chart_html_gender = fig_gender.to_html(full_html=False)

    return chart_html_gender


# Function to fetch data from the database and generate the pie chart for file extensions
def generate_extension_pie_chart(cursor):
    global total_files
    # Extension options
    extension_options = [".npy", ".jpeg", ".png", ".mp4", ".csv", ".pcl"]
    extension_results = {}
    for extension in extension_options:
        query = f"SELECT row_count FROM `incabin_db`.`data_vis` WHERE condition_ = '{extension}';"  # Updated table name
        result = execute_custom_query(query, cursor)
        extension_results[extension] = result

    # Create a DataFrame for the pie chart
    df_extension = pd.DataFrame(list(extension_results.items()), columns=['Extension', 'Files Detected'])

    # Create a Plotly pie chart for extensions
    fig_extension = px.pie(df_extension, names='Extension', values='Files Detected',
                           title='<b>Extension</b>')
    fig_extension.update_layout(title_x=0.5)

    # Save the plot to HTML file
    chart_html_extension = fig_extension.to_html(full_html=False)
    tfiles = df_extension['Files Detected']
    total_files = 0
    for tf in tfiles:
        if not pd.isna(tf):
            total_files += tf
    # print(total_files)
    return chart_html_extension


# Function to fetch data from the database and generate the bar plot for age
def generate_age_bar_plot(cursor):
    # Age options
    age_options = ["Age_10_to_20", "Age_21_to_30", "Age_31_to_40", "Age_41_to_50", "Age_51_to_60", "Age_61_to_70",
                   "Age_71_to_80", "Age_81_to_90", "Age_91_to_100"]
    age_labels = ["10-20", "21-30", "31-40", "41-50", "51-60", "61-70", "71-80", "81-90", "91-100"]

    age_results = {}

    for age, label in zip(age_options, age_labels):
        query = f"SELECT row_count FROM `incabin_db`.`data_vis` WHERE condition_ = '{age}';"  # Updated table name
        result = execute_custom_query(query, cursor)
        age_results[label] = result

    # Create a DataFrame for the bar plot
    df_age = pd.DataFrame(list(age_results.items()), columns=['Age', 'Subjects'])

    # Create a Plotly bar plot for age
    fig_age = px.bar(df_age, x='Age', y='Subjects', text='Subjects', title='<b>Number of Subjects in Age Group</b>')
    fig_age.update_layout(title_x=0.5)

    # Save the plot to HTML file
    chart_html_age = fig_age.to_html(full_html=False)

    return chart_html_age


# Function to fetch data from the database and generate the progress chart for extension
def generate_extension_progress_chart(cursor):
    # print(total_files)
    # Extension options
    extension_options = '.txt'
    extension_results = {}

    query = f"SELECT row_count FROM `incabin_db`.`data_vis` WHERE condition_ = '{extension_options}';"  # Updated table name
    result = execute_custom_query(query, cursor)
    extension_results[extension_options] = result

    # Create a DataFrame for the progress chart
    df_extension = pd.DataFrame(list(extension_results.items()), columns=['Annotated Data', 'Files Detected'])

    # Create a Plotly radial gauge chart for extension progress
    fig_extension = go.Figure()

    fig_extension.add_trace(go.Indicator(
        mode="gauge+number",
        value=df_extension['Files Detected'].iloc[0],
        title={'text': '<b>Annotated Data</b>'},
        gauge={
            'axis': {'range': [None, total_files]},
            'steps': [
                {'range': [0, df_extension['Files Detected'].max() / 3], 'color': "lightgray"},
                {'range': [df_extension['Files Detected'].max() / 3, 2 * df_extension['Files Detected'].max() / 3],
                 'color': "gray"},
                {'range': [2 * df_extension['Files Detected'].max() / 3, df_extension['Files Detected'].max()],
                 'color': "darkgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': df_extension['Files Detected'].iloc[0]
            }
        }
    ))

    # Save the plot to HTML file
    chart_html_extension2 = fig_extension.to_html(full_html=False)

    return chart_html_extension2


# Function to fetch data from the database and generate the pie chart for lux values
def generate_lux_pie_chart(cursor):
    # Lux value options
    lux_options = ["Low_Ambience", "Moderate_Ambience", "Intense_Ambience"]
    lux_results = {}
    for lux_value in lux_options:
        query = f"SELECT row_count FROM `incabin_db`.`data_vis` WHERE condition_ = '{lux_value}';"  # Updated table name
        result = execute_custom_query(query, cursor)
        lux_results[lux_value] = result

    # Create a DataFrame for the pie chart
    df_lux = pd.DataFrame(list(lux_results.items()), columns=['Ambience', 'Files Detected'])

    # Create a Plotly pie chart for lux values
    fig_lux = px.pie(df_lux, names='Ambience', values='Files Detected',
                     title='<b>Ambient Lighting</b>')
    fig_lux.update_layout(title_x=0.5)

    # Save the plot to HTML file
    chart_html_lux = fig_lux.to_html(full_html=False)

    return chart_html_lux


def generate_Unique_subjects(cursor):
    query = f"SELECT row_count FROM `incabin_db`.`data_vis` WHERE condition_ = 'Unique_subjects';"
    result = execute_custom_query(query, cursor)
    chart_html_Unique_subjects = result
    return chart_html_Unique_subjects


# Function to check if the user is logged in
def is_logged_in():
    return 'username' in session


# Function to check if the user is logged in
def is_logged_in():
    return 'username' in session


@app.route('/')
def index():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username and password match
        if username == 'admin' and password == '123':
            session['username'] = username
            return redirect(url_for('index'))

        # Incorrect credentials
        return render_template('login.html', error='Invalid username or password')

    # GET request for login page
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


annotated_files_paths = []
not_annotated_path = []
result = 0


@app.route('/search', methods=['POST'])
def search():
    print('SEARCH', file=sys.stdout)
    global abs_filepath, result, annotated_files_paths, not_annotated_path  # Ensure variables are accessible

    # Initialize variables
    result = 0
    annotated_files_paths = []

    conn, cursor = connect_to_mysql()
    file_size = 0

    if not is_logged_in():
        return redirect(url_for('login'))

    try:
        # Rest of the code for constructing and executing the SQL query
        task = request.form.get('task')
        sensor = request.form.get('sensor')
        date = request.form.get('date')  # Add date query parameter

        # Inside the /search route
        query = "SELECT absolute_path FROM incabin_db.data_path WHERE extension NOT LIKE %s "

        placeholders = ['%.hpt']

        if task and task != '.*' and task != 'all':
            query += f" AND task regexp '\\\\b{task}\\\\b'"
        if sensor and sensor != '.*' and sensor != 'all':
            query += f" AND sensor regexp '\\\\b{sensor}\\\\b'"

        # Mapping short forms for locations
        location_short_forms = {
            'Lab': 'la',
            'city outskirts': 'co',
            'city (inside bangalore)': 'cc',
            'Parking': 'pa'
        }

        # Inside the /search route
        locations = request.form.getlist('location')  # Get multiple selected options as a list

        # Construct the query to handle multiple selected options for location
        if 'all' in locations:
            # If 'all' is selected, no need to filter by location
            pass
        else:
            if locations and locations != ['.*']:
                query += " AND ("
                placeholders_loc = []  # Placeholder list for locations
                for location in locations:
                    short_form = location_short_forms.get(location, location)
                    query += "location LIKE %s OR "
                    placeholders_loc.append(f"%{short_form}%")
                # Remove the last ' OR ' from the query
                query = query[:-4]
                query += ")"
                placeholders.extend(placeholders_loc)

        # Mapping short forms for gender
        gender_short_forms = {
            'Male': 'm',
            'Female': 'f',
            'Trans': 't'
        }

        gender = request.form.get('gender')
        if gender and gender != '.*' and gender != 'all':
            short_form = gender_short_forms.get(gender, gender)
            query += f" AND gender LIKE %s "
            placeholders.append(f'%{short_form}%')

        age_from = request.form.get('age_from')
        age_operator = request.form.get('age_operator')
        age_to = request.form.get('age_to')

        if age_from and age_from != '.*':
            if age_operator == 'Range' and age_to and age_to != '.*':
                # Include records where age is within the specified range or age is NULL
                query += f" AND (age BETWEEN %s AND %s OR age IS NULL)"
                placeholders.extend([int(age_from), int(age_to)])
            elif age_operator == 'And' and age_to and age_to != '.*':
                # Include records where age is equal to either age_from or age_to or age is NULL
                query += f" AND (age = %s OR age = %s OR age IS NULL)"
                placeholders.extend([int(age_from), int(age_to)])
            else:
                # Include records where age is equal to age_from or age is NULL
                query += f" AND (age = %s OR age IS NULL)"
                placeholders.extend([int(age_from)])

        # Mapping short forms for spectacles
        spectacles_short_forms = {
            'With Glasses': 'wg',
            'No Glasses': 'ng',
            'Sun Glasses': 'sg'
        }

        spectacles = request.form.get('spectacles')
        if spectacles and spectacles != '.*' and spectacles != 'all':
            short_form = spectacles_short_forms.get(spectacles, spectacles)
            query += f" AND spectacles LIKE %s "
            placeholders.append(f"%{short_form}%")

        # Lux_Values condition
        lux_values_range = request.form.get('lux_values_range')
        lux_values_conditions = {
            '00001 to 00050': 'Lux_Values BETWEEN 00001 AND 00050',
            '00051 to 00700': 'Lux_Values BETWEEN 00051 AND 00700',
            '00701 to 99999': 'Lux_Values BETWEEN 00701 AND 99999'
        }

        if lux_values_range and lux_values_range in lux_values_conditions:
            query += f" AND {lux_values_conditions[lux_values_range]}"

        # Extension condition
        extension = request.form.get('extension')
        if extension and extension != '.*' and extension != 'all':
            query += f" AND extension LIKE %s "
            placeholders.append(f"%{extension}%")

        # Add date condition
        if date:
            query += f" AND date = %s "
            placeholders.append(date)

        # print("Query:", query)
        # print("Placeholders:", placeholders)

        cursor.execute(query, tuple(placeholders))

        result_path = cursor.fetchall()  # Consuming the result set
        result = len(result_path)  # Number of total files

        abs_filepath = [item for sublist in result_path for item in sublist]  # convert the tuple to list

        if len(query) > 75:
            new_query = query.replace('extension NOT LIKE %s  AND', '')
            placeholders.pop(0)
            annotated_data_query = new_query + " AND txt_exist = 1"
            non_annotated_data_query = new_query + " AND txt_exist = 0"

        else:
            annotated_data_query = "SELECT absolute_path FROM incabin_db.data_path WHERE txt_exist = 1"
            non_annotated_data_query = "SELECT absolute_path FROM incabin_db.data_path WHERE txt_exist = 0"
            placeholders.pop(0)

        # print(new_query)
        cursor.execute(annotated_data_query, tuple(placeholders))
        annotated_paths = cursor.fetchall()

        # Has both txt files and the data files
        annotated_files_paths = [item for sublist in annotated_paths for item in sublist]  # convert the tuple to list

        cursor.execute(non_annotated_data_query, tuple(placeholders))
        non_annotated_path = cursor.fetchall()

        # has non annotated data files only.
        not_annotated_path = [item for sublist in non_annotated_path for item in sublist]  # convert the tuple to list
        # print(len(not_annotated_path))

        # Get selected options
        selected_options = {
            'task': task,
            'sensor': sensor,
            'location': locations,
            'gender': gender,
            'age_from': age_from,
            'age_operator': age_operator,
            'age_to': age_to,
            'spectacles': spectacles,
            'lux_values_range': lux_values_range,
            'extension': extension,
            'date': date  # Add date to selected options
        }

        # Get file size
        for f in abs_filepath:
            file_size += os.path.getsize(f)
        total_size = round((file_size / (1024 * 1024 * 1024)), 2)

        # Return a valid response with selected options
        return render_template('result.html', result=result,
                               txt_files_count=int((len(annotated_files_paths) / 2)),
                               non_anno_file_count=len(not_annotated_path),
                               total_size=total_size, **selected_options)

    except mysql.connector.Error as err:
        # Handle database errors
        return f"Database Error: {err}"

    finally:
        print('cursor closed', file=sys.stdout)
        if cursor is None:
            conn, cursor = connect_to_mysql()
        cursor.close()
        close_db()  # Close the database connection


def connect_to_mysql():
    print('called connection', file=sys.stdout)
    global db
    try:
        # Check if the connection is active or if it's None
        if db is None:
            print('inside if statement', file=sys.stdout)
            db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Incabin@123",
                database="incabin_db",
                pool_size=10,  # Adjust the pool size as needed
                pool_name="mypool",
                pool_reset_session=True
            )
            print('Connected to MySQL database', file=sys.stdout)

        cursor = db.cursor()
        return db, cursor

    except mysql.connector.Error as e:
        print(f"Error: {e}", file=sys.stdout)
        return None, None


def close_db():
    global db
    if db is not None and db.is_connected():
        db.close()
        db = None
        print('Connection closed', file=sys.stdout)


@app.route('/download', methods=['POST'])
def download():
    global progress, total_files, done
    progress = 0
    done = 0

    start_time = time.time()
    temp_dir = tempfile.mkdtemp()

    try:
        # Get the value of include annotated files checkbox
        include_annotated_files = request.form.get('include_annotated_flag')

        # If include annotated files is checked, include both annotated_files_paths and different_extension_paths
        if include_annotated_files:
            files_to_download = annotated_files_paths
            total_files = len(annotated_files_paths)
        else:
            files_to_download = not_annotated_path
            total_files = len(not_annotated_path)

        for progress, file_path in enumerate(files_to_download):
            dest_path = os.path.join(temp_dir, os.path.relpath(file_path, path_to_data))
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copyfile(file_path, dest_path)

        # Zip the files
        shutil.make_archive(temp_dir, 'tar', temp_dir)
        total_time = time.time() - start_time
        print(total_time, file=sys.stdout)
        done = 1
        return send_file(f'{temp_dir}.tar', as_attachment=True, download_name='selected_files.tar')

    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)


@app.route('/get_progress')
def get_progress():
    global progress, done  # Use the global variable
    done = str(done)

    # Calculate progress percentage
    prog_bar = int((progress + 1) / total_files * 100)
    return jsonify({'progress': prog_bar, 'done': done})


@app.route('/refresh', methods=['GET'])
def refresh():
    # Redirect to the index page to refresh the GUI
    return redirect(url_for('index'))


@app.route('/visualization')
def visualization():
    if not is_logged_in():
        return redirect(url_for('login'))

    connection = mysql.connector.connect(host="localhost", user="root", password="Incabin@123", database="incabin_db")

    cursor = connection.cursor()
    sub_numb = generate_Unique_subjects(cursor)

    chart_html_task = generate_task_pie_chart(cursor)
    chart_html_sensor = generate_sensor_pie_chart(cursor)
    chart_html_location = generate_location_pie_chart(cursor)
    chart_html_spectacles = generate_spectacles_pie_chart(cursor)
    chart_html_gender = generate_gender_pie_chart(cursor)
    chart_html_extension = generate_extension_pie_chart(cursor)
    chart_html_age = generate_age_bar_plot(cursor)
    chart_html_extension2 = generate_extension_progress_chart(cursor)
    chart_html_lux = generate_lux_pie_chart(cursor)  # Added lux pie chart

    cursor.close()
    connection.close()

    return render_template('visualization.html', chart_html_task=chart_html_task,
                           chart_html_sensor=chart_html_sensor, chart_html_location=chart_html_location,
                           chart_html_spectacles=chart_html_spectacles, chart_html_gender=chart_html_gender,
                           chart_html_extension=chart_html_extension, chart_html_age=chart_html_age,
                           chart_html_extension2=chart_html_extension2, chart_html_lux=chart_html_lux,
                           sub_numb=sub_numb)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
