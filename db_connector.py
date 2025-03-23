#db_connector.py
import secrets
import mysql.connector
import threading
import pandas as pd
import tkinter as tk
from datetime import datetime
from tkinter import filedialog
import os
import time
import random
from tkinter import filedialog, messagebox
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from mysql.connector import Error
import re

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "root"),
            database=os.getenv("DB_NAME", "anonymat"),
            ssl_ca="/app/tidb-ca.pem",  # المسار الكامل على Render
            ssl_verify_cert=True
        )
        if conn.is_connected():
            print("✅ Successfully connected to the database!")
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Database Connection Error: {err}")
        return None

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

def delete_all_data(confirm_window, entry):
    """حذف جميع البيانات من الجداول عند تأكيد المستخدم."""
    if entry.get() == "YES":
        conn = get_db_connection()
        if conn is None:
            messagebox.showerror("Error", "Failed to connect to database.")
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM exams")
            cursor.execute("DELETE FROM candidats")
            cursor.execute("DELETE FROM salles")
            cursor.execute("DELETE FROM institutes")
            cursor.execute("DELETE FROM professors")
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "All data has been deleted successfully.")
            confirm_window.destroy()

        except Exception as err:
            messagebox.showerror("Error", f"Database error: {err}")
            confirm_window.destroy()
    else:
        messagebox.showwarning("Warning", "Incorrect input! Type 'YES' to confirm.")
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

def save_student(name, surname, dob, salle_code, exam_option):
    """Save student details in the database while preventing duplicates and checking salle capacity"""
    if not (name and surname and dob and exam_option):
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

        # 🔹 2. التحقق من سعة القاعة قبل الإضافة
        if salle_code:
            cursor.execute(
                """
                SELECT capacity FROM salles WHERE name_salle = %s
                """,
                (salle_code,)
            )
            salle_capacity = cursor.fetchone()
            
            if salle_capacity:
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM candidats WHERE salle_name = %s
                    """,
                    (salle_code,)
                )
                current_count = cursor.fetchone()[0]
                
                if current_count >= salle_capacity[0]:  # مقارنة العدد الحالي بالسعة القصوى
                    return f"❌ Salle {salle_code} is full! Capacity: {salle_capacity[0]}"
        
        # 🔹 3. إدراج الطالب إذا لم يكن مسجلاً مسبقًا ولم تتجاوز القاعة سعتها
        anonymous_id = generate_anonymous_id()
        cursor.execute(
            """
            INSERT INTO candidats (name, surname, birthday, anonymous_id, moyen, decision, absence, salle_name)
            VALUES (%s, %s, %s, %s, 10.00, 'Pending', 0, %s)
            """,
            (name, surname, dob, anonymous_id, salle_code if salle_code else None)
        )
        
        conn.commit()
        return "✅ Student data saved successfully!"
    
    except mysql.connector.Error as err:
        return f"❌ Database error: {err}"
    
    finally:
        cursor.close()
        conn.close()

def import_students_from_excel(file_path):
    """Import student data from an Excel file and save it to the database."""
    try:
        df = pd.read_excel(file_path)  # Read the Excel file into a DataFrame

        # Check if the required columns are present
        required_columns = {"Name", "Surname", "Birthday", "Salle Name", "Exam Option"}
        if not required_columns.issubset(df.columns):
            return "❌ The Excel file must contain the following columns: Name, Surname, Birthday, Salle Name, Exam Option"

        # Convert Birthday to text format YYYY-MM-DD to avoid MySQL errors
        df["Birthday"] = pd.to_datetime(df["Birthday"], errors='coerce').dt.strftime('%Y-%m-%d')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert data into the "candidats" table
        for _, row in df.iterrows():
            # Ensure the row does not contain null values to avoid errors
            if pd.notnull(row["Name"]) and pd.notnull(row["Surname"]) and pd.notnull(row["Birthday"]):
                anonymous_id = generate_anonymous_id()  # Generate an anonymous ID for each student
                
                sql = """
                    INSERT INTO candidats (name, surname, birthday, anonymous_id, moyen, decision, absence, salle_name)
                    VALUES (%s, %s, %s, %s, 10.00, 'Pending', 0, %s)
                """
                cursor.execute(sql, (row["Name"], row["Surname"], row["Birthday"], anonymous_id, row["Salle Name"]))

        conn.commit()
        cursor.close()
        conn.close()
        return "✅ Data imported successfully!"
    
    except Exception as e:
        return f"❌ Error during import: {str(e)}"


    
# students page //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\\

# Prof page //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\\
def generate_password(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def fetch_modules():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT module_name FROM exams")
        modules = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return modules
    except mysql.connector.Error as e:
        print("Database Error:", e)
        return []


def add_professor(name, surname, email, correction, module):
    try:
        conn = get_db_connection()
        if conn is None:
            return "Database connection failed!", None

        cursor = conn.cursor()
        if cursor is None:
            return "Cursor creation failed!", None


        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return "Invalid email format!", None


        cursor.execute("SELECT id FROM professors WHERE email = %s", (email,))
        if cursor.fetchone():
            return "Email already exists!", None


        password = generate_password()
        

        cursor.execute(
            "INSERT INTO professors (name, surname, email, correction, password, module) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, surname, email, int(correction), password, module)
        )
        conn.commit()
        return "Professor added successfully!", password

    except mysql.connector.Error as e:
        return f"Database Error: {e}", None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

            
def get_profs_from_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, email, password, Correction, surname FROM professors")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        print("Database Error:", e)
        return []
    
def delete_professor(email):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()


        cursor.execute("SELECT * FROM professors WHERE email = %s", (email,))
        if cursor.fetchone() is None:
            return "Professor not found!"


        cursor.execute("DELETE FROM professors WHERE email = %s", (email,))
        conn.commit()

        return "Professor deleted successfully!"
    
    except mysql.connector.Error as e:
        return f"Database Error: {e}"
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def send_emails():
    SENDER_EMAIL = "temouchentpfc@gmail.com"
    SENDER_PASSWORD = "xrgg eqlu qkji tdcc"
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

    professors = get_profs_from_db()
    if not professors:
        print("No professors found in the database.")
        return

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        for prof in professors:
            name, email, password, correction, surname = prof
            subject = "Your Account Details"
            body = f"""
            Salam alikoum Prof. {name} {surname},

            Your account details are:
            📧 Email: {email}
            🔑 Password: {password}
            ✅ Correction Number: {correction}

            Please keep this information secure.

            Best regards,
            Your Team
            """

            msg = MIMEMultipart()
            msg["From"] = SENDER_EMAIL
            msg["To"] = email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            server.sendmail(SENDER_EMAIL, email, msg.as_string())

        server.quit()
        print("Emails sent successfully!")

    except Exception as e:
        print("Failed to send emails:", e)
# Prof page //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\\
    
#attendee list///////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\\\\\

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
#attendee list///////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\\\\\

#Result page///////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\\\\\
def institute_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name_post, nbr_exams FROM institutes LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result if result else ("No data", 0)  # Return tuple (name_post, nbr_exams)
    except Error:
        return ("Error", 0)  # Fallback values if fetch fails
    

import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from openpyxl.utils import get_column_letter

def calculate_candidate_moyen(candidat_id, conn):
    try:
        cursor = conn.cursor()
        query = """
            SELECT finale_g, coefficient 
            FROM exams 
            WHERE candidat_id = %s AND finale_g IS NOT NULL
        """
        cursor.execute(query, (candidat_id,))
        results = cursor.fetchall()

        if not results:
            return None

        weighted_sum = 0
        total_coefficient = 0
        for finale_g, coefficient in results:
            weighted_sum += finale_g * coefficient
            total_coefficient += coefficient

        if total_coefficient == 0:
            return None

        moyen = weighted_sum / total_coefficient
        moyen = max(0, min(20, moyen))

        update_query = "UPDATE candidats SET moyen = %s WHERE id = %s"
        cursor.execute(update_query, (moyen, candidat_id))
        conn.commit()
        return moyen
    except Error as err:
        print(f"Error calculating moyen: {err}")
        return None

def calculate_and_export_results(salle_name, language):
    try:
        # Database connection
        conn = get_db_connection()  # Assumes this exists
        cursor = conn.cursor()

        # Fetch candidates, their exam data, and absence for the selected salle
        query = """
            SELECT c.id, c.name, c.surname, c.birthday, c.absence,
                   GROUP_CONCAT(e.module_name SEPARATOR ',') AS modules,
                   GROUP_CONCAT(e.finale_g SEPARATOR ',') AS grades
            FROM candidats c
            LEFT JOIN exams e ON c.id = e.candidat_id
            WHERE c.salle_name = %s
            GROUP BY c.id, c.name, c.surname, c.birthday, c.absence
        """
        cursor.execute(query, (salle_name,))
        candidates = cursor.fetchall()

        if not candidates:
            print(f"No candidates found for salle: {salle_name}")
            return

        # Prepare data for Excel
        data = []
        module_list = None  # To use for headers later
        for candidat_id, name, surname, birthday, absence, modules, grades in candidates:
            # Calculate moyen for this candidate
            moyen = calculate_candidate_moyen(candidat_id, conn)
            
            # Store the original moyen for sorting purposes
            moyen_for_sorting = moyen if moyen is not None else -1  # Use -1 for N/A to rank them low
            
            # Determine what to display in the Moyen column based on absence
            if absence is not None and absence > 2:
                moyen = "Rejected" if language == "English" else "مرفوض"
                moyen_for_sorting = -1  # Treat "Rejected" as the lowest rank
            else:
                moyen = "N/A" if moyen is None else moyen

            # Format birthday for Excel compatibility
            if isinstance(birthday, str):
                birthday = datetime.strptime(birthday, '%Y-%m-%d')  # Parse if string
            elif birthday is None:
                birthday = "N/A"
            # birthday remains a datetime object, which pandas will handle for Excel

            # Split grades and modules into a list
            module_list = modules.split(',') if modules else []
            grade_list = [float(g) if g else "N/A" for g in (grades.split(',') if grades else [])]

            # Construct row with an additional column for sorting
            row = [name, surname, birthday] + grade_list + [moyen, moyen_for_sorting]
            data.append(row)

        # Define column headers based on language (include a hidden sorting column)
        if language == "Arabic":
            headers = ["الاسم", "اللقب", "تاريخ الميلاد"]  # Name, Surname, Birthday
            headers += module_list  # Just the module names
            headers.append("المعدل")  # Moyen
            headers.append("Sort_Moyen")  # Hidden column for sorting
            default_filename = f"نتائج_{salle_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        else:  # English
            headers = ["Name", "Surname", "Birthday"]
            headers += module_list  # Just the module names
            headers.append("Moyen")
            headers.append("Sort_Moyen")  # Hidden column for sorting
            default_filename = f"results_{salle_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        # Create DataFrame
        df = pd.DataFrame(data, columns=headers)

        # Format the birthday column in Excel as a date
        df['تاريخ الميلاد' if language == "Arabic" else 'Birthday'] = pd.to_datetime(
            df['تاريخ الميلاد' if language == "Arabic" else 'Birthday'], errors='coerce'
        )

        # Sort by the Sort_Moyen column in descending order
        df = df.sort_values(by='Sort_Moyen', ascending=False)

        # Drop the Sort_Moyen column before exporting
        df = df.drop(columns=['Sort_Moyen'])

        # Prompt user to choose save location
        root = tk.Tk()
        root.withdraw()  # Hide the main Tkinter window
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=default_filename,
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Save Results As"
        )
        root.destroy()  # Clean up the hidden window

        # If user cancels the dialog, file_path will be empty
        if not file_path:
            print("Export canceled by user.")
            return

        # Export to Excel with custom date formatting and column width
        with pd.ExcelWriter(file_path, engine='openpyxl', date_format='dd/mm/yyyy') as writer:
            df.to_excel(writer, index=False)
            worksheet = writer.sheets['Sheet1']
            # Format birthday column
            date_col_idx = headers.index('تاريخ الميلاد' if language == "Arabic" else 'Birthday') + 1  # 1-based indexing
            for cell in worksheet[f'{chr(64 + date_col_idx)}:{chr(64 + date_col_idx)}']:
                cell.number_format = 'DD/MM/YYYY'
            # Adjust column width for birthday
            date_col_letter = get_column_letter(date_col_idx)
            worksheet.column_dimensions[date_col_letter].width = 15

        print(f"Excel file saved at: {file_path}")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()
#Result page///////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\\\\\
    
#correction_page////////////////////////////////////////////////////////////////////////////
# دالة لحساب الدرجة النهائية
def calculate_final_grade(corr1, corr2, corr3, dif=2):
    # تحويل القيم إلى float، مع تعيين 0 إذا كانت القيمة فارغة
    c1 = float(corr1) if corr1 is not None else 0
    c2 = float(corr2) if corr2 is not None else 0
    c3 = float(corr3) if corr3 is not None else 0

    # حساب المتوسطات
    m1 = abs(c1 + c3) / 2
    m2 = abs(c2 + c3) / 2
    m3 = abs(c1 + c2) / 2

    # حساب الفروقات
    d1 = abs(c1 - c3)
    d2 = abs(c2 - c3)
    d3 = abs(c1 - c2)

    final_grade = 0

    # الشرط الأول
    if d1 <= dif or d2 <= dif:
        if d1 < d2:
            final_grade = m1
        elif d2 < d1:
            final_grade = m2
        elif d1 == d2:
            final_grade = max(m1, m2)

    # الشرط الثاني
    elif d1 >= dif and d2 >= dif:
        if d1 < d2 and d1 < d3:
            final_grade = m1
        elif d2 < d1 and d2 < d3:
            final_grade = m2
        elif d3 < d1 and d3 < d2:
            final_grade = m3
        elif d2 == d1 and d1 < d3:
            final_grade = max(m2, m1)
        elif d3 == d1 and d1 < d2:
            final_grade = max(m3, m1)
        elif d2 == d3 and d2 < d1:
            final_grade = max(m3, m2)

    return round(final_grade, 2)  # تقريب الدرجة إلى منزلتين عشريتين

# دالة لحفظ الدرجة والدرجة النهائية
def save_grade(anonymous_id, exam_name, correction, grade, coeff):
    db = get_db_connection()
    if db is None:
        return

    cursor = db.cursor()
    try:
        # Convert coeff to float for database storage
        try:
            coeff = float(coeff)
        except ValueError:
            print("Error: Coefficient must be a valid number. Using default value 1.0")
            coeff = 1.0

        # 1. جلب candidat_id باستخدام anonymous_id
        cursor.execute("SELECT id FROM candidats WHERE anonymous_id = %s", (anonymous_id,))
        candidat_result = cursor.fetchone()
        if not candidat_result:
            print(f"Error: No candidate found with anonymous_id '{anonymous_id}'")
            return
        candidat_id = candidat_result[0]

        # 2. التحقق من وجود سجل في exams
        cursor.execute("SELECT id FROM exams WHERE candidat_id = %s AND module_name = %s", (candidat_id, exam_name))
        exam_record = cursor.fetchone()

        if not exam_record:
            # إنشاء سجل جديد إذا لم يكن موجودًا مع القيمة coeff
            cursor.execute(
                "INSERT INTO exams (candidat_id, module_name, coefficient) VALUES (%s, %s, %s)",
                (candidat_id, exam_name, coeff)
            )
            db.commit()
            print(f"Created new exam record for candidat_id {candidat_id} and module_name '{exam_name}' with coefficient {coeff}")
        else:
            # تحديث القيمة coeff إذا كان السجل موجودًا
            cursor.execute(
                "UPDATE exams SET coefficient = %s WHERE candidat_id = %s AND module_name = %s",
                (coeff, candidat_id, exam_name)
            )
            db.commit()
            print(f"Updated coefficient to {coeff} for candidat_id {candidat_id} and module_name '{exam_name}'")

        # 3. تحديث الدرجة بناءً على correction
        if correction == 1:
            sql = "UPDATE exams SET grade_1 = %s WHERE candidat_id = %s AND module_name = %s"
        elif correction == 2:
            sql = "UPDATE exams SET grade_2 = %s WHERE candidat_id = %s AND module_name = %s"
        elif correction == 3:
            sql = "UPDATE exams SET grade_3 = %s WHERE candidat_id = %s AND module_name = %s"

        values = (grade, candidat_id, exam_name)
        cursor.execute(sql, values)
        db.commit()
        print(f"Grade {grade} saved for {exam_name} with correction {correction}")

        # 4. جلب جميع الدرجات لحساب الدرجة النهائية
        cursor.execute(
            "SELECT grade_1, grade_2, grade_3, coefficient FROM exams WHERE candidat_id = %s AND module_name = %s",
            (candidat_id, exam_name)
        )
        result = cursor.fetchone()
        if result:
            grades = result[0:3]  # grade_1, grade_2, grade_3
            db_coeff = result[3]  # coefficient from database
            final_grade = calculate_final_grade(grades[0], grades[1], grades[2], db_coeff)  # Pass coefficient to calculation
            # 5. تحديث الدرجة النهائية
            cursor.execute(
                "UPDATE exams SET finale_g = %s WHERE candidat_id = %s AND module_name = %s",
                (final_grade, candidat_id, exam_name)
            )
            db.commit()
            print(f"Final grade {final_grade} calculated and saved for {exam_name} with coefficient {db_coeff}")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        cursor.close()
        db.close()
        
def fetch_exam_modules():
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return []
        
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT module_name FROM exams")
        modules = [row[0] for row in cursor.fetchall()]
        return modules

    except Error as err:
        print(f"Database Error: {err}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def fetch_exam_details(module_name):
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return ("", 0.0)
        
        cursor = conn.cursor()
        cursor.execute("SELECT module_name, coefficient FROM exams WHERE module_name = %s", (module_name,))
        result = cursor.fetchone()
        return result if result else ("", 0.0)

    except Error as err:
        print(f"Database Error: {err}")
        return ("", 0.0)
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()