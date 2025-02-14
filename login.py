import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from db_connection import connect_to_database
import subprocess  

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
bg_img = Image.open(r"C:\Users\yoga\Desktop\PythonProject\Application-de-Correction-d-Examen\background.png")

photo = ImageTk.PhotoImage(bg_img)
label1 = tk.Label(window, image=photo)
label1.place(x=-5, y=0)  

logo = Image.open(r"C:\Users\yoga\Desktop\PythonProject\Application-de-Correction-d-Examen/Logo.png")
photo2 = ImageTk.PhotoImage(logo)
label2 = tk.Label(window, image=photo2)
label2.place(x=319, y=12)  

# إضافة عناصر الإدخال
Login = tk.Label(window, text="Profil Login", font=("Arial", 20, "bold"), bg="#FBFBFB", fg="#333333")
Login.place(x=470, y=103)

username = tk.Label(window, text="Username", font=("Arial", 12, "bold"), bg="#FBFBFB", fg="#555555")
username.place(x=435, y=180)

username_entry = tk.Entry(window, font=("Arial", 14), bd=2, relief="groove", bg="#FFFFFF", fg="#333333")
username_entry.place(x=435, y=208, width=242, height=36)

password = tk.Label(window, text="Password", font=("Arial", 12, "bold"), bg="#FBFBFB", fg="#555555")
password.place(x=435, y=274)  

password_entry = tk.Entry(window, font=("Arial", 14), show="*", bd=2, relief="groove", bg="#FFFFFF", fg="#333333")
password_entry.place(x=435, y=302, width=242, height=36)  

# دالة تسجيل الدخول
def on_login():
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        messagebox.showerror("Error", "Please enter both username and password.")
        return

    try:
        db = connect_to_database()
        if not db:
            messagebox.showerror("Database Error", "Failed to connect to the database.")
            return

        cursor = db.cursor()

        # البحث في جدول المسؤولين
        cursor.execute("SELECT * FROM responsables WHERE username = %s AND password = %s", (username, password))
        responsable = cursor.fetchone()

        # البحث في جدول الأساتذة
        cursor.execute("SELECT * FROM professors WHERE username = %s AND password = %s", (username, password))
        professor = cursor.fetchone()

        cursor.close()
        db.close()

        if responsable:
            window.destroy()
            subprocess.run(["python", "background.png"], check=True)
        elif professor:
            window.destroy()
            subprocess.run(["python", "Logo.png"], check=True)
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    except Exception as err:
        messagebox.showerror("Error", f"An error occurred: {err}")
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
