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

# دالة الاتصال بقاعدة البيانات باستخدام pymysql
def get_db_connection():
    """
    إنشاء اتصال بقاعدة البيانات باستخدام pymysql.

    Returns:
        pymysql.connections.Connection: كائن الاتصال بقاعدة البيانات، أو None في حالة الفشل.
    """
    try:
        conn = pymysql.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", "4000")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME", "anonymat"),
            ssl={"ca": "isrgrootx1.pem"},  # استخدام ملف الشهادة
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
    حفظ بيانات المعهد في جدول institutes.

    Args:
        institute_name (str): اسم المعهد.
        exam_option (str): خيار الامتحان.
        name_post (str): اسم المنصب.
        nbr_exams (int): عدد الامتحانات.

    Returns:
        str: رسالة توضح نجاح أو فشل العملية.
    """
    if not institute_name or not exam_option or not name_post or not isinstance(nbr_exams, int):
        return "❌ يرجى ملء جميع الحقول بشكل صحيح!"

    conn = get_db_connection()
    if conn is None:
        return "❌ فشل الاتصال بقاعدة البيانات!"

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO institutes (institute_name, exam_option, name_post, nbr_exams) VALUES (%s, %s, %s, %s)",
                (institute_name, exam_option, name_post, nbr_exams)
            )
            conn.commit()
            return "✅ تم حفظ البيانات بنجاح!"
    except pymysql.Error as err:
        print(f"❌ Database Error in op_save_data: {err}")
        return f"❌ خطأ في قاعدة البيانات: {err}"
    finally:
        conn.close()

# Exams Window //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\

def insert_exam(candidat_id, module, coefficient):
    """
    إدراج بيانات امتحان جديد في جدول exams.

    Args:
        candidat_id (int): معرف الطالب (يمكن أن يكون 0 إذا لم يكن مرتبطًا بطالب).
        module (str): اسم المادة.
        coefficient (float): معامل المادة.

    Returns:
        dict: قاموس يحتوي على 'error' (رسالة الخطأ أو None) و 'success' (True/False).
    """
    if not isinstance(candidat_id, int) or not module or not isinstance(coefficient, (int, float)):
        return {"error": "❌ جميع الحقول مطلوبة ويجب أن تكون بالنوع الصحيح!", "success": False}

    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ فشل الاتصال بقاعدة البيانات!", "success": False}

    try:
        with conn.cursor() as cursor:
            # تعطيل قيود المفتاح الأجنبي
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            # إدراج بيانات الامتحان
            sql = "INSERT INTO exams (candidat_id, module_name, coefficient) VALUES (%s, %s, %s)"
            cursor.execute(sql, (candidat_id, module, coefficient))
            # إعادة تفعيل قيود المفتاح الأجنبي
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
            return {"error": None, "success": True}
    except pymysql.Error as err:
        print(f"❌ Database Error in insert_exam: {err}")
        return {"error": f"❌ خطأ في قاعدة البيانات: {err}", "success": False}
    finally:
        conn.close()

def get_exams():
    """
    استرجاع جميع الامتحانات من جدول exams.

    Returns:
        dict: قاموس يحتوي على 'error' (رسالة الخطأ أو None) و 'data' (قائمة الامتحانات).
    """
    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ فشل الاتصال بقاعدة البيانات!", "data": []}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, module_name, coefficient FROM exams")
            exams = cursor.fetchall()
            return {"error": None, "data": [{"id": e['id'], "module": e['module_name'], "coefficient": e['coefficient']} for e in exams]}
    except pymysql.Error as err:
        print(f"❌ Database Error in get_exams: {err}")
        return {"error": f"❌ خطأ في قاعدة البيانات: {err}", "data": []}
    finally:
        conn.close()

def delete_exam(exam_id):
    """
    حذف امتحان من جدول exams بناءً على المعرف.

    Args:
        exam_id (int): معرف الامتحان.

    Returns:
        dict: قاموس يحتوي على 'error' (رسالة الخطأ أو None) و 'success' (True/False).
    """
    if not isinstance(exam_id, int):
        return {"error": "❌ معرف الامتحان يجب أن يكون رقمًا!", "success": False}

    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ فشل الاتصال بقاعدة البيانات!", "success": False}

    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM exams WHERE id = %s", (exam_id,))
            conn.commit()
            return {"error": None, "success": True}
    except pymysql.Error as err:
        print(f"❌ Database Error in delete_exam: {err}")
        return {"error": f"❌ خطأ في قاعدة البيانات: {err}", "success": False}
    finally:
        conn.close()
        
def delete_all_data():
    conn = get_db_connection()
    if conn is None:
        return {"success": False, "error": "❌ فشل الاتصال بقاعدة البيانات!"}
    
    cursor = conn.cursor()
    try:
        tables = ["professors", "institutes", "salles", "candidats", "exams"]
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
        conn.commit()
        return {"success": True, "error": None}
    except Exception as e:
        conn.rollback()
        return {"success": False, "error": f"❌ خطأ أثناء حذف البيانات: {str(e)}"}
    finally:
        cursor.close()
        conn.close()
        
# Salles Window //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\

def generate_code_salle():
    """
    توليد رمز قاعة فريد بصيغة SALLE-XXXX.

    Returns:
        str: رمز القاعة الفريد.
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
    إضافة قاعة جديدة إلى جدول salles.

    Args:
        name (str): اسم القاعة.
        capacity (int): سعة القاعة.
        institute_id (int, optional): معرف المعهد. الافتراضي 1.

    Returns:
        dict: قاموس يحتوي على 'error' (رسالة الخطأ أو None) و 'code_salle' (رمز القاعة).
    """
    if not name or not isinstance(capacity, int) or capacity <= 0:
        return {"error": "❌ اسم القاعة وسعتها مطلوبان، ويجب أن تكون السعة رقمًا موجبًا!", "code_salle": None}

    code_salle = generate_code_salle()
    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ فشل الاتصال بقاعدة البيانات!", "code_salle": None}

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
        return {"error": f"❌ خطأ في قاعدة البيانات: {err}", "code_salle": None}
    finally:
        conn.close()

def get_all_salles():
    """
    استرجاع جميع القاعات من جدول salles.

    Returns:
        dict: قاموس يحتوي على 'error' (رسالة الخطأ أو None) و 'data' (قائمة القاعات).
    """
    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ فشل الاتصال بقاعدة البيانات!", "data": []}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT code_salle, name_salle, capacity FROM salles")
            salles = cursor.fetchall()
            return {"error": None, "data": [{"code_salle": s['code_salle'], "name_salle": s['name_salle'], "capacity": s['capacity']} for s in salles]}
    except pymysql.Error as err:
        print(f"❌ Database Error in get_all_salles: {err}")
        return {"error": f"❌ خطأ في قاعدة البيانات: {err}", "data": []}
    finally:
        conn.close()

def delete_salle(code_salle):
    """
    حذف قاعة من جدول salles بناءً على رمز القاعة.

    Args:
        code_salle (str): رمز القاعة.

    Returns:
        dict: قاموس يحتوي على 'error' (رسالة الخطأ أو None) و 'success' (True/False).
    """
    if not code_salle:
        return {"error": "❌ رمز القاعة مطلوب!", "success": False}

    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ فشل الاتصال بقاعدة البيانات!", "success": False}

    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM salles WHERE code_salle = %s", (code_salle,))
            conn.commit()
            return {"error": None, "success": True}
    except pymysql.Error as err:
        print(f"❌ Database Error in delete_salle: {err}")
        return {"error": f"❌ خطأ في قاعدة البيانات: {err}", "success": False}
    finally:
        conn.close()

# Students Page //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\

def get_salle_names():
    """
    استرجاع أسماء القاعات من جدول salles.

    Returns:
        dict: قاموس يحتوي على 'error' (رسالة الخطأ أو None) و 'data' (قائمة أسماء القاعات).
    """
    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ فشل الاتصال بقاعدة البيانات!", "data": []}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name_salle FROM salles")
            salles = [row['name_salle'] for row in cursor.fetchall()]
            return {"error": None, "data": salles}
    except pymysql.Error as err:
        print(f"❌ Database Error in get_salle_names: {err}")
        return {"error": f"❌ خطأ في قاعدة البيانات: {err}", "data": []}
    finally:
        conn.close()

def get_exam_options():
    """
    استرجاع خيارات الامتحانات من جدول institutes.

    Returns:
        dict: قاموس يحتوي على 'error' (رسالة الخطأ أو None) و 'data' (قائمة خيارات الامتحانات).
    """
    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ فشل الاتصال بقاعدة البيانات!", "data": ["Error Fetching Data"]}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT exam_option FROM institutes")
            options = [row['exam_option'] for row in cursor.fetchall()]
            return {"error": None, "data": options if options else ["No Options Available"]}
    except pymysql.Error as err:
        print(f"❌ Database Error in get_exam_options: {err}")
        return {"error": f"❌ خطأ في قاعدة البيانات: {err}", "data": ["Error Fetching Data"]}
    finally:
        conn.close()

def generate_anonymous_id():
    """
    توليد معرف مجهول للطالب (8 أرقام، يبدأ برقم غير صفري).

    Returns:
        str: المعرف المجهول.
    """
    first_digit = random.choice("123456789")
    other_digits = ''.join(random.choices("0123456789", k=7))
    return first_digit + other_digits

def save_student(name, surname, dob, salle_code, exam_option):
    """
    حفظ بيانات طالب جديد في جدول candidats مع التحقق من التكرار وسعة القاعة.

    Args:
        name (str): اسم الطالب.
        surname (str): لقب الطالب.
        dob (str): تاريخ الميلاد (بصيغة YYYY-MM-DD).
        salle_code (str): اسم القاعة.
        exam_option (str): خيار الامتحان.

    Returns:
        dict: قاموس يحتوي على 'error' (رسالة الخطأ أو None) و 'success' (True/False).
    """
    if not (name and surname and dob and exam_option):
        return {"error": "❌ جميع الحقول مطلوبة!", "success": False}

    try:
        datetime.strptime(dob, '%Y-%m-%d')
    except ValueError:
        return {"error": "❌ تاريخ الميلاد يجب أن يكون بصيغة YYYY-MM-DD!", "success": False}

    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ فشل الاتصال بقاعدة البيانات!", "success": False}

    try:
        with conn.cursor() as cursor:
            # التحقق من وجود الطالب
            cursor.execute(
                "SELECT id FROM candidats WHERE name = %s AND surname = %s AND birthday = %s",
                (name, surname, dob)
            )
            if cursor.fetchone():
                return {"error": "❌ هذا الطالب مسجل بالفعل!", "success": False}

            # التحقق من سعة القاعة
            if salle_code:
                cursor.execute("SELECT capacity FROM salles WHERE name_salle = %s", (salle_code,))
                salle_capacity = cursor.fetchone()
                if not salle_capacity:
                    return {"error": f"❌ القاعة {salle_code} غير موجودة!", "success": False}
                cursor.execute("SELECT COUNT(*) as count FROM candidats WHERE salle_name = %s", (salle_code,))
                current_count = cursor.fetchone()['count']
                if current_count >= salle_capacity['capacity']:
                    return {"error": f"❌ القاعة {salle_code} ممتلئة! السعة: {salle_capacity['capacity']}", "success": False}

            # إدراج الطالب
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
        return {"error": f"❌ خطأ في قاعدة البيانات: {err}", "success": False}
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
        df["Birthday"] = pd.to_datetime(df["Birthday"], errors='coerce').dt.strftime('%Y-%m-%d')

        # Sort students alphabetically by Name and Surname
        df = df.sort_values(by=["Name", "Surname"])

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
                salles = cursor.fetchall()  # List of tuples (name_salle, capacity)
                if not salles:
                    return {"error": "❌ No salles found in the database!", "success": False}

                # Track remaining capacity for each salle
                salle_capacity = {salle[0]: salle[1] for salle in salles}
                salle_current_count = {salle[0]: 0 for salle in salles}
                salle_index = 0

                # Assign students to salles
                for _, row in df.iterrows():
                    if pd.notnull(row["Name"]) and pd.notnull(row["Surname"]) and pd.notnull(row["Birthday"]):
                        # Find a salle with available capacity
                        while salle_index < len(salles):
                            current_salle = salles[salle_index][0]
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

                        if salle_index >= len(salles):
                            return {"error": "❌ Insufficient salle capacity to accommodate all students!", "success": False}

                conn.commit()
                return {"error": None, "success": True}

        finally:
            conn.close()

    except Exception as e:
        print(f"❌ Error in import_students_from_excel: {e}")
        return {"error": f"❌ Import error: {str(e)}", "success": False}

# Prof Page //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\\

def generate_password(length=10):
    """
    توليد كلمة مرور عشوائية.

    Args:
        length (int, optional): طول كلمة المرور. الافتراضي 10.

    Returns:
        str: كلمة المرور العشوائية.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def fetch_modules():
    """
    استرجاع قائمة المواد الدراسية من جدول exams.

    Returns:
        dict: قاموس يحتوي على 'error' (رسالة الخطأ أو None) و 'data' (قائمة المواد).
    """
    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ فشل الاتصال بقاعدة البيانات!", "data": []}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT module_name FROM exams")
            modules = [row['module_name'] for row in cursor.fetchall()]
            return {"error": None, "data": modules}
    except pymysql.Error as err:
        print(f"❌ Database Error in fetch_modules: {err}")
        return {"error": f"❌ خطأ في قاعدة البيانات: {err}", "data": []}
    finally:
        conn.close()

def add_professor(name, surname, email, correction, module):
    """
    إضافة أستاذ جديد إلى جدول professors.

    Args:
        name (str): اسم الأستاذ.
        surname (str): لقب الأستاذ.
        email (str): البريد الإلكتروني.
        correction (int): رقم التصحيح (1, 2, 3).
        module (str): المادة التي يُدرّسها.

    Returns:
        dict: قاموس يحتوي على 'error' (رسالة الخطأ أو None)، 'success' (True/False)، و 'password' (كلمة المرور).
    """
    if not (name and surname and email and module) or not isinstance(correction, int):
        return {"error": "❌ جميع الحقول مطلوبة ويجب أن تكون بالنوع الصحيح!", "success": False, "password": None}

    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ فشل الاتصال بقاعدة البيانات!", "success": False, "password": None}

    try:
        with conn.cursor() as cursor:
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                return {"error": "❌ تنسيق الإيميل غير صحيح!", "success": False, "password": None}

            cursor.execute("SELECT id FROM professors WHERE email = %s", (email,))
            if cursor.fetchone():
                return {"error": "❌ الإيميل موجود بالفعل!", "success": False, "password": None}

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
        return {"error": f"❌ خطأ في قاعدة البيانات: {err}", "success": False, "password": None}
    finally:
        conn.close()

def get_profs_from_db():
    """
    استرجاع جميع الأساتذة من جدول professors.

    Returns:
        dict: قاموس يحتوي على 'error' (رسالة الخطأ أو None) و 'data' (قائمة الأساتذة).
    """
    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ فشل الاتصال بقاعدة البيانات!", "data": []}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, email, password, correction, surname FROM professors")
            profs = cursor.fetchall()
            return {"error": None, "data": [{"name": p['name'], "email": p['email'], "password": p['password'], "correction": p['correction'], "surname": p['surname']} for p in profs]}
    except pymysql.Error as err:
        print(f"❌ Database Error in get_profs_from_db: {err}")
        return {"error": f"❌ خطأ في قاعدة البيانات: {err}", "data": []}
    finally:
        conn.close()

def delete_professor(email):
    """
    حذف أستاذ من جدول professors بناءً على البريد الإلكتروني.

    Args:
        email (str): البريد الإلكتروني للأستاذ.

    Returns:
        dict: قاموس يحتوي على 'error' (رسالة الخطأ أو None) و 'success' (True/False).
    """
    if not email:
        return {"error": "❌ الإيميل مطلوب!", "success": False}

    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ فشل الاتصال بقاعدة البيانات!", "success": False}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM professors WHERE email = %s", (email,))
            if not cursor.fetchone():
                return {"error": "❌ الأستاذ غير موجود!", "success": False}

            cursor.execute("DELETE FROM professors WHERE email = %s", (email,))
            conn.commit()
            return {"error": None, "success": True}
    except pymysql.Error as err:
        print(f"❌ Database Error in delete_professor: {err}")
        return {"error": f"❌ خطأ في قاعدة البيانات: {err}", "success": False}
    finally:
        conn.close()

def send_emails():
    """
    إرسال إيميلات إلى الأساتذة تحتوي على بيانات الحساب.

    Returns:
        dict: قاموس يحتوي على 'error' (رسالة الخطأ أو None) و 'success' (True/False).
    """
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "temouchentpfc@gmail.com")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "xrgg eqlu qkji tdcc")
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

    if not SENDER_EMAIL or not SENDER_PASSWORD:
        return {"error": "❌ يجب تحديد SENDER_EMAIL و SENDER_PASSWORD في متغيرات البيئة!", "success": False}

    professors = get_profs_from_db()
    if professors['error']:
        return {"error": professors['error'], "success": False}
    if not professors['data']:
        return {"error": "لا يوجد أساتذة في قاعدة البيانات.", "success": False}

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
        return {"error": f"فشل في إرسال الإيميلات: {e}", "success": False}

# Attendee List //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\

def get_candidates_by_salle(salle):
    """
    استرجاع المرشحين حسب اسم القاعة من جدول candidats.

    Args:
        salle (str): اسم القاعة.

    Returns:
        dict: قاموس يحتوي على 'error' (رسالة الخطأ أو None) و 'data' (قائمة المرشحين).
    """
    if not salle:
        return {"error": "❌ اسم القاعة مطلوب!", "data": []}

    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ فشل الاتصال بقاعدة البيانات!", "data": []}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, surname, salle_name FROM candidats WHERE salle_name = %s", (salle,))
            candidates = cursor.fetchall()
            return {"error": None, "data": [{"name": c['name'], "surname": c['surname'], "salle": c['salle_name']} for c in candidates]}
    except pymysql.Error as err:
        print(f"❌ Database Error in get_candidates_by_salle: {err}")
        return {"error": f"❌ خطأ في قاعدة البيانات: {err}", "data": []}
    finally:
        conn.close()

def get_all_candidates():
    """
    استرجاع جميع المرشحين من جدول candidats.

    Returns:
        dict: قاموس يحتوي على 'error' (رسالة الخطأ أو None) و 'data' (قائمة المرشحين).
    """
    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ فشل الاتصال بقاعدة البيانات!", "data": []}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, surname, anonymous_id FROM candidats")
            candidates = cursor.fetchall()
            return {"error": None, "data": [{"name": c['name'], "surname": c['surname'], "anonymous_id": c['anonymous_id']} for c in candidates]}
    except pymysql.Error as err:
        print(f"❌ Database Error in get_all_candidates: {err}")
        return {"error": f"❌ خطأ في قاعدة البيانات: {err}", "data": []}
    finally:
        conn.close()

def import_absences(file_path):
    """
    استيراد الغيابات من ملف Excel وتحديث جدول candidats.

    Args:
        file_path (str): مسار ملف Excel.

    Returns:
        dict: قاموس يحتوي على 'error' (رسالة الخطأ أو None) و 'success' (True/False).
    """
    if not os.path.exists(file_path):
        return {"error": "❌ الملف غير موجود!", "success": False}

    try:
        df = pd.read_excel(file_path)
        required_columns = {"name", "surname", "salle", "audience"}
        if not required_columns.issubset(df.columns):
            return {"error": "❌ تنسيق الملف غير صحيح. الأعمدة المطلوبة: name, surname, salle, audience", "success": False}

        conn = get_db_connection()
        if conn is None:
            return {"error": "❌ فشل الاتصال بقاعدة البيانات!", "success": False}

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
        return {"error": f"❌ خطأ أثناء استيراد الملف: {e}", "success": False}

# Result Page //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\

def institute_data():
    """
    استرجاع بيانات المعهد من جدول institutes.

    Returns:
        dict: قاموس يحتوي على 'error' (رسالة الخطأ أو None) و 'data' (بيانات المعهد).
    """
    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ فشل الاتصال بقاعدة البيانات!", "data": ("Error", 0)}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name_post, nbr_exams FROM institutes LIMIT 1")
            result = cursor.fetchone()
            return {"error": None, "data": (result['name_post'], result['nbr_exams']) if result else ("No data", 0)}
    except pymysql.Error as err:
        print(f"❌ Database Error in institute_data: {err}")
        return {"error": f"❌ خطأ في قاعدة البيانات: {err}", "data": ("Error", 0)}
    finally:
        conn.close()

def calculate_candidate_moyen(candidat_id, conn):
    """
    حساب المعدل لمرشح معين بناءً على درجاته.

    Args:
        candidat_id (int): معرف الطالب.
        conn (pymysql.connections.Connection): كائن الاتصال بقاعدة البيانات.

    Returns:
        float or None: المعدل المحسوب، أو None إذا لم تكن هناك درجات.
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
    حساب النتائج وتصديرها إلى ملف Excel.

    Args:
        salle_name (str): اسم القاعة.
        language (str): اللغة (Arabic أو English).
        output_path (str, optional): مسار حفظ ملف Excel. إذا لم يُحدد، يتم استخدام مسار افتراضي.

    Returns:
        dict: قاموس يحتوي على 'error' (رسالة الخطأ أو None)، 'success' (True/False)، و 'file_path' (مسار الملف).
    """
    if not salle_name or language not in ["Arabic", "English"]:
        return {"error": "❌ اسم القاعة واللغة مطلوبان (Arabic أو English)!", "success": False, "file_path": None}

    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ فشل الاتصال بقاعدة البيانات!", "success": False, "file_path": None}

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
                return {"error": f"لا يوجد مرشحون للقاعة: {salle_name}", "success": False, "file_path": None}

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
                    moyen = "Rejected" if language == "English" else "مرفوض"
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
                headers = ["الاسم", "اللقب", "تاريخ الميلاد"] + module_list + ["المعدل", "Sort_Moyen"]
                default_filename = f"نتائج_{salle_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            else:
                headers = ["Name", "Surname", "Birthday"] + module_list + ["Moyen", "Sort_Moyen"]
                default_filename = f"results_{salle_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

            df = pd.DataFrame(data, columns=headers)
            df['تاريخ الميلاد' if language == "Arabic" else 'Birthday'] = pd.to_datetime(
                df['تاريخ الميلاد' if language == "Arabic" else 'Birthday'], errors='coerce'
            )

            df = df.sort_values(by='Sort_Moyen', ascending=False)
            df = df.drop(columns=['Sort_Moyen'])

            file_path = output_path if output_path else os.path.join(os.getcwd(), default_filename)

            with pd.ExcelWriter(file_path, engine='openpyxl', date_format='dd/mm/yyyy') as writer:
                df.to_excel(writer, index=False)
                worksheet = writer.sheets['Sheet1']
                date_col_idx = headers.index('تاريخ الميلاد' if language == "Arabic" else 'Birthday') + 1
                for cell in worksheet[f'{chr(64 + date_col_idx)}:{chr(64 + date_col_idx)}']:
                    cell.number_format = 'DD/MM/YYYY'
                date_col_letter = get_column_letter(date_col_idx)
                worksheet.column_dimensions[date_col_letter].width = 15

            return {"error": None, "success": True, "file_path": file_path}
    except pymysql.Error as err:
        print(f"❌ Database Error in calculate_and_export_results: {err}")
        return {"error": f"❌ خطأ في قاعدة البيانات: {err}", "success": False, "file_path": None}
    except Exception as e:
        print(f"❌ Error in calculate_and_export_results: {e}")
        return {"error": f"❌ خطأ: {e}", "success": False, "file_path": None}
    finally:
        conn.close()

# Correction Page //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\

def calculate_final_grade(corr1, corr2, corr3, dif=2):
    """
    حساب الدرجة النهائية بناءً على التصحيحات الثلاثة.

    Args:
        corr1 (float): الدرجة الأولى.
        corr2 (float): الدرجة الثانية.
        corr3 (float): الدرجة الثالثة.
        dif (float, optional): الحد الأقصى للفرق المسموح. الافتراضي 2.

    Returns:
        float: الدرجة النهائية (مُقربة إلى 2 منازل عشرية).
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
    حفظ درجة الطالب وحساب الدرجة النهائية في جدول exams.

    Args:
        anonymous_id (str): المعرف المجهول للطالب.
        exam_name (str): اسم المادة.
        correction (int): رقم التصحيح (1, 2, 3).
        grade (float): الدرجة.
        coeff (float): المعامل.

    Returns:
        dict: قاموس يحتوي على 'error' (رسالة الخطأ أو None) و 'success' (True/False).
    """
    if not (anonymous_id and exam_name and isinstance(correction, int) and correction in [1, 2, 3]):
        return {"error": "❌ جميع الحقول مطلوبة ويجب أن يكون رقم التصحيح 1 أو 2 أو 3!", "success": False}

    try:
        grade = float(grade)
        coeff = float(coeff)
    except (ValueError, TypeError):
        return {"error": "❌ الدرجة والمعامل يجب أن يكونا أرقامًا!", "success": False}

    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ فشل الاتصال بقاعدة البيانات!", "success": False}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM candidats WHERE anonymous_id = %s", (anonymous_id,))
            candidat_result = cursor.fetchone()
            if not candidat_result:
                return {"error": f"❌ لا يوجد مرشح بـ anonymous_id '{anonymous_id}'", "success": False}
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
        return {"error": f"❌ خطأ في قاعدة البيانات: {err}", "success": False}
    finally:
        conn.close()

def fetch_exam_modules():
    """
    استرجاع قائمة المواد الدراسية من جدول exams.

    Returns:
        dict: قاموس يحتوي على 'error' (رسالة الخطأ أو None) و 'data' (قائمة المواد).
    """
    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ فشل الاتصال بقاعدة البيانات!", "data": []}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT module_name FROM exams")
            modules = [row['module_name'] for row in cursor.fetchall()]
            return {"error": None, "data": modules}
    except pymysql.Error as err:
        print(f"❌ Database Error in fetch_exam_modules: {err}")
        return {"error": f"❌ خطأ في قاعدة البيانات: {err}", "data": []}
    finally:
        conn.close()

def fetch_exam_details(module_name):
    """
    استرجاع تفاصيل الامتحان بناءً على اسم المادة.

    Args:
        module_name (str): اسم المادة.

    Returns:
        dict: قاموس يحتوي على 'error' (رسالة الخطأ أو None) و 'data' (تفاصيل الامتحان).
    """
    if not module_name:
        return {"error": "❌ اسم المادة مطلوب!", "data": ("", 0.0)}

    conn = get_db_connection()
    if conn is None:
        return {"error": "❌ فشل الاتصال بقاعدة البيانات!", "data": ("", 0.0)}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT module_name, coefficient FROM exams WHERE module_name = %s", (module_name,))
            result = cursor.fetchone()
            return {"error": None, "data": (result['module_name'], result['coefficient']) if result else ("", 0.0)}
    except pymysql.Error as err:
        print(f"❌ Database Error in fetch_exam_details: {err}")
        return {"error": f"❌ خطأ في قاعدة البيانات: {err}", "data": ("", 0.0)}
    finally:
        conn.close()