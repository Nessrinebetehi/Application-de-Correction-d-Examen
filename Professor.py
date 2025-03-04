#professor.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from db_connector import get_exam_options,fetch_exam_modules,fetch_exam_details

# إنشاء النافذة الرئيسية
window = tk.Tk()
window.title("Professor Window")

# ضبط حجم النافذة الأولي وجعلها قابلة للتغيير
window_width = 800
window_height = 500
window.resizable(True, True)  # Changed to True, True to make window resizable
window.configure(bg="#FFFFFF")
window.geometry(f"{window_width}x{window_height}")

# توسيط النافذة على الشاشة
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x_position = int((screen_width - window_width) / 2)
y_position = int((screen_height - window_height) / 2)
window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# إضافة عنوان
header_label = tk.Label(window, text="Management of Post-Graduation\nCompetitions", 
                       font=("Arial", 24, "bold"), fg="#5A7EC7", bg="#FFFFFF", justify="left")
header_label.pack(pady=15, anchor="w", padx=20)

# إنشاء إطار القائمة
menu_frame = tk.Frame(window, bg="#5A7EC7")
menu_frame.pack(fill=tk.X, side=tk.TOP)

# عنوان القائمة
menu_buttons = ["Corrections", "About"]
button_width = 15

pages = {}

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
    
Corrections_page = tk.Frame(window, bg="white")
About_page = tk.Frame(window, bg="white")

# Correction Page ////////////////////////////////////////////////////////////////////////////////
tk.Label(Corrections_page, text="Option", font=("Arial", 14), bg="white").place(x=24, y=30)
def update_combobox():
    """Update combobox values dynamically"""
    new_options = get_exam_options()  # استرجاع القيم الجديدة من قاعدة البيانات
    cr_option["values"] = new_options  # تحديث القيم في Combobox

    # إذا كانت القائمة تحتوي على عناصر، اضبط العنصر الافتراضي على الأول
    if new_options:
        cr_option.current(0)

    Corrections_page.after(5000, update_combobox)  # جدولة التحديث بعد 5 ثوانٍ

options = get_exam_options()
cr_option= ttk.Combobox(Corrections_page, values=options,state="readonly")
cr_option.place(x=135, y=26, width=237, height=36)
update_combobox()

tk.Label(Corrections_page, text="Anonymat", font=("Arial", 14), bg="white").place(x=24, y=90)
cr_anonyme_entry = tk.Entry(Corrections_page, font=("Arial", 14), bd=2, relief="groove", bg="#FFFFFF", fg="#333333")
cr_anonyme_entry.place(x=135, y=84, width=114, height=36)

def update_entry_state(event):
    """Enable only the selected correction entry and disable the others."""
    selected_correction = cr_number.get()
    
    # Disable all entries first
    cr_1_entry.config(state="disabled")
    cr_2_entry.config(state="disabled")
    cr_3_entry.config(state="disabled")
    
    # Enable the selected correction entry
    if selected_correction == "1":
        cr_1_entry.config(state="normal")
    elif selected_correction == "2":
        cr_2_entry.config(state="normal")
    elif selected_correction == "3":
        cr_3_entry.config(state="normal")

# Labels and UI elements
tk.Label(Corrections_page, text="Corrections", font=("Arial", 14), bg="white").place(x=430, y=90)
cr_number = ttk.Combobox(Corrections_page, state="readonly")
cr_number["values"] = [1, 2, 3]  # Adding values to the combobox
cr_number.place(x=540, y=84, width=95, height=36)
cr_number.bind("<<ComboboxSelected>>", update_entry_state)  # Bind event

# Separator line
separator = tk.Frame(Corrections_page, bg="#D9D9D9", height=2)
separator.place(x=100, y=155, width=560)

tk.Label(Corrections_page, text="Exam :", font=("Arial", 14, "bold"), bg="white").place(x=24, y=140)

def update_exam_details(event):
    selected_exam = cr_exam.get()
    subject, coeff = fetch_exam_details(selected_exam)
    
    subject_label.config(text=subject)  # Update subject label
    coeff_label.config(text=str(coeff))  # Update coefficient label

# Label and Combobox for Exam Selection
tk.Label(Corrections_page, text="Exam", font=("Arial", 14), bg="white").place(x=264, y=90)
cr_exam = ttk.Combobox(Corrections_page, state="readonly")
cr_exam.place(x=325, y=84, width=95, height=36)

# Populate Combobox
exam_modules = fetch_exam_modules()
cr_exam["values"] = exam_modules  
cr_exam.bind("<<ComboboxSelected>>", update_exam_details)  # Bind event to update labels

# Labels for Subject and Coefficient
tk.Label(Corrections_page, text="Subject :", font=("Arial", 14), bg="white").place(x=24, y=180)
subject_label = tk.Label(Corrections_page, text="", font=("Arial", 14), bg="white")
subject_label.place(x=140, y=180)

tk.Label(Corrections_page, text="Coeffs :", font=("Arial", 14), bg="white").place(x=370, y=180)
coeff_label = tk.Label(Corrections_page, text="", font=("Arial", 14), bg="white")
coeff_label.place(x=490, y=180)


tk.Label(Corrections_page, text="Correction 1", font=("Arial", 14), bg="white").place(x=24, y=230)
cr_1_entry = tk.Entry(Corrections_page, font=("Arial", 14), bd=2, relief="groove", bg="#FFFFFF", fg="#333333", state="disabled")
cr_1_entry.place(x=140, y=225, width=114, height=36)

tk.Label(Corrections_page, text="Correction 2", font=("Arial", 14), bg="white").place(x=24, y=275)
cr_2_entry = tk.Entry(Corrections_page, font=("Arial", 14), bd=2, relief="groove", bg="#FFFFFF", fg="#333333", state="disabled")
cr_2_entry.place(x=140, y=270, width=114, height=36)

tk.Label(Corrections_page, text="Correction 3", font=("Arial", 14), bg="white").place(x=370, y=230)
cr_3_entry = tk.Entry(Corrections_page, font=("Arial", 14), bd=2, relief="groove", bg="#FFFFFF", fg="#333333", state="disabled")
cr_3_entry.place(x=490, y=225, width=114, height=36)

tk.Label(Corrections_page, text="Finale grade", font=("Arial", 14), bg="white").place(x=370, y=275)
cr_grade_entry = tk.Entry(Corrections_page, font=("Arial", 14), bd=2, relief="groove", bg="#FFFFFF", fg="#333333", state="readonly")
cr_grade_entry.place(x=490, y=270, width=114, height=36)


cr_done_btn = tk.Button(Corrections_page, text="Done", font=("Arial", 14), bg="#00B400", fg="white", bd=0)
cr_done_btn.place(relx=0.97, y=290, width=148, height=27, anchor="e")

# Correction Page ////////////////////////////////////////////////////////////////////////////////

# About Page /////////////////////////////////////////////////////////////////////////////////////
tk.Label(About_page, text="Faculty of Science and Technology, Ain Temouchent Province", 
         font=("Arial", 16), bg="white").place(relx=0.5, y=34, anchor="n")
# About Page /////////////////////////////////////////////////////////////////////////////////////

pages["Corrections"] = Corrections_page
pages["About"] = About_page

show_page("Corrections")

# تحميل وعرض شعار الجامعة
try:
    logo = Image.open("Logo.png")
    logo = logo.resize((80, 80), Image.LANCZOS)
    photo = ImageTk.PhotoImage(logo)
    labellogo = tk.Label(window, image=photo, bg="#FFFFFF")
    labellogo.image = photo
    labellogo.place(relx=1.0, y=8, anchor="ne")  # Using relx for responsive positioning
except FileNotFoundError:
    print("Logo.png not found.")

# تشغيل التطبيق
window.mainloop()