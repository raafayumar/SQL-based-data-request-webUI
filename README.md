# SQL-based-data-request-webUI

## Overview

This repository contains a set of Python scripts for managing and accessing stored data through a SQL-based data request web user interface (WebUI). The main functionality is provided by the `main.py` script, which creates a local web server allowing users to interact with the stored data.

## Scripts

### main.py

The `main.py` script serves as the main entry point for the SQL-based data request WebUI. It creates a local web server and provides functionalities for data access, request submission, and dashboard visualization.

### auto_db_updator.py

The `auto_db_updator.py` script automates the process of updating the database with new data. It handles periodic updates to ensure the database remains current.

### manual_db_update.py

The `manual_db_update.py` script provides a manual option for updating the database with new data. It allows users to initiate database updates as needed.


## WebUI Functionality

The SQL-based data request WebUI provides the following functionality:

- **Authentication**: Users are required to provide credentials to access the WebUI.
- **Data Request Page**: Once authenticated, users can access the data request page where they can specify criteria such as task, sensor, location, gender, and file extension for data retrieval.
- **Data Summary**: After selecting desired options, users can submit their request and receive a summary of the selected options, including total files, annotated files, file size, and selected options.
- **File Download**: Users have the option to download selected files, which are gathered from the server and sent to the user's local PC as a zip file.
- **Dashboard**: The WebUI includes a dashboard feature displaying graphs and visualizations of the stored data.

## Usage

To use the SQL-based data request WebUI:

1. Run the `main.py` script to start the local web server.
2. Access the WebUI through a web browser.
3. Authenticate using the provided credentials.
4. Navigate through the data request page, select desired options, and submit the request.
5. Review the summary of selected options and download the requested files as needed.
6. Explore the dashboard for visual representations of the stored data.

## Additional Information

- For more details on the database updater scripts and their usage, refer to the respective script files.
- Ensure that the necessary dependencies are installed before running the scripts.
- For troubleshooting or further assistance, refer to the documentation or contact the repository owner.

