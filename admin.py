#admin.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkcalendar import DateEntry
from tkinter import messagebox
import socket
import threading  # لتعدد المهام في الخادم
import mysql.connector
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import secrets
import string
import os
import sqlite3
from cryptography.fernet import Fernet
import random
import barcode
from barcode.writer import ImageWriter
from tkinter import filedialog, messagebox, Label, Tk, Entry, Frame
import qrcode  # Bibliothèque pour générer des QR codes
from pyzbar.pyzbar import decode
from PIL import Image  # Bibliothèque pour ouvrir les images scannées

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
menu_buttons = ["Option", "Students list","QR/Bar code", "Professors list", "Attendee list", "Results"]
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
code_page=tk.Frame(window, bg="white")

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

    columns = ("Module", "Coefficient")
    table = ttk.Treeview(add_exam_window, columns=columns, show="headings", height=8)

    table.heading("Module", text="Module")
    table.heading("Coefficient", text="Coefficient")

    table.column("Module", width=300, anchor="center")
    table.column("Coefficient", width=100, anchor="center")

    table.place(x=14, y=92, width=705, height=160)

    def add_item():
        if len(table.get_children()) < num_exams:
            module = module_entry.get().strip()
            coeff = coeff_entry.get().strip()

            if module and coeff.isdigit():
                table.insert("", "end", values=(module, coeff))
                module_entry.delete(0, tk.END)
                coeff_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Please enter a valid Module and Coefficient!")
        else:
            messagebox.showwarning("Warning", f"You can only add {num_exams} exams!")

    def delete_item():
        selected_item = table.selection()
        if selected_item:
            for item in selected_item:
                table.delete(item)
        else:
            messagebox.showwarning("Warning", "Please select an item to delete.")

    add_button = tk.Button(add_exam_window, text="Add", bg="#00B400", fg="white", command=add_item, width=8, bd=0)
    add_button.place(x=590, y=39, width=91, height=27)

    delete_button = tk.Button(add_exam_window, text="Delete", bg="#D10801", fg="white", command=delete_item, width=10, bd=0)
    delete_button.place(x=411, y=280, width=147, height=27)
    

    done_button = tk.Button(add_exam_window, text="Done", bg="#00B400", fg="white", command=add_exam_window.destroy, width=10, bd=0)
    done_button.place(x=570, y=280, width=147, height=27)

tk.Label(option_page, text="Add exams", font=("Arial", 14), bg="white").place(x=24, y=227)
add_exams_btn = tk.Button(option_page, text="Add", font=("Arial", 16), bg="#5D8BCD", fg="white", bd=0, command=add_exams_window)
add_exams_btn.place(x=190, y=230, width=148, height=27)

def add_salles_window():
    add_salle_window = tk.Toplevel(window)
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

    columns = ("Salle name", "Capacity")
    table = ttk.Treeview(add_salle_window, columns=columns, show="headings", height=8)

    table.heading("Salle name", text="Salle name")
    table.heading("Capacity", text="Capacity")

    table.column("Salle name", width=300, anchor="center")
    table.column("Capacity", width=100, anchor="center")

    table.place(x=14, y=92, width=705, height=160)

    def add_item():
        salle = salle_entry.get().strip()
        capacity = capacity_entry.get().strip()

        if salle and capacity.isdigit():
            table.insert("", "end", values=(salle, capacity))
            salle_entry.delete(0, tk.END)
            capacity_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Please enter a valid Salle name and Capacity!")

    def delete_item():
        selected_item = table.selection()
        if selected_item:
            for item in selected_item:
                table.delete(item)
        else:
            messagebox.showwarning("Warning", "Please select an item to delete.")

    add_button = tk.Button(add_salle_window, text="Add", bg="#00B400", fg="white", command=add_item, width=8, bd=0)
    add_button.place(x=590, y=39, width=91, height=27)

    delete_button = tk.Button(add_salle_window, text="Delete", bg="#D10801", fg="white", command=delete_item, width=10, bd=0)
    delete_button.place(x=411, y=280, width=147, height=27)

    done_button = tk.Button(add_salle_window, text="Done", bg="#00B400", fg="white", command=add_salle_window.destroy, width=10, bd=0)
    done_button.place(x=570, y=280, width=147, height=27)

tk.Label(option_page, text="Add salles", font=("Arial", 14), bg="white").place(x=24, y=275)
add_salles_btn = tk.Button(option_page, text="Add", font=("Arial", 16), bg="#5D8BCD", fg="white", bd=0, command=add_salles_window)
add_salles_btn.place(x=190, y=275, width=148, height=27)

op_done_btn = tk.Button(option_page, text="Done", font=("Arial", 14), bg="#00B400", fg="white", bd=0)
op_done_btn.place(relx=0.9, y=300, width=148, height=27, anchor="e")

# Option page /////////////////////////////////////////////////////////////////////////////////////

# Students page /////////////////////////////////////////////////////////////////////////////////////

# Fonction pour générer un code aléatoire unique
def generate_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Fonction pour importer et anonymiser un fichier Excel
def import_excel():
    global df  # Pour qu'on puisse accéder à df dans d'autres fonctions
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
    
    if file_path:
        df = pd.read_excel(file_path)
        
        # Vérifier si les colonnes nécessaires existent
        required_columns = ['Nom', 'Prenom', 'Filière', 'CodeSalle', 'Date_N']
        if all(col in df.columns for col in required_columns):
            
            # Création d'une copie pour l'administration
            df_admin = df.copy()

            # Ajout d'une colonne avec des codes anonymes
            df['Code Anonyme'] = [generate_code() for _ in range(len(df))]
            
            # Ajouter le code anonyme dans la copie pour l'administration
            df_admin['Code Anonyme'] = df['Code Anonyme']
            
            # Création du fichier anonymisé (sans nom, prénom, date de naissance)
            df_anonymized = df[['Code Anonyme', 'Filière', 'CodeSalle']]
            
            # Sauvegarder les fichiers
            save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], title="Save the file")
            
            if save_path:
                with pd.ExcelWriter(save_path) as writer:
                    df_anonymized.to_excel(writer, sheet_name="Anonymized", index=False)
                    df_admin.to_excel(writer, sheet_name="Administration", index=False)
                
                messagebox.showinfo("Success", "Files saved successfully!")
                display_data(df)
        else:
            messagebox.showerror("Error", "The file does not contain all the required columns!")

# Fonction pour afficher les candidats avec leur code anonyme
def display_data(df):
    for i in tree.get_children():
        tree.delete(i)
    for _, row in df.iterrows():
        tree.insert("", "end", values=(row['Nom'], row['Prenom'], row['Filière'], row['CodeSalle'], row['Date_N'], row['Code Anonyme']))

# Fonction pour ajouter un candidat manuellement
def add_candidate(entry_nom, entry_prenom, entry_filiere, entry_codesalle, entry_date_n):
    nom = entry_nom.get()
    prenom = entry_prenom.get()
    filiere = entry_filiere.get()
    codesalle = entry_codesalle.get()
    date_n = entry_date_n.get()
    
    if not nom or not prenom or not filiere or not codesalle or not date_n:
        messagebox.showwarning("Error", "Please fill in all the information.")
        return
    
    # Génération d'un code anonyme pour ce candidat
    code_anonyme = generate_code()
    
    # Ajouter ce candidat à la DataFrame
    global df
    new_row = pd.DataFrame([[nom, prenom, filiere, codesalle, date_n, code_anonyme]], columns=['Nom', 'Prenom', 'Filière', 'CodeSalle', 'Date_N', 'Code Anonyme'])
    df = pd.concat([df, new_row], ignore_index=True)
    
    # Mise à jour de l'affichage dans le tableau
    display_data(df)
    
    # Demander où sauvegarder le fichier Excel
    save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], title="Save the file")
    
    if save_path:
        df_admin = df.copy()
        df_anonymized = df[['Code Anonyme', 'Filière', 'CodeSalle']]
        
        with pd.ExcelWriter(save_path) as writer:
            df_anonymized.to_excel(writer, sheet_name="Anonymized", index=False)
            df_admin.to_excel(writer, sheet_name="Administration", index=False)
        
        messagebox.showinfo("Success", "Candidate added and file saved successfully!")

# Fonction pour ouvrir la fenêtre d'ajout de candidat
def open_add_candidate_window():
    add_candidate_window = tk.Toplevel(students_page)
    add_candidate_window.title("Add Candidate")
    add_candidate_window.configure(bg="white")
    add_candidate_window.geometry("750x450")
    
    
    # Définir la taille minimale et maximale de la fenêtre d'ajout de candidat
    add_candidate_window.minsize(750, 450)  # Taille minimale
    add_candidate_window.maxsize(750, 450)  # Taille maximale
    
    # Création d'un cadre principal pour une organisation propre
    frame_main = tk.Frame(add_candidate_window, padx=20, pady=20)
    frame_main.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Titre de la fenêtre
    tk.Label(frame_main, text="Add Candidate", font=("Arial", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=20)
    
    # Création des champs de saisie
    tk.Label(frame_main, text="Name:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5)
    entry_nom = tk.Entry(frame_main, font=("Arial", 12))
    entry_nom.grid(row=1, column=1, padx=10, pady=5, ipadx=5, ipady=5, sticky="ew")

    tk.Label(frame_main, text="First Name:", font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=5)
    entry_prenom = tk.Entry(frame_main, font=("Arial", 12))
    entry_prenom.grid(row=2, column=1, padx=10, pady=5, ipadx=5, ipady=5, sticky="ew")

    tk.Label(frame_main, text="Course:",font=("Arial", 12)).grid(row=3, column=0, sticky="w", pady=5)
    entry_filiere = tk.Entry(frame_main, font=("Arial", 12))
    entry_filiere.grid(row=3, column=1, padx=10, pady=5, ipadx=5, ipady=5, sticky="ew")

    tk.Label(frame_main, text="Room Code:",font=("Arial", 12)).grid(row=4, column=0, sticky="w", pady=5)
    entry_codesalle = tk.Entry(frame_main, font=("Arial", 12))
    entry_codesalle.grid(row=4, column=1, padx=10, pady=5, ipadx=5, ipady=5, sticky="ew")

    tk.Label(frame_main, text="Date of Birth:",font=("Arial", 12)).grid(row=5, column=0, sticky="w", pady=5)
    entry_date_n = tk.Entry(frame_main, font=("Arial", 12))
    entry_date_n.grid(row=5, column=1, padx=10, pady=5, ipadx=5, ipady=5, sticky="ew")
    
    # Ajouter un bouton pour soumettre les informations
    btn_add_candidate = tk.Button(frame_main, text="Add Candidate", font=("Arial", 12), command=lambda: add_candidate(entry_nom, entry_prenom, entry_filiere, entry_codesalle, entry_date_n), bg="#5D8BCD", fg="white")
    btn_add_candidate.grid(row=6, column=0, columnspan=2, pady=20, padx=10, sticky="ew")
    
    # Bouton pour revenir à la fenêtre principale
    btn_back = tk.Button(frame_main, text="Back", font=("Arial", 12), command=add_candidate_window.destroy, bg="black", fg="white")
    btn_back.grid(row=7, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

def export_excel():
    global df, file_path
    if df is not None and file_path:
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        messagebox.showinfo("Success", "Données mises à jour et sauvegardées dans le fichier d'origine!")
    else:
        messagebox.showwarning("Warning", "Aucun fichier importé!")

# Cadre pour les boutons
frame_buttons = tk.Frame(students_page)
frame_buttons.configure(bg="white")
frame_buttons.pack(pady=10)

btn_import = tk.Button(frame_buttons, text="Import Excel File",font=("Arial", 11), command=import_excel, width=20, bg="#5D8BCD", fg="white")
btn_import.grid(row=0, column=0, padx=10, pady=10)

btn_export = tk.Button(frame_buttons, text="Export Data",font=("Arial", 11),command=export_excel, width=20, bg="#5D8BCD", fg="white")
btn_export.grid(row=0, column=1, padx=10, pady=10)

btn_add_candidate_window = tk.Button(frame_buttons, text="Add Candidate Manually",font=("Arial", 11), command=open_add_candidate_window, width=20,bg="#00B400", fg="white")
btn_add_candidate_window.grid(row=0, column=2, padx=10, pady=10)


# Label de statut
lbl_status = tk.Label(students_page, text="Select a file to anonymize", fg="red")  # Changer la couleur du texte ici
lbl_status.pack()

# Tableau pour afficher les candidats avec leurs codes anonymes
columns = ("Name", "First Name", "Course", "Room Code", "Date of Birth", "Anonymous Code")
tree = ttk.Treeview(students_page, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)
tree.pack(expand=True, fill="both", padx=10, pady=10)


# Students page /////////////////////////////////////////////////////////////////////////////////////
# code page ////////////////////////////////////////////////////////////////////////////////////////

# Variable globale pour stocker le fichier Excel
df = None

# Fonction pour importer le fichier Excel
def import_excel():
    global df
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
    if not file_path:
        return
    try:
        df = pd.read_excel(file_path)
        required_columns = ['Nom', 'Prenom', 'Filière', 'CodeSalle', 'Date_N', 'Code Anonyme']
        if not all(col in df.columns for col in required_columns):
            messagebox.showerror("Error", "The Excel file does not contain all required columns.")
            df = None
            return
        messagebox.showinfo("Success", "Excel file successfully imported")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while importing the file: {e}")
        df = None

# Fonction pour générer les codes-barres et sauvegarder dans un fichier Excel
def save_barcodes_to_excel():
    global df
    if df is None:
        messagebox.showerror("Error", "Please import an Excel file first.")
        return
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    output_dir = os.path.join(desktop_path, "code_bars")
    os.makedirs(output_dir, exist_ok=True)
    barcode_data = []
    for index, row in df.iterrows():
        code_anonyme = str(row['Code Anonyme'])
        code = barcode.get_barcode_class('code128')(code_anonyme, writer=ImageWriter())
        barcode_filename = os.path.join(output_dir, f"barcode_{code_anonyme}.png")
        code.save(barcode_filename)
        barcode_data.append({
            "Nom": row['Nom'], "Prenom": row['Prenom'], "Filière": row['Filière'],
            "CodeSalle": row['CodeSalle'], "Date_N": row['Date_N'], "Code Anonyme": code_anonyme,
            "Nom du fichier de code-barres": barcode_filename
        })
    barcode_df = pd.DataFrame(barcode_data)
    barcode_df.to_excel(os.path.join(desktop_path, "code_bars.xlsx"), index=False)
    messagebox.showinfo("Success", "Barcodes have been generated and saved on your desktop.")

# Fonction pour générer des QR Codes et les sauvegarder
# Fonction pour générer des QR Codes et les sauvegarder dans un fichier Excel
def generate_qr_codes():
    global df
    if df is None:
        messagebox.showerror("Error", "Please import an Excel file first.")
        return
    
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    qr_dir = os.path.join(desktop_path, "code_qr")
    os.makedirs(qr_dir, exist_ok=True)
    
    qr_data = []  # Liste pour stocker les informations des QR codes
    
    for index, row in df.iterrows():
        code_anonyme = str(row['Code Anonyme'])
        
        # Génération du QR code
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(code_anonyme)
        qr.make(fit=True)
        qr_img = qr.make_image(fill='black', back_color='white')
        
        # Sauvegarde de l'image du QR code
        qr_filename = os.path.join(qr_dir, f"qr_code_{code_anonyme}.png")
        qr_img.save(qr_filename)
        
        # Ajouter les informations à la liste
        qr_data.append({
            "Nom": row['Nom'], "Prenom": row['Prenom'], "Filière": row['Filière'],
            "CodeSalle": row['CodeSalle'], "Date_N": row['Date_N'], "Code Anonyme": code_anonyme,
            "Nom du fichier QR Code": qr_filename
        })
    
    # Sauvegarde des informations dans un fichier Excel
    qr_df = pd.DataFrame(qr_data)
    qr_df.to_excel(os.path.join(desktop_path, "code_qr.xlsx"), index=False)
    
    messagebox.showinfo("Success", "QR codes have been generated and saved on your desktop.")

# Fonction pour scanner un code-barres ou un QR code et afficher les informations
# Fonction pour scanner un code-barres ou un QR code et afficher les informations
def scan_code():
    # Ouvre une fenêtre pour sélectionner une image à scanner
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if not file_path:
        return
    
    try:
        # Ouvre l'image avec PIL
        img = Image.open(file_path)
        decoded_objects = decode(img)  # Décode le code-barres ou QR code dans l'image
        if not decoded_objects:
            messagebox.showerror("Error", "No barcode or QR code detected.")
            return
        
        # Afficher les informations du code scanné
        for obj in decoded_objects:
            data = obj.data.decode('utf-8')  # Convertir les données en texte (Code Anonyme)
            
            # Rechercher les informations de l'étudiant dans le fichier Excel
            if df is not None:
                student_info = df[df['Code Anonyme'] == data]  # Trouver la ligne correspondant au Code Anonyme
                if not student_info.empty:
                    student_details = student_info.iloc[0]  # Prendre la première ligne trouvée
                    student_info_text = (
                        f"Nom: {student_details['Nom']}\n"
                        f"Prénom: {student_details['Prenom']}\n"
                        f"Filière: {student_details['Filière']}\n"
                        f"Code Salle: {student_details['CodeSalle']}\n"
                        f"Date de Naissance: {student_details['Date_N']}\n"
                        f"Code Anonyme: {student_details['Code Anonyme']}"
                    )
                    messagebox.showinfo("Informations de l'Étudiant", student_info_text)
                else:
                    messagebox.showerror("Error", "No information found for this code.")
            else:
                messagebox.showerror("Error", "Please import an Excel file first.")
                
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during scanning: {e}")

# Style pour ttk
style = ttk.Style()
style.configure("TButton", font=("Helvetica", 12), background="#5cb85c", padding=10)
style.configure("TLabel", font=("Helvetica", 14), background="#f2f2f2", foreground="#333")
style.configure("TFrame", background="#f2f2f2")

# Création des cadres pour l'interface
frame_top = Frame(code_page)
frame_top.pack(pady=30)

frame_import = Frame(code_page)
frame_import.pack(pady=20)

frame_generate_barcode = Frame(code_page)
frame_generate_barcode.pack(pady=20)

frame_generate_qr = Frame(code_page)
frame_generate_qr.pack(pady=20)

frame_scan_code = Frame(code_page)
frame_scan_code.pack(pady=20)

# Titre de l'application
Label(frame_top, text="Import your Excel file", font=("Arial", 18, "bold"), bg="#f2f2f2").pack()

# Bouton pour importer le fichier Excel
ttk.Button(frame_import, text="Import Excel File", command=import_excel,width=20).pack(fill="x", expand=True, pady=5)

# Bouton pour générer les codes-barres
ttk.Button(frame_generate_barcode, text="Generate Barcodes", command=save_barcodes_to_excel,width=20).pack(fill="x", expand=True, pady=5)

# Bouton pour générer les QR codes
ttk.Button(frame_generate_qr, text="Generate QR Codes", command=generate_qr_codes,width=20).pack(fill="x", expand=True, pady=5)

# Bouton pour scanner un code
ttk.Button(frame_scan_code, text="Scan a Code", command=scan_code,width=20).pack(fill="x", expand=True, pady=5)



# code page ////////////////////////////////////////////////////////////////////////////////////////

# Professors page /////////////////////////////////////////////////////////////////////////////////////
# 📧 Configuration Gmail
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "batehibellkirnesrin@gmail.com"  # Remplace par ton adresse Gmail
EMAIL_PASSWORD = "adfu hhbs tcim axfy"  # Remplace par ton mot de passe d'application

# 📌 Initialisation de la base de données
DB_FILE = "professeurs.db"
CLE_FICHIER = "key.key"
fichier_importe = None  # Variable pour stocker le fichier Excel

# 🔐 Générer et charger la clé de chiffrement
def generer_cle():
    if not os.path.exists(CLE_FICHIER):
        cle = Fernet.generate_key()
        with open(CLE_FICHIER, "wb") as fichier_cle:
            fichier_cle.write(cle)

def charger_cle():
    with open(CLE_FICHIER, "rb") as fichier_cle:
        return fichier_cle.read()

generer_cle()
fernet = Fernet(charger_cle())

# 📌 Connexion à SQLite
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS professeurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    prenom TEXT,
    email TEXT,
    mot_de_passe TEXT
)
""")
conn.commit()

# 🔑 Générer un mot de passe sécurisé
def generer_mot_de_passe():
    caracteres = string.ascii_letters + string.digits
    return ''.join(secrets.choice(caracteres) for _ in range(8))

# 🔒 Chiffrer et déchiffrer les mots de passe
def chiffrer_mot_de_passe(mot_de_passe):
    return fernet.encrypt(mot_de_passe.encode()).decode()

def dechiffrer_mot_de_passe(mot_de_passe_chiffre):
    return fernet.decrypt(mot_de_passe_chiffre.encode()).decode()

# 📩 Fonction d'envoi d'email
def envoyer_email(destinataire, nom, prenom, mot_de_passe):
    try:
        sujet = "Votre mot de passe pour la plateforme"
        message = f"""
        Bonjour {prenom} {nom},

        Voici vos informations de connexion :
        Email : {destinataire}
        Mot de passe : {mot_de_passe}

        Merci de garder ces informations en sécurité.

        Cordialement,
        L'administration.
        """

        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = destinataire
        msg["Subject"] = sujet
        msg.attach(MIMEText(message, "plain"))

        context = ssl.create_default_context()
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls(context=context)
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, destinataire, msg.as_string())
        server.quit()

        print(f"✅ Email envoyé à {destinataire}")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi à {destinataire} : {e}")


# 📂 Importer un fichier Excel
def importer_fichier():
    global fichier_importe, df
    fichier_importe = filedialog.askopenfilename(filetypes=[("Fichiers Excel", "*.xlsx;*.xls")])
    if not fichier_importe:
        return
    try:
        df = pd.read_excel(fichier_importe)
        if 'Nom' in df.columns and 'Prenom' in df.columns and 'Email' in df.columns:
            cursor.execute("DELETE FROM professeurs")
            conn.commit()

            for row in table.get_children():
                table.delete(row)

            messagebox.showinfo("Succès", "Fichier importé avec succès et ancienne liste supprimée.")
            lbl_fichier.config(text=f"Fichier chargé : {os.path.basename(fichier_importe)}")
            
            # Activation des boutons après l'importation réussie
            btn_generer.config(state=tk.NORMAL)
            btn_envoyer.config(state=tk.NORMAL)
            btn_exporter.config(state=tk.NORMAL)  # Activation du bouton Export
            
        else:
            messagebox.showerror("Erreur", "Le fichier doit contenir 'Nom', 'Prenom' et 'Email'.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de lire le fichier : {e}")

# 🔑 Générer et stocker les mots de passe
def generer_mots_de_passe():
    global df
    if df is not None:
        for _, row in df.iterrows():
            mot_de_passe = generer_mot_de_passe()
            mot_de_passe_chiffre = chiffrer_mot_de_passe(mot_de_passe)

            cursor.execute("INSERT INTO professeurs (nom, prenom, email, mot_de_passe) VALUES (?, ?, ?, ?)",
                           (row['Nom'], row['Prenom'], row['Email'], mot_de_passe_chiffre))
        conn.commit()

        messagebox.showinfo("Succès", "Mots de passe générés et enregistrés.")
        afficher_donnees()

# 📩 Envoyer les emails à tous les professeurs
def envoyer_tous_emails():
    cursor.execute("SELECT nom, prenom, email, mot_de_passe FROM professeurs")
    professeurs = cursor.fetchall()

    if not professeurs:
        messagebox.showerror("Erreur", "Aucun professeur enregistré dans la base de données.")
        return

    for nom, prenom, email, mot_de_passe_chiffre in professeurs:
        mot_de_passe_dechiffre = dechiffrer_mot_de_passe(mot_de_passe_chiffre)
        envoyer_email(email, nom, prenom, mot_de_passe_dechiffre)

    messagebox.showinfo("Succès", "Emails envoyés à tous les professeurs.")

# 📊 Afficher les données
def afficher_donnees():
    for row in table.get_children():
        table.delete(row)

    cursor.execute("SELECT id, nom, prenom, email, mot_de_passe FROM professeurs")
    for row in cursor.fetchall():
        id_prof, nom, prenom, email, mot_de_passe_chiffre = row
        mot_de_passe_dechiffre = dechiffrer_mot_de_passe(mot_de_passe_chiffre)
        table.insert("", "end", values=(id_prof, nom, prenom, email, mot_de_passe_dechiffre))

# 📌 Fonction pour vider le tableau
def vider_tableau():
    confirmation = messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer toutes les données ?")
    if confirmation:
        cursor.execute("DELETE FROM professeurs")
        conn.commit()

        for row in table.get_children():
            table.delete(row)

        messagebox.showinfo("Succès", "Toutes les données ont été supprimées.")
        # 📂 Exporter vers le fichier Excel importé
def exporter_fichier():
    global fichier_importe, df
    if fichier_importe and df is not None:
        try:
            # Récupérer les mots de passe depuis la base de données
            cursor.execute("SELECT nom, prenom, email, mot_de_passe FROM professeurs")
            professeurs = cursor.fetchall()
            
            # Vérifier si la colonne "Mot de passe" existe déjà
            if "Mot de passe" not in df.columns:
                df["Mot de passe"] = ""

            # Mettre à jour les mots de passe dans le DataFrame
            for i, (_, _, email, mot_de_passe_chiffre) in enumerate(professeurs):
                mot_de_passe_dechiffre = dechiffrer_mot_de_passe(mot_de_passe_chiffre)
                df.at[i, "Mot de passe"] = mot_de_passe_dechiffre

            # Sauvegarder dans le fichier Excel
            df.to_excel(fichier_importe, index=False)
            messagebox.showinfo("Succès", "Exportation réussie dans le même fichier Excel !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'exporter : {e}")

            # ➕ Ajouter un professeur manuellement

def ajouter_professeur():
    def sauvegarder_professeur():
        nom = entry_nom.get().strip()
        prenom = entry_prenom.get().strip()
        email = entry_email.get().strip()
        
        if nom and prenom and email:
            mot_de_passe = generer_mot_de_passe()
            mot_de_passe_chiffre = chiffrer_mot_de_passe(mot_de_passe)
            
            cursor.execute("INSERT INTO professeurs (nom, prenom, email, mot_de_passe) VALUES (?, ?, ?, ?)",
                           (nom, prenom, email, mot_de_passe_chiffre))
            conn.commit()
            afficher_donnees()
            
            messagebox.showinfo("Succès", f"Professeur {prenom} {nom} ajouté avec succès !")
            fenetre_ajout.destroy()
        else:
            messagebox.showerror("Erreur", "Tous les champs sont obligatoires.")

    # Création de la fenêtre d'ajout plus grande
    fenetre_ajout = tk.Toplevel(professors_page)
    fenetre_ajout.title("Ajouter un Professeur")
    fenetre_ajout.geometry("730x320")
    fenetre_ajout.resizable(False, False)

    frame = tk.Frame(fenetre_ajout, padx=30, pady=30)
    frame.pack(expand=True)

    # Titre
    tk.Label(frame, text="Ajouter un Nouveau Professeur", font=("Arial", 16, "bold"), fg="black").grid(row=0, column=0, columnspan=2, pady=15)

    # Champs de saisie avec labels bien alignés
    tk.Label(frame,fg="red" ,text="Nom :", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=10)
    entry_nom = tk.Entry(frame, font=("Arial", 14), width=27)
    entry_nom.grid(row=1, column=1, pady=10)

    tk.Label(frame, fg="red",text="Prénom :", font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=10)
    entry_prenom = tk.Entry(frame, font=("Arial", 14), width=27)
    entry_prenom.grid(row=2, column=1, pady=10)

    tk.Label(frame,fg="red" ,text="Email :", font=("Arial", 12)).grid(row=3, column=0, sticky="w", pady=10)
    entry_email = tk.Entry(frame, font=("Arial", 14), width=27)
    entry_email.grid(row=3, column=1, pady=10)

    # Boutons d'action bien positionnés
    btn_sauvegarder = tk.Button(frame, text="Sauvegarder", font=("Arial", 12, "bold"), bg="#5D8BCD", fg="white", command=sauvegarder_professeur, width=15, height=1)
    btn_sauvegarder.grid(row=4, column=0, columnspan=2, pady=20, ipadx=45, ipady=5)


  # 🖥 Interface Tkinter


espacement_x = 150  # Distance horizontale entre les boutons
position_x = 10  
button_width = 20  # Largeur des boutons (en nombre de caractères)
button_height = 1

btn_importer = tk.Button(professors_page, text="Importer un fichier Excel", command=importer_fichier, width=button_width, height=button_height , bg="#5D8BCD", fg="white")
btn_importer.place(x=position_x, y=20)

btn_generer = tk.Button(professors_page, text="Générer les mots de passe", command=generer_mots_de_passe, state=tk.DISABLED, width=button_width, height=button_height)
btn_generer.place(x=position_x +1.01* espacement_x, y=20)

btn_envoyer = tk.Button(professors_page, text="Envoyer les mots de passe par email", command=envoyer_tous_emails, state=tk.DISABLED, width=27, height=button_height)
btn_envoyer.place(x=position_x + 2.035* espacement_x, y=20)

btn_exporter = tk.Button(professors_page, text="Exporter vers Excel", command=exporter_fichier, state=tk.DISABLED, width=18, height=button_height)
btn_exporter.place(x=position_x + 3.375* espacement_x, y=20)

btn_ajouter = tk.Button(professors_page, text="Ajouter un professeur", command=ajouter_professeur, width=18, height=button_height, bg="#5D8BCD", fg="white")
btn_ajouter.place(x=position_x + 4.3 * espacement_x, y=20)

lbl_fichier = tk.Label(professors_page, text="Aucun fichier chargé", fg="blue", width=18, height=button_height)
lbl_fichier.place(x=10, y=80)

frame_table = tk.Frame(professors_page)
frame_table.pack(pady=110)

table = ttk.Treeview(frame_table, columns=("ID", "Nom", "Prenom", "Email", "Mot de passe"), show="headings")
table.heading("ID", text="ID")
table.heading("Nom", text="Nom")
table.heading("Prenom", text="Prénom")
table.heading("Email", text="Email")
table.heading("Mot de passe", text="Mot de passe")
table.pack()

btn_vider = tk.Button(professors_page, text="Vider le tableau",font=("Arial", 10, "bold"), command=vider_tableau, fg="white", bg="red", width=18, height=button_height )
btn_vider.pack(pady=10)
btn_vider.place(x=327,y=300)

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
pages["QR/Bar code"] = code_page

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