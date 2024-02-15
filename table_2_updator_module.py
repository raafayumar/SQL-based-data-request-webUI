import mysql.connector

def table_two():
    cursor = None
    connection = None

    # Function to create the "data_vis" table if not exists
    def create_data_vis_table(cursor):
        cursor.execute("USE incabin_db")
        cursor.execute("""DROP TABLE IF EXISTS incabin_db.data_vis""")
        cursor.execute("""
            CREATE TABLE data_vis (
                `condition_` VARCHAR(255),
                `row_count` INT 
            )
        """)

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

        # Create the "data_vis" table if not exists
        create_data_vis_table(cursor)

        # Execute the SQL query for data_vis
        cursor.execute(sql_query_data_vis)
        connection.commit()
        print("Query executed successfully for data_vis.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()
            print("Connection closed.")

    return "table_2_created"
