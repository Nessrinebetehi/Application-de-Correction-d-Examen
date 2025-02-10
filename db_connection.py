import mysql.connector
from mysql.connector import Error

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="",
            database="Anonymat"  # يربط القاعدة تلقائيًا
        )
        if connection.is_connected():
            print("✅ Connected to the database")
            return connection
    except Error as err:
        print(f"❌ Error: {err}")
        return None

def close_connection(connection):
    if connection and connection.is_connected():
        connection.close()
        print("🔌 Connection closed.")
