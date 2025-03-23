from flask import Flask, request, jsonify, send_file
import os
from datetime import datetime

from db_connector import (
    get_db_connection, op_save_data, delete_all_data, insert_exam, get_exams, delete_exam,
    generate_code_salle, add_salle, get_all_salles, delete_salle, get_salle_names,
    update_salle_comboboxes, get_exam_options, generate_anonymous_id, save_student,
    import_students_from_excel, generate_password, fetch_modules, add_professor,
    get_profs_from_db, delete_professor, send_emails, get_candidates_by_salle,
    get_all_candidates, import_absences, institute_data, calculate_and_export_results,
    calculate_final_grade, save_grades, fetch_exam_modules, fetch_exam_details
)

app = Flask(__name__)
def home():
    return "Hello, Flask on Render!"

# نقطة نهاية لاختبار الاتصال بقاعدة البيانات (get_db_connection)
@app.route('/api/db-connection', methods=['GET'])
def test_db_connection():
    conn = get_db_connection()
    if conn:
        conn.close()
        return jsonify({"message": "Successfully connected to the database"}), 200
    return jsonify({"error": "Database connection failed"}), 500

# نقطة نهاية لحفظ بيانات المعهد (op_save_data)
@app.route('/api/institutes', methods=['POST'])
def save_institute_data():
    data = request.get_json()
    institute_name = data.get('institute_name')
    exam_option = data.get('exam_option')
    name_post = data.get('name_post')
    nbr_exams = data.get('nbr_exams')

    if not all([institute_name, exam_option, name_post]):
        return jsonify({"error": "All fields (institute_name, exam_option, name_post) are required"}), 400

    result = op_save_data(institute_name, exam_option, name_post, nbr_exams)
    if "✅" in result:
        return jsonify({"message": "Institute data saved successfully"}), 201
    return jsonify({"error": result}), 400

# نقطة نهاية لحذف جميع البيانات (delete_all_data)
@app.route('/api/delete-all-data', methods=['DELETE'])
def delete_all():
    confirmation = request.args.get('confirmation')
    if confirmation != "YES":
        return jsonify({"error": "Confirmation must be 'YES'"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Failed to connect to database"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM exams")
        cursor.execute("DELETE FROM candidats")
        cursor.execute("DELETE FROM salles")
        cursor.execute("DELETE FROM institutes")
        cursor.execute("DELETE FROM professors")
        conn.commit()
        return jsonify({"message": "All data deleted successfully"}), 200
    except Exception as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        conn.close()

# نقطة نهاية لإدراج امتحان (insert_exam)
@app.route('/api/exams', methods=['POST'])
def add_exam():
    data = request.get_json()
    candidat_id = data.get('candidat_id')
    module = data.get('module')
    coefficient = data.get('coefficient')

    if not all([candidat_id, module, coefficient]):
        return jsonify({"error": "All fields (candidat_id, module, coefficient) are required"}), 400

    result = insert_exam(candidat_id, module, coefficient)
    if result is True:
        return jsonify({"message": "Exam inserted successfully"}), 201
    return jsonify({"error": result}), 400

# نقطة نهاية لاسترجاع جميع الامتحانات (get_exams)
@app.route('/api/exams', methods=['GET'])
def get_all_exams():
    exams = get_exams()
    if isinstance(exams, list):
        return jsonify([{"id": exam[0], "module_name": exam[1], "coefficient": exam[2]} for exam in exams]), 200
    return jsonify({"error": "Failed to fetch exams"}), 500

# نقطة نهاية لحذف امتحان (delete_exam)
@app.route('/api/exams/<int:exam_id>', methods=['DELETE'])
def remove_exam(exam_id):
    result = delete_exam(exam_id)
    if result is True:
        return jsonify({"message": "Exam deleted successfully"}), 200
    return jsonify({"error": result}), 400

# نقطة نهاية لتوليد رمز قاعة (generate_code_salle)
@app.route('/api/salles/generate-code', methods=['GET'])
def generate_salle_code():
    code = generate_code_salle()
    return jsonify({"code_salle": code}), 200

# نقطة نهاية لإضافة قاعة (add_salle)
@app.route('/api/salles', methods=['POST'])
def add_new_salle():
    data = request.get_json()
    name = data.get('name')
    capacity = data.get('capacity')
    institute_id = data.get('institute_id', 1)

    if not all([name, capacity]):
        return jsonify({"error": "Name and capacity are required"}), 400

    try:
        code_salle = add_salle(name, capacity, institute_id)
        return jsonify({"message": "Salle added successfully", "code_salle": code_salle}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# نقطة نهاية لاسترجاع جميع القاعات (get_all_salles)
@app.route('/api/salles', methods=['GET'])
def get_salles():
    salles = get_all_salles()
    return jsonify([{"code_salle": salle[0], "name_salle": salle[1], "capacity": salle[2]} for salle in salles]), 200

# نقطة نهاية لحذف قاعة (delete_salle)
@app.route('/api/salles/<code_salle>', methods=['DELETE'])
def remove_salle(code_salle):
    try:
        delete_salle(code_salle)
        return jsonify({"message": "Salle deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# نقطة نهاية لاسترجاع أسماء القاعات (get_salle_names)
@app.route('/api/salle-names', methods=['GET'])
def get_salle_names_list():
    salle_names = get_salle_names()
    return jsonify({"salle_names": salle_names}), 200

# نقطة نهاية لتحديث القوائم المنسدلة (update_salle_comboboxes)
# ملاحظة: هذه الدالة تعتمد على tkinter، لذا لن تُستخدم مباشرة في الـ API
# بدلاً من ذلك، يمكننا استخدام get_salle_names لتحديث القوائم في تطبيق العميل
@app.route('/api/update-salle-list', methods=['GET'])
def update_salle_list():
    salle_names = get_salle_names()
    return jsonify({"message": "Salle list updated", "salle_names": salle_names}), 200

# نقطة نهاية لاسترجاع خيارات الامتحانات (get_exam_options)
@app.route('/api/exam-options', methods=['GET'])
def get_exam_options_list():
    options = get_exam_options()
    return jsonify({"exam_options": options}), 200

# نقطة نهاية لتوليد anonymous_id (generate_anonymous_id)
@app.route('/api/anonymous-id', methods=['GET'])
def generate_new_anonymous_id():
    anonymous_id = generate_anonymous_id()
    return jsonify({"anonymous_id": anonymous_id}), 200

# نقطة نهاية لإضافة طالب (save_student)
@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json()
    name = data.get('name')
    surname = data.get('surname')
    dob = data.get('dob')
    salle_code = data.get('salle_code')
    exam_option = data.get('exam_option')

    if not all([name, surname, dob, exam_option]):
        return jsonify({"error": "All fields (name, surname, dob, exam_option) are required"}), 400

    result = save_student(name, surname, dob, salle_code, exam_option)
    if "✅" in result:
        return jsonify({"message": "Student added successfully"}), 201
    return jsonify({"error": result}), 400

# نقطة نهاية لاستيراد الطلاب من Excel (import_students_from_excel)
@app.route('/api/students/import', methods=['POST'])
def import_students():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({"error": "File must be an Excel file (.xlsx or .xls)"}), 400

    file_path = "temp_import.xlsx"
    file.save(file_path)

    result = import_students_from_excel(file_path)
    os.remove(file_path)

    if "✅" in result:
        return jsonify({"message": "Students imported successfully"}), 201
    return jsonify({"error": result}), 400

# نقطة نهاية لتوليد كلمة مرور (generate_password)
@app.route('/api/generate-password', methods=['GET'])
def generate_new_password():
    length = request.args.get('length', default=10, type=int)
    password = generate_password(length)
    return jsonify({"password": password}), 200

# نقطة نهاية لاسترجاع الوحدات (fetch_modules)
@app.route('/api/modules', methods=['GET'])
def get_modules():
    modules = fetch_modules()
    return jsonify({"modules": modules}), 200

# نقطة نهاية لإضافة أستاذ (add_professor)
@app.route('/api/professors', methods=['POST'])
def add_new_professor():
    data = request.get_json()
    name = data.get('name')
    surname = data.get('surname')
    email = data.get('email')
    correction = data.get('correction')
    module = data.get('module')

    if not all([name, surname, email, correction, module]):
        return jsonify({"error": "All fields (name, surname, email, correction, module) are required"}), 400

    result, password = add_professor(name, surname, email, correction, module)
    if "successfully" in result:
        return jsonify({"message": result, "password": password}), 201
    return jsonify({"error": result}), 400

# نقطة نهاية لاسترجاع جميع الأساتذة (get_profs_from_db)
@app.route('/api/professors', methods=['GET'])
def get_professors():
    profs = get_profs_from_db()
    return jsonify([{"name": prof[0], "email": prof[1], "password": prof[2], "correction": prof[3], "surname": prof[4]} for prof in profs]), 200

# نقطة نهاية لحذف أستاذ (delete_professor)
@app.route('/api/professors/<email>', methods=['DELETE'])
def remove_professor(email):
    result = delete_professor(email)
    if "successfully" in result:
        return jsonify({"message": result}), 200
    return jsonify({"error": result}), 400

# نقطة نهاية لإرسال رسائل بريد إلكتروني للأساتذة (send_emails)
@app.route('/api/professors/send-emails', methods=['POST'])
def send_professor_emails():
    try:
        send_emails()
        return jsonify({"message": "Emails sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to send emails: {str(e)}"}), 500

# نقطة نهاية لاسترجاع المرشحين حسب القاعة (get_candidates_by_salle)
@app.route('/api/candidates/salle/<salle>', methods=['GET'])
def get_candidates_in_salle(salle):
    candidates = get_candidates_by_salle(salle)
    return jsonify([{"name": cand[0], "surname": cand[1], "salle_name": cand[2]} for cand in candidates]), 200

# نقطة نهاية لاسترجاع جميع المرشحين (get_all_candidates)
@app.route('/api/candidates', methods=['GET'])
def get_all_candidates_list():
    candidates = get_all_candidates()
    return jsonify([{"name": cand[0], "surname": cand[1], "anonymous_id": cand[2]} for cand in candidates]), 200

# نقطة نهاية لاستيراد الغيابات (import_absences)
@app.route('/api/absences/import', methods=['POST'])
def import_absences_data():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({"error": "File must be an Excel file (.xlsx or .xls)"}), 400

    file_path = "temp_absences.xlsx"
    file.save(file_path)

    try:
        # تعديل import_absences لتتماشى مع بيئة الـ API
        import pandas as pd
        df = pd.read_excel(file_path)
        required_columns = {"name", "surname", "salle", "audience"}
        if not required_columns.issubset(df.columns):
            return jsonify({"error": "Invalid file format. Required columns: name, surname, salle, audience"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        for _, row in df.iterrows():
            name, surname, salle, audience = row["name"], row["surname"], row["salle"], row["audience"]
            if audience == "A":
                update_query = """
                UPDATE candidats 
                SET absence = absence + 1 
                WHERE name = %s AND surname = %s AND salle_name = %s
                """
                cursor.execute(update_query, (name, surname, salle))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Absences updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to import absences: {str(e)}"}), 400
    finally:
        os.remove(file_path)

# نقطة نهاية لاسترجاع بيانات المعهد (institute_data)
@app.route('/api/institute-data', methods=['GET'])
def get_institute_data():
    name_post, nbr_exams = institute_data()
    return jsonify({"name_post": name_post, "nbr_exams": nbr_exams}), 200

# نقطة نهاية لحساب وتصدير النتائج (calculate_and_export_results)
@app.route('/api/results', methods=['POST'])
def calculate_results():
    data = request.get_json()
    selected_salle = data.get('selected_salle')
    selected_language = data.get('selected_language')

    if not all([selected_salle, selected_language]):
        return jsonify({"error": "Selected salle and language are required"}), 400

    try:
        # تعديل calculate_and_export_results لتخزين الملف في مسار محدد
        default_filename = f"results_{selected_salle}_{selected_language}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = os.path.join("results", default_filename)
        os.makedirs("results", exist_ok=True)

        # تعديل الدالة لتقبل file_path مباشرة (يجب تعديل الكود في db_connector.py أيضاً)
        calculate_and_export_results(selected_salle, selected_language, file_path=file_path)
        return jsonify({"message": "Results calculated", "file_url": f"/results/{default_filename}"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to calculate results: {str(e)}"}), 400

# نقطة نهاية لتحميل ملف النتائج
@app.route('/results/<filename>', methods=['GET'])
def download_results(filename):
    file_path = os.path.join("results", filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

# نقطة نهاية لحساب الدرجة النهائية (calculate_final_grade)
@app.route('/api/calculate-final-grade', methods=['POST'])
def calculate_grade():
    data = request.get_json()
    corr1 = data.get('corr1')
    corr2 = data.get('corr2')
    corr3 = data.get('corr3')
    dif = data.get('dif', 5)

    final_grade = calculate_final_grade(corr1, corr2, corr3, dif)
    return jsonify({"final_grade": final_grade}), 200

# نقطة نهاية لحفظ الدرجات (save_grades)
@app.route('/api/grades', methods=['POST'])
def save_student_grades():
    data = request.get_json()
    anonyme_id = data.get('anonyme_id')
    exam_module = data.get('exam_module')
    grade1 = data.get('grade1')
    grade2 = data.get('grade2')
    grade3 = data.get('grade3')
    final_grade = data.get('final_grade')
    coefficient = data.get('coefficient')

    if not all([anonyme_id, exam_module, final_grade, coefficient]):
        return jsonify({"error": "anonyme_id, exam_module, final_grade, and coefficient are required"}), 400

    success = save_grades(anonyme_id, exam_module, grade1, grade2, grade3, final_grade, coefficient)
    if success:
        return jsonify({"message": "Grades saved successfully"}), 201
    return jsonify({"error": "Failed to save grades"}), 400

# نقطة نهاية لاسترجاع وحدات الامتحانات (fetch_exam_modules)
@app.route('/api/exam-modules', methods=['GET'])
def get_exam_modules():
    modules = fetch_exam_modules()
    if modules:
        return jsonify({"modules": modules}), 200
    return jsonify({"error": "No exam modules found"}), 404

# نقطة نهاية لاسترجاع تفاصيل الامتحان (fetch_exam_details)
@app.route('/api/exam-details/<module_name>', methods=['GET'])
def get_exam_details(module_name):
    module_name, coefficient = fetch_exam_details(module_name)
    return jsonify({"module_name": module_name, "coefficient": coefficient}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
