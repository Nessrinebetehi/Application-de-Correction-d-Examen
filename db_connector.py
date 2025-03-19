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
from flask import Flask, request, jsonify, render_template

# Initialize Flask app
app = Flask(__name__)

# Database Connection Function
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

# Flask Routes

# Home Route
@app.route('/')
def home():
    return render_template('index.html')

# Option Page Routes
@app.route('/api/save_institute', methods=['POST'])
def save_institute():
    data = request.get_json()
    institute_name = data.get('institute_name')
    exam_option = data.get('exam_option')
    name_post = data.get('name_post')
    nbr_exams = data.get('nbr_exams')
    
    result = op_save_data(institute_name, exam_option, name_post, nbr_exams)
    return jsonify({'message': result})

# Exams Routes
@app.route('/api/add_exam', methods=['POST'])
def add_exam():
    data = request.get_json()
    candidat_id = data.get('candidat_id')
    module = data.get('module')
    coefficient = data.get('coefficient')
    
    result = insert_exam(candidat_id, module, coefficient)
    return jsonify({'success': isinstance(result, bool) and result, 'message': result if isinstance(result, str) else "Exam added"})

@app.route('/api/get_exams', methods=['GET'])
def api_get_exams():
    exams = get_exams()
    return jsonify({'exams': [{'id': e[0], 'module_name': e[1], 'coefficient': e[2]} for e in exams]})

@app.route('/api/delete_exam/<int:exam_id>', methods=['DELETE'])
def api_delete_exam(exam_id):
    result = delete_exam(exam_id)
    return jsonify({'success': isinstance(result, bool) and result, 'message': result if isinstance(result, str) else "Exam deleted"})

# Salles Routes
@app.route('/api/add_salle', methods=['POST'])
def api_add_salle():
    data = request.get_json()
    name = data.get('name')
    capacity = data.get('capacity')
    institute_id = data.get('institute_id', 1)
    
    try:
        code_salle = add_salle(name, capacity, institute_id)
        return jsonify({'success': True, 'code_salle': code_salle})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/get_salles', methods=['GET'])
def api_get_salles():
    salles = get_all_salles()
    return jsonify({'salles': [{'code_salle': s[0], 'name_salle': s[1], 'capacity': s[2]} for s in salles]})

@app.route('/api/delete_salle/<code_salle>', methods=['DELETE'])
def api_delete_salle(code_salle):
    delete_salle(code_salle)
    return jsonify({'success': True, 'message': 'Salle deleted'})

# Students Routes
@app.route('/api/get_salle_names', methods=['GET'])
def api_get_salle_names():
    salles = get_salle_names()
    return jsonify({'salle_names': salles})

@app.route('/api/get_exam_options', methods=['GET'])
def api_get_exam_options():
    options = get_exam_options()
    return jsonify({'exam_options': options})

@app.route('/api/save_student', methods=['POST'])
def api_save_student():
    data = request.get_json()
    name = data.get('name')
    surname = data.get('surname')
    dob = data.get('dob')
    salle_code = data.get('salle_code')
    exam_option = data.get('exam_option')
    
    result = save_student(name, surname, dob, salle_code, exam_option)
    return jsonify({'message': result})

@app.route('/api/import_students', methods=['POST'])
def api_import_students():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'})
    file = request.files['file']
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)
    
    result = import_students_from_excel(file_path)
    os.remove(file_path)
    return jsonify({'message': result})

# Professors Routes
@app.route('/api/add_professor', methods=['POST'])
def api_add_professor():
    data = request.get_json()
    name = data.get('name')
    surname = data.get('surname')
    email = data.get('email')
    correction = data.get('correction')
    module = data.get('module')
    
    message, password = add_professor(name, surname, email, correction, module)
    return jsonify({'message': message, 'password': password})

@app.route('/api/get_professors', methods=['GET'])
def api_get_professors():
    profs = get_profs_from_db()
    return jsonify({'professors': [{'name': p[0], 'email': p[1], 'password': p[2], 'correction': p[3], 'surname': p[4]} for p in profs]})

@app.route('/api/delete_professor/<email>', methods=['DELETE'])
def api_delete_professor(email):
    result = delete_professor(email)
    return jsonify({'message': result})

@app.route('/api/send_emails', methods=['POST'])
def api_send_emails():
    send_emails()
    return jsonify({'message': 'Emails sent successfully'})

# Attendee List Routes
@app.route('/api/get_candidates_by_salle/<salle>', methods=['GET'])
def api_get_candidates_by_salle(salle):
    candidates = get_candidates_by_salle(salle)
    return jsonify({'candidates': [{'name': c[0], 'surname': c[1], 'salle_name': c[2]} for c in candidates]})

@app.route('/api/get_all_candidates', methods=['GET'])
def api_get_all_candidates():
    candidates = get_all_candidates()
    return jsonify({'candidates': [{'name': c[0], 'surname': c[1], 'anonymous_id': c[2]} for c in candidates]})

@app.route('/api/import_absences', methods=['POST'])
def api_import_absences():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'})
    file = request.files['file']
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)
    
    # Since import_absences uses messagebox, we'll simulate it for Flask
    try:
        df = pd.read_excel(file_path)
        required_columns = {"name", "surname", "salle", "audience"}
        if not required_columns.issubset(df.columns):
            return jsonify({'success': False, 'message': "Invalid file format. Required columns: name, surname, salle, audience"})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        for _, row in df.iterrows():
            name, surname, salle, audience = row["name"], row["surname"], row["salle"], row["audience"]
            if audience == "A":
                cursor.execute(
                    "UPDATE candidats SET absence = absence + 1 WHERE name = %s AND surname = %s AND salle_name = %s",
                    (name, surname, salle)
                )
        conn.commit()
        cursor.close()
        conn.close()
        os.remove(file_path)
        return jsonify({'success': True, 'message': "Absences updated successfully"})
    except Exception as e:
        os.remove(file_path)
        return jsonify({'success': False, 'message': f"Failed to import file: {e}"})

# Result Routes
@app.route('/api/institute_data', methods=['GET'])
def api_institute_data():
    name_post, nbr_exams = institute_data()
    return jsonify({'name_post': name_post, 'nbr_exams': nbr_exams})

@app.route('/api/calculate_and_export_results', methods=['POST'])
def api_calculate_and_export_results():
    data = request.get_json()
    selected_salle = data.get('selected_salle')
    selected_language = data.get('selected_language')
    
    # Since this function uses filedialog and messagebox, we'll modify it for Flask
    result = calculate_and_export_results_api(selected_salle, selected_language)
    return jsonify(result)

# Correction Routes
@app.route('/api/calculate_final_grade', methods=['POST'])
def api_calculate_final_grade():
    data = request.get_json()
    corr1 = data.get('corr1')
    corr2 = data.get('corr2')
    corr3 = data.get('corr3')
    dif = data.get('dif', 5)
    
    final_grade = calculate_final_grade(corr1, corr2, corr3, dif)
    return jsonify({'final_grade': final_grade})

@app.route('/api/save_grades', methods=['POST'])
def api_save_grades():
    data = request.get_json()
    anonyme_id = data.get('anonyme_id')
    exam_module = data.get('exam_module')
    grade1 = data.get('grade1')
    grade2 = data.get('grade2')
    grade3 = data.get('grade3')
    final_grade = data.get('final_grade')
    coefficient = data.get('coefficient')
    
    success = save_grades(anonyme_id, exam_module, grade1, grade2, grade3, final_grade, coefficient)
    return jsonify({'success': success})

@app.route('/api/fetch_exam_modules', methods=['GET'])
def api_fetch_exam_modules():
    modules = fetch_exam_modules()
    return jsonify({'modules': modules})

@app.route('/api/fetch_exam_details/<module_name>', methods=['GET'])
def api_fetch_exam_details(module_name):
    module_name, coefficient = fetch_exam_details(module_name)
    return jsonify({'module_name': module_name, 'coefficient': coefficient})

# Existing Functions

# Option Page
def op_save_data(institute_name, exam_option, name_post, nbr_exams):
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

# Exams
def insert_exam(candidat_id, module, coefficient):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        sql = "INSERT INTO exams (candidat_id, module_name, coefficient) VALUES (%s, %s, %s)"
        cursor.execute(sql, (candidat_id, module, coefficient))
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        return str(err)

def get_exams():
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

# Salles
def generate_code_salle():
    while True:
        random_code = "SALLE-" + ''.join(random.choices(string.digits, k=4))
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT code_salle FROM salles WHERE code_salle = %s", (random_code,))
        result = cursor.fetchone()
        conn.close()
        if not result:
            return random_code

def add_salle(name, capacity, institute_id=1):
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
        return code_salle
    except Exception as e:
        conn.close()
        raise e

def get_all_salles():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT code_salle, name_salle, capacity FROM salles")
    salles = cursor.fetchall()
    conn.close()
    return salles

def delete_salle(code_salle):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM salles WHERE code_salle = %s", (code_salle,))
    conn.commit()
    conn.close()

# Students
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
    salles = get_salle_names()
    for combobox in [st_salle_combobox, at_salle_combobox, r_salle_combobox]:
        combobox['values'] = salles
        if salles:
            combobox.current(0)
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
    if not (name and surname and dob and exam_option):
        return "❌ All fields are required!"
    
    conn = get_db_connection()
    if conn is None:
        return "❌ Database connection failed!"
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM candidats WHERE name = %s AND surname = %s AND birthday = %s",
            (name, surname, dob)
        )
        existing_student = cursor.fetchone()
        if existing_student:
            return "❌ This student is already registered!"

        if salle_code:
            cursor.execute(
                "SELECT capacity FROM salles WHERE name_salle = %s",
                (salle_code,)
            )
            salle_capacity = cursor.fetchone()
            if salle_capacity:
                cursor.execute(
                    "SELECT COUNT(*) FROM candidats WHERE salle_name = %s",
                    (salle_code,)
                )
                current_count = cursor.fetchone()[0]
                if current_count >= salle_capacity[0]:
                    return f"❌ Salle {salle_code} is full! Capacity: {salle_capacity[0]}"
        
        anonymous_id = generate_anonymous_id()
        cursor.execute(
            "INSERT INTO candidats (name, surname, birthday, anonymous_id, moyen, decision, absence, salle_name) VALUES (%s, %s, %s, %s, 10.00, 'Pending', 0, %s)",
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
    try:
        df = pd.read_excel(file_path)
        required_columns = {"Name", "Surname", "Birthday", "Salle Name", "Exam Option"}
        if not required_columns.issubset(df.columns):
            return "❌ The Excel file must contain the following columns: Name, Surname, Birthday, Salle Name, Exam Option"

        df["Birthday"] = pd.to_datetime(df["Birthday"], errors='coerce').dt.strftime('%Y-%m-%d')
        conn = get_db_connection()
        cursor = conn.cursor()
        for _, row in df.iterrows():
            if pd.notnull(row["Name"]) and pd.notnull(row["Surname"]) and pd.notnull(row["Birthday"]):
                anonymous_id = generate_anonymous_id()
                sql = "INSERT INTO candidats (name, surname, birthday, anonymous_id, moyen, decision, absence, salle_name) VALUES (%s, %s, %s, %s, 10.00, 'Pending', 0, %s)"
                cursor.execute(sql, (row["Name"], row["Surname"], row["Birthday"], anonymous_id, row["Salle Name"]))
        conn.commit()
        cursor.close()
        conn.close()
        return "✅ Data imported successfully!"
    except Exception as e:
        return f"❌ Error during import: {str(e)}"

# Professors
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
    SENDER_PASSWORD = "temouchentpfc2025"
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

# Attendee List
def get_candidates_by_salle(salle):
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
        print(f"Database Error: {err}")
        return []

def get_all_candidates():
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
        print(f"Database Error: {err}")
        return []

def import_absences():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
    if not file_path:
        return
    try:
        df = pd.read_excel(file_path)
        required_columns = {"name", "surname", "salle", "audience"}
        if not required_columns.issubset(df.columns):
            messagebox.showerror("Error", "Invalid file format. Required columns: name, surname, salle, audience")
            return
        conn = get_db_connection()
        cursor = conn.cursor()
        for _, row in df.iterrows():
            name, surname, salle, audience = row["name"], row["surname"], row["salle"], row["audience"]
            if audience == "A":
                update_query = "UPDATE candidats SET absence = absence + 1 WHERE name = %s AND surname = %s AND salle_name = %s"
                cursor.execute(update_query, (name, surname, salle))
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Success", "Absences updated successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to import file: {e}")

# Result Page
def institute_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name_post, nbr_exams FROM institutes LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result if result else ("No data", 0)
    except Error:
        return ("Error", 0)

def calculate_and_export_results(selected_salle, selected_language):
    if not selected_salle or not selected_language:
        tk.messagebox.showerror("Error", "Please select a salle and language!")
        return
    try:
        all_exams = get_exams()
        if not all_exams:
            tk.messagebox.showwarning("Warning", "No exams found in the database!")
        all_module_names = list(dict.fromkeys([exam[1] for exam in all_exams]))
        conn = get_db_connection()
        if not conn:
            tk.messagebox.showerror("Error", "Database connection failed!")
            return
        cursor = conn.cursor()
        query = """
        SELECT 
            c.id, c.name, c.surname, c.birthday, i.exam_option,
            e.module_name, e.finale_g, e.coefficient, c.absence, c.decision
        FROM candidats c
        LEFT JOIN exams e ON c.id = e.candidat_id
        JOIN salles s ON c.salle_name = s.name_salle
        JOIN institutes i ON s.institute_id = i.id
        WHERE c.salle_name = %s
        """
        cursor.execute(query, (selected_salle,))
        results = cursor.fetchall()
        students_data = {}
        for row in results:
            candidat_id, name, surname, birthday, exam_option, module_name, finale_g, coefficient, absence, decision = row
            if candidat_id not in students_data:
                students_data[candidat_id] = {
                    "name": name,
                    "surname": surname,
                    "birthday": birthday,
                    "option": exam_option,
                    "modules": {},
                    "total_weighted_grade": 0,
                    "total_coefficient": 0,
                    "absence": absence,
                    "decision": decision
                }
            if module_name and finale_g is not None and coefficient is not None:
                students_data[candidat_id]["modules"][module_name] = finale_g
                students_data[candidat_id]["total_weighted_grade"] += finale_g * coefficient
                students_data[candidat_id]["total_coefficient"] += coefficient
        student_list = []
        update_query = "UPDATE candidats SET moyen = %s, decision = %s WHERE id = %s"
        for candidat_id, data in students_data.items():
            if data["absence"] > 2:
                data["decision"] = "Rejected"
                moyenne = 0
            else:
                moyenne = (data["total_weighted_grade"] / data["total_coefficient"]) if data["total_coefficient"] > 0 else 0
            cursor.execute(update_query, (round(moyenne, 2), data["decision"], candidat_id))
            conn.commit()
            student_list.append({
                "id": candidat_id,
                "name": data["name"],
                "surname": data["surname"],
                "birthday": data["birthday"],
                "option": data["option"],
                "modules": data["modules"],
                "moyen": round(moyenne, 2),
                "absence": data["absence"],
                "decision": data["decision"]
            })
        cursor.close()
        conn.close()
        student_list.sort(key=lambda x: x["moyen"], reverse=True)
        if selected_language == "English":
            columns = ["Name", "Surname", "Birthday", "Option"] + all_module_names + ["Average", "Absence", "Decision"]
            rows = [
                [s["name"], s["surname"], s["birthday"].strftime("%Y-%m-%d"), s["option"]] + 
                [s["modules"].get(module, "") for module in all_module_names] + [s["moyen"], s["absence"], s["decision"]]
                for s in student_list
            ]
            df = pd.DataFrame(rows, columns=columns)
        elif selected_language == "Arabic":
            columns = ["الاسم", "اللقب", "تاريخ الميلاد", "الخيار"] + all_module_names + ["المعدل", "الغياب", "القرار"]
            rows = [
                [s["name"], s["surname"], s["birthday"].strftime("%Y-%m-%d"), s["option"]] + 
                [s["modules"].get(module, "") for module in all_module_names] + [s["moyen"], s["absence"], s["decision"]]
                for s in student_list
            ]
            df = pd.DataFrame(rows, columns=columns)
        default_filename = f"results_{selected_salle}_{selected_language}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=default_filename,
            title="Save Results As"
        )
        if file_path:
            df.to_excel(file_path, index=False)
            tk.messagebox.showinfo("Success", f"Excel file saved to '{file_path}' and database updated!")
        else:
            tk.messagebox.showinfo("Cancelled", "Export cancelled by user.")
    except Error as e:
        tk.messagebox.showerror("Error", f"Database error: {e}")
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def calculate_and_export_results_api(selected_salle, selected_language):
    if not selected_salle or not selected_language:
        return {'success': False, 'message': "Please select a salle and language!"}
    try:
        all_exams = get_exams()
        if not all_exams:
            return {'success': False, 'message': "No exams found in the database!"}
        all_module_names = list(dict.fromkeys([exam[1] for exam in all_exams]))
        conn = get_db_connection()
        if not conn:
            return {'success': False, 'message': "Database connection failed!"}
        cursor = conn.cursor()
        query = """
        SELECT 
            c.id, c.name, c.surname, c.birthday, i.exam_option,
            e.module_name, e.finale_g, e.coefficient, c.absence, c.decision
        FROM candidats c
        LEFT JOIN exams e ON c.id = e.candidat_id
        JOIN salles s ON c.salle_name = s.name_salle
        JOIN institutes i ON s.institute_id = i.id
        WHERE c.salle_name = %s
        """
        cursor.execute(query, (selected_salle,))
        results = cursor.fetchall()
        students_data = {}
        for row in results:
            candidat_id, name, surname, birthday, exam_option, module_name, finale_g, coefficient, absence, decision = row
            if candidat_id not in students_data:
                students_data[candidat_id] = {
                    "name": name,
                    "surname": surname,
                    "birthday": birthday,
                    "option": exam_option,
                    "modules": {},
                    "total_weighted_grade": 0,
                    "total_coefficient": 0,
                    "absence": absence,
                    "decision": decision
                }
            if module_name and finale_g is not None and coefficient is not None:
                students_data[candidat_id]["modules"][module_name] = finale_g
                students_data[candidat_id]["total_weighted_grade"] += finale_g * coefficient
                students_data[candidat_id]["total_coefficient"] += coefficient
        student_list = []
        update_query = "UPDATE candidats SET moyen = %s, decision = %s WHERE id = %s"
        for candidat_id, data in students_data.items():
            if data["absence"] > 2:
                data["decision"] = "Rejected"
                moyenne = 0
            else:
                moyenne = (data["total_weighted_grade"] / data["total_coefficient"]) if data["total_coefficient"] > 0 else 0
            cursor.execute(update_query, (round(moyenne, 2), data["decision"], candidat_id))
            conn.commit()
            student_list.append({
                "id": candidat_id,
                "name": data["name"],
                "surname": data["surname"],
                "birthday": data["birthday"].strftime("%Y-%m-%d"),
                "option": data["option"],
                "modules": data["modules"],
                "moyen": round(moyenne, 2),
                "absence": data["absence"],
                "decision": data["decision"]
            })
        cursor.close()
        conn.close()
        student_list.sort(key=lambda x: x["moyen"], reverse=True)
        if selected_language == "English":
            columns = ["Name", "Surname", "Birthday", "Option"] + all_module_names + ["Average", "Absence", "Decision"]
            rows = [
                [s["name"], s["surname"], s["birthday"], s["option"]] + 
                [s["modules"].get(module, "") for module in all_module_names] + [s["moyen"], s["absence"], s["decision"]]
                for s in student_list
            ]
            df = pd.DataFrame(rows, columns=columns)
        elif selected_language == "Arabic":
            columns = ["الاسم", "اللقب", "تاريخ الميلاد", "الخيار"] + all_module_names + ["المعدل", "الغياب", "القرار"]
            rows = [
                [s["name"], s["surname"], s["birthday"], s["option"]] + 
                [s["modules"].get(module, "") for module in all_module_names] + [s["moyen"], s["absence"], s["decision"]]
                for s in student_list
            ]
            df = pd.DataFrame(rows, columns=columns)
        default_filename = f"results_{selected_salle}_{selected_language}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = os.path.join('results', default_filename)
        if not os.path.exists('results'):
            os.makedirs('results')
        df.to_excel(file_path, index=False)
        return {'success': True, 'message': f"Results exported to {file_path}", 'file_path': file_path}
    except Error as e:
        return {'success': False, 'message': f"Database error: {e}"}

# Correction Page
def calculate_final_grade(corr1, corr2, corr3, dif=5):
    try:
        c1 = float(corr1) if corr1 else 0
        c2 = float(corr2) if corr2 else 0
        c3 = float(corr3) if corr3 else 0
        m1 = abs(c1 + c3) / 2
        m2 = abs(c2 + c3) / 2
        m3 = abs(c1 + c2) / 2
        d1 = abs(c1 - c3)
        d2 = abs(c2 - c3)
        d3 = abs(c1 - c2)
        final_grade = 0
        if d1 <= dif or d2 <= dif:
            if d1 < d2:
                final_grade = m1
            elif d2 < d1:
                final_grade = m2
            elif d1 == d2:
                final_grade = max(m1, m2)
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
        return round(final_grade, 2)
    except ValueError:
        return 0

def save_grades(anonyme_id, exam_module, grade1, grade2, grade3, final_grade, coefficient):
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM candidats WHERE anonymous_id = %s", (anonyme_id,))
        result = cursor.fetchone()
        if not result:
            print("Error: No candidate found with this anonymous ID")
            return False
        candidat_id = result[0]
        grade1 = float(grade1) if grade1 else None
        grade2 = float(grade2) if grade2 else None
        grade3 = float(grade3) if grade3 else None
        final_grade = float(final_grade) if final_grade else None
        cursor.execute("""
            INSERT INTO exams (candidat_id, module_name, coefficient, grade_1, grade_2, grade_3, finale_g)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            coefficient = VALUES(coefficient),
            grade_1 = VALUES(grade_1),
            grade_2 = VALUES(grade_2),
            grade_3 = VALUES(grade_3),
            finale_g = VALUES(finale_g)
        """, (candidat_id, exam_module, coefficient, grade1, grade2, grade3, final_grade))
        conn.commit()
        return True
    except Error as e:
        print(f"Error saving grades: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

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

# Main Execution
if __name__ == "__main__":
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    if not os.path.exists('results'):
        os.makedirs('results')
    app.run(debug=True, host='0.0.0.0', port=5000)