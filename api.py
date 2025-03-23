import os
from flask import Flask, request, jsonify, send_file
from db_connector import (
    get_db_connection, op_save_data, insert_exam, get_exams, delete_exam,
    generate_code_salle, add_salle, get_all_salles, delete_salle,
    get_salle_names, get_exam_options, generate_anonymous_id, save_student,
    import_students_from_excel, generate_password, fetch_modules, add_professor,
    get_profs_from_db, delete_professor, send_emails, get_candidates_by_salle,
    get_all_candidates, import_absences, institute_data, calculate_candidate_moyen,
    calculate_and_export_results, save_grade, fetch_exam_modules, fetch_exam_details
)
import pandas as pd
from io import BytesIO
import mysql.connector

app = Flask(__name__)

# Root endpoint
@app.route("/")
def home():
    return jsonify({"message": "Flask API is running on Render!"}), 200

# --- Institutes ---
@app.route("/institutes", methods=["POST"])
def save_institute():
    try:
        data = request.get_json()
        institute_name = data.get("institute_name")
        exam_option = data.get("exam_option")
        name_post = data.get("name_post")
        nbr_exams = data.get("nbr_exams")
        result = op_save_data(institute_name, exam_option, name_post, nbr_exams)
        return jsonify({"message": result}), 200 if "✅" in result else 400
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/institutes/data", methods=["GET"])
def get_institute_data():
    try:
        name_post, nbr_exams = institute_data()
        return jsonify({"name_post": name_post, "nbr_exams": nbr_exams}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

# --- Delete All Data ---
@app.route("/delete_all", methods=["POST"])
def delete_all():
    try:
        data = request.get_json()
        confirmation = data.get("confirmation")
        if confirmation != "YES":
            return jsonify({"message": "Send 'confirmation': 'YES' to proceed."}), 400
        
        conn = get_db_connection()
        if conn is None:
            return jsonify({"message": "Database connection failed!"}), 500
        
        cursor = conn.cursor()
        for table in ["exams", "candidats", "salles", "institutes", "professors"]:
            cursor.execute(f"DELETE FROM {table}")
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "All data deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

# --- Exams ---
@app.route("/exams", methods=["POST"])
def add_exam():
    try:
        data = request.get_json()
        candidat_id = data.get("candidat_id")
        module = data.get("module")
        coefficient = data.get("coefficient")
        result = insert_exam(candidat_id, module, coefficient)
        return jsonify({"message": "Exam inserted!" if result is True else f"Error: {result}"}), 201 if result is True else 400
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/exams", methods=["GET"])
def list_exams():
    try:
        exams = get_exams()
        return jsonify({"exams": [{"id": e[0], "module_name": e[1], "coefficient": e[2]} for e in exams]}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/exams/<int:exam_id>", methods=["DELETE"])
def remove_exam(exam_id):
    try:
        result = delete_exam(exam_id)
        return jsonify({"message": "Exam deleted!" if result is True else f"Error: {result}"}), 200 if result is True else 400
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/exams/modules", methods=["GET"])
def list_exam_modules():
    try:
        modules = fetch_exam_modules()
        return jsonify({"modules": modules}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/exams/details/<string:module_name>", methods=["GET"])
def get_exam_details(module_name):
    try:
        module_name, coefficient = fetch_exam_details(module_name)
        return jsonify({"module_name": module_name, "coefficient": coefficient}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

# --- Salles ---
@app.route("/salles", methods=["POST"])
def create_salle():
    try:
        data = request.get_json()
        name = data.get("name")
        capacity = data.get("capacity")
        institute_id = data.get("institute_id", 1)
        code_salle = add_salle(name, capacity, institute_id)
        return jsonify({"message": "Room added!", "code_salle": code_salle}), 201
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 400

@app.route("/salles", methods=["GET"])
def list_salles():
    try:
        salles = get_all_salles()
        return jsonify({"salles": [{"code_salle": s[0], "name_salle": s[1], "capacity": s[2]} for s in salles]}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/salles/<string:code_salle>", methods=["DELETE"])
def remove_salle(code_salle):
    try:
        delete_salle(code_salle)
        return jsonify({"message": "Room deleted!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 400

@app.route("/salles/names", methods=["GET"])
def list_salle_names():
    try:
        salles = get_salle_names()
        return jsonify({"salle_names": salles}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

# --- Students ---
@app.route("/students", methods=["POST"])
def add_student():
    try:
        data = request.get_json()
        name = data.get("name")
        surname = data.get("surname")
        dob = data.get("birthday")
        salle_code = data.get("salle_name")
        exam_option = data.get("exam_option")
        result = save_student(name, surname, dob, salle_code, exam_option)
        return jsonify({"message": result}), 200 if "✅" in result else 400
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/students/import", methods=["POST"])
def import_students():
    try:
        if 'file' not in request.files:
            return jsonify({"message": "No file uploaded!"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"message": "No file selected!"}), 400
        file_content = BytesIO(file.read())
        result = import_students_from_excel(file_content)
        return jsonify({"message": result}), 200 if "✅" in result else 400
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/exam_options", methods=["GET"])
def list_exam_options():
    try:
        options = get_exam_options()
        return jsonify({"exam_options": options}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

# --- Professors ---
@app.route("/professors", methods=["POST"])
def create_professor():
    try:
        data = request.get_json()
        name = data.get("name")
        surname = data.get("surname")
        email = data.get("email")
        correction = data.get("correction")
        module = data.get("module")
        result, password = add_professor(name, surname, email, correction, module)
        return jsonify({"message": result, "password": password}), 200 if "successfully" in result else 400
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/professors", methods=["GET"])
def list_professors():
    try:
        profs = get_profs_from_db()
        return jsonify({"professors": [{"name": p[0], "email": p[1], "password": p[2], "correction": p[3], "surname": p[4]} for p in profs]}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/professors/<string:email>", methods=["DELETE"])
def remove_professor(email):
    try:
        result = delete_professor(email)
        return jsonify({"message": result}), 200 if "successfully" in result else 400
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/professors/send_emails", methods=["POST"])
def trigger_send_emails():
    try:
        send_emails()
        return jsonify({"message": "Emails sent successfully!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/modules", methods=["GET"])
def list_modules():
    try:
        modules = fetch_modules()
        return jsonify({"modules": modules}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

# --- Candidates ---
@app.route("/candidates/salle/<string:salle>", methods=["GET"])
def list_candidates_by_salle(salle):
    try:
        candidates = get_candidates_by_salle(salle)
        return jsonify({"candidates": [{"name": c[0], "surname": c[1], "salle_name": c[2]} for c in candidates]}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/candidates", methods=["GET"])
def list_all_candidates():
    try:
        candidates = get_all_candidates()
        return jsonify({"candidates": [{"name": c[0], "surname": c[1], "anonymous_id": c[2]} for c in candidates]}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/candidates/import_absences", methods=["POST"])
def upload_absences():
    try:
        if 'file' not in request.files:
            return jsonify({"message": "No file uploaded!"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"message": "No file selected!"}), 400
        file_content = BytesIO(file.read())
        result = import_absences(file_content)  # Adapted to accept BytesIO
        return jsonify({"message": "Absences updated successfully!" if not result else result}), 200 if not result or "successfully" in result else 400
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

# --- Results ---
@app.route("/results/<string:salle_name>", methods=["GET"])
def export_results(salle_name):
    try:
        language = request.args.get("language", "English")
        conn = get_db_connection()
        if not conn:
            return jsonify({"message": "Database connection failed!"}), 500
        
        cursor = conn.cursor()
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
            return jsonify({"message": f"No candidates found for salle: {salle_name}"}), 404

        data = []
        module_list = None
        for candidat_id, name, surname, birthday, absence, modules, grades in candidates:
            moyen = calculate_candidate_moyen(candidat_id, conn)
            moyen_for_sorting = moyen if moyen is not None else -1
            if absence and absence > 2:
                moyen = "Rejected" if language == "English" else "مرفوض"
                moyen_for_sorting = -1
            else:
                moyen = "N/A" if moyen is None else moyen

            module_list = modules.split(',') if modules else []
            grade_list = [float(g) if g else "N/A" for g in (grades.split(',') if grades else [])]
            row = [name, surname, birthday] + grade_list + [moyen]
            data.append(row)

        headers = ["Name", "Surname", "Birthday"] if language == "English" else ["الاسم", "اللقب", "تاريخ الميلاد"]
        headers += module_list
        headers.append("Moyen" if language == "English" else "المعدل")

        df = pd.DataFrame(data, columns=headers)
        df['Birthday' if language == "English" else 'تاريخ الميلاد'] = pd.to_datetime(df['Birthday' if language == "English" else 'تاريخ الميلاد'], errors='coerce')

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
            worksheet = writer.sheets['Sheet1']
            worksheet.column_dimensions['C'].width = 15  # Adjust birthday column width
        output.seek(0)

        filename = f"results_{salle_name}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return send_file(output, download_name=filename, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

# --- Corrections ---
@app.route("/grades", methods=["POST"])
def save_exam_grade():
    try:
        data = request.get_json()
        anonymous_id = data.get("anonymous_id")
        exam_name = data.get("exam_name")
        correction = data.get("correction")
        grade = data.get("grade")
        coeff = data.get("coefficient")
        save_grade(anonymous_id, exam_name, correction, grade, coeff)
        return jsonify({"message": "Grade saved successfully!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

# Run the app for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)