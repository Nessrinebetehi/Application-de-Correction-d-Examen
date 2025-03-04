import mysql.connector
import threading
import pandas as pd
import time
import random
from tkinter import filedialog, messagebox
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
    """Insert exam data into the database while disabling foreign key checks"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # تعطيل قيود المفتاح الأجنبي
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

        # إدراج بيانات الامتحان
        sql = "INSERT INTO exams (candidat_id, module_name, coefficient) VALUES (%s, %s, %s)"
        cursor.execute(sql, (candidat_id, module, coefficient))

        # إعادة تفعيل قيود المفتاح الأجنبي
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

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
    
# students page //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\\
def get_salle_names():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name_salle FROM salles")
        salles = [row[0] for row in cursor.fetchall()]
        conn.close()
        return salles
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []

def update_salle_comboboxes(st_salle_combobox, at_salle_combobox, r_salle_combobox, root_window):
    """تحديث جميع القوائم المنسدلة كل 5 ثوانٍ"""
    salles = get_salle_names()
    
    # تحديث القوائم الثلاثة
    for combobox in [st_salle_combobox, at_salle_combobox, r_salle_combobox]:
        combobox['values'] = salles
        if salles:
            combobox.current(0)  # تحديد أول خيار بشكل افتراضي

    # جدولة التحديث التالي بعد 5 ثوانٍ
    root_window.after(5000, lambda: update_salle_comboboxes(st_salle_combobox, at_salle_combobox, r_salle_combobox, root_window))
    

    
def get_exam_options():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT exam_option FROM institutes")
        options = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return options if options else ["No Options Available"]

    except mysql.connector.Error as err:
        print("Database Error:", err)
        return ["Error Fetching Data"]
    
def generate_anonymous_id():
        first_digit = random.choice("123456789")
        other_digits = ''.join(random.choices("0123456789", k=7))
        return first_digit + other_digits

def save_student(name, surname, dob, sex, salle_code, exam_option):
    """Save student details in the database while preventing duplicates"""
    if not (name and surname and dob and sex and exam_option):
        return "❌ All fields are required!"
    
    conn = get_db_connection()
    if conn is None:
        return "❌ Database connection failed!"
    
    cursor = conn.cursor()
    
    try:
        # 🔹 1. التحقق مما إذا كان الطالب مسجلاً بالفعل
        cursor.execute(
            """
            SELECT id FROM candidats WHERE name = %s AND surname = %s AND birthday = %s
            """,
            (name, surname, dob)
        )
        existing_student = cursor.fetchone()
        
        if existing_student:
            return "❌ This student is already registered!"
        
        

        # 🔹 2. إدراج الطالب إذا لم يكن مسجلاً مسبقًا
        anonymous_id = generate_anonymous_id()
        cursor.execute(
            """
            INSERT INTO candidats (name, surname, birthday, sex, anonymous_id, salle_name)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (name, surname, dob, sex, anonymous_id, salle_code if salle_code else None)
        )
        
        conn.commit()
        return "✅ Student data saved successfully!"
    
    except mysql.connector.Error as err:
        return f"❌ Database error: {err}"
    
    finally:
        cursor.close()
        conn.close()

def import_students_from_excel(file_path):
    """استيراد بيانات الطلاب من ملف Excel وحفظها في قاعدة البيانات"""
    try:
        df = pd.read_excel(file_path)  # قراءة ملف Excel إلى DataFrame

        # التحقق مما إذا كانت الأعمدة المطلوبة موجودة
        required_columns = {"Name", "Surname", "Birthday", "Sex", "Salle Name", "Exam Option"}
        if not required_columns.issubset(df.columns):
            return "❌ ملف Excel يجب أن يحتوي على الأعمدة التالية: Name, Surname, Birthday, Sex, Salle Name, Exam Option"

        # تحويل تاريخ الميلاد إلى نص بصيغة YYYY-MM-DD لتجنب خطأ MySQL
        df["Birthday"] = pd.to_datetime(df["Birthday"], errors='coerce').dt.strftime('%Y-%m-%d')

        conn = get_db_connection()
        cursor = conn.cursor()

        # إدخال البيانات إلى الجدول "candidats"
        for _, row in df.iterrows():
            # التحقق من أن الصف لا يحتوي على قيم فارغة لتجنب الأخطاء
            if pd.notnull(row["Name"]) and pd.notnull(row["Surname"]) and pd.notnull(row["Birthday"]):
                anonymous_id = generate_anonymous_id()  # توليد معرف مجهول لكل طالب
                
                sql = """
                    INSERT INTO candidats (name, surname, birthday, sex, salle_name, anonymous_id, decision)
                    VALUES (%s, %s, %s, %s, %s, %s, 'Pending')
                """
                cursor.execute(sql, (row["Name"], row["Surname"], row["Birthday"], row["Sex"], row["Salle Name"], anonymous_id))

        conn.commit()
        cursor.close()
        conn.close()
        return "✅ تم استيراد البيانات بنجاح!"
    
    except Exception as e:
        return f"❌ خطأ أثناء الاستيراد: {str(e)}"
    
    
#attendee list//////////////////////////////////////////////////////////////////////

def get_candidates_by_salle(salle):
    """Fetch candidates by salle name."""
    try:
        conn = get_db_connection()
        if conn is None:
            return []

        cursor = conn.cursor()
        cursor.execute("SELECT name, surname, salle_name FROM candidats WHERE salle_name = %s", (salle,))
        candidates = cursor.fetchall()

        cursor.close()
        conn.close()

        return candidates

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to fetch data: {err}")
        return []
    

def get_all_candidates():
    """Fetch all candidates from the database."""
    try:
        conn = get_db_connection()
        if conn is None:
            return []

        cursor = conn.cursor()
        cursor.execute("SELECT name, surname, anonymous_id FROM candidats")
        candidates = cursor.fetchall()

        cursor.close()
        conn.close()

        return candidates

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to fetch candidates: {err}")
        return []
    
def import_absences():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
    if not file_path:
        return
    
    try:
        df = pd.read_excel(file_path)  # Read the Excel file
        
        # Check required columns
        required_columns = {"name", "surname", "salle", "audience"}
        if not required_columns.issubset(df.columns):
            messagebox.showerror("Error", "Invalid file format. Required columns: name, surname, salle, audience")
            return
        
        conn = get_db_connection()
        cursor = conn.cursor()

        for _, row in df.iterrows():
            name, surname, salle, audience = row["name"], row["surname"], row["salle"], row["audience"]
            
            if audience == "A":  # Only update absence count if the person is absent
                update_query = """
                UPDATE candidats 
                SET absence = absence + 1 
                WHERE name = %s AND surname = %s AND salle_name = %s
                """
                cursor.execute(update_query, (name, surname, salle))
        
        conn.commit()
        cursor.close()
        conn.close()

        messagebox.showinfo("Success", "Absences updated successfully!")
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to import file: {e}")
#correction_page////////////////////////////////////////////////////////////////////////////
def fetch_exam_modules():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT module_name FROM exams")
        modules = [row[0] for row in cursor.fetchall()]
        connection.close()
        return modules
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return []
    
def fetch_exam_details(module_name):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT module_name, coefficient FROM exams WHERE module_name = %s", (module_name,))
        result = cursor.fetchone()
        connection.close()
        return result if result else ("", "")
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return ("", "")