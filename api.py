from flask import Flask, jsonify, request
import os
from db_connector import (
    get_all_salles, add_salle, delete_salle, get_salle_names,
    save_student, get_exam_options, import_students_from_excel,
    add_professor,import_professors_from_excel, get_profs_from_db, delete_professor, send_emails,
    get_candidates_by_salle, get_all_candidates, import_absences,
    institute_data, calculate_and_export_results,
    save_grade, fetch_exam_modules, fetch_exam_details, insert_exam,
    op_save_data, delete_exam, delete_all_data,check_login  # New imports added
)
from flask import send_file

app = Flask(__name__)

@app.route('/api/login', methods=['POST'])
def login():
    """
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    result = check_login(email, password)
    if result['error']:
        return jsonify({"error": result['error']}), 401
    return jsonify({"role": result['role'], "correction": result['correction']}), 200


@app.route('/api/salles', methods=['GET'])
def list_salles():

    result = get_all_salles()
    if result['error']:
        return jsonify({"error": result['error'], "salles": []}), 500
    return jsonify({"salles": result['data']}), 200


@app.route('/api/salles', methods=['POST'])
def create_salle():

    data = request.get_json()
    name = data.get('name')
    capacity = data.get('capacity')

    if not name or not isinstance(capacity, int) or capacity <= 0:
        return jsonify({"error": "Name and capacity (positive integer) are required!"}), 400

    result = add_salle(name, capacity)
    if result['error']:
        return jsonify({"error": result['error']}), 400
    return jsonify({"message": "Salle added", "code_salle": result['code_salle']}), 200


@app.route('/api/salles/<code_salle>', methods=['DELETE'])
def remove_salle(code_salle):

    result = delete_salle(code_salle)
    if result['error']:
        return jsonify({"error": result['error']}), 400
    return jsonify({"message": "Salle deleted"}), 200


@app.route('/api/salle_names', methods=['GET'])
def salle_names():

    result = get_salle_names()
    if result['error']:
        return jsonify({"error": result['error'], "salle_names": []}), 500
    return jsonify({"salle_names": result['data']}), 200


@app.route('/api/students', methods=['POST'])
def add_student():

    data = request.get_json()
    name = data.get('name')
    surname = data.get('surname')
    dob = data.get('dob')
    salle_name = data.get('salle_name')
    exam_option = data.get('exam_option')

    result = save_student(name, surname, dob, salle_name, exam_option)
    if result['error']:
        return jsonify({"error": result['error']}), 400
    return jsonify({"message": "Student added successfully"}), 200


@app.route('/api/exam_options', methods=['GET'])
def exam_options():

    result = get_exam_options()
    if result['error']:
        return jsonify({"error": result['error'], "options": []}), 500
    return jsonify({"options": result['data']}), 200


@app.route('/api/exams', methods=['POST'])
def add_exam_endpoint():

    data = request.get_json()
    module = data.get('module')
    coefficient = data.get('coefficient')

    if not module or not isinstance(coefficient, (int, float)):
        return jsonify({"error": "Module and coefficient (number) are required!"}), 400


    result = insert_exam(0, module, coefficient)
    if result['error']:
        return jsonify({"error": result['error']}), 400
    return jsonify({"message": "Exam added successfully"}), 200


@app.route('/api/students/import', methods=['POST'])
def import_students():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    file_path = f"temp_{file.filename}"
    file.save(file_path)
    result = import_students_from_excel(file_path)
    os.remove(file_path) 

    if result['error']:
        return jsonify({"error": result['error']}), 400
    return jsonify({"message": "Students imported successfully"}), 200


@app.route('/api/professors/import', methods=['POST'])
def import_professors():
    """
    Import professors from an uploaded Excel file.
    Expects columns: Name, Surname, Email, Correction, Module.
    Returns summary of successful imports and any errors.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        return jsonify({"error": "File must be an Excel file (.xlsx or .xls)"}), 400

    # Check if file is empty
    file.seek(0, os.SEEK_END)
    if file.tell() == 0:
        return jsonify({"error": "Uploaded file is empty"}), 400
    file.seek(0)  # Reset file pointer to beginning

    # Call the import function from db_connector
    result = import_professors_from_excel(file)

    if result['error']:
        return jsonify({"error": result['error']}), 400

    response = {
        "message": f"Imported {result['success_count']} professor(s) successfully",
        "success_count": result['success_count'],
        "errors": result['errors']
    }
    return jsonify(response), 200 if result['success_count'] > 0 else 400

@app.route('/api/professors', methods=['POST'])
def create_professor():

    data = request.get_json()
    name = data.get('name')
    surname = data.get('surname')
    email = data.get('email')
    correction = data.get('correction')
    module = data.get('module')

    result = add_professor(name, surname, email, correction, module)
    if result['error']:
        return jsonify({"error": result['error']}), 400
    return jsonify({"message": "Professor added", "password": result['password']}), 200


@app.route('/api/professors', methods=['GET'])
def list_professors():

    result = get_profs_from_db()
    if result['error']:
        return jsonify({"error": result['error'], "professors": []}), 500
    return jsonify({"professors": result['data']}), 200


@app.route('/api/professors/<email>', methods=['DELETE'])
def remove_professor(email):

    result = delete_professor(email)
    if result['error']:
        return jsonify({"error": result['error']}), 400
    return jsonify({"message": "Professor deleted"}), 200


@app.route('/api/professors/send_emails', methods=['POST'])
def trigger_send_emails():

    result = send_emails()
    if result['error']:
        return jsonify({"error": result['error']}), 400
    return jsonify({"message": "Emails sent successfully"}), 200


@app.route('/api/candidates/salle/<salle_name>', methods=['GET'])
def candidates_by_salle(salle_name):

    result = get_candidates_by_salle(salle_name)
    if result['error']:
        return jsonify({"error": result['error'], "candidates": []}), 500
    return jsonify({"candidates": result['data']}), 200


@app.route('/api/candidates', methods=['GET'])
def all_candidates():

    result = get_all_candidates()
    if result['error']:
        return jsonify({"error": result['error'], "candidates": []}), 500
    return jsonify({"candidates": result['data']}), 200


@app.route('/api/absences/import', methods=['POST'])
def import_absences_endpoint():

    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    file_path = f"temp_{file.filename}"
    file.save(file_path)
    result = import_absences(file_path)
    os.remove(file_path)

    if result['error']:
        return jsonify({"error": result['error']}), 400
    return jsonify({"message": "Absences imported successfully"}), 200


@app.route('/api/institute', methods=['GET'])
def get_institute_data():

    result = institute_data()
    if result['error']:
        return jsonify({"error": result['error'], "name_post": "Error", "nbr_exams": 0}), 500
    name_post, nbr_exams = result['data']
    return jsonify({"name_post": name_post, "nbr_exams": nbr_exams}), 200


@app.route('/api/institutes', methods=['POST'])
def save_institute_data():

    data = request.get_json()
    institute_name = data.get('institute_name')
    exam_option = data.get('exam_option')
    name_post = data.get('name_post')
    nbr_exams = data.get('nbr_exams')

    if not all([institute_name, exam_option, name_post]) or not isinstance(nbr_exams, int):
        return jsonify({"error": "All fields (institute_name, exam_option, name_post, nbr_exams) are required and nbr_exams must be an integer!"}), 400

    result = op_save_data(institute_name, exam_option, name_post, nbr_exams)
    if "❌" in result:
        return jsonify({"error": result}), 400
    return jsonify({"message": result}), 200


@app.route('/api/exams/<int:exam_id>', methods=['DELETE'])
def remove_exam(exam_id):

    result = delete_exam(exam_id)
    if result['error']:
        return jsonify({"error": result['error']}), 400
    return jsonify({"message": "Exam deleted successfully"}), 200


@app.route('/api/data', methods=['DELETE'])
def delete_all():

    result = delete_all_data()
    if result['error']:
        return jsonify({"error": result['error']}), 400
    return jsonify({"message": "All data deleted successfully"}), 200


@app.route('/api/results', methods=['POST'])
def export_results():

    data = request.get_json()
    salle_name = data.get('salle_name')
    language = data.get('language')
    result = calculate_and_export_results(salle_name, language)
    if result['error']:
        return jsonify({"error": result['error']}), 400
    return send_file(result['file_path'], as_attachment=True)


@app.route('/api/grades', methods=['POST'])
def save_grade_endpoint():

    data = request.get_json()
    anonymous_id = data.get('anonymous_id')
    exam_name = data.get('exam_name')
    correction = data.get('correction')
    grade = data.get('grade')
    coeff = data.get('coeff')

    result = save_grade(anonymous_id, exam_name, correction, grade, coeff)
    if result['error']:
        return jsonify({"error": result['error']}), 400
    return jsonify({"message": "Grade saved successfully"}), 200


@app.route('/api/exam_modules', methods=['GET'])
def exam_modules():

    result = fetch_exam_modules()
    if result['error']:
        return jsonify({"error": result['error'], "modules": []}), 500
    return jsonify({"modules": result['data']}), 200


@app.route('/api/exam_details/<module_name>', methods=['GET'])
def exam_details(module_name):

    result = fetch_exam_details(module_name)
    if result['error']:
        return jsonify({"error": result['error'], "subject": "", "coefficient": 0.0}), 500
    subject, coeff = result['data']
    return jsonify({"subject": subject, "coefficient": coeff}), 200

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)