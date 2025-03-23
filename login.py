# login.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import subprocess
from db_connector import get_db_connection

# إنشاء النافذة
window = tk.Tk()
window.title("Login")  
window_width = 800
window_height = 500
window.resizable(False, False)  
window.configure(bg="#FBFBFB")  
window.geometry(f"{window_width}x{window_height}")

# توسيط النافذة
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x_position = int((screen_width - window_width) / 2)
y_position = int((screen_height - window_height) / 2)
window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# تحميل الصور
bg_img = Image.open(r"background.png")
photo = ImageTk.PhotoImage(bg_img)
label1 = tk.Label(window, image=photo)
label1.place(x=-5, y=0)  

logo = Image.open(r"Logo.png")
photo2 = ImageTk.PhotoImage(logo)
label2 = tk.Label(window, image=photo2)
label2.place(x=319, y=12)  

# إضافة عناصر الإدخال
Login = tk.Label(window, text="Profil Login", font=("Arial", 20, "bold"), bg="#FBFBFB", fg="#333333")
Login.place(x=470, y=103)

email = tk.Label(window, text="Email", font=("Arial", 12, "bold"), bg="#FBFBFB", fg="#555555")
email.place(x=435, y=180)

email_entry = tk.Entry(window, font=("Arial", 14), bd=2, relief="groove", bg="#FFFFFF", fg="#333333")
email_entry.place(x=435, y=208, width=242, height=36)

password = tk.Label(window, text="Password", font=("Arial", 12, "bold"), bg="#FBFBFB", fg="#555555")
password.place(x=435, y=274)  

password_entry = tk.Entry(window, font=("Arial", 14), show="*", bd=2, relief="groove", bg="#FFFFFF", fg="#333333")
password_entry.place(x=435, y=302, width=242, height=36)  


def on_login(): 
    email = email_entry.get().strip()
    password = password_entry.get().strip()

    if not email or not password:
        messagebox.showerror("Error", "Please enter both email and password.")
        return

    try:
        conn = get_db_connection()
        if conn is None:
            return
        
        cursor = conn.cursor()


        cursor.execute("SELECT 'responsable' FROM responsables WHERE email = %s AND password = %s", (email, password))
        result = cursor.fetchone()


        if not result:
            cursor.execute("SELECT 'professor', correction FROM professors WHERE email = %s AND password = %s", (email, password))
            result = cursor.fetchone()

        conn.close()

        if result:
            role = result[0]
            window.destroy()
            if role == "responsable":
                subprocess.run(["python", "admin.py"], check=True)
            elif role == "professor":
                correction_number = result[1]
                subprocess.run(["python", "professor.py", str(correction_number)], check=True)  
            else:
                messagebox.showerror("Error", "Unauthorized access.")
        else:
            messagebox.showerror("Error", "Invalid email or password.")

    except Exception as err:
        messagebox.showerror("Error", f"Database Query Error: {err}")

# زر تسجيل الدخول
login_button = tk.Button(
    window, 
    text="Login", 
    font=("Arial", 15, "bold"), 
    bg="#5D8BCD", 
    fg="white", 
    bd=0, 
    command=on_login
)
login_button.place(x=477, y=398, width=162, height=26)

# تشغيل النافذة الرئيسية
window.mainloop()
