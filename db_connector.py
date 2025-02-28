import mysql.connector

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="root",
            database="anonymat"
        )
        if conn.is_connected():
            print("✅ Successfully connected to the database!")
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Database Connection Error: {err}")
        return None

# اختبار الاتصال عند تشغيل الملف مباشرة
if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        conn.close()
        print("🔌 Connection closed.")
