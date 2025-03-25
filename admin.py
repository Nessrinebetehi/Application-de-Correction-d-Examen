import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkcalendar import DateEntry
from tkinter import messagebox, filedialog
from tkinter.filedialog import asksaveasfilename
import pandas as pd
import os
import qrcode
import requests
from datetime import date
from db_connector import (
    op_save_data, insert_exam, delete_exam, delete_all_data,

)

# Create the main window
window = tk.Tk()
window.title("Admin window")

# Set window size and configuration
window_width = 800
window_height = 500
window.resizable(True, True)
window.configure(bg="#FFFFFF")
window.geometry(f"{window_width}x{window_height}")

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x_position = int((screen_width - window_width) / 2)
y_position = int((screen_height - window_height) / 2)
window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Header
header_label = tk.Label(window, text="Management of Post-Graduation\nCompetitions",
                        font=("Arial", 24, "bold"), fg="#5A7EC7", bg="#FFFFFF", justify="left")
header_label.pack(pady=15, anchor="w", padx=20)

# Menu frame
menu_frame = tk.Frame(window, bg="#5A7EC7")
menu_frame.pack(fill=tk.X, side=tk.TOP)

menu_buttons = ["Option", "Students list", "Professors list", "Attendee list", "Results"]
button_width = 15

pages = {}

def show_page(page_name):
    for page in pages.values():
        page.pack_forget()
    pages[page_name].pack(fill=tk.BOTH, expand=True)

def on_enter(button):
    button.config(bg="#4A66B0", fg="#FFFFFF")

def on_leave(button):
    button.config(bg="#5A7EC7", fg="#FFFFFF")

for idx, text in enumerate(menu_buttons):
    btn = tk.Button(menu_frame, text=text, font=("Arial", 10, "bold"), fg="#FFFFFF", bg="#5A7EC7",
                    relief=tk.FLAT, width=button_width, command=lambda page=text: show_page(page))
    btn.bind("<Enter>", lambda event, b=btn: on_enter(b))
    btn.bind("<Leave>", lambda event, b=btn: on_leave(b))
    btn.pack(side=tk.LEFT, padx=5, pady=5)

# Create pages
option_page = tk.Frame(window, bg="white")
students_page = tk.Frame(window, bg="white")
professors_page = tk.Frame(window, bg="white")
attendee_page = tk.Frame(window, bg="white")
results_page = tk.Frame(window, bg="white")

# Option page /////////////////////////////////////////////////////////////////////////////////////
tk.Label(option_page, text="Institute", font=("Arial", 14), bg="white").place(x=24, y=15)
institute_entry = tk.Entry(option_page, font=("Arial", 14), bd=2, relief="groove", bg="#FFFFFF", fg="#333333")
institute_entry.place(x=190, y=14, width=330, height=36)

tk.Label(option_page, text="Option", font=("Arial", 14), bg="white").place(x=24, y=61)
option_entry = tk.Entry(option_page, font=("Arial", 12), bd=2, relief="groove", bg="#FFFFFF", fg="#333333")
option_entry.place(x=190, y=60, width=330, height=36)

tk.Label(option_page, text="Name of posts", font=("Arial", 14), bg="white").place(x=24, y=110)
name_post_entry = tk.Entry(option_page, font=("Arial", 12), bd=2, relief="groove", bg="#FFFFFF", fg="#333333")
name_post_entry.place(x=190, y=110, width=120, height=36)

tk.Label(option_page, text="Number of exams", font=("Arial", 14), bg="white").place(x=24, y=160)
nbr_exams_options = ["1", "2", "3", "4", "5", "6"]
nbr_exams_combobox = ttk.Combobox(option_page, values=nbr_exams_options, font=("Arial", 14), state="readonly")
nbr_exams_combobox.place(x=190, y=160, width=120, height=36)
nbr_exams_combobox.current(0)

def add_exams_window():
    num_exams = int(nbr_exams_combobox.get())

    add_exam_window = tk.Toplevel(window)
    add_exam_window.title("Add Exam")
    add_exam_window.geometry("730x320")
    add_exam_window.configure(bg="white")
    add_exam_window.resizable(False, False)

    tk.Label(add_exam_window, text="Module", bg="white").place(x=54, y=43)
    tk.Label(add_exam_window, text="Coefficient", bg="white").place(x=374, y=43)

    module_entry = tk.Entry(add_exam_window, width=25)
    module_entry.place(x=120, y=39, width=217, height=27)

    coeff_entry = tk.Entry(add_exam_window, width=5)
    coeff_entry.place(x=455, y=39, width=78, height=27)

    columns = ("ID", "Module", "Coefficient")
    table = ttk.Treeview(add_exam_window, columns=columns, show="headings", height=8)

    table.heading("ID", text="ID")
    table.heading("Module", text="Module")
    table.heading("Coefficient", text="Coefficient")

    table.column("ID", width=50, anchor="center")
    table.column("Module", width=300, anchor="center")
    table.column("Coefficient", width=100, anchor="center")

    table.place(x=14, y=92, width=705, height=160)

    def load_exams():
        response = requests.get("https://pfcc.onrender.com/api/exam_modules")
        if response.status_code == 200:
            modules = response.json().get("modules", [])
            for row in table.get_children():
                table.delete(row)
            for idx, module in enumerate(modules, 1):
                detail_response = requests.get(f"https://pfcc.onrender.com/api/exam_details/{module}")
                if detail_response.status_code == 200:
                    data = detail_response.json()
                    table.insert("", "end", values=(idx, data["subject"], data["coefficient"]))
                else:
                    messagebox.showerror("Error", detail_response.json().get("error", "Failed to fetch exam details"))
        else:
            messagebox.showerror("Error", response.json().get("error", "Failed to fetch exams"))

    def add_item():
        if len(table.get_children()) < num_exams:
            module = module_entry.get().strip()
            coeff = coeff_entry.get().strip()
            if module and coeff.replace('.', '', 1).isdigit():
                result = insert_exam(module, float(coeff))
                if result["success"]:
                    load_exams()
                    module_entry.delete(0, tk.END)
                    coeff_entry.delete(0, tk.END)
                else:
                    messagebox.showerror("Error", result["error"])
            else:
                messagebox.showerror("Error", "Please enter a valid Module and Coefficient!")
        else:
            messagebox.showerror("Error", f"Cannot add more than {num_exams} exams!")

    def delete_item():
        selected_item = table.selection()
        if selected_item:
            exam_id = table.item(selected_item[0])["values"][0]
            result = delete_exam(exam_id)
            if result["success"]:
                table.delete(selected_item[0])
            else:
                messagebox.showerror("Error", result["error"])
        else:
            messagebox.showwarning("Warning", "Please select an exam to delete.")

    add_button = tk.Button(add_exam_window, text="Add", bg="#00B400", fg="white", command=add_item, width=8, bd=0)
    add_button.place(x=590, y=39, width=91, height=27)

    delete_button = tk.Button(add_exam_window, text="Delete", bg="#D10801", fg="white", command=delete_item, width=10, bd=0)
    delete_button.place(x=411, y=280, width=147, height=27)

    done_button = tk.Button(add_exam_window, text="Done", bg="#00B400", fg="white", command=add_exam_window.destroy, width=10, bd=0)
    done_button.place(x=570, y=280, width=147, height=27)

    load_exams()

tk.Label(option_page, text="Add exams", font=("Arial", 14), bg="white").place(x=24, y=227)
add_exams_btn = tk.Button(option_page, text="Add", font=("Arial", 16), bg="#5D8BCD", fg="white", bd=0, command=add_exams_window)
add_exams_btn.place(x=190, y=230, width=148, height=27)

def add_salles_window():
    add_salle_window = tk.Toplevel()
    add_salle_window.title("Add Salles")
    add_salle_window.geometry("730x320")
    add_salle_window.configure(bg="white")
    add_salle_window.resizable(False, False)

    tk.Label(add_salle_window, text="Salle name", bg="white").place(x=54, y=43)
    tk.Label(add_salle_window, text="Capacity", bg="white").place(x=374, y=43)

    salle_entry = tk.Entry(add_salle_window, width=25)
    salle_entry.place(x=120, y=39, width=217, height=27)

    capacity_entry = tk.Entry(add_salle_window, width=5)
    capacity_entry.place(x=455, y=39, width=78, height=27)

    columns = ("Code Salle", "Salle name", "Capacity")
    table = ttk.Treeview(add_salle_window, columns=columns, show="headings", height=8)

    table.heading("Code Salle", text="Code Salle")
    table.heading("Salle name", text="Salle name")
    table.heading("Capacity", text="Capacity")

    table.column("Code Salle", width=150, anchor="center")
    table.column("Salle name", width=300, anchor="center")
    table.column("Capacity", width=100, anchor="center")

    table.place(x=14, y=92, width=705, height=160)

    def load_salles():
        response = requests.get("https://pfcc.onrender.com/api/salles")
        if response.status_code == 200:
            salles = response.json().get("salles", [])
            for row in table.get_children():
                table.delete(row)
            for salle in salles:
                table.insert("", "end", values=(salle["code_salle"], salle["name_salle"], salle["capacity"]))
        else:
            messagebox.showerror("Error", response.json().get("error", "Failed to fetch salles"))

    def add_item():
        salle = salle_entry.get().strip()
        capacity = capacity_entry.get().strip()
        if salle and capacity.isdigit():
            response = requests.post(
                "https://pfcc.onrender.com/api/salles",
                json={"name": salle, "capacity": int(capacity)}
            )
            if response.status_code == 200:
                load_salles()
                salle_entry.delete(0, tk.END)
                capacity_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", response.json().get("error", "Failed to add salle"))
        else:
            messagebox.showerror("Error", "Please enter a valid Salle name and Capacity!")

    def delete_item():
        selected_item = table.selection()
        if selected_item:
            code_salle = table.item(selected_item[0])["values"][0]
            response = requests.delete(f"https://pfcc.onrender.com/api/salles/{code_salle}")
            if response.status_code == 200:
                table.delete(selected_item[0])
            else:
                messagebox.showerror("Error", response.json().get("error", "Failed to delete salle"))

    add_button = tk.Button(add_salle_window, text="Add", bg="#00B400", fg="white", command=add_item, width=8, bd=0)
    add_button.place(x=590, y=39, width=91, height=27)

    delete_button = tk.Button(add_salle_window, text="Delete", bg="#D10801", fg="white", command=delete_item, width=10, bd=0)
    delete_button.place(x=411, y=280, width=147, height=27)

    done_button = tk.Button(add_salle_window, text="Done", bg="#00B400", fg="white", command=add_salle_window.destroy, width=10, bd=0)
    done_button.place(x=570, y=280, width=147, height=27)

    load_salles()

tk.Label(option_page, text="Add salles", font=("Arial", 14), bg="white").place(x=24, y=275)
add_salles_btn = tk.Button(option_page, text="Add", font=("Arial", 16), bg="#5D8BCD", fg="white", bd=0, command=add_salles_window)
add_salles_btn.place(x=190, y=275, width=148, height=27)

def on_save():
    institute_name = institute_entry.get().strip()
    exam_option = option_entry.get().strip()
    name_post = name_post_entry.get().strip()
    nbr_exams = nbr_exams_combobox.get().strip()
    if not institute_name or not exam_option or not name_post or not nbr_exams:
        messagebox.showerror("Error", "Please fill in all required fields.")
        return
    result = op_save_data(institute_name, exam_option, name_post, int(nbr_exams))
    if result["success"]:
        messagebox.showinfo("Success", "Institute data saved successfully")
        institute_entry.delete(0, tk.END)
        option_entry.delete(0, tk.END)
        name_post_entry.delete(0, tk.END)
        nbr_exams_combobox.current(0)
    else:
        messagebox.showerror("Error", result["error"])

def show_delete_confirmation():
    confirm_window = tk.Toplevel(window)
    confirm_window.title("Confirm Deletion")
    confirm_window.geometry("300x130")

    label = tk.Label(confirm_window, text="Type 'YES' to confirm deletion:", font=("Arial", 12))
    label.pack(pady=5)

    entry = tk.Entry(confirm_window, font=("Arial", 12))
    entry.pack(pady=5)

    def confirm_delete():
        if entry.get().strip().upper() == "YES":
            result = delete_all_data()
            if result["success"]:
                messagebox.showinfo("Success", "All data deleted successfully")
            else:
                messagebox.showerror("Error", result["error"])
            confirm_window.destroy()
        else:
            messagebox.showerror("Error", "Please type 'YES' to confirm")
            confirm_window.destroy()

    ok_button = tk.Button(confirm_window, text="OK", font=("Arial", 12), bg="#D10801", fg="white",
                          command=confirm_delete)
    ok_button.pack(pady=6)
    ok_button.config(width=10)

op_delete_btn = tk.Button(option_page, text="Delete", font=("Arial", 14), bg="#D10801", fg="white", bd=0, command=show_delete_confirmation)
op_delete_btn.place(relx=0.9, y=260, width=148, height=27, anchor="e")

op_done_btn = tk.Button(option_page, text="Done", font=("Arial", 14), bg="#00B400", fg="white", bd=0, command=on_save)
op_done_btn.place(relx=0.9, y=300, width=148, height=27, anchor="e")

# Students page /////////////////////////////////////////////////////////////////////////////////////
tk.Label(students_page, text="Students list", font=("Arial", 14), bg="white").place(x=22, y=27)

def import_excel():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
    if file_path:
        with open(file_path, 'rb') as f:
            response = requests.post(
                "https://pfcc.onrender.com/api/students/import",
                files={"file": f}
            )
        if response.status_code == 200:
            messagebox.showinfo("Import Result", response.json().get("message", "Students imported successfully"))
        else:
            messagebox.showerror("Error", response.json().get("error", "Failed to import students"))

st_import_btn = tk.Button(students_page, text="Import List", font=("Arial", 14), bg="#D9D9D9", fg="black", bd=0, command=import_excel)
st_import_btn.place(x=163, y=27, width=148, height=27)

separator = ttk.Separator(students_page, orient="horizontal")
separator.place(x=270, y=66, width=300, height=2)

tk.Label(students_page, text="Option", font=("Arial", 14), bg="white").place(x=22, y=82)

def update_combobox():
    response = requests.get("https://pfcc.onrender.com/api/exam_options")
    if response.status_code == 200:
        options = response.json().get("options", [])
        st_option_combo["values"] = options
        if st_option_combo["values"]:
            st_option_combo.current(0)
    students_page.after(5000, update_combobox)

st_option_combo = ttk.Combobox(students_page, font=("Arial", 14), state="readonly")
st_option_combo.place(x=163, y=80, width=237, height=36)
update_combobox()

tk.Label(students_page, text="Name", font=("Arial", 14), bg="white").place(x=22, y=127)
name_entry = tk.Entry(students_page, font=("Arial", 14), bd=2, relief="groove", bg="#FFFFFF", fg="#333333")
name_entry.place(x=163, y=125, width=237, height=36)

tk.Label(students_page, text="Surname", font=("Arial", 14), bg="white").place(x=22, y=175)
surname_entry = tk.Entry(students_page, font=("Arial", 14), bd=2, relief="groove", bg="#FFFFFF", fg="#333333")
surname_entry.place(x=163, y=173, width=237, height=36)

tk.Label(students_page, text="Date of Birth", font=("Arial", 14), bg="white").place(x=22, y=225)
dob_entry = DateEntry(students_page, font=("Arial", 14), bg="white", fg="black",
                      date_pattern="yyyy-mm-dd", width=18)
dob_entry.place(x=163, y=220, width=237, height=36)

tk.Label(students_page, text="Salle", font=("Arial", 14), bg="white").place(x=414, y=82)
st_salle_combobox = ttk.Combobox(students_page, font=("Arial", 14), state="readonly")
st_salle_combobox.place(x=480, y=80, width=175, height=36)

def save_student_data():
    name = name_entry.get().strip()
    surname = surname_entry.get().strip()
    dob = dob_entry.get_date().strftime("%Y-%m-%d")
    salle_name = st_salle_combobox.get().strip()
    exam_option = st_option_combo.get().strip()
    if not name or not surname or not dob or not salle_name or not exam_option:
        messagebox.showerror("Error", "Please fill in all required fields.")
        return
    response = requests.post(
        "https://pfcc.onrender.com/api/students",
        json={"name": name, "surname": surname, "dob": dob, "salle_name": salle_name, "exam_option": exam_option}
    )
    if response.status_code == 200:
        messagebox.showinfo("Success", response.json().get("message", "Student added successfully"))
        name_entry.delete(0, tk.END)
        surname_entry.delete(0, tk.END)
        dob_entry.set_date(date.today())
        if st_salle_combobox['values']:
            st_salle_combobox.current(0)
        if st_option_combo['values']:
            st_option_combo.current(0)
    else:
        messagebox.showerror("Error", response.json().get("error", "Failed to add student"))

st_done_btn = tk.Button(students_page, text="Done", font=("Arial", 14), bg="#00B400", fg="white", bd=0, command=save_student_data)
st_done_btn.place(relx=0.9, y=300, width=148, height=27, anchor="e")

# Professors page /////////////////////////////////////////////////////////////////////////////////////
def import_professors():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
    if file_path:
        messagebox.showinfo("Info", "Importing professors from Excel is not yet implemented.")

tk.Label(professors_page, text="Import Prof List", font=("Arial", 14), bg="white").place(x=28, y=15)
prof_imp_btn = tk.Button(professors_page, text="Import", font=("Arial", 12), bg="#D9D9D9", fg="black", bd=0,
                         command=import_professors)
prof_imp_btn.place(x=190, y=15, width=148, height=27)

tk.Label(professors_page, text="OR", font=("Arial", 14, "bold"), bg="white").place(x=355, y=15)

def delete_selected_prof():
    selected_items = table_prof.selection()
    if not selected_items:
        messagebox.showerror("Error", "No professor selected!")
        return
    confirm = messagebox.askyesno("Confirmation", "Are you sure you want to delete the selected professor(s)?")
    if confirm:
        for item in selected_items:
            email = table_prof.item(item, "values")[1]
            response = requests.delete(f"https://pfcc.onrender.com/api/professors/{email}")
            if response.status_code == 200:
                table_prof.delete(item)
            else:
                messagebox.showerror("Error", response.json().get("error", "Failed to delete professor"))

delete_btn = tk.Button(professors_page, text="Delete", font=("Arial", 12), bg="#D10801", fg="white", bd=0, command=delete_selected_prof)
delete_btn.place(relx=0.7, y=305, width=148, height=27, anchor="e")

def send_emails_to_profs():
    response = requests.post("https://pfcc.onrender.com/api/professors/send_emails")
    if response.status_code == 200:
        messagebox.showinfo("Success", response.json().get("message", "Emails sent successfully"))
    else:
        messagebox.showerror("Error", response.json().get("error", "Failed to send emails"))

send_emails_btn = tk.Button(professors_page, text="Send Emails", font=("Arial", 12), bg="#00B400", fg="white", bd=0, command=send_emails_to_profs)
send_emails_btn.place(relx=0.9, y=305, width=148, height=27, anchor="e")

def add_prof_window():
    add_prof_window = tk.Toplevel()
    add_prof_window.title("Add Professors")
    add_prof_window.geometry("800x340")
    add_prof_window.configure(bg="white")
    add_prof_window.resizable(False, False)

    tk.Label(add_prof_window, text="Name", bg="white", font=("Arial", 12)).place(x=50, y=45)
    tk.Label(add_prof_window, text="Email", bg="white", font=("Arial", 12)).place(x=428, y=45)
    tk.Label(add_prof_window, text="Surname", bg="white", font=("Arial", 12)).place(x=50, y=120)
    tk.Label(add_prof_window, text="Module", bg="white", font=("Arial", 12)).place(x=428, y=120)
    tk.Label(add_prof_window, text="Correction", bg="white", font=("Arial", 12)).place(x=50, y=195)

    name_entry = tk.Entry(add_prof_window, font=("Arial", 12), bd=2, relief="groove")
    name_entry.place(x=135, y=36, width=235, height=36)

    email_entry = tk.Entry(add_prof_window, font=("Arial", 12), bd=2, relief="groove")
    email_entry.place(x=520, y=36, width=235, height=36)

    surname_entry = tk.Entry(add_prof_window, font=("Arial", 12), bd=2, relief="groove")
    surname_entry.place(x=135, y=111, width=235, height=36)

    corr_combobox = ttk.Combobox(add_prof_window, font=("Arial", 12), state="readonly")
    corr_combobox['values'] = ("1", "2", "3")
    corr_combobox.place(x=135, y=186, width=235, height=36)
    corr_combobox.current(0)

    module_combobox = ttk.Combobox(add_prof_window, font=("Arial", 12), state="readonly")
    module_combobox.place(x=520, y=111, width=235, height=36)
    response = requests.get("https://pfcc.onrender.com/api/exam_modules")
    if response.status_code == 200:
        module_combobox['values'] = response.json().get("modules", [])
        if module_combobox['values']:
            module_combobox.current(0)

    def cancel():
        add_prof_window.destroy()

    def done():
        name = name_entry.get().strip()
        surname = surname_entry.get().strip()
        email = email_entry.get().strip()
        correction = corr_combobox.get().strip()
        module = module_combobox.get().strip()
        if not (name and surname and email and correction and module):
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        response = requests.post(
            "https://pfcc.onrender.com/api/professors",
            json={"name": name, "surname": surname, "email": email, "correction": int(correction), "module": module}
        )
        if response.status_code == 200:
            data = response.json()
            messagebox.showinfo("Success", f"{data.get('message', 'Professor added')}\nGenerated Password: {data.get('password', 'N/A')}")
            add_prof_window.destroy()
            update_table()
        else:
            messagebox.showerror("Error", response.json().get("error", "Failed to add professor"))

    cancel_button = tk.Button(add_prof_window, text="Cancel", bg="#D10801", fg="white", font=("Arial", 12), bd=0, command=cancel)
    cancel_button.place(x=472, y=299, width=148, height=27)

    done_button = tk.Button(add_prof_window, text="Done", bg="#00B400", fg="white", font=("Arial", 12), bd=0, command=done)
    done_button.place(x=634, y=299, width=148, height=27)

add_pr_btn = tk.Button(professors_page, text="Add Prof", font=("Arial", 12), bg="#D9D9D9", fg="black", bd=0, command=add_prof_window)
add_pr_btn.place(x=406, y=15, width=148, height=27)

columns_prof = ("name", "Email", "Password")
table_prof = ttk.Treeview(professors_page, columns=columns_prof, show="headings", height=8)

for col in columns_prof:
    table_prof.heading(col, text=col)
    table_prof.column(col, anchor="center")

table_prof.place(x=25, y=55, relwidth=0.95, height=228)

def update_table():
    response = requests.get("https://pfcc.onrender.com/api/professors")
    if response.status_code == 200:
        profs = response.json().get("professors", [])
        table_prof.delete(*table_prof.get_children())
        for prof in profs:
            table_prof.insert("", "end", values=(prof["name"], prof["email"], prof["password"]))
    window.after(10000, update_table)

update_table()

# Attendee page /////////////////////////////////////////////////////////////////////////////////////
tk.Label(attendee_page, text="Export attendee List", font=("Arial", 12, "bold"), bg="white").place(x=24, y=37)

tk.Label(attendee_page, text="Salle", font=("Arial", 12), bg="white").place(x=32, y=88)
at_salle_combobox = ttk.Combobox(attendee_page, state="readonly")
at_salle_combobox.place(x=88, y=80, width=175, height=36)

def generate_excel():
    salle = at_salle_combobox.get().strip()
    if not salle:
        messagebox.showerror("Error", "Please select a salle.")
        return
    response = requests.get(f"https://pfcc.onrender.com/api/candidates/salle/{salle}")
    if response.status_code == 200:
        candidates = response.json().get("candidates", [])
        if not candidates:
            messagebox.showinfo("Info", "No candidates found for the selected salle.")
            return
        df = pd.DataFrame(candidates)
        df["audience"] = ""
        file_path = asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            df.to_excel(file_path, index=False, engine="openpyxl")
            messagebox.showinfo("Success", f"Excel file saved successfully:\n{file_path}")
    else:
        messagebox.showerror("Error", response.json().get("error", "Failed to fetch candidates"))

print_btn = tk.Button(attendee_page, text="Print", font=("Arial", 12), bg="#D9D9D9", fg="black", bd=0, command=generate_excel)
print_btn.place(x=294, y=84, width=148, height=27)

def generate_qr_codes():
    response = requests.get("https://pfcc.onrender.com/api/candidates")
    if response.status_code == 200:
        candidates = response.json().get("candidates", [])
        if not candidates:
            messagebox.showinfo("Info", "No candidates found in the database.")
            return
        qr_folder = filedialog.askdirectory(title="Select Folder to Save QR Codes")
        if qr_folder:
            qr_count = 0
            for candidate in candidates:
                qr = qrcode.make(candidate["anonymous_id"])
                filename = f"{candidate['name']}_{candidate['surname']}.png".replace(" ", "_")
                file_path = os.path.join(qr_folder, filename)
                qr.save(file_path)
                qr_count += 1
            if qr_count > 0:
                messagebox.showinfo("Success", f"{qr_count} QR codes saved successfully in '{qr_folder}'.")
    else:
        messagebox.showerror("Error", response.json().get("error", "Failed to fetch candidates"))

qr_code_btn = tk.Button(attendee_page, text="QR Code", font=("Arial", 12), bg="#D9D9D9", fg="black", bd=0, command=generate_qr_codes)
qr_code_btn.place(x=452, y=84, width=148, height=27)

separator = tk.Frame(attendee_page, bg="#D9D9D9", height=2)
separator.place(x=216, y=160, relwidth=0.45)

tk.Label(attendee_page, text="Import absences List", font=("Arial", 14), bg="white").place(x=24, y=209)

def import_absences_list():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
    if file_path:
        with open(file_path, 'rb') as f:
            response = requests.post(
                "https://pfcc.onrender.com/api/absences/import",
                files={"file": f}
            )
        if response.status_code == 200:
            messagebox.showinfo("Success", response.json().get("message", "Absences imported successfully"))
        else:
            messagebox.showerror("Error", response.json().get("error", "Failed to import absences"))

import_btn = tk.Button(attendee_page, text="Import", font=("Arial", 12), bg="#D9D9D9", bd=0, command=import_absences_list)
import_btn.place(x=294, y=209, width=162, height=26)

# Results page /////////////////////////////////////////////////////////////////////////////////////
tk.Label(results_page, text="Results List ", font=("Arial", 14, "bold"), bg="white").place(x=32, y=15)
tk.Label(results_page, text="Salle", font=("Arial", 12), bg="white").place(x=32, y=59)
r_salle_combobox = ttk.Combobox(results_page, state="readonly")
r_salle_combobox.place(x=139, y=51, width=237, height=36)

tk.Label(results_page, text="Language", font=("Arial", 12), bg="white").place(x=32, y=110)
language_combobox = ttk.Combobox(results_page, state="readonly")
language_combobox['values'] = ("English", "Arabic")
language_combobox.place(x=139, y=102, width=175, height=36)
language_combobox.current(0)

tk.Label(results_page, text="Name of posts", font=("Arial", 12), bg="white").place(x=32, y=161)
tk.Label(results_page, text="Number of exams", font=("Arial", 12), bg="white").place(x=32, y=208)

def update_institute_data():
    response = requests.get("https://pfcc.onrender.com/api/institute")
    if response.status_code == 200:
        data = response.json()
        name_post_label.config(text=data.get("name_post", "N/A"))
        nbr_exams_label.config(text=str(data.get("nbr_exams", 0)))
    results_page.after(10000, update_institute_data)

name_post_label = tk.Label(results_page, font=("Arial", 12), bg="white")
name_post_label.place(x=170, y=161)
nbr_exams_label = tk.Label(results_page, font=("Arial", 12), bg="white")
nbr_exams_label.place(x=170, y=208)
update_institute_data()

def export_results():
    salle_name = r_salle_combobox.get().strip()
    language = language_combobox.get().strip()
    if not salle_name or not language:
        messagebox.showerror("Error", "Please select a salle and language.")
        return
    response = requests.post(
        "https://pfcc.onrender.com/api/results",
        json={"salle_name": salle_name, "language": language}
    )
    if response.status_code == 200:
        data = response.json()
        messagebox.showinfo("Success", f"{data.get('message', 'Results exported successfully')}\nFile saved at: {data.get('file_path', 'N/A')}")
    else:
        messagebox.showerror("Error", response.json().get("error", "Failed to export results"))

rs_done_btn = tk.Button(
    results_page,
    text="Result",
    font=("Arial", 14),
    bg="#00B400",
    fg="white",
    bd=0,
    command=export_results
)
rs_done_btn.place(relx=0.9, y=300, width=148, height=27, anchor="e")

# Define update_salle_combobox after all comboboxes are created
def update_salle_combobox():
    response = requests.get("https://pfcc.onrender.com/api/salle_names")
    if response.status_code == 200:
        salle_names = response.json().get("salle_names", [])
        st_salle_combobox['values'] = salle_names
        at_salle_combobox['values'] = salle_names
        r_salle_combobox['values'] = salle_names
        if st_salle_combobox['values']:
            st_salle_combobox.current(0)
            at_salle_combobox.current(0)
            r_salle_combobox.current(0)
    students_page.after(5000, update_salle_combobox)

# Call update_salle_combobox after all comboboxes are defined
update_salle_combobox()

# Store pages in the dictionary
pages["Option"] = option_page
pages["Students list"] = students_page
pages["Professors list"] = professors_page
pages["Attendee list"] = attendee_page
pages["Results"] = results_page

# Show the default page
show_page("Option")

# Load and display the university logo
try:
    logo = Image.open("Logo.png")
    logo = logo.resize((80, 80), Image.LANCZOS)
    photo = ImageTk.PhotoImage(logo)
    labellogo = tk.Label(window, image=photo, bg="#FFFFFF")
    labellogo.image = photo
    labellogo.place(relx=1.0, y=8, anchor="ne")
except FileNotFoundError:
    print("Logo.png not found.")

# Run the application
window.mainloop()