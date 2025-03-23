#admin.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkcalendar import DateEntry
from tkinter import messagebox
from tkinter import filedialog, messagebox
from tkinter.filedialog import asksaveasfilename
import pandas as pd
import os
import qrcode
from datetime import date
from db_connector import op_save_data,insert_exam,get_exams,delete_exam,delete_all_data
from db_connector import add_salle,get_all_salles,delete_salle,generate_code_salle
from db_connector import get_db_connection
from db_connector import get_salle_names,update_salle_comboboxes,get_exam_options,save_student,import_students_from_excel 
from db_connector import get_candidates_by_salle,get_all_candidates,import_absences
from db_connector import fetch_modules, add_professor,get_profs_from_db,delete_professor,send_emails
from db_connector import institute_data,calculate_and_export_results
import mysql.connector


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


header_label = tk.Label(window, text="Management of Post-Graduation\nCompetitions", 
                        font=("Arial", 24, "bold"), fg="#5A7EC7", bg="#FFFFFF", justify="left")
header_label.pack(pady=15, anchor="w", padx=20)


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
    button.config(bg="#4A66B0", fg="#FFFFFF")  # Darken background on hover

def on_leave(button):
    button.config(bg="#5A7EC7", fg="#FFFFFF")  # Revert back when mouse leaves


for idx, text in enumerate(menu_buttons):
    btn = tk.Button(menu_frame, text=text, font=("Arial", 10, "bold"), fg="#FFFFFF", bg="#5A7EC7", 
                    relief=tk.FLAT, width=button_width, command=lambda page=text: show_page(page))
    

    btn.bind("<Enter>", lambda event, b=btn: on_enter(b))
    btn.bind("<Leave>", lambda event, b=btn: on_leave(b))

    btn.pack(side=tk.LEFT, padx=5, pady=5)


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
        """Load exams from the database and display them in the table"""
        for row in table.get_children():
            table.delete(row)

        exams = get_exams()
        for exam in exams:
            table.insert("", "end", values=exam)

    def add_item():
        """Add a new exam to the database and display it in the table"""
        if len(table.get_children()) < num_exams:
            module = module_entry.get().strip()
            coeff = coeff_entry.get().strip()

            if module and coeff.replace('.', '', 1).isdigit():
                candidat_id = 1  # This should be set based on actual data

                result = insert_exam(candidat_id, module, float(coeff))

                if result is True:
                    load_exams()  # Refresh the table after insertion
                    module_entry.delete(0, tk.END)
                    coeff_entry.delete(0, tk.END)
                else:
                    messagebox.showerror("Database Error", f"Error: {result}")
            else:
                messagebox.showerror("Error", "Please enter a valid Module and Coefficient!")
        else:
            messagebox.showwarning("Warning", f"You can only add {num_exams} exams!")

    def delete_item():
        """Delete the selected exam from the database"""
        selected_item = table.selection()
        if selected_item:
            for item in selected_item:
                exam_id = table.item(item)["values"][0]  # Retrieve exam ID
                result = delete_exam(exam_id)

                if result is True:
                    table.delete(item)
                else:
                    messagebox.showerror("Database Error", f"Error: {result}")
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
        for row in table.get_children():
            table.delete(row)

        salles = get_all_salles()
        for salle in salles:
            table.insert("", "end", values=salle)

    def add_item():
        salle = salle_entry.get().strip()
        capacity = capacity_entry.get().strip()

        if salle and capacity.isdigit():
            try:
                code_salle = add_salle(salle, int(capacity))  # Call function from database.py
                table.insert("", "end", values=(code_salle, salle, capacity))

                salle_entry.delete(0, tk.END)
                capacity_entry.delete(0, tk.END)

            except Exception as e:
                messagebox.showerror("Database Error", f"Error: {e}")

        else:
            messagebox.showerror("Error", "Please enter a valid Hall name and Capacity!")

    def delete_item():
        selected_item = table.selection()
        if selected_item:
            for item in selected_item:
                code_salle = table.item(item)["values"][0]  # Retrieve `code_salle`
                delete_salle(code_salle)  # Call delete function

                table.delete(item)

        else:
            messagebox.showwarning("Warning", "Please select an item to delete.")


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

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

def on_save():
    institute_name = institute_entry.get().strip()
    exam_option = option_entry.get().strip()
    name_post = name_post_entry.get().strip()
    nbr_exams = nbr_exams_combobox.get().strip()

    # Check for empty fields
    if not institute_name or not exam_option or not name_post or not nbr_exams:
        messagebox.showerror("Error", "Please fill in all required fields.")
        return
    
    result = op_save_data(institute_name, exam_option, name_post, nbr_exams)

    if "✅" in result:
        messagebox.showinfo("Success", result)
        # Reset fields after successful save
        institute_entry.delete(0, tk.END)
        option_entry.delete(0, tk.END)
        name_post_entry.delete(0, tk.END)
        nbr_exams_combobox.current(0)
    else:
        messagebox.showerror("Error", result)

def show_delete_confirmation():
    """فتح نافذة التأكيد لحذف جميع البيانات."""
    confirm_window = tk.Toplevel(window)
    confirm_window.title("Confirm Deletion")
    confirm_window.geometry("300x130")

    label = tk.Label(confirm_window, text="Type 'YES' to confirm deletion:", font=("Arial", 12))
    label.pack(pady=5)

    entry = tk.Entry(confirm_window, font=("Arial", 12))
    entry.pack(pady=5)

    ok_button = tk.Button(confirm_window, text="OK", font=("Arial", 12), bg="#D10801", fg="white",
                          command=lambda: delete_all_data(confirm_window, entry))
    ok_button.pack(pady=6)
    ok_button.config(width=10)  # Adds width to the button

op_delete_btn = tk.Button(option_page, text="Delete", font=("Arial", 14), bg="#D10801", fg="white", bd=0, command=show_delete_confirmation)
op_delete_btn.place(relx=0.9, y=260, width=148, height=27, anchor="e")

# Add button
op_done_btn = tk.Button(option_page, text="Done", font=("Arial", 14), bg="#00B400", fg="white", bd=0, command=on_save)
op_done_btn.place(relx=0.9, y=300, width=148, height=27, anchor="e")


# Option page /////////////////////////////////////////////////////////////////////////////////////

# Students page /////////////////////////////////////////////////////////////////////////////////////
tk.Label(students_page, text="Students list", font=("Arial", 14), bg="white").place(x=22, y=27)

students_data = None
def import_excel():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
    if file_path:
        result = import_students_from_excel(file_path)
        messagebox.showinfo("Import Result", result)

st_import_btn = tk.Button(students_page, text="Import List", font=("Arial", 14), bg="#D9D9D9", fg="black", bd=0, command=import_excel)
st_import_btn.place(x=163, y=27, width=148, height=27)

separator = ttk.Separator(students_page, orient="horizontal")
separator.place(x=270, y=66, width=300, height=2)

tk.Label(students_page, text="Option", font=("Arial", 14), bg="white").place(x=22, y=82)


def update_combobox():
    """Update combobox values dynamically"""
    new_options = get_exam_options() 
    st_option_combo["values"] = new_options  


    if new_options:
        st_option_combo.current(0)

    students_page.after(5000, update_combobox) 

options = get_exam_options()
st_option_combo = ttk.Combobox(students_page, values=options, font=("Arial", 14), state="readonly")
st_option_combo.place(x=163, y=80, width=237, height=36)
st_option_combo.current(0)  

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

#//////////////////////////////////////////////////////
def update_salle_combobox():
    """Fetches updated salle names from the database and updates the combobox."""
    salles = get_salle_names()
    st_salle_combobox['values'] = salles
    if salles:
        st_salle_combobox.current(0)  # Set default selection
    students_page.after(5000, update_salle_combobox)


tk.Label(students_page, text="Salle", font=("Arial", 14), bg="white").place(x=414, y=82)
st_salle_combobox = ttk.Combobox(students_page, font=("Arial", 14), state="readonly")
st_salle_combobox.place(x=480, y=80, width=175, height=36)
st_salle_combobox['values'] = get_salle_names()

update_salle_combobox()

def save_student_data():
    name = name_entry.get().strip()
    surname = surname_entry.get().strip()
    dob = dob_entry.get_date().strftime("%Y-%m-%d") if dob_entry.get_date() else ""
    salle = st_salle_combobox.get().strip()
    exam_option = st_option_combo.get().strip()

    if not name or not surname or not dob or not salle or not exam_option:
        messagebox.showerror("Error", "Please fill in all required fields.")
        return

    result = save_student(name, surname, dob, salle, exam_option)

    if "Student data saved successfully!" in result:
        messagebox.showinfo("Success", result.replace("✅ ", "")) 

        name_entry.delete(0, tk.END)
        surname_entry.delete(0, tk.END)
        dob_entry.set_date(None)
        st_salle_combobox.current(0)
        st_option_combo.current(0)
    else:
        messagebox.showerror("Error", result)



# "Done" button linked to the save function
st_done_btn = tk.Button(students_page, text="Done", font=("Arial", 14), bg="#00B400", fg="white", bd=0, command=save_student_data)
st_done_btn.place(relx=0.9, y=300, width=148, height=27, anchor="e")
# Students page /////////////////////////////////////////////////////////////////////////////////////

# Professors page /////////////////////////////////////////////////////////////////////////////////////
def import_professors():
    file_path = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel Files", "*.xlsx *.xls")]
    )

    if not file_path:
        return

    try:
        df = pd.read_excel(file_path)

        required_columns = {"name", "surname", "email","module","correction"}
        if not required_columns.issubset(df.columns):
            messagebox.showerror("Error", "Invalid file format. Columns should be: name, surname, email, correction")
            return

        added_count = 0
        for _, row in df.iterrows():
            name = row["name"]
            surname = row["surname"]
            email = row["email"]
            module= row["module"]
            correction = row["correction"]

            result = add_professor(name, surname, email, module,correction)
            if "successfully" in result:
                added_count += 1

        messagebox.showinfo("Success", f"Successfully added {added_count} professors!")
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to import: {e}")


tk.Label(professors_page, text="Import Prof List", font=("Arial", 14), bg="white").place(x=28, y=15)
prof_imp_btn = tk.Button(professors_page, text="Import", font=("Arial", 12), bg="#D9D9D9", fg="black", bd=0,
    command=import_professors).place(x=190, y=15, width=148, height=27)

tk.Label(professors_page, text="OR", font=("Arial", 14, "bold"), bg="white").place(x=355, y=15)

def delete_selected_prof():
    selected_items = table_prof.selection()

    if not selected_items:
        messagebox.showerror("Error", "No professor selected!")
        return

    confirm = messagebox.askyesno("Confirmation", "Are you sure you want to delete the selected professor(s)?")
    if not confirm:
        return

    deleted_count = 0
    for item in selected_items:
        email = table_prof.item(item, "values")[1]  

        result = delete_professor(email)
        if "successfully" in result:
            deleted_count += 1
            table_prof.delete(item)  



delete_btn = tk.Button(professors_page, text="Delete", font=("Arial", 12), bg="#D10801", fg="white", bd=0, command=delete_selected_prof)
delete_btn.place(relx=0.7, y=305, width=148, height=27, anchor="e")


send_emails_btn = tk.Button(professors_page, text="Send Emails", font=("Arial", 12), bg="#00B400", fg="white", bd=0, command=send_emails )
send_emails_btn.place(relx=0.9, y=305, width=148, height=27, anchor="e")

def add_prof_window():
    add_prof_window = tk.Toplevel()
    add_prof_window.title("Add Professors")
    add_prof_window.geometry("800x340")
    add_prof_window.configure(bg="white")
    add_prof_window.resizable(False, False)

    # Labels
    tk.Label(add_prof_window, text="Name", bg="white", font=("Arial", 12)).place(x=50, y=45)
    tk.Label(add_prof_window, text="Email", bg="white", font=("Arial", 12)).place(x=428, y=45)
    tk.Label(add_prof_window, text="Surname", bg="white", font=("Arial", 12)).place(x=50, y=120)
    tk.Label(add_prof_window, text="Module", bg="white", font=("Arial", 12)).place(x=428, y=120)
    tk.Label(add_prof_window, text="Correction", bg="white", font=("Arial", 12)).place(x=50, y=195)
    
    # Entry Fields
    name_entry = tk.Entry(add_prof_window, font=("Arial", 12), bd=2, relief="groove")
    name_entry.place(x=135, y=36, width=235, height=36)

    email_entry = tk.Entry(add_prof_window, font=("Arial", 12), bd=2, relief="groove")
    email_entry.place(x=520, y=36, width=235, height=36)

    surname_entry = tk.Entry(add_prof_window, font=("Arial", 12), bd=2, relief="groove")
    surname_entry.place(x=135, y=111, width=235, height=36)
    
    corr_combobox = ttk.Combobox(add_prof_window, font=("Arial", 12), state="readonly")
    corr_combobox['values'] = ("1","2","3")
    corr_combobox.place(x=135, y=186, width=235, height=36)
     

    module_combobox = ttk.Combobox(add_prof_window, font=("Arial", 12), state="readonly")
    module_combobox.place(x=520, y=111, width=235, height=36)
    module_combobox['values'] = fetch_modules()

    # Button Functions
    def cancel():
        add_prof_window.destroy()

    def done():
        name = name_entry.get().strip()
        surname = surname_entry.get().strip()
        email = email_entry.get().strip()
        correction = corr_combobox.get().strip()
        module = module_combobox.get().strip()  # ✅ الحصول على قيمة module

        if not (name and surname and email and correction and module):  # ✅ التحقق من إدخال جميع القيم
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        
        result, password = add_professor(name, surname, email, correction, module)  # ✅ تمرير module

        if "successfully" in result:
            messagebox.showinfo("Success", f"{result}\nGenerated Password: {password}")
            add_prof_window.destroy()
        else:
            messagebox.showerror("Error", result)


    # Buttons
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
    rows = get_profs_from_db()

    table_prof.delete(*table_prof.get_children())

    for row in rows:
        table_prof.insert("", "end", values=row)

    window.after(10000, update_table)

update_table()
# Professors page /////////////////////////////////////////////////////////////////////////////////////

# Attendee page /////////////////////////////////////////////////////////////////////////////////////
tk.Label(attendee_page, text="Export attendee List", font=("Arial", 12, "bold"), bg="white").place(x=24, y=37)

tk.Label(attendee_page, text="Salle", font=("Arial", 12), bg="white").place(x=32, y=88)
at_salle_combobox = ttk.Combobox(attendee_page, state="readonly")
at_salle_combobox.place(x=88, y=80, width=175, height=36)
at_salle_combobox['values'] = get_salle_names()

def generate_excel():
    salle = at_salle_combobox.get().strip()

    if not salle:
        messagebox.showerror("Error", "Please select a salle.")
        return

    # Fetch candidates' data
    candidates = get_candidates_by_salle(salle)

    if not candidates:
        messagebox.showinfo("Info", "No candidates found for the selected salle.")
        return

    # Create a DataFrame
    df = pd.DataFrame(candidates, columns=["name", "surname", "salle"])
    df["audience"] = ""  # Add empty column

    # Ask user where to save the file
    file_path = asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])

    if not file_path:
        return  # User canceled save dialog

    # Save to Excel
    try:
        df.to_excel(file_path, index=False, engine="openpyxl")
        messagebox.showinfo("Success", f"Excel file saved successfully:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save Excel file:\n{e}")

print_btn = tk.Button(attendee_page, text="Print", font=("Arial", 12), bg="#D9D9D9", fg="black", bd=0,command=generate_excel)
print_btn.place(x=294, y=84, width=148, height=27)


def generate_qr_codes():
    candidates = get_all_candidates()

    if not candidates:
        messagebox.showinfo("Info", "No candidates found in the database.")
        return

    # Let the user choose the folder to save QR codes
    qr_folder = filedialog.askdirectory(title="Select Folder to Save QR Codes")

    # If the user cancels, return
    if not qr_folder:
        return

    qr_count = 0  # Counter for QR codes generated

    for name, surname, anonymous_id in candidates:
        if not anonymous_id:
            continue  # Skip if anonymous_id is empty

        try:
            # Generate QR code
            qr = qrcode.make(anonymous_id)

            # Define file path (e.g., selected_folder/John_Doe.png)
            filename = f"{name}_{surname}.png".replace(" ", "_")  # Remove spaces
            file_path = os.path.join(qr_folder, filename)

            # Save the QR code image
            qr.save(file_path)
            qr_count += 1  # Increment counter

        except Exception as e:
            messagebox.showerror("QR Code Error", f"Failed to generate QR for {name} {surname}: {e}")

    # Show success message if at least one QR was created
    if qr_count > 0:
        messagebox.showinfo("Success", f"{qr_count} QR codes saved successfully in '{qr_folder}'.")
    else:
        messagebox.showwarning("Warning", "No QR codes were generated.")

# Create "QR Code" Button
qr_code_btn = tk.Button(attendee_page, text="QR Code", font=("Arial", 12), bg="#D9D9D9", fg="black", bd=0, command=generate_qr_codes)
qr_code_btn.place(x=452, y=84, width=148, height=27)

separator = tk.Frame(attendee_page, bg="#D9D9D9", height=2)
separator.place(x=216, y=160, relwidth=0.45)  # Using relwidth for responsiveness

tk.Label(attendee_page, text="Import absences List", font=("Arial", 14), bg="white").place(x=24, y=209)
import_btn = tk.Button(attendee_page, text="Import", font=("Arial", 12), bg="#D9D9D9", bd=0,command=import_absences)
import_btn.place(x=294, y=209, width=162, height=26)

# Attendee page /////////////////////////////////////////////////////////////////////////////////////

# Results page /////////////////////////////////////////////////////////////////////////////////////
tk.Label(results_page, text="Results List ", font=("Arial", 14,"bold"), bg="white").place(x=32, y=15)
tk.Label(results_page, text="Salle", font=("Arial", 12), bg="white").place(x=32, y=59)
r_salle_combobox = ttk.Combobox(results_page, state="readonly")
r_salle_combobox.place(x=139, y=51, width=237, height=36)
r_salle_combobox['values'] = get_salle_names()

tk.Label(results_page, text="Language", font=("Arial", 12), bg="white").place(x=32, y=110)
language_combobox = ttk.Combobox(results_page, state="readonly")
language_combobox['values'] = ("English", "Arabic")  # Add language options here
language_combobox.place(x=139, y=102, width=175, height=36)

tk.Label(results_page, text="Name of posts", font=("Arial", 12), bg="white").place(x=32, y=161)
tk.Label(results_page, text="Number of exams", font=("Arial", 12), bg="white").place(x=32, y=208)

name_post, nbr_exams = institute_data()
tk.Label(results_page, text=name_post, font=("Arial", 12), bg="white").place(x=170, y=161)
tk.Label(results_page, text=nbr_exams, font=("Arial", 12), bg="white").place(x=170, y=208)

rs_done_btn = tk.Button(
     results_page, 
     text="Result", 
     font=("Arial", 14), 
     bg="#00B400", 
     fg="white", 
     bd=0,
     command=lambda: calculate_and_export_results(r_salle_combobox.get(), language_combobox.get())
)
rs_done_btn.place(relx=0.9, y=300, width=148, height=27, anchor="e")

# Results page /////////////////////////////////////////////////////////////////////////////////////

update_salle_comboboxes(st_salle_combobox, at_salle_combobox, r_salle_combobox, window)

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
    logo = logo.resize((80, 80), Image.LANCZOS)  # Resizing for consistency
    photo = ImageTk.PhotoImage(logo)
    labellogo = tk.Label(window, image=photo, bg="#FFFFFF")
    labellogo.image = photo
    labellogo.place(relx=1.0, y=8, anchor="ne")  # Responsive positioning
except FileNotFoundError:
    print("Logo.png not found.")
    
# Run the application
window.mainloop()