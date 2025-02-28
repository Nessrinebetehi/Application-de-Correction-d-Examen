import mysql.connector
import random
import string

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

# Test connection when running the file directly
if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        conn.close()
        print("🔌 Connection closed.")
# option page //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\

def op_save_data(institute_name, exam_option, name_post, nbr_exams):
    """Save data in the institutes table"""
    if not institute_name or not exam_option or not name_post:
        return "❌ Please fill in all fields!"

    conn = get_db_connection()
    if conn is None:
        return "❌ Database connection failed!"

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO institutes (institute_name, exam_option, name_post, nbr_exams) VALUES (%s, %s, %s, %s)",
            (institute_name, exam_option, name_post, nbr_exams)
        )
        conn.commit()
        return "✅ Data saved successfully!"
    except mysql.connector.Error as err:
        return f"❌ Database error: {err}"
    finally:
        cursor.close()
        conn.close()
#exams_window///////////////////////////////////////////////////////////////////////////////////

def insert_exam(candidat_id, module, coefficient):
    """Insert exam data into the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "INSERT INTO exams (candidat_id, module_name, coefficient) VALUES (%s, %s, %s)"
        cursor.execute(sql, (candidat_id, module, coefficient))

        conn.commit()
        cursor.close()
        conn.close()
        
        return True  # Successfully inserted
    except mysql.connector.Error as err:
        return str(err)  # Return the error if it occurs
    
def get_exams():
    """Retrieve all exams from the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "SELECT id, module_name, coefficient FROM exams"
        cursor.execute(sql)
        exams = cursor.fetchall()

        cursor.close()
        conn.close()
        
        return exams
    except mysql.connector.Error as err:
        return []

def delete_exam(exam_id):
    """Delete an exam based on ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "DELETE FROM exams WHERE id = %s"
        cursor.execute(sql, (exam_id,))

        conn.commit()
        cursor.close()
        conn.close()
        
        return True
    except mysql.connector.Error as err:
        return str(err)
#exams_window///////////////////////////////////////////////////////////////////////////////////

#salles_window///////////////////////////////////////////////////////////////////////////////////

def generate_code_salle():
    """Generate a unique room code in the format SALLE-XXXX"""
    while True:
        random_code = "SALLE-" + ''.join(random.choices(string.digits, k=4))  # Example: SALLE-1234
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT code_salle FROM salles WHERE code_salle = %s", (random_code,))
        result = cursor.fetchone()
        conn.close()
        if not result:  # If the code is not already used, accept it
            return random_code

def add_salle(name, capacity, institute_id=1):
    """Add a new room to the database"""
    code_salle = generate_code_salle()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO salles (code_salle, name_salle, capacity, institute_id) VALUES (%s, %s, %s, %s)",
            (code_salle, name, capacity, institute_id)
        )
        conn.commit()
        conn.close()
        return code_salle  # Return the added code
    except Exception as e:
        conn.close()
        raise e  # Re-raise the exception to handle it in the UI

def get_all_salles():
    """Retrieve all rooms from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT code_salle, name_salle, capacity FROM salles")
    salles = cursor.fetchall()
    conn.close()
    return salles  # Return the list of rooms

def delete_salle(code_salle):
    """Delete a room from the database using the code"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM salles WHERE code_salle = %s", (code_salle,))
    conn.commit()
    conn.close()
#salles_window///////////////////////////////////////////////////////////////////////////////////
# option page //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\\
