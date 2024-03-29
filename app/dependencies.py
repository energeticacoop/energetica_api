import mysql.connector
from dotenv import dotenv_values
import os
import requests

script_dir = os.path.dirname(__file__)
energetica_db_config = dotenv_values(os.path.join(script_dir, ".env.db"))
cels_db_config = dotenv_values(os.path.join(script_dir, ".env.cels.db"))
google_api_key = dotenv_values(os.path.join(script_dir, ".env.googleapikey"))[
    "GOOGLE_API_KEY"]


def get_db_connection(database):
    db_config = cels_db_config if database == "cels" else energetica_db_config
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as e:
        print("Error:", e)
        return None


def get_db_query_result(sql_query, database="energetica"):
    connection = get_db_connection(database)
    if connection is None:
        return False

    try:
        cursor = connection.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchone(
        )[0] if database == "energetica" else dict(zip([column[0] for column in cursor.description], cursor.fetchone()))
    except mysql.connector.Error as e:
        print("Error:", e)
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    return result


def get_json_from_google_spreadsheet_api(spreadsheet_id, named_range):
    api_url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{named_range}?key={google_api_key}'
    try:
        # Send a GET request to the API
        response = requests.get(api_url)
        response.raise_for_status()  # This will raise an exception for non-200 status codes

        # Parse the JSON response
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        # Handle general request exceptions
        raise e
