import secrets
import pymysql
import pandas as pd
import os
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
from datetime import datetime
from openpyxl.utils import get_column_letter


def get_db_connection():
    try:
        conn = pymysql.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", "4000")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME", "anonymat"),
            ssl={"ca": "isrgrootx1.pem"}, 
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        if conn.ping():
            print("✅ Successfully connected to the database!")
        return conn
    except pymysql.Error as err:
        print(f"❌ Database Connection Error: {err}")
        return None

# Option Page //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\

def op_save_data(institute_name, exam_option, name_post, nbr_exams):
    """
    Save institute data into the institutes table.

    Args:
        institute_name (str): Name of the institute.
        exam_option (str): Exam option.
        name_post (str): Name of the post.
        nbr_exams (int): Number of exams.

    Returns:
        str: Message indicating success or failure of the operation.
    """
    if not institute_name or not exam_option or not name_post or not isinstance(nbr_exams, int):
        return "❌ Please fill in all the fields correctly!"

    conn = get_db_connection()
    if conn is None:
        return "❌ Failed to connect to the database!"

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO institutes (institute_name, exam_option, name_post, nbr_exams) VALUES (%s, %s, %s, %s)",
                (institute_name, exam_option, name_post, nbr_exams)
            )
            conn.commit()
            return "✅ Data saved successfully!"
    except pymysql.Error as err:
        print(f"❌ Database Error in op_save_data: {err}")
        return f"❌ Database error: {err}"
    finally:
        conn.close()

# Exams Window //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\

def insert_exam(candidat_id, module, coefficient):
    if not isinstance(candidat_id, int) or not module or not isinstance(coefficient, (int, float)):
        return {"error": "❌ All fields are required and must be of the correct type!", "success": False}

    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ Failed to connect to the database!", "success": False}

    try:
        with conn.cursor() as cursor:
            # Disable foreign key constraints
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            # Insert exam data
            sql = "INSERT INTO exams (candidat_id, module_name, coefficient) VALUES (%s, %s, %s)"
            cursor.execute(sql, (candidat_id, module, coefficient))
            # Re-enable foreign key constraints
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
            return {"error": None, "success": True}
    except pymysql.Error as err:
        print(f"❌ Database Error in insert_exam: {err}")
        return {"error": f"❌ Database error: {err}", "success": False}
    finally:
        conn.close()

def get_exams():
    """
    Retrieve all exams from the exams table.

    Returns:
        dict: Dictionary containing 'error' (error message or None) and 'data' (list of exams).
    """
    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ Failed to connect to the database!", "data": []}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, module_name, coefficient FROM exams")
            exams = cursor.fetchall()
            return {"error": None, "data": [{"id": e['id'], "module": e['module_name'], "coefficient": e['coefficient']} for e in exams]}
    except pymysql.Error as err:
        print(f"❌ Database Error in get_exams: {err}")
        return {"error": f"❌ Database error: {err}", "data": []}
    finally:
        conn.close()

def delete_exam(exam_id):
    """
    Delete an exam from the exams table based on the ID.

    Args:
        exam_id (int): Exam ID.

    Returns:
        dict: Dictionary containing 'error' (error message or None) and 'success' (True/False).
    """
    if not isinstance(exam_id, int):
        return {"error": "❌ Exam ID must be a number!", "success": False}

    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ Failed to connect to the database!", "success": False}

    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM exams WHERE id = %s", (exam_id,))
            conn.commit()
            return {"error": None, "success": True}
    except pymysql.Error as err:
        print(f"❌ Database Error in delete_exam: {err}")
        return {"error": f"❌ Database error: {err}", "success": False}
    finally:
        conn.close()
        
def delete_all_data():
    conn = get_db_connection()
    if conn is None:
        return {"success": False, "error": "❌ Failed to connect to the database!"}
    
    cursor = conn.cursor()
    try:
        tables = ["professors", "institutes", "salles", "candidats", "exams"]
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
        conn.commit()
        return {"success": True, "error": None}
    except Exception as e:
        conn.rollback()
        return {"success": False, "error": f"❌ Error while deleting data: {str(e)}"}
    finally:
        cursor.close()
        conn.close()
        
# Salles Window //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\

def generate_code_salle():
    """
    Generate a unique salle code in the format SALLE-XXXX.

    Returns:
        str: Unique salle code.
    """
    while True:
        random_code = "SALLE-" + ''.join(random.choices(string.digits, k=4))
        conn = get_db_connection()
        if conn is None:
            continue
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT code_salle FROM salles WHERE code_salle = %s", (random_code,))
                result = cursor.fetchone()
                if not result:
                    return random_code
        finally:
            conn.close()

def add_salle(name, capacity, institute_id=1):
    """
    Add a new salle to the salles table.

    Args:
        name (str): Salle name.
        capacity (int): Salle capacity.
        institute_id (int, optional): Institute ID. Defaults to 1.

    Returns:
        dict: Dictionary containing 'error' (error message or None) and 'code_salle' (salle code).
    """
    if not name or not isinstance(capacity, int) or capacity <= 0:
        return {"error": "❌ Salle name and capacity are required, and capacity must be a positive number!", "code_salle": None}

    code_salle = generate_code_salle()
    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ Failed to connect to the database!", "code_salle": None}

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO salles (code_salle, name_salle, capacity, institute_id) VALUES (%s, %s, %s, %s)",
                (code_salle, name, capacity, institute_id)
            )
            conn.commit()
            return {"error": None, "code_salle": code_salle}
    except pymysql.Error as err:
        print(f"❌ Database Error in add_salle: {err}")
        return {"error": f"❌ Database error: {err}", "code_salle": None}
    finally:
        conn.close()

def get_all_salles():
    """
    Retrieve all salles from the salles table.

    Returns:
        dict: Dictionary containing 'error' (error message or None) and 'data' (list of salles).
    """
    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ Failed to connect to the database!", "data": []}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT code_salle, name_salle, capacity FROM salles")
            salles = cursor.fetchall()
            return {"error": None, "data": [{"code_salle": s['code_salle'], "name_salle": s['name_salle'], "capacity": s['capacity']} for s in salles]}
    except pymysql.Error as err:
        print(f"❌ Database Error in get_all_salles: {err}")
        return {"error": f"❌ Database error: {err}", "data": []}
    finally:
        conn.close()

def delete_salle(code_salle):
    """
    Delete a salle from the salles table based on the salle code.

    Args:
        code_salle (str): Salle code.

    Returns:
        dict: Dictionary containing 'error' (error message or None) and 'success' (True/False).
    """
    if not code_salle:
        return {"error": "❌ Salle code is required!", "success": False}

    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ Failed to connect to the database!", "success": False}

    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM salles WHERE code_salle = %s", (code_salle,))
            conn.commit()
            return {"error": None, "success": True}
    except pymysql.Error as err:
        print(f"❌ Database Error in delete_salle: {err}")
        return {"error": f"❌ Database error: {err}", "success": False}
    finally:
        conn.close()

# Students Page //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\

def get_salle_names():
    """
    Retrieve salle names from the salles table.

    Returns:
        dict: Dictionary containing 'error' (error message or None) and 'data' (list of salle names).
    """
    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ Failed to connect to the database!", "data": []}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name_salle FROM salles")
            salles = [row['name_salle'] for row in cursor.fetchall()]
            return {"error": None, "data": salles}
    except pymysql.Error as err:
        print(f"❌ Database Error in get_salle_names: {err}")
        return {"error": f"❌ Database error: {err}", "data": []}
    finally:
        conn.close()

def get_exam_options():
    """
    Retrieve exam options from the institutes table.

    Returns:
        dict: Dictionary containing 'error' (error message or None) and 'data' (list of exam options).
    """
    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ Failed to connect to the database!", "data": ["Error Fetching Data"]}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT exam_option FROM institutes")
            options = [row['exam_option'] for row in cursor.fetchall()]
            return {"error": None, "data": options if options else ["No Options Available"]}
    except pymysql.Error as err:
        print(f"❌ Database Error in get_exam_options: {err}")
        return {"error": f"❌ Database error: {err}", "data": ["Error Fetching Data"]}
    finally:
        conn.close()

def generate_anonymous_id():
    """
    Generate an anonymous ID for a student (8 digits, starting with a non-zero digit).

    Returns:
        str: Anonymous ID.
    """
    first_digit = random.choice("123456789")
    other_digits = ''.join(random.choices("0123456789", k=7))
    return first_digit + other_digits

def save_student(name, surname, dob, salle_code, exam_option):
    """
    Save a new student's data into the candidats table with duplication and capacity checks.

    Args:
        name (str): Student's name.
        surname (str): Student's surname.
        dob (str): Date of birth (in YYYY-MM-DD format).
        salle_code (str): Salle name.
        exam_option (str): Exam option.

    Returns:
        dict: Dictionary containing 'error' (error message or None) and 'success' (True/False).
    """
    if not (name and surname and dob and exam_option):
        return {"error": "❌ All fields are required!", "success": False}

    try:
        datetime.strptime(dob, '%Y-%m-%d')
    except ValueError:
        return {"error": "❌ Date of birth must be in YYYY-MM-DD format!", "success": False}

    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ Failed to connect to the database!", "success": False}

    try:
        with conn.cursor() as cursor:
            # Check for existing student
            cursor.execute(
                "SELECT id FROM candidats WHERE name = %s AND surname = %s AND birthday = %s",
                (name, surname, dob)
            )
            if cursor.fetchone():
                return {"error": "❌ This student is already registered!", "success": False}

            # Check salle capacity
            if salle_code:
                cursor.execute("SELECT capacity FROM salles WHERE name_salle = %s", (salle_code,))
                salle_capacity = cursor.fetchone()
                if not salle_capacity:
                    return {"error": f"❌ Salle {salle_code} does not exist!", "success": False}
                cursor.execute("SELECT COUNT(*) as count FROM candidats WHERE salle_name = %s", (salle_code,))
                current_count = cursor.fetchone()['count']
                if current_count >= salle_capacity['capacity']:
                    return {"error": f"❌ Salle {salle_code} is full! Capacity: {salle_capacity['capacity']}", "success": False}

            # Insert student
            anonymous_id = generate_anonymous_id()
            cursor.execute(
                "INSERT INTO candidats (name, surname, birthday, anonymous_id, moyen, decision, absence, salle_name) "
                "VALUES (%s, %s, %s, %s, 10.00, 'Pending', 0, %s)",
                (name, surname, dob, anonymous_id, salle_code if salle_code else None)
            )
            conn.commit()
            return {"error": None, "success": True}
    except pymysql.Error as err:
        print(f"❌ Database Error in save_student: {err}")
        return {"error": f"❌ Database error: {err}", "success": False}
    finally:
        conn.close()

def import_students_from_excel(file_path):
    """
    Import student data from an Excel file, assign them to salles alphabetically,
    and respect salle capacity.

    Args:
        file_path (str): Path to the Excel file.

    Returns:
        dict: Dictionary with 'error' (message or None) and 'success' (True/False).
    """
    if not os.path.exists(file_path):
        return {"error": "❌ File does not exist!", "success": False}

    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        required_columns = {"Name", "Surname", "Birthday", "Exam Option"}
        if not required_columns.issubset(df.columns):
            return {"error": "❌ Excel file must contain columns: Name, Surname, Birthday, Exam Option", "success": False}

        # Convert Birthday to proper date format
        df["Birthday"] = pd.to_datetime(df["Birthday"], format='%d-%m-%Y', errors='coerce').dt.strftime('%Y-%m-%d')

        # Sort students alphabetically by Name and Surname
        df = df.sort_values(by=["Name", "Surname"])
        print("Data after sorting:", df)  # Print for verification

        # Connect to the database
        conn = get_db_connection()
        if conn is None:
            return {"error": "❌ Database connection failed!", "success": False}

        try:
            with conn.cursor() as cursor:
                # Fetch all salles with their capacities
                cursor.execute("""
                    SELECT name_salle, capacity 
                    FROM salles 
                    ORDER BY name_salle
                """)
                salles = cursor.fetchall()
                print("Contents of salles:", salles)  # Print for verification

                if not salles:
                    return {"error": "❌ No salles found in the database!", "success": False}

                # Track remaining capacity for each salle
                salle_capacity = {}
                salle_current_count = {}
                for salle in salles:
                    if isinstance(salle, dict):
                        # If the result is a dictionary
                        name = salle['name_salle']
                        capacity = salle['capacity']
                    else:
                        # If the result is a tuple
                        name = salle[0]
                        capacity = salle[1]
                    salle_capacity[name] = capacity
                    salle_current_count[name] = 0

                print("Salle capacities:", salle_capacity)  # Print for verification

                salle_names = list(salle_capacity.keys())
                salle_index = 0

                # Assign students to salles
                for _, row in df.iterrows():
                    if pd.notnull(row["Name"]) and pd.notnull(row["Surname"]) and pd.notnull(row["Birthday"]):
                        # Find a salle with available capacity
                        while salle_index < len(salle_names):
                            current_salle = salle_names[salle_index]
                            if salle_current_count[current_salle] < salle_capacity[current_salle]:
                                # Assign student to this salle
                                anonymous_id = generate_anonymous_id()
                                cursor.execute(
                                    """
                                    INSERT INTO candidats (name, surname, birthday, anonymous_id, moyen, decision, absence, salle_name)
                                    VALUES (%s, %s, %s, %s, 10.00, 'Pending', 0, %s)
                                    """,
                                    (row["Name"], row["Surname"], row["Birthday"], anonymous_id, current_salle)
                                )
                                salle_current_count[current_salle] += 1
                                break
                            else:
                                salle_index += 1  # Move to the next salle

                        if salle_index >= len(salle_names):
                            return {"error": "❌ Insufficient salle capacity to accommodate all students!", "success": False}

                conn.commit()
                return {"error": None, "success": True}

        finally:
            conn.close()

    except Exception as e:
        import traceback
        print(f"❌ Error in import_students_from_excel: {e}")
        traceback.print_exc()  # Prints the full error traceback
        return {"error": f"❌ Import error: {str(e)}", "success": False}

# Prof Page //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\\

def generate_password(length=10):
    """
    Generate a random password.

    Args:
        length (int, optional): Password length. Defaults to 10.

    Returns:
        str: Random password.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def fetch_modules():
    """
    Retrieve a list of modules from the exams table.

    Returns:
        dict: Dictionary containing 'error' (error message or None) and 'data' (list of modules).
    """
    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ Failed to connect to the database!", "data": []}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT module_name FROM exams")
            modules = [row['module_name'] for row in cursor.fetchall()]
            return {"error": None, "data": modules}
    except pymysql.Error as err:
        print(f"❌ Database Error in fetch_modules: {err}")
        return {"error": f"❌ Database error: {err}", "data": []}
    finally:
        conn.close()

def add_professor(name, surname, email, correction, module):
    """
    Add a new professor to the professors table.

    Args:
        name (str): Professor's name.
        surname (str): Professor's surname.
        email (str): Email address.
        correction (int): Correction number (1, 2, 3).
        module (str): Module taught.

    Returns:
        dict: Dictionary containing 'error' (error message or None), 'success' (True/False), and 'password' (password).
    """
    if not (name and surname and email and module) or not isinstance(correction, int):
        return {"error": "❌ All fields are required and must be of the correct type!", "success": False, "password": None}

    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ Failed to connect to the database!", "success": False, "password": None}

    try:
        with conn.cursor() as cursor:
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                return {"error": "❌ Invalid email format!", "success": False, "password": None}

            cursor.execute("SELECT id FROM professors WHERE email = %s", (email,))
            if cursor.fetchone():
                return {"error": "❌ Email already exists!", "success": False, "password": None}

            password = generate_password()
            cursor.execute(
                "INSERT INTO professors (name, surname, email, correction, password, module) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (name, surname, email, int(correction), password, module)
            )
            conn.commit()
            return {"error": None, "success": True, "password": password}
    except pymysql.Error as err:
        print(f"❌ Database Error in add_professor: {err}")
        return {"error": f"❌ Database error: {err}", "success": False, "password": None}
    finally:
        conn.close()

def get_profs_from_db():
    """
    Retrieve all professors from the professors table.

    Returns:
        dict: Dictionary containing 'error' (error message or None) and 'data' (list of professors).
    """
    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ Failed to connect to the database!", "data": []}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, email, password, correction, surname FROM professors")
            profs = cursor.fetchall()
            return {"error": None, "data": [{"name": p['name'], "email": p['email'], "password": p['password'], "correction": p['correction'], "surname": p['surname']} for p in profs]}
    except pymysql.Error as err:
        print(f"❌ Database Error in get_profs_from_db: {err}")
        return {"error": f"❌ Database error: {err}", "data": []}
    finally:
        conn.close()

def delete_professor(email):
    """
    Delete a professor from the professors table based on email.

    Args:
        email (str): Professor's email.

    Returns:
        dict: Dictionary containing 'error' (error message or None) and 'success' (True/False).
    """
    if not email:
        return {"error": "❌ Email is required!", "success": False}

    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ Failed to connect to the database!", "success": False}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM professors WHERE email = %s", (email,))
            if not cursor.fetchone():
                return {"error": "❌ Professor not found!", "success": False}

            cursor.execute("DELETE FROM professors WHERE email = %s", (email,))
            conn.commit()
            return {"error": None, "success": True}
    except pymysql.Error as err:
        print(f"❌ Database Error in delete_professor: {err}")
        return {"error": f"❌ Database error: {err}", "success": False}
    finally:
        conn.close()

def send_emails():
    """
    Send emails to professors with their account details.

    Returns:
        dict: Dictionary containing 'error' (error message or None) and 'success' (True/False).
    """
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

    if not SENDER_EMAIL or not SENDER_PASSWORD:
        return {"error": "❌ SENDER_EMAIL and SENDER_PASSWORD must be set in environment variables!", "success": False}

    professors = get_profs_from_db()
    if professors['error']:
        return {"error": professors['error'], "success": False}
    if not professors['data']:
        return {"error": "No professors found in the database.", "success": False}

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        for prof in professors['data']:
            name, email, password, correction, surname = prof['name'], prof['email'], prof['password'], prof['correction'], prof['surname']
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
        return {"error": None, "success": True}
    except Exception as e:
        print(f"❌ Error in send_emails: {e}")
        return {"error": f"Failed to send emails: {e}", "success": False}

# Attendee List //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\

def get_candidates_by_salle(salle):
    """
    Retrieve candidates by salle name from the candidats table.

    Args:
        salle (str): Salle name.

    Returns:
        dict: Dictionary containing 'error' (error message or None) and 'data' (list of candidates).
    """
    if not salle:
        return {"error": "❌ Salle name is required!", "data": []}

    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ Failed to connect to the database!", "data": []}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, surname, salle_name FROM candidats WHERE salle_name = %s", (salle,))
            candidates = cursor.fetchall()
            return {"error": None, "data": [{"name": c['name'], "surname": c['surname'], "salle": c['salle_name']} for c in candidates]}
    except pymysql.Error as err:
        print(f"❌ Database Error in get_candidates_by_salle: {err}")
        return {"error": f"❌ Database error: {err}", "data": []}
    finally:
        conn.close()

def get_all_candidates():
    """
    Retrieve all candidates from the candidats table.

    Returns:
        dict: Dictionary containing 'error' (error message or None) and 'data' (list of candidates).
    """
    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ Failed to connect to the database!", "data": []}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, surname, anonymous_id FROM candidats")
            candidates = cursor.fetchall()
            return {"error": None, "data": [{"name": c['name'], "surname": c['surname'], "anonymous_id": c['anonymous_id']} for c in candidates]}
    except pymysql.Error as err:
        print(f"❌ Database Error in get_all_candidates: {err}")
        return {"error": f"❌ Database error: {err}", "data": []}
    finally:
        conn.close()

def import_absences(file_path):
    """
    Import absences from an Excel file and update the candidats table.

    Args:
        file_path (str): Path to the Excel file.

    Returns:
        dict: Dictionary containing 'error' (error message or None) and 'success' (True/False).
    """
    if not os.path.exists(file_path):
        return {"error": "❌ File does not exist!", "success": False}

    try:
        df = pd.read_excel(file_path)
        required_columns = {"name", "surname", "salle", "audience"}
        if not required_columns.issubset(df.columns):
            return {"error": "❌ Invalid file format. Required columns: name, surname, salle, audience", "success": False}

        conn = get_db_connection()
        if conn is None:
            return {"error": "❌ Failed to connect to the database!", "success": False}

        try:
            with conn.cursor() as cursor:
                for _, row in df.iterrows():
                    name, surname, salle, audience = row["name"], row["surname"], row["salle"], row["audience"]
                    if audience == "A":
                        cursor.execute(
                            "UPDATE candidats SET absence = absence + 1 WHERE name = %s AND surname = %s AND salle_name = %s",
                            (name, surname, salle)
                        )
                conn.commit()
                return {"error": None, "success": True}
        finally:
            conn.close()
    except Exception as e:
        print(f"❌ Error in import_absences: {e}")
        return {"error": f"❌ Error while importing file: {e}", "success": False}

# Result Page //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\

def institute_data():
    """
    Retrieve institute data from the institutes table.

    Returns:
        dict: Dictionary containing 'error' (error message or None) and 'data' (institute data).
    """
    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ Failed to connect to the database!", "data": ("Error", 0)}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name_post, nbr_exams FROM institutes LIMIT 1")
            result = cursor.fetchone()
            return {"error": None, "data": (result['name_post'], result['nbr_exams']) if result else ("No data", 0)}
    except pymysql.Error as err:
        print(f"❌ Database Error in institute_data: {err}")
        return {"error": f"❌ Database error: {err}", "data": ("Error", 0)}
    finally:
        conn.close()

def calculate_candidate_moyen(candidat_id, conn):
    """
    Calculate the average grade for a specific candidate based on their grades.

    Args:
        candidat_id (int): Candidate ID.
        conn (pymysql.connections.Connection): Database connection object.

    Returns:
        float or None: Calculated average, or None if no grades exist.
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT finale_g, coefficient FROM exams WHERE candidat_id = %s AND finale_g IS NOT NULL",
                (candidat_id,)
            )
            results = cursor.fetchall()
            if not results:
                return None

            weighted_sum = 0
            total_coefficient = 0
            for row in results:
                weighted_sum += row['finale_g'] * row['coefficient']
                total_coefficient += row['coefficient']

            if total_coefficient == 0:
                return None

            moyen = weighted_sum / total_coefficient
            moyen = max(0, min(20, moyen))

            cursor.execute("UPDATE candidats SET moyen = %s WHERE id = %s", (moyen, candidat_id))
            conn.commit()
            return moyen
    except pymysql.Error as err:
        print(f"❌ Database Error in calculate_candidate_moyen: {err}")
        return None

def calculate_and_export_results(salle_name, language, output_path=None):
    """
    Calculate results and export them to an Excel file.

    Args:
        salle_name (str): Salle name.
        language (str): Language (Arabic or English).
        output_path (str, optional): Path to save the Excel file. If not specified, a default path is used.

    Returns:
        dict: Dictionary containing 'error' (error message or None), 'success' (True/False), and 'file_path' (file path).
    """
    if not salle_name or language not in ["Arabic", "English"]:
        return {"error": "❌ Salle name and language are required (Arabic or English)!", "success": False, "file_path": None}

    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ Failed to connect to the database!", "success": False, "file_path": None}

    try:
        with conn.cursor() as cursor:
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
                return {"error": f"No candidates found for salle: {salle_name}", "success": False, "file_path": None}

            data = []
            module_list = None
            for candidate in candidates:
                candidat_id = candidate['id']
                name = candidate['name']
                surname = candidate['surname']
                birthday = candidate['birthday']
                absence = candidate['absence']
                modules = candidate['modules']
                grades = candidate['grades']

                moyen = calculate_candidate_moyen(candidat_id, conn)
                moyen_for_sorting = moyen if moyen is not None else -1

                if absence is not None and absence > 2:
                    moyen = "Rejected" if language == "English" else "Rejected"
                    moyen_for_sorting = -1
                else:
                    moyen = "N/A" if moyen is None else moyen

                if isinstance(birthday, str):
                    birthday = datetime.strptime(birthday, '%Y-%m-%d')
                elif birthday is None:
                    birthday = "N/A"

                module_list = modules.split(',') if modules else []
                grade_list = [float(g) if g else "N/A" for g in (grades.split(',') if grades else [])]

                row = [name, surname, birthday] + grade_list + [moyen, moyen_for_sorting]
                data.append(row)

            if language == "Arabic":
                headers = ["Name", "Surname", "Birthday"] + module_list + ["Average", "Sort_Moyen"]
                default_filename = f"results_{salle_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            else:
                headers = ["Name", "Surname", "Birthday"] + module_list + ["Average", "Sort_Moyen"]
                default_filename = f"results_{salle_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

            df = pd.DataFrame(data, columns=headers)
            df['Birthday'] = pd.to_datetime(
                df['Birthday'], errors='coerce'
            )

            df = df.sort_values(by='Sort_Moyen', ascending=False)
            df = df.drop(columns=['Sort_Moyen'])

            file_path = output_path if output_path else os.path.join(os.getcwd(), default_filename)

            with pd.ExcelWriter(file_path, engine='openpyxl', date_format='dd/mm/yyyy') as writer:
                df.to_excel(writer, index=False)
                worksheet = writer.sheets['Sheet1']
                date_col_idx = headers.index('Birthday') + 1
                for cell in worksheet[f'{chr(64 + date_col_idx)}:{chr(64 + date_col_idx)}']:
                    cell.number_format = 'DD/MM/YYYY'
                date_col_letter = get_column_letter(date_col_idx)
                worksheet.column_dimensions[date_col_letter].width = 15

            return {"error": None, "success": True, "file_path": file_path}
    except pymysql.Error as err:
        print(f"❌ Database Error in calculate_and_export_results: {err}")
        return {"error": f"❌ Database error: {err}", "success": False, "file_path": None}
    except Exception as e:
        print(f"❌ Error in calculate_and_export_results: {e}")
        return {"error": f"❌ Error: {e}", "success": False, "file_path": None}
    finally:
        conn.close()

# Correction Page //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\

def calculate_final_grade(corr1, corr2, corr3, dif=2):
    """
    Calculate the final grade based on three corrections.

    Args:
        corr1 (float): First grade.
        corr2 (float): Second grade.
        corr3 (float): Third grade.
        dif (float, optional): Maximum allowed difference. Defaults to 2.

    Returns:
        float: Final grade (rounded to 2 decimal places).
    """
    c1 = float(corr1) if corr1 is not None else 0
    c2 = float(corr2) if corr2 is not None else 0
    c3 = float(corr3) if corr3 is not None else 0

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

def save_grade(anonymous_id, exam_name, correction, grade, coeff):
    """
    Save a student's grade and calculate the final grade in the exams table.

    Args:
        anonymous_id (str): Student's anonymous ID.
        exam_name (str): Exam name.
        correction (int): Correction number (1, 2, 3).
        grade (float): Grade.
        coeff (float): Coefficient.

    Returns:
        dict: Dictionary containing 'error' (error message or None) and 'success' (True/False).
    """
    if not (anonymous_id and exam_name and isinstance(correction, int) and correction in [1, 2, 3]):
        return {"error": "❌ All fields are required and correction number must be 1, 2, or 3!", "success": False}

    try:
        grade = float(grade)
        coeff = float(coeff)
    except (ValueError, TypeError):
        return {"error": "❌ Grade and coefficient must be numbers!", "success": False}

    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ Failed to connect to the database!", "success": False}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM candidats WHERE anonymous_id = %s", (anonymous_id,))
            candidat_result = cursor.fetchone()
            if not candidat_result:
                return {"error": f"❌ No candidate found with anonymous_id '{anonymous_id}'", "success": False}
            candidat_id = candidat_result['id']

            cursor.execute("SELECT id FROM exams WHERE candidat_id = %s AND module_name = %s", (candidat_id, exam_name))
            exam_record = cursor.fetchone()

            if not exam_record:
                cursor.execute(
                    "INSERT INTO exams (candidat_id, module_name, coefficient) VALUES (%s, %s, %s)",
                    (candidat_id, exam_name, coeff)
                )
                conn.commit()
            else:
                cursor.execute(
                    "UPDATE exams SET coefficient = %s WHERE candidat_id = %s AND module_name = %s",
                    (coeff, candidat_id, exam_name)
                )
                conn.commit()

            if correction == 1:
                sql = "UPDATE exams SET grade_1 = %s WHERE candidat_id = %s AND module_name = %s"
            elif correction == 2:
                sql = "UPDATE exams SET grade_2 = %s WHERE candidat_id = %s AND module_name = %s"
            elif correction == 3:
                sql = "UPDATE exams SET grade_3 = %s WHERE candidat_id = %s AND module_name = %s"

            cursor.execute(sql, (grade, candidat_id, exam_name))
            conn.commit()

            cursor.execute(
                "SELECT grade_1, grade_2, grade_3, coefficient FROM exams WHERE candidat_id = %s AND module_name = %s",
                (candidat_id, exam_name)
            )
            result = cursor.fetchone()
            if result:
                grades = [result['grade_1'], result['grade_2'], result['grade_3']]
                db_coeff = result['coefficient']
                final_grade = calculate_final_grade(grades[0], grades[1], grades[2], db_coeff)
                cursor.execute(
                    "UPDATE exams SET finale_g = %s WHERE candidat_id = %s AND module_name = %s",
                    (final_grade, candidat_id, exam_name)
                )
                conn.commit()
            return {"error": None, "success": True}
    except pymysql.Error as err:
        print(f"❌ Database Error in save_grade: {err}")
        return {"error": f"❌ Database error: {err}", "success": False}
    finally:
        conn.close()

def fetch_exam_modules():
    """
    Retrieve a list of exam modules from the exams table.

    Returns:
        dict: Dictionary containing 'error' (error message or None) and 'data' (list of modules).
    """
    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ Failed to connect to the database!", "data": []}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT module_name FROM exams")
            modules = [row['module_name'] for row in cursor.fetchall()]
            return {"error": None, "data": modules}
    except pymysql.Error as err:
        print(f"❌ Database Error in fetch_exam_modules: {err}")
        return {"error": f"❌ Database error: {err}", "data": []}
    finally:
        conn.close()

def fetch_exam_details(module_name):
    """
    Retrieve exam details based on the module name.

    Args:
        module_name (str): Module name.

    Returns:
        dict: Dictionary containing 'error' (error message or None) and 'data' (exam details).
    """
    if not module_name:
        return {"error": "❌ Module name is required!", "data": ("", 0.0)}

    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ Failed to connect to the database!", "data": ("", 0.0)}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT module_name, coefficient FROM exams WHERE module_name = %s", (module_name,))
            result = cursor.fetchone()
            return {"error": None, "data": (result['module_name'], result['coefficient']) if result else ("", 0.0)}
    except pymysql.Error as err:
        print(f"❌ Database Error in fetch_exam_details: {err}")
        return {"error": f"❌ Database error: {err}", "data": ("", 0.0)}
    finally:
        conn.close()