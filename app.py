import sqlite3
import hashlib
import tkinter as tk
from tkinter import messagebox, Menu
from PIL import Image, ImageTk

# Initialisation de la base de données
def init_db():
    conn = sqlite3.connect("app_data.db")
    cursor = conn.cursor()
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('teacher', 'admin'))
        )
    """)
    add_test_users(cursor)
    conn.commit()
    conn.close()

# Ajout d'utilisateurs tests
def add_test_users(cursor):
    users = [
        ("nessrine", "password123", "teacher"),
        ("aymen", "adminpass", "admin"),
        ("abdrahmane", "teacherpass", "teacher"),
    ]
    for username, password, role in users:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_password, role))

# Fonction d'authentification
def authenticate_user(username, password):
    conn = sqlite3.connect("app_data.db")
    cursor = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT username, role FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = cursor.fetchone()
    conn.close()
    return user



# Configuration commune des fenêtres
def configure_window(win, title):
    win.title(title)
    win.geometry("750x450+250+100")
    win.config(bg="#f0f0f0")

# Ajout d'une image d'arrière-plan
def add_background(win, image_path):
    bg_image = Image.open(image_path).resize((750, 450), Image.LANCZOS)
    bg_image_tk = ImageTk.PhotoImage(bg_image)

    canvas = tk.Canvas(win, width=750, height=450)
    canvas.create_image(0, 0, anchor=tk.NW, image=bg_image_tk)
    canvas.image = bg_image_tk  # Empêche l'image d'être supprimée par le garbage collector
    canvas.place(x=0, y=0)



# Interface principale
init_db()
root = tk.Tk()
root.iconbitmap("img/exam_2641409.ico")
configure_window(root, "Application de Correction d'Examen")

# Arrière-plan principal
add_background(root, "img/istockphoto-1146368775-612x612 (1).jpg")  # Remplacez par votre image

# Formulaire de connexion
frame_form = tk.Frame(root, bg="white", bd=2, relief=tk.RIDGE)
frame_form.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=350, height=250)

# Titre
tk.Label(frame_form, text="User Login", font=("Arial", 16, "bold"), fg="#000080").pack(pady=10)

# Champs
tk.Label(frame_form, text="Username:", font=("Arial", 12), bg="white").pack(anchor="w", padx=20)
entry_username = tk.Entry(frame_form, font=("Arial", 12), justify='center')
entry_username.pack(pady=5, padx=20, fill=tk.X)

tk.Label(frame_form, text="Password:", font=("Arial", 12), bg="white").pack(anchor="w", padx=20)
entry_password = tk.Entry(frame_form, font=("Arial", 12), show="*", justify='center')
entry_password.pack(pady=5, padx=20, fill=tk.X)

# Bouton de connexion
tk.Button(frame_form, text="Login", font=("Arial", 12), bg="#000080", fg="white" , width=20).pack(pady=20)

root.mainloop()
