import secrets
import pymysql
import pandas as pd
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox
import os
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
from openpyxl.utils import get_column_letter

# دالة الاتصال بقاعدة البيانات باستخدام pymysql
def get_db_connection():
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

# option page //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\

def op_save_data(institute_name, exam_option, name_post, nbr_exams):
    """حفظ البيانات في جدول institutes"""
    if not institute_name or not exam_option or not name_post:
        return "❌ يرجى ملء جميع الحقول!"

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
        return f"❌ خطأ في قاعدة البيانات: {err}"
    finally:
        conn.close()

def delete_all_data(confirm_window, entry):
    """حذف جميع البيانات من الجداول عند تأكيد المستخدم."""
    if entry.get() != "YES":
        messagebox.showwarning("تحذير", "إدخال غير صحيح! اكتب 'YES' للتأكيد.")
        return

    conn = get_db_connection()
    if conn is None:
        messagebox.showerror("خطأ", "فشل الاتصال بقاعدة البيانات.")
        return

    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM exams")
            cursor.execute("DELETE FROM candidats")
            cursor.execute("DELETE FROM salles")
            cursor.execute("DELETE FROM institutes")
            cursor.execute("DELETE FROM professors")
            conn.commit()
            messagebox.showinfo("نجاح", "تم حذف جميع البيانات بنجاح.")
            confirm_window.destroy()
    except pymysql.Error as err:
        messagebox.showerror("خطأ", f"خطأ في قاعدة البيانات: {err}")
        confirm_window.destroy()
    finally:
        conn.close()

# exams_window //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\

def insert_exam(candidat_id, module, coefficient):
    """إدراج بيانات الامتحان مع تعطيل قيود المفتاح الأجنبي مؤقتًا"""
    conn = get_db_connection()
    if conn is None:
        return "❌ فشل الاتصال بقاعدة البيانات!"

    try:
        with conn.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            sql = "INSERT INTO exams (candidat_id, module_name, coefficient) VALUES (%s, %s, %s)"
            cursor.execute(sql, (candidat_id, module, coefficient))
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
            return True
    except pymysql.Error as err:
        return f"❌ خطأ في قاعدة البيانات: {err}"
    finally:
        conn.close()

def get_exams():
    """استرجاع جميع الامتحانات من قاعدة البيانات"""
    conn = get_db_connection()
    if conn is None:
        return []

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, module_name, coefficient FROM exams")
            exams = cursor.fetchall()
            return exams
    except pymysql.Error as err:
        print(f"❌ خطأ في قاعدة البيانات: {err}")
        return []
    finally:
        conn.close()

def delete_exam(exam_id):
    """حذف امتحان بناءً على المعرف"""
    conn = get_db_connection()
    if conn is None:
        return "❌ فشل الاتصال بقاعدة البيانات!"

    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM exams WHERE id = %s", (exam_id,))
            conn.commit()
            return True
    except pymysql.Error as err:
        return f"❌ خطأ في قاعدة البيانات: {err}"
    finally:
        conn.close()

# salles_window //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\

def generate_code_salle():
    """توليد رمز قاعة فريد بصيغة SALLE-XXXX"""
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
    """إضافة قاعة جديدة إلى قاعدة البيانات"""
    code_salle = generate_code_salle()
    conn = get_db_connection()
    if conn is None:
        raise Exception("❌ فشل الاتصال بقاعدة البيانات!")

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO salles (code_salle, name_salle, capacity, institute_id) VALUES (%s, %s, %s, %s)",
                (code_salle, name, capacity, institute_id)
            )
            conn.commit()
            return code_salle
    except pymysql.Error as err:
        raise Exception(f"❌ خطأ في قاعدة البيانات: {err}")
    finally:
        conn.close()

def get_all_salles():
    """استرجاع جميع القاعات من قاعدة البيانات"""
    conn = get_db_connection()
    if conn is None:
        return []

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT code_salle, name_salle, capacity FROM salles")
            salles = cursor.fetchall()
            return salles
    except pymysql.Error as err:
        print(f"❌ خطأ في قاعدة البيانات: {err}")
        return []
    finally:
        conn.close()

def delete_salle(code_salle):
    """حذف قاعة من قاعدة البيانات باستخدام الرمز"""
    conn = get_db_connection()
    if conn is None:
        return

    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM salles WHERE code_salle = %s", (code_salle,))
            conn.commit()
    except pymysql.Error as err:
        print(f"❌ خطأ في قاعدة البيانات: {err}")
    finally:
        conn.close()

# students page //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\

def get_salle_names():
    """استرجاع أسماء القاعات"""
    conn = get_db_connection()
    if conn is None:
        print("❌ فشل الاتصال بقاعدة البيانات!")
        return []

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name_salle FROM salles")
            salles = [row['name_salle'] for row in cursor.fetchall()]
            return salles
    except pymysql.Error as err:
        print(f"❌ خطأ في قاعدة البيانات: {err}")
        return []
    finally:
        conn.close()

def update_salle_comboboxes(st_salle_combobox, at_salle_combobox, r_salle_combobox, root_window):
    """تحديث القوائم المنسدلة للقاعات كل 5 ثوانٍ"""
    salles = get_salle_names()
    for combobox in [st_salle_combobox, at_salle_combobox, r_salle_combobox]:
        combobox['values'] = salles
        if salles:
            combobox.current(0)
    root_window.after(5000, lambda: update_salle_comboboxes(st_salle_combobox, at_salle_combobox, r_salle_combobox, root_window))

def get_exam_options():
    """استرجاع خيارات الامتحانات"""
    conn = get_db_connection()
    if conn is None:
        print("❌ فشل الاتصال بقاعدة البيانات!")
        return ["Error Fetching Data"]

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT exam_option FROM institutes")
            options = [row['exam_option'] for row in cursor.fetchall()]
            return options if options else ["No Options Available"]
    except pymysql.Error as err:
        print(f"❌ خطأ في قاعدة البيانات: {err}")
        return ["Error Fetching Data"]
    finally:
        conn.close()

def generate_anonymous_id():
    """توليد معرف مجهول للطالب"""
    first_digit = random.choice("123456789")
    other_digits = ''.join(random.choices("0123456789", k=7))
    return first_digit + other_digits

def save_student(name, surname, dob, salle_code, exam_option):
    """حفظ بيانات الطالب مع التحقق من التكرار والسعة"""
    if not (name and surname and dob and exam_option):
        return "❌ جميع الحقول مطلوبة!"

    conn = get_db_connection()
    if conn is None:
        return "❌ فشل الاتصال بقاعدة البيانات!"

    try:
        with conn.cursor() as cursor:
            # التحقق من وجود الطالب
            cursor.execute(
                "SELECT id FROM candidats WHERE name = %s AND surname = %s AND birthday = %s",
                (name, surname, dob)
            )
            if cursor.fetchone():
                return "❌ هذا الطالب مسجل بالفعل!"

            # التحقق من سعة القاعة
            if salle_code:
                cursor.execute("SELECT capacity FROM salles WHERE name_salle = %s", (salle_code,))
                salle_capacity = cursor.fetchone()
                if salle_capacity:
                    cursor.execute("SELECT COUNT(*) as count FROM candidats WHERE salle_name = %s", (salle_code,))
                    current_count = cursor.fetchone()['count']
                    if current_count >= salle_capacity['capacity']:
                        return f"❌ القاعة {salle_code} ممتلئة! السعة: {salle_capacity['capacity']}"

            # إدراج الطالب
            anonymous_id = generate_anonymous_id()
            cursor.execute(
                "INSERT INTO candidats (name, surname, birthday, anonymous_id, moyen, decision, absence, salle_name) "
                "VALUES (%s, %s, %s, %s, 10.00, 'Pending', 0, %s)",
                (name, surname, dob, anonymous_id, salle_code if salle_code else None)
            )
            conn.commit()
            return "✅ تم حفظ بيانات الطالب بنجاح!"
    except pymysql.Error as err:
        return f"❌ خطأ في قاعدة البيانات: {err}"
    finally:
        conn.close()

def import_students_from_excel(file_path):
    """استيراد بيانات الطلاب من ملف Excel"""
    try:
        df = pd.read_excel(file_path)
        required_columns = {"Name", "Surname", "Birthday", "Salle Name", "Exam Option"}
        if not required_columns.issubset(df.columns):
            return "❌ ملف Excel يجب أن يحتوي على الأعمدة: Name, Surname, Birthday, Salle Name, Exam Option"

        df["Birthday"] = pd.to_datetime(df["Birthday"], errors='coerce').dt.strftime('%Y-%m-%d')

        conn = get_db_connection()
        if conn is None:
            return "❌ فشل الاتصال بقاعدة البيانات!"

        try:
            with conn.cursor() as cursor:
                for _, row in df.iterrows():
                    if pd.notnull(row["Name"]) and pd.notnull(row["Surname"]) and pd.notnull(row["Birthday"]):
                        anonymous_id = generate_anonymous_id()
                        cursor.execute(
                            "INSERT INTO candidats (name, surname, birthday, anonymous_id, moyen, decision, absence, salle_name) "
                            "VALUES (%s, %s, %s, %s, 10.00, 'Pending', 0, %s)",
                            (row["Name"], row["Surname"], row["Birthday"], anonymous_id, row["Salle Name"])
                        )
                conn.commit()
                return "✅ تم استيراد البيانات بنجاح!"
        finally:
            conn.close()
    except Exception as e:
        return f"❌ خطأ أثناء الاستيراد: {str(e)}"

# Prof page //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\\

def generate_password(length=10):
    """توليد كلمة مرور عشوائية"""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def fetch_modules():
    """استرجاع المواد من قاعدة البيانات"""
    conn = get_db_connection()
    if conn is None:
        print("❌ فشل الاتصال بقاعدة البيانات!")
        return []

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT module_name FROM exams")
            modules = [row['module_name'] for row in cursor.fetchall()]
            return modules
    except pymysql.Error as err:
        print(f"❌ خطأ في قاعدة البيانات: {err}")
        return []
    finally:
        conn.close()

def add_professor(name, surname, email, correction, module):
    """إضافة أستاذ جديد إلى قاعدة البيانات"""
    conn = get_db_connection()
    if conn is None:
        return "❌ فشل الاتصال بقاعدة البيانات!", None

    try:
        with conn.cursor() as cursor:
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                return "❌ تنسيق الإيميل غير صحيح!", None

            cursor.execute("SELECT id FROM professors WHERE email = %s", (email,))
            if cursor.fetchone():
                return "❌ الإيميل موجود بالفعل!", None

            password = generate_password()
            cursor.execute(
                "INSERT INTO professors (name, surname, email, correction, password, module) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (name, surname, email, int(correction), password, module)
            )
            conn.commit()
            return "✅ تم إضافة الأستاذ بنجاح!", password
    except pymysql.Error as err:
        return f"❌ خطأ في قاعدة البيانات: {err}", None
    finally:
        conn.close()

def get_profs_from_db():
    """استرجاع الأساتذة من قاعدة البيانات"""
    conn = get_db_connection()
    if conn is None:
        print("❌ فشل الاتصال بقاعدة البيانات!")
        return []

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, email, password, correction, surname FROM professors")
            rows = cursor.fetchall()
            return rows
    except pymysql.Error as err:
        print(f"❌ خطأ في قاعدة البيانات: {err}")
        return []
    finally:
        conn.close()

def delete_professor(email):
    """حذف أستاذ بناءً على الإيميل"""
    conn = get_db_connection()
    if conn is None:
        return "❌ فشل الاتصال بقاعدة البيانات!"

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM professors WHERE email = %s", (email,))
            if not cursor.fetchone():
                return "❌ الأستاذ غير موجود!"

            cursor.execute("DELETE FROM professors WHERE email = %s", (email,))
            conn.commit()
            return "✅ تم حذف الأستاذ بنجاح!"
    except pymysql.Error as err:
        return f"❌ خطأ في قاعدة البيانات: {err}"
    finally:
        conn.close()

def send_emails():
    """إرسال إيميلات إلى الأساتذة مع بيانات الحساب"""
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "temouchentpfc@gmail.com")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "xrgg eqlu qkji tdcc")
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("❌ يجب تحديد SENDER_EMAIL و SENDER_PASSWORD في متغيرات البيئة!")
        return

    professors = get_profs_from_db()
    if not professors:
        print("لا يوجد أساتذة في قاعدة البيانات.")
        return

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        for prof in professors:
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
        print("تم إرسال الإيميلات بنجاح!")
    except Exception as e:
        print(f"فشل في إرسال الإيميلات: {e}")

# attendee list //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\

def get_candidates_by_salle(salle):
    """استرجاع المرشحين حسب اسم القاعة"""
    conn = get_db_connection()
    if conn is None:
        return []

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, surname, salle_name FROM candidats WHERE salle_name = %s", (salle,))
            candidates = cursor.fetchall()
            return candidates
    except pymysql.Error as err:
        messagebox.showerror("خطأ في قاعدة البيانات", f"فشل في استرجاع البيانات: {err}")
        return []
    finally:
        conn.close()

def get_all_candidates():
    """استرجاع جميع المرشحين من قاعدة البيانات"""
    conn = get_db_connection()
    if conn is None:
        return []

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, surname, anonymous_id FROM candidats")
            candidates = cursor.fetchall()
            return candidates
    except pymysql.Error as err:
        messagebox.showerror("خطأ في قاعدة البيانات", f"فشل في استرجاع المرشحين: {err}")
        return []
    finally:
        conn.close()

def import_absences():
    """استيراد الغيابات من ملف Excel"""
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
    if not file_path:
        return

    try:
        df = pd.read_excel(file_path)
        required_columns = {"name", "surname", "salle", "audience"}
        if not required_columns.issubset(df.columns):
            messagebox.showerror("خطأ", "تنسيق الملف غير صحيح. الأعمدة المطلوبة: name, surname, salle, audience")
            return

        conn = get_db_connection()
        if conn is None:
            messagebox.showerror("خطأ", "فشل الاتصال بقاعدة البيانات!")
            return

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
                messagebox.showinfo("نجاح", "تم تحديث الغيابات بنجاح!")
        finally:
            conn.close()
    except Exception as e:
        messagebox.showerror("خطأ", f"فشل في استيراد الملف: {e}")

# Result page //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\

def institute_data():
    """استرجاع بيانات المعهد"""
    conn = get_db_connection()
    if conn is None:
        return ("Error", 0)

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name_post, nbr_exams FROM institutes LIMIT 1")
            result = cursor.fetchone()
            return (result['name_post'], result['nbr_exams']) if result else ("No data", 0)
    except pymysql.Error:
        return ("Error", 0)
    finally:
        conn.close()

def calculate_candidate_moyen(candidat_id, conn):
    """حساب المعدل لمرشح معين"""
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
        print(f"❌ خطأ في حساب المعدل: {err}")
        return None

def calculate_and_export_results(salle_name, language):
    """حساب وتصدير النتائج إلى ملف Excel"""
    conn = get_db_connection()
    if conn is None:
        print("❌ فشل الاتصال بقاعدة البيانات!")
        return

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
                print(f"لا يوجد مرشحون للقاعة: {salle_name}")
                return

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

            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=default_filename,
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Save Results As"
            )
            root.destroy()

            if not file_path:
                print("تم إلغاء التصدير من قبل المستخدم.")
                return

            with pd.ExcelWriter(file_path, engine='openpyxl', date_format='dd/mm/yyyy') as writer:
                df.to_excel(writer, index=False)
                worksheet = writer.sheets['Sheet1']
                date_col_idx = headers.index('تاريخ الميلاد' if language == "Arabic" else 'Birthday') + 1
                for cell in worksheet[f'{chr(64 + date_col_idx)}:{chr(64 + date_col_idx)}']:
                    cell.number_format = 'DD/MM/YYYY'
                date_col_letter = get_column_letter(date_col_idx)
                worksheet.column_dimensions[date_col_letter].width = 15

            print(f"تم حفظ ملف Excel في: {file_path}")
    except pymysql.Error as err:
        print(f"❌ خطأ في قاعدة البيانات: {err}")
    except Exception as e:
        print(f"❌ خطأ: {e}")
    finally:
        conn.close()

# correction_page //////////////////////////////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\

def calculate_final_grade(corr1, corr2, corr3, dif=2):
    """حساب الدرجة النهائية بناءً على التصحيحات"""
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
    """حفظ الدرجة والدرجة النهائية"""
    conn = get_db_connection()
    if conn is None:
        print("❌ فشل الاتصال بقاعدة البيانات!")
        return

    try:
        with conn.cursor() as cursor:
            try:
                coeff = float(coeff)
            except ValueError:
                print("❌ خطأ: يجب أن يكون المعامل رقمًا صالحًا. سيتم استخدام القيمة الافتراضية 1.0")
                coeff = 1.0

            cursor.execute("SELECT id FROM candidats WHERE anonymous_id = %s", (anonymous_id,))
            candidat_result = cursor.fetchone()
            if not candidat_result:
                print(f"❌ خطأ: لا يوجد مرشح بـ anonymous_id '{anonymous_id}'")
                return
            candidat_id = candidat_result['id']

            cursor.execute("SELECT id FROM exams WHERE candidat_id = %s AND module_name = %s", (candidat_id, exam_name))
            exam_record = cursor.fetchone()

            if not exam_record:
                cursor.execute(
                    "INSERT INTO exams (candidat_id, module_name, coefficient) VALUES (%s, %s, %s)",
                    (candidat_id, exam_name, coeff)
                )
                conn.commit()
                print(f"تم إنشاء سجل امتحان جديد لـ candidat_id {candidat_id} و module_name '{exam_name}' بمعامل {coeff}")
            else:
                cursor.execute(
                    "UPDATE exams SET coefficient = %s WHERE candidat_id = %s AND module_name = %s",
                    (coeff, candidat_id, exam_name)
                )
                conn.commit()
                print(f"تم تحديث المعامل إلى {coeff} لـ candidat_id {candidat_id} و module_name '{exam_name}'")

            if correction == 1:
                sql = "UPDATE exams SET grade_1 = %s WHERE candidat_id = %s AND module_name = %s"
            elif correction == 2:
                sql = "UPDATE exams SET grade_2 = %s WHERE candidat_id = %s AND module_name = %s"
            elif correction == 3:
                sql = "UPDATE exams SET grade_3 = %s WHERE candidat_id = %s AND module_name = %s"

            cursor.execute(sql, (grade, candidat_id, exam_name))
            conn.commit()
            print(f"تم حفظ الدرجة {grade} لـ {exam_name} مع التصحيح {correction}")

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
                print(f"تم حساب الدرجة النهائية {final_grade} وحفظها لـ {exam_name} بمعامل {db_coeff}")
    except pymysql.Error as err:
        print(f"❌ خطأ في قاعدة البيانات: {err}")
    finally:
        conn.close()

def fetch_exam_modules():
    """استرجاع المواد الدراسية للامتحانات"""
    conn = get_db_connection()
    if conn is None:
        return []

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT module_name FROM exams")
            modules = [row['module_name'] for row in cursor.fetchall()]
            return modules
    except pymysql.Error as err:
        print(f"❌ خطأ في قاعدة البيانات: {err}")
        return []
    finally:
        conn.close()

def fetch_exam_details(module_name):
    """استرجاع تفاصيل الامتحان بناءً على اسم المادة"""
    conn = get_db_connection()
    if conn is None:
        return ("", 0.0)

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT module_name, coefficient FROM exams WHERE module_name = %s", (module_name,))
            result = cursor.fetchone()
            return (result['module_name'], result['coefficient']) if result else ("", 0.0)
    except pymysql.Error as err:
        print(f"❌ خطأ في قاعدة البيانات: {err}")
        return ("", 0.0)
    finally:
        conn.close()