#professor.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

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
tk.Label(Corrections_page, text="Students List", font=("Arial", 14), bg="white").place(x=24, y=34)
import_btn = tk.Button(Corrections_page, text="Export", font=("Arial", 12), bg="#D9D9D9", bd=0)
import_btn.place(x=170, y=36, width=162, height=26)

separator = tk.Frame(Corrections_page, bg="#D9D9D9", height=2)
separator.place(x=216, y=96, width=360)  # تحديد الموقع تحت زر Import مباشرة

tk.Label(Corrections_page, text="List of grades", font=("Arial", 14), bg="white").place(x=24, y=134)
import_btn = tk.Button(Corrections_page, text="Import", font=("Arial", 12), bg="#D9D9D9", bd=0)
import_btn.place(x=170, y=134, width=162, height=26)

done_btn = tk.Button(Corrections_page, text="Done", font=("Arial", 12), bg="#00B400", fg="white", bd=0)
done_btn.place(relx=0.9, y=300, width=148, height=27, anchor="e")  # Using relx for responsive positioning
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