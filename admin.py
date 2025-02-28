#admin.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkcalendar import DateEntry
from tkinter import messagebox
from db_connector import op_save_data,insert_exam,get_exams,delete_exam
from db_connector import add_salle,get_all_salles,delete_salle,generate_code_salle
from db_connector import get_db_connection
import mysql.connector


# Create the main window
window = tk.Tk()
window.title("Admin window")

# Set window size and configuration
window_width = 800
window_height = 500
window.resizable(True, True)  # Changed to True, True to make window resizable
window.configure(bg="#FFFFFF")
window.geometry(f"{window_width}x{window_height}")

# Center the window on the screen
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x_position = int((screen_width - window_width) / 2)
y_position = int((screen_height - window_height) / 2)
window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Add a header label
header_label = tk.Label(window, text="Management of Post-Graduation\nCompetitions", 
                        font=("Arial", 24, "bold"), fg="#5A7EC7", bg="#FFFFFF", justify="left")
header_label.pack(pady=15, anchor="w", padx=20)

# Create the menu frame
menu_frame = tk.Frame(window, bg="#5A7EC7")
menu_frame.pack(fill=tk.X, side=tk.TOP)

# Define button names
menu_buttons = ["Option", "Students list", "Professors list", "Attendee list", "Results"]
button_width = 15

# Create a dictionary to store pages
pages = {}

# Define function to switch between pages
def show_page(page_name):
    for page in pages.values():
        page.pack_forget()
    pages[page_name].pack(fill=tk.BOTH, expand=True)

# Function for hover effect
def on_enter(button):
    button.config(bg="#4A66B0", fg="#FFFFFF")  # Darken background on hover

def on_leave(button):
    button.config(bg="#5A7EC7", fg="#FFFFFF")  # Revert back when mouse leaves

# Create buttons with hover effects and link them to pages
for idx, text in enumerate(menu_buttons):
    btn = tk.Button(menu_frame, text=text, font=("Arial", 10, "bold"), fg="#FFFFFF", bg="#5A7EC7", 
                    relief=tk.FLAT, width=button_width, command=lambda page=text: show_page(page))
    
    # Add hover effect with event bindings
    btn.bind("<Enter>", lambda event, b=btn: on_enter(b))
    btn.bind("<Leave>", lambda event, b=btn: on_leave(b))

    btn.pack(side=tk.LEFT, padx=5, pady=5)

# Create frames (pages) for different sections
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
        """تحميل الامتحانات من قاعدة البيانات وعرضها في الجدول"""
        for row in table.get_children():
            table.delete(row)

        exams = get_exams()
        for exam in exams:
            table.insert("", "end", values=exam)

    def add_item():
        """إضافة امتحان جديد إلى قاعدة البيانات وعرضه في الجدول"""
        if len(table.get_children()) < num_exams:
            module = module_entry.get().strip()
            coeff = coeff_entry.get().strip()

            if module and coeff.replace('.', '', 1).isdigit():
                candidat_id = 1  # يجب تعيين هذا الرقم بناءً على البيانات الفعلية

                result = insert_exam(candidat_id, module, float(coeff))

                if result is True:
                    load_exams()  # تحديث الجدول بعد الإدخال
                    module_entry.delete(0, tk.END)
                    coeff_entry.delete(0, tk.END)
                    messagebox.showinfo("Success", "Exam added successfully!")
                else:
                    messagebox.showerror("Database Error", f"Error: {result}")
            else:
                messagebox.showerror("Error", "Please enter a valid Module and Coefficient!")
        else:
            messagebox.showwarning("Warning", f"You can only add {num_exams} exams!")

    def delete_item():
        """حذف الامتحان المحدد من قاعدة البيانات"""
        selected_item = table.selection()
        if selected_item:
            for item in selected_item:
                exam_id = table.item(item)["values"][0]  # جلب ID الامتحان
                result = delete_exam(exam_id)

                if result is True:
                    table.delete(item)
                    messagebox.showinfo("Success", "Exam deleted successfully!")
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

    load_exams()  # تحميل الامتحانات عند فتح النافذة


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
        """تحميل القاعات من قاعدة البيانات وعرضها في الجدول"""
        for row in table.get_children():
            table.delete(row)

        salles = get_all_salles()  # جلب جميع القاعات من قاعدة البيانات
        for salle in salles:
            table.insert("", "end", values=salle)

    def add_item():
        """إضافة قاعة جديدة وحفظها في قاعدة البيانات"""
        salle = salle_entry.get().strip()
        capacity = capacity_entry.get().strip()

        if salle and capacity.isdigit():
            try:
                code_salle = add_salle(salle, int(capacity))  # استدعاء الدالة من database.py
                table.insert("", "end", values=(code_salle, salle, capacity))

                salle_entry.delete(0, tk.END)
                capacity_entry.delete(0, tk.END)

                messagebox.showinfo("Success", "Salle added successfully!")
            except Exception as e:
                messagebox.showerror("Database Error", f"Error: {e}")

        else:
            messagebox.showerror("Error", "Please enter a valid Salle name and Capacity!")

    def delete_item():
        """حذف القاعة من الجدول ومن قاعدة البيانات"""
        selected_item = table.selection()
        if selected_item:
            for item in selected_item:
                code_salle = table.item(item)["values"][0]  # جلب `code_salle`
                delete_salle(code_salle)  # استدعاء دالة الحذف

                table.delete(item)
                messagebox.showinfo("Success", "Salle deleted successfully!")

        else:
            messagebox.showwarning("Warning", "Please select an item to delete.")

    add_button = tk.Button(add_salle_window, text="Add", bg="#00B400", fg="white", command=add_item, width=8, bd=0)
    add_button.place(x=590, y=39, width=91, height=27)

    delete_button = tk.Button(add_salle_window, text="Delete", bg="#D10801", fg="white", command=delete_item, width=10, bd=0)
    delete_button.place(x=411, y=280, width=147, height=27)

    done_button = tk.Button(add_salle_window, text="Done", bg="#00B400", fg="white", command=add_salle_window.destroy, width=10, bd=0)
    done_button.place(x=570, y=280, width=147, height=27)

    load_salles()  # تحميل القاعات عند فتح النافذة

tk.Label(option_page, text="Add salles", font=("Arial", 14), bg="white").place(x=24, y=275)
add_salles_btn = tk.Button(option_page, text="Add", font=("Arial", 16), bg="#5D8BCD", fg="white", bd=0, command=add_salles_window)
add_salles_btn.place(x=190, y=275, width=148, height=27)

def on_save():
    institute_name = institute_entry.get()
    exam_option = option_entry.get()
    name_post = name_post_entry.get()
    nbr_exams = nbr_exams_combobox.get()

    result = op_save_data(institute_name, exam_option, name_post, nbr_exams)

    if "✅" in result:
        messagebox.showinfo("نجاح", result)
        institute_entry.delete(0, tk.END)
        option_entry.delete(0, tk.END)
        name_post_entry.delete(0, tk.END)
        nbr_exams_combobox.current(0)
    else:
        messagebox.showerror("خطأ", result)

# زر الإضافة
op_done_btn = tk.Button(option_page, text="Done", font=("Arial", 14), bg="#00B400", fg="white", bd=0, command=on_save)
op_done_btn.place(relx=0.9, y=300, width=148, height=27, anchor="e")

# Option page /////////////////////////////////////////////////////////////////////////////////////

# Students page /////////////////////////////////////////////////////////////////////////////////////
tk.Label(students_page, text="Students list", font=("Arial", 14), bg="white").place(x=22, y=27)
st_import_btn = tk.Button(students_page, text="Import List", font=("Arial", 14), bg="#D9D9D9", fg="black", bd=0)
st_import_btn.place(x=163, y=27, width=148, height=27)

separator = ttk.Separator(students_page, orient="horizontal")
separator.place(x=270, y=66, width=300, height=2)

tk.Label(students_page, text="Option", font=("Arial", 14), bg="white").place(x=22, y=82)
st_option_entry = tk.Entry(students_page, font=("Arial", 14), bd=2, relief="groove", bg="#FFFFFF", fg="#333333")
st_option_entry.place(x=163, y=80, width=237, height=36)

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

tk.Label(students_page, text="Sex", font=("Arial", 14), bg="white").place(x=414, y=82)
sex_combobox = ttk.Combobox(students_page, font=("Arial", 14), state="readonly")
sex_combobox['values'] = ("Male", "Female")
sex_combobox.place(x=480, y=80, width=175, height=36)

tk.Label(students_page, text="Salle", font=("Arial", 14), bg="white").place(x=414, y=127)
salle_combobox = ttk.Combobox(students_page, font=("Arial", 14), state="readonly")
salle_combobox['values'] = ("A", "B", "C", "D")
salle_combobox.place(x=480, y=125, width=175, height=36)

st_done_btn = tk.Button(students_page, text="Done", font=("Arial", 14), bg="#00B400", fg="white", bd=0)
st_done_btn.place(relx=0.9, y=300, width=148, height=27, anchor="e")
# Students page /////////////////////////////////////////////////////////////////////////////////////

# Professors page /////////////////////////////////////////////////////////////////////////////////////
tk.Label(professors_page, text="Import Prof List", font=("Arial", 14), bg="white").place(x=28, y=15)
prof_imp_btn = tk.Button(professors_page, text="Import", font=("Arial", 12), bg="#D9D9D9", fg="black", bd=0)
prof_imp_btn.place(x=190, y=15, width=148, height=27)

tk.Label(professors_page, text="OR", font=("Arial", 14, "bold"), bg="white").place(x=355, y=15)

delete_btn = tk.Button(professors_page, text="Delete", font=("Arial", 12), bg="#D10801", fg="white", bd=0)
delete_btn.place(relx=0.7, y=305, width=148, height=27, anchor="e")

send_emails = tk.Button(professors_page, text="Send Emails", font=("Arial", 12), bg="#00B400", fg="white", bd=0)
send_emails.place(relx=0.9, y=305, width=148, height=27, anchor="e")

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

    # Entry Fields
    name_entry = tk.Entry(add_prof_window, font=("Arial", 12), bd=2, relief="groove")
    name_entry.place(x=135, y=36, width=235, height=36)

    email_entry = tk.Entry(add_prof_window, font=("Arial", 12), bd=2, relief="groove")
    email_entry.place(x=520, y=36, width=235, height=36)

    surname_entry = tk.Entry(add_prof_window, font=("Arial", 12), bd=2, relief="groove")
    surname_entry.place(x=135, y=111, width=235, height=36)

    module_combobox = ttk.Combobox(add_prof_window, font=("Arial", 12), state="readonly")
    module_combobox['values'] = ("Mathematics", "Physics", "Computer Science", "Biology")
    module_combobox.place(x=520, y=111, width=235, height=36)

    # Button Functions
    def cancel():
        add_prof_window.destroy()

    def done():
        name = name_entry.get().strip()
        surname = surname_entry.get().strip()
        email = email_entry.get().strip()
        module = module_combobox.get().strip()

        if name and surname and email and module:
            messagebox.showinfo("Success", "Professor added successfully!")
            add_prof_window.destroy()
        else:
            messagebox.showerror("Error", "Please fill in all fields.")

    # Buttons
    cancel_button = tk.Button(add_prof_window, text="Cancel", bg="#D10801", fg="white", font=("Arial", 12), bd=0, command=cancel)
    cancel_button.place(x=472, y=299, width=148, height=27)

    done_button = tk.Button(add_prof_window, text="Done", bg="#00B400", fg="white", font=("Arial", 12), bd=0, command=done)
    done_button.place(x=634, y=299, width=148, height=27)
    
add_pr_btn = tk.Button(professors_page, text="Add Prof", font=("Arial", 12), bg="#D9D9D9", fg="black", bd=0, command=add_prof_window)
add_pr_btn.place(x=406, y=15, width=148, height=27)

columns_prof = ("name", "Email", "Password")
table_prof = ttk.Treeview(professors_page, columns=columns_prof, show="headings", height=8)
table_prof.place(x=25, y=55, relwidth=0.95, height=228)  # Using relwidth for responsiveness
# Professors page /////////////////////////////////////////////////////////////////////////////////////

# Attendee page /////////////////////////////////////////////////////////////////////////////////////
tk.Label(attendee_page, text="Export attendee List", font=("Arial", 12, "bold"), bg="white").place(x=24, y=37)

tk.Label(attendee_page, text="Salle", font=("Arial", 12), bg="white").place(x=32, y=88)
salle_combobox = ttk.Combobox(attendee_page, state="readonly")
salle_combobox.place(x=88, y=80, width=175, height=36)

print_btn = tk.Button(attendee_page, text="Print", font=("Arial", 12), bg="#D9D9D9", fg="black", bd=0)
print_btn.place(x=294, y=84, width=148, height=27)

qr_code_btn = tk.Button(attendee_page, text="QR Code", font=("Arial", 12), bg="#D9D9D9", fg="black", bd=0)
qr_code_btn.place(x=452, y=84, width=148, height=27)

separator = tk.Frame(attendee_page, bg="#D9D9D9", height=2)
separator.place(x=216, y=160, relwidth=0.45)  # Using relwidth for responsiveness

tk.Label(attendee_page, text="Import absences List", font=("Arial", 14), bg="white").place(x=24, y=209)
import_btn = tk.Button(attendee_page, text="Import", font=("Arial", 12), bg="#D9D9D9", bd=0)
import_btn.place(x=294, y=209, width=162, height=26)

# Attendee page /////////////////////////////////////////////////////////////////////////////////////

# Results page /////////////////////////////////////////////////////////////////////////////////////
tk.Label(results_page, text="Results List ", font=("Arial", 14,"bold"), bg="white").place(x=32, y=15)
tk.Label(results_page, text="Salle", font=("Arial", 12), bg="white").place(x=32, y=59)
salle_combobox = ttk.Combobox(results_page, state="readonly")
salle_combobox.place(x=139, y=51, width=237, height=36)

tk.Label(results_page, text="Language", font=("Arial", 12), bg="white").place(x=32, y=110)
language_combobox = ttk.Combobox(results_page, state="readonly")
language_combobox.place(x=139, y=102, width=175, height=36)

tk.Label(results_page, text="Name of posts", font=("Arial", 12), bg="white").place(x=32, y=161)
tk.Label(results_page, text="Number of exams", font=("Arial", 12), bg="white").place(x=32, y=208)

rs_done_btn = tk.Button(results_page, text="Done", font=("Arial", 14), bg="#00B400", fg="white", bd=0)
rs_done_btn.place(relx=0.9, y=300, width=148, height=27, anchor="e")

# Results page /////////////////////////////////////////////////////////////////////////////////////

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