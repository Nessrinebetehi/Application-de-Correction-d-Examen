import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkcalendar import DateEntry
# Create the main window
window = tk.Tk()
window.title("Admin window")

# Set window size and configuration
window_width = 800
window_height = 500
window.resizable(False, False)
window.configure(bg="#FFFFFF")

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
menu_frame = tk.Frame(window, bg="#5A7EC7", height=40)
menu_frame.pack(fill=tk.X, side=tk.TOP)

# Define button names
menu_buttons = ["Option","Students list", "Professors list", "Attendee list", "Absences list", "Results"]
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
option_page = tk.Frame(window, bg="white", width=800, height=460)
students_page = tk.Frame(window, bg="white", width=800, height=460)
professors_page = tk.Frame(window, bg="white", width=800, height=460)
absences_page = tk.Frame(window, bg="white", width=800, height=460)
attendee_page = tk.Frame(window, bg="white", width=800, height=460)
results_page = tk.Frame(window, bg="white", width=800, height=460)

#option page /////////////////////////////////////////////////////////////////////////////////////
tk.Label(option_page, text="Institue", font=("Arial", 14), bg="white").place(x=24, y=15)
institue_entry = tk.Entry(option_page, font=("Arial", 14), bd=2, relief="groove", bg="#FFFFFF", fg="#333333")
institue_entry.place(x=190, y=14, width=330, height=36)

tk.Label(option_page, text="Option", font=("Arial", 14), bg="white").place(x=24, y=61)
option_entry = tk.Entry(option_page, font=("Arial", 12), bd=2, relief="groove", bg="#FFFFFF", fg="#333333")
option_entry.place(x=190, y=60, width=330, height=36)

tk.Label(option_page, text="Name of posts", font=("Arial", 14), bg="white").place(x=24, y=110)
salle_options = ["Salle 1", "Salle 2", "Salle 3"]
salle_combobox = ttk.Combobox(option_page, values=salle_options, font=("Arial", 14), state="readonly")
salle_combobox.place(x=190, y=110, width=120, height=36)
salle_combobox.current(0)


tk.Label(option_page, text="Number of exams", font=("Arial", 14), bg="white").place(x=24, y=160)
salle_options = ["Salle 1", "Salle 2", "Salle 3"]
salle_combobox = ttk.Combobox(option_page, values=salle_options, font=("Arial", 14), state="readonly")
salle_combobox.place(x=190, y=160, width=120, height=36)
salle_combobox.current(0)

def add_exams_window():
    add_exam_window = tk.Toplevel(window)
    add_exam_window.title("Add Exam")
    add_exam_window.geometry("730x320")  
    add_exam_window.configure(bg="white")
    
tk.Label(option_page, text="Add exams", font=("Arial", 14), bg="white").place(x=24, y=227)
add_exams_btn=tk.Button(option_page,text="Add",font=("Arial", 16 ), bg="#5D8BCD",fg="white",bd=0,command=add_exams_window)
add_exams_btn.place(x=190, y=230, width=148, height=27)

def add_salles_window():
    add_exam_window = tk.Toplevel(window)
    add_exam_window.title("Add Exam")
    add_exam_window.geometry("730x320")  
    add_exam_window.configure(bg="white")


tk.Label(option_page, text="Add salles", font=("Arial", 14), bg="white").place(x=24, y=275)
add_salles_btn=tk.Button(option_page,text="Add",font=("Arial", 16 ), bg="#5D8BCD",fg="white",bd=0,command=add_salles_window)
add_salles_btn.place(x=190, y=275, width=148, height=27)

op_done_btn=tk.Button(option_page,text="Done",font=("Arial", 14 ), bg="#00B400",fg="white",bd=0)
op_done_btn.place(x=630, y=300, width=148, height=27)

#option page /////////////////////////////////////////////////////////////////////////////////////

#students page /////////////////////////////////////////////////////////////////////////////////////
tk.Label(students_page, text="Option", font=("Arial", 14), bg="white").place(x=22, y=15)
option_entry = tk.Entry(students_page, font=("Arial", 14), bd=2, relief="groove", bg="#FFFFFF", fg="#333333")
option_entry.place(x=163, y=14, width=237, height=36)

# Name
tk.Label(students_page, text="Name", font=("Arial", 14), bg="white").place(x=22, y=65)
name_entry = tk.Entry(students_page, font=("Arial", 14), bd=2, relief="groove", bg="#FFFFFF", fg="#333333")
name_entry.place(x=163, y=64, width=237, height=36)

# Surname
tk.Label(students_page, text="Surname", font=("Arial", 14), bg="white").place(x=22, y=115)
surname_entry = tk.Entry(students_page, font=("Arial", 14), bd=2, relief="groove", bg="#FFFFFF", fg="#333333")
surname_entry.place(x=163, y=114, width=237, height=36)

# Date of Birth
tk.Label(students_page, text="Date of Birth", font=("Arial", 14), bg="white").place(x=22, y=165)
dob_entry = DateEntry(students_page, font=("Arial", 14), bg="white", fg="black", 
                      date_pattern="yyyy-mm-dd", width=18)
dob_entry.place(x=163, y=164, width=237, height=36)

tk.Label(students_page, text="Sex", font=("Arial", 14), bg="white").place(x=414, y=15)
sex_combobox = ttk.Combobox(students_page, font=("Arial", 14), state="readonly")
sex_combobox['values'] = ("Male", "Female")
sex_combobox.place(x=480, y=14, width=175, height=36)

tk.Label(students_page, text="Salle", font=("Arial", 14), bg="white").place(x=414, y=65)
salle_combobox = ttk.Combobox(students_page, font=("Arial", 14), state="readonly")
salle_combobox['values'] = ("A", "B", "C", "D")
salle_combobox.place(x=480, y=64, width=175, height=36)

st_done_btn=tk.Button(students_page,text="Done",font=("Arial", 14 ), bg="#00B400",fg="white",bd=0)
st_done_btn.place(x=630, y=300, width=148, height=27)
#students page /////////////////////////////////////////////////////////////////////////////////////

#profs page /////////////////////////////////////////////////////////////////////////////////////
tk.Label(professors_page, text="Select Prof", font=("Arial", 14), bg="white").place(x=22, y=36)
sex_combobox = ttk.Combobox(professors_page, font=("Arial", 14), state="readonly")
sex_combobox['values'] = ("Male", "Female")
sex_combobox.place(x=163, y=34, width=231, height=36)
prof_print_btn=tk.Button(professors_page,text="Print",font=("Arial", 12 ), bg="#D9D9D9",fg="black",bd=0)
prof_print_btn.place(x=437, y=36, width=148, height=27)

tk.Label(professors_page, text="All Prof list", font=("Arial", 14), bg="white").place(x=22, y=110)
all_print_btn=tk.Button(professors_page,text="Print",font=("Arial", 12 ), bg="#D9D9D9",fg="black",bd=0)
all_print_btn.place(x=163, y=110, width=148, height=27)


delete_pr_btn=tk.Button(professors_page,text="Delete",font=("Arial", 12 ), bg="#D10801",fg="white",bd=0)
delete_pr_btn.place(x=460, y=300, width=148, height=27)

add_pr_btn=tk.Button(professors_page,text="Add Prof",font=("Arial", 12 ), bg="#00B400",fg="white",bd=0)
add_pr_btn.place(x=630, y=300, width=148, height=27)
#profs page /////////////////////////////////////////////////////////////////////////////////////

#attendee page /////////////////////////////////////////////////////////////////////////////////////

tk.Label(attendee_page, text="Export List", font=("Arial", 12, "bold"), bg="white").place(x=32, y=44)
# قائمة "Salle"
tk.Label(attendee_page, text="Salle", font=("Arial", 12), bg="white").place(x=32, y=88)
salle_combobox = ttk.Combobox(attendee_page, state="readonly")
salle_combobox.place(x=139, y=80, width=175, height=36)

# قائمة "Language"
tk.Label(attendee_page, text="language", font=("Arial", 12), bg="white").place(x=32, y=145)
language_combobox = ttk.Combobox(attendee_page, state="readonly")
language_combobox.place(x=139, y=136, width=174, height=36)

# زر "QR list"
qr_list_btn = tk.Button(attendee_page, text="QR list", font=("Arial", 12), bg="#D9D9D9", fg="black", bd=0)
qr_list_btn.place(x=630, y=250, width=148, height=36)

# زر "Print"
print_btn = tk.Button(attendee_page, text="Print", font=("Arial", 12), bg="#D9D9D9", fg="black", bd=0)
print_btn.place(x=630, y=290, width=148, height=36)

#attendee page /////////////////////////////////////////////////////////////////////////////////////

#absence page /////////////////////////////////////////////////////////////////////////////////////
tk.Label(absences_page, text="Import List", font=("Arial", 12, "bold"), bg="white").place(x=32, y=32)
abs_print_btn=tk.Button(absences_page,text="Print",font=("Arial", 12 ), bg="#D9D9D9",fg="black",bd=0)
abs_print_btn.place(x=166, y=33, width=148, height=27)

separator = tk.Frame(absences_page, bg="#D9D9D9", height=2, width=360)  # خط فاصل بلون رمادي
separator.place(x=216, y=96)  # تحديد الموقع تحت زر Import مباشرة

tk.Label(absences_page, text="Export List", font=("Arial", 12, "bold"), bg="white").place(x=32, y=100)
# قائمة "Salle"
tk.Label(absences_page, text="Salle", font=("Arial", 12), bg="white").place(x=32, y=157)
salle_combobox = ttk.Combobox(absences_page, state="readonly")
salle_combobox.place(x=139, y=149, width=175, height=36)

# قائمة "Language"
tk.Label(absences_page, text="language", font=("Arial", 12), bg="white").place(x=32, y=214)
language_combobox = ttk.Combobox(absences_page, state="readonly")
language_combobox.place(x=139, y=207, width=174, height=36)

abs_print_btn2=tk.Button(absences_page,text="Print",font=("Arial", 14 ), bg="#D9D9D9",fg="black",bd=0)
abs_print_btn2.place(x=630, y=300, width=148, height=27)
# absence page/////////////////////////////////////////////////////////////////////////////////////

#result page /////////////////////////////////////////////////////////////////////////////////////
tk.Label(results_page, text="Salle", font=("Arial", 12), bg="white").place(x=32, y=59)
salle_combobox = ttk.Combobox(results_page, state="readonly")
salle_combobox.place(x=139, y=51, width=237, height=36)

# قائمة "Language"
tk.Label(results_page, text="language", font=("Arial", 12), bg="white").place(x=32, y=110)
language_combobox = ttk.Combobox(results_page, state="readonly")
language_combobox.place(x=139, y=102, width=175, height=36)

tk.Label(results_page, text="Name of posts", font=("Arial", 12), bg="white").place(x=32, y=161)

tk.Label(results_page, text="Number of exams", font=("Arial", 12), bg="white").place(x=32, y=208)

rs_done_btn=tk.Button(results_page,text="Done",font=("Arial", 14 ), bg="#00B400",fg="white",bd=0)
rs_done_btn.place(x=630, y=300, width=148, height=27)

#result page /////////////////////////////////////////////////////////////////////////////////////


# Store pages in the dictionary
pages["Option"] = option_page
pages["Students list"] = students_page
pages["Professors list"] = professors_page
pages["Absences list"] = absences_page
pages["Attendee list"] = attendee_page
pages["Results"] = results_page

# Show the default page (e.g., "Students list")
show_page("Option")

# Load and display the university logo
try:
    logo = Image.open("Logo.png")
    photo = ImageTk.PhotoImage(logo)
    labellogo = tk.Label(window, image=photo, bg="#FFFFFF")
    labellogo.image = photo  # This is necessary to keep the image from being garbage collected
    labellogo.place(x=702, y=8)
except FileNotFoundError:
    print("Logo.png not found.")

# Run the application
window.mainloop()
