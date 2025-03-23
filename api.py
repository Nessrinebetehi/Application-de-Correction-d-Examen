from flask import Flask, request, jsonify
import os
from flask_cors import CORS
from db_connector import (
    get_db_connection, op_save_data, insert_exam, get_exams, delete_exam, 
    add_salle, get_all_salles, delete_salle, save_student, import_students_from_excel,
    get_salle_names, get_exam_options, add_professor, get_profs_from_db, delete_professor,
    send_emails, get_candidates_by_salle, get_all_candidates, import_absences,
    calculate_and_export_results, save_grade, fetch_exam_modules, fetch_exam_details
)
app = Flask(__name__)
CORS(app)

# نقطة نهاية للتحقق من حالة الخادم
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "API is running"}), 200

# نقاط نهاية لـ Option Page
@app.route('/api/institute', methods=['POST'])
def save_institute():
    data = request.get_json()
    institute_name = data.get('institute_name')
    exam_option = data.get('exam_option')
    name_post = data.get('name_post')
    nbr_exams = data.get('nbr_exams')
    result = op_save_data(institute_name, exam_option, name_post, nbr_exams)
    return jsonify({"message": result}), 200 if "✅" in result else 400

# نقاط نهاية لـ Exams
@app.route('/api/exams', methods=['POST'])
def add_exam():
    data = request.get_json()
    candidat_id = data.get('candidat_id', 1)  # افتراضي إذا لم يُحدد
    module = data.get('module')
    coefficient = data.get('coefficient')
    result = insert_exam(candidat_id, module, coefficient)
    return jsonify({"message": "Exam added" if result is True else str(result)}), 200 if result is True else 400

@app.route('/api/exams', methods=['GET'])
def list_exams():
    exams = get_exams()
    return jsonify({"exams": [{"id": e[0], "module": e[1], "coefficient": e[2]} for e in exams]}), 200

@app.route('/api/exams/<int:exam_id>', methods=['DELETE'])
def remove_exam(exam_id):
    result = delete_exam(exam_id)
    return jsonify({"message": "Exam deleted" if result is True else str(result)}), 200 if result is True else 400

# نقاط نهاية لـ Salles
@app.route('/api/salles', methods=['POST'])
def create_salle():
    data = request.get_json()
    name = data.get('name')
    capacity = data.get('capacity')
    code_salle = add_salle(name, capacity)
    return jsonify({"message": "Salle added", "code_salle": code_salle}), 200

@app.route('/api/salles', methods=['GET'])
def list_salles():
    salles = get_all_salles()
    return jsonify({"salles": [{"code_salle": s[0], "name": s[1], "capacity": s[2]} for s in salles]}), 200

@app.route('/api/salles/<code_salle>', methods=['DELETE'])
def remove_salle(code_salle):
    delete_salle(code_salle)
    return jsonify({"message": "Salle deleted"}), 200

# نقاط نهاية لـ Students
@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json()
    name = data.get('name')
    surname = data.get('surname')
    dob = data.get('dob')
    salle_code = data.get('salle_code')
    exam_option = data.get('exam_option')
    result = save_student(name, surname, dob, salle_code, exam_option)
    return jsonify({"message": result}), 200 if "✅" in result else 400

@app.route('/api/students/import', methods=['POST'])
def import_students():
    file = request.files.get('file')
    if not file:
        return jsonify({"message": "No file uploaded"}), 400
    file_path = f"temp_{file.filename}"
    file.save(file_path)
    result = import_students_from_excel(file_path)
    os.remove(file_path)  # حذف الملف المؤقت بعد الاستيراد
    return jsonify({"message": result}), 200 if "✅" in result else 400

@app.route('/api/salle_names', methods=['GET'])
def salle_names():
    salles = get_salle_names()
    return jsonify({"salle_names": salles}), 200

@app.route('/api/exam_options', methods=['GET'])
def exam_options():
    options = get_exam_options()
    return jsonify({"exam_options": options}), 200

# نقاط نهاية لـ Professors
@app.route('/api/professors', methods=['POST'])
def create_professor():
    data = request.get_json()
    name = data.get('name')
    surname = data.get('surname')
    email = data.get('email')
    correction = data.get('correction')
    module = data.get('module')
    result, password = add_professor(name, surname, email, correction, module)
    return jsonify({"message": result, "password": password}), 200 if "successfully" in result else 400

@app.route('/api/professors', methods=['GET'])
def list_professors():
    profs = get_profs_from_db()
    return jsonify({"professors": [{"name": p[0], "email": p[1], "password": p[2], "correction": p[3], "surname": p[4]} for p in profs]}), 200

@app.route('/api/professors/<email>', methods=['DELETE'])
def remove_professor(email):
    result = delete_professor(email)
    return jsonify({"message": result}), 200 if "successfully" in result else 400

@app.route('/api/professors/send_emails', methods=['POST'])
def trigger_send_emails():
    send_emails()
    return jsonify({"message": "Emails sent"}), 200

# نقاط نهاية لـ Attendee
@app.route('/api/candidates/<salle>', methods=['GET'])
def candidates_by_salle(salle):
    candidates = get_candidates_by_salle(salle)
    return jsonify({"candidates": [{"name": c[0], "surname": c[1], "salle": c[2]} for c in candidates]}), 200

@app.route('/api/candidates', methods=['GET'])
def all_candidates():
    candidates = get_all_candidates()
    return jsonify({"candidates": [{"name": c[0], "surname": c[1], "anonymous_id": c[2]} for c in candidates]}), 200

@app.route('/api/absences/import', methods=['POST'])
def import_absences_endpoint():
    file = request.files.get('file')
    if not file:
        return jsonify({"message": "No file uploaded"}), 400
    file_path = f"temp_{file.filename}"
    file.save(file_path)
    import_absences(file_path)  # يفترض أن يتم تعديل الدالة لقبول مسار الملف
    os.remove(file_path)
    return jsonify({"message": "Absences imported"}), 200

# نقاط نهاية لـ Results
@app.route('/api/results', methods=['POST'])
def export_results():
    data = request.get_json()
    salle_name = data.get('salle_name')
    language = data.get('language')
    calculate_and_export_results(salle_name, language)
    return jsonify({"message": "Results exported"}), 200

# نقاط نهاية لـ Corrections
@app.route('/api/grades', methods=['POST'])
def save_grade_endpoint():
    data = request.get_json()
    anonymous_id = data.get('anonymous_id')
    exam_name = data.get('exam_name')
    correction = data.get('correction')
    grade = data.get('grade')
    coeff = data.get('coeff')
    save_grade(anonymous_id, exam_name, correction, grade, coeff)
    return jsonify({"message": "Grade saved"}), 200

@app.route('/api/exam_modules', methods=['GET'])
def exam_modules():
    modules = fetch_exam_modules()
    return jsonify({"modules": modules}), 200

@app.route('/api/exam_details/<module_name>', methods=['GET'])
def exam_details(module_name):
    subject, coeff = fetch_exam_details(module_name)
    return jsonify({"subject": subject, "coefficient": coeff}), 200

# تشغيل الخادم على Render
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))