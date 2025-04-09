import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
import os
import sys
import admin  # استيراد admin.py
import Professor  # استيراد Professor.py

# إنشاء النافذة
window = tk.Tk()
window.title("Login")

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

ICON_PATH = os.path.join(base_path, "favicon.ico")
window.wm_iconbitmap(ICON_PATH)
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

# المسارات إلى الصور
BACKGROUND_PATH = os.path.join(base_path, "background.png")
LOGO_PATH = os.path.join(base_path, "logo.png")

# تحميل الصور مع معالجة الاستثناءات
try:
    bg_img = Image.open(BACKGROUND_PATH)
    photo = ImageTk.PhotoImage(bg_img)
    label1 = tk.Label(window, image=photo)
    label1.image = photo
    label1.place(x=-5, y=0)
except FileNotFoundError:
    print("background.png not found.")

try:
    logo = Image.open(LOGO_PATH)
    photo2 = ImageTk.PhotoImage(logo)
    label2 = tk.Label(window, image=photo2)
    label2.image = photo2
    label2.place(x=319, y=12)
except FileNotFoundError:
    print("logo.png not found.")

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
        response = requests.post(
            "https://pfcc.onrender.com/api/login",
            json={"email": email, "password": password}
        )
        data = response.json()

        if response.status_code == 200 and "role" in data:
            role = data["role"]
            window.destroy()  # إغلاق نافذة تسجيل الدخول
            if role == "responsable":
                admin_window = admin.create_admin_window()  # استدعاء واجهة admin
                admin_window.mainloop()
            elif role == "professor":
                correction_number = data.get("correction", 1)
                professor_window = Professor.create_professor_window(correction_number)  # استدعاء واجهة Professor
                professor_window.mainloop()
            else:
                messagebox.showerror("Error", "Unauthorized access.")
        else:
            messagebox.showerror("Error", data.get("error", "Invalid email or password."))

    except requests.RequestException as err:
        messagebox.showerror("Error", f"API Error: {err}")

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