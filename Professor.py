import sys
import tkinter as tk
from tkinter import ttk, messagebox
import socket
import qrcode
import threading
from PIL import Image, ImageTk
import requests


# Create the main window
window = tk.Tk()
window.title("Professor Window")
window.iconbitmap('app-icon.png')
window_width = 800
window_height = 500
window.resizable(True, True)
window.configure(bg="#FFFFFF")
window.geometry(f"{window_width}x{window_height}")

# Center the window on the screen
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x_position = int((screen_width - window_width) / 2)
y_position = int((screen_height - window_height) / 2)
window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Header
header_label = tk.Label(window, text="Management of Post-Graduation\nCompetitions",
                        font=("Arial", 24, "bold"), fg="#5A7EC7", bg="#FFFFFF", justify="left")
header_label.pack(pady=15, anchor="w", padx=20)

# Menu frame
menu_frame = tk.Frame(window, bg="#5A7EC7")
menu_frame.pack(fill=tk.X, side=tk.TOP)

# Pages dictionary to manage frames
pages = {}

# Function to switch pages
def show_page(page_name):
    for page in pages.values():
        page.pack_forget()
    pages[page_name].pack(fill=tk.BOTH, expand=True)

# Button hover effects
def on_enter(button):
    button.config(bg="#4A66B0", fg="#FFFFFF")

def on_leave(button):
    button.config(bg="#5A7EC7", fg="#FFFFFF")

# Create menu buttons
menu_buttons = ["Corrections", "About"]
button_width = 15
for idx, text in enumerate(menu_buttons):
    btn = tk.Button(menu_frame, text=text, font=("Arial", 10, "bold"), fg="#FFFFFF", bg="#5A7EC7",
                    relief=tk.FLAT, width=button_width, command=lambda page=text: show_page(page))
    btn.bind("<Enter>", lambda event, b=btn: on_enter(b))
    btn.bind("<Leave>", lambda event, b=btn: on_leave(b))
    btn.pack(side=tk.LEFT, padx=5, pady=5)

# Create page frames
Corrections_page = tk.Frame(window, bg="white")
About_page = tk.Frame(window, bg="white")
pages["Corrections"] = Corrections_page
pages["About"] = About_page

# Correction Page ////////////////////////////////////////////////////////////////////////////////
def get_correction():
    """Get correction value from command-line arguments passed by on_login()"""
    if len(sys.argv) < 2:
        print("Usage: python professor.py <correction>")
        return 1
    try:
        correction = int(sys.argv[1])
        if correction not in [1, 2, 3]:
            print("Error: <correction> must be 1, 2, or 3")
            return 1
        return correction
    except ValueError:
        print("Error: <correction> must be an integer (1, 2, or 3)")
        return 1

# Get correction value
correction = get_correction()

# GUI setup for Corrections page
tk.Label(Corrections_page, text="Option", font=("Arial", 14), bg="white").place(x=24, y=30)

cr_option = ttk.Combobox(Corrections_page, state="readonly")
cr_option.place(x=135, y=26, width=237, height=36)

def update_options():
    response = requests.get("https://pfcc.onrender.com/api/exam_options")
    if response.status_code == 200:
        options = response.json().get("options", [])
        cr_option["values"] = options
        if options:
            cr_option.current(0)
        else:
            cr_option.set("No options available")
    else:
        messagebox.showerror("Error", response.json().get("error", "Failed to fetch exam options"))
    Corrections_page.after(5000, update_options)

update_options()

tk.Label(Corrections_page, text="Anonymat", font=("Arial", 14), bg="white").place(x=24, y=90)
cr_anonyme_entry = tk.Entry(Corrections_page, font=("Arial", 14), bd=2, relief="groove", bg="#FFFFFF", fg="#333333")
cr_anonyme_entry.place(x=135, y=84, width=114, height=36)

# Separator line
separator = tk.Frame(Corrections_page, bg="#D9D9D9", height=2)
separator.place(x=100, y=155, width=560)

tk.Label(Corrections_page, text="Exam :", font=("Arial", 14, "bold"), bg="white").place(x=24, y=140)

tk.Label(Corrections_page, text="Exam", font=("Arial", 14), bg="white").place(x=264, y=90)
cr_exam = ttk.Combobox(Corrections_page, state="readonly")
cr_exam.place(x=325, y=84, width=95, height=36)

tk.Label(Corrections_page, text="Subject :", font=("Arial", 14), bg="white").place(x=24, y=180)
subject_label = tk.Label(Corrections_page, text="", font=("Arial", 14), bg="white")
subject_label.place(x=140, y=180)

tk.Label(Corrections_page, text="Coeffs :", font=("Arial", 14), bg="white").place(x=370, y=180)
coeff_label = tk.Label(Corrections_page, text="", font=("Arial", 14), bg="white")
coeff_label.place(x=490, y=180)

# Store coefficient globally to use in save_grades
current_coefficient = 0.0

def update_exam_details(event):
    global current_coefficient
    selected_exam = cr_exam.get()
    if not selected_exam:
        return
    response = requests.get(f"https://pfcc.onrender.com/api/exam_details/{selected_exam}")
    if response.status_code == 200:
        data = response.json()
        subject_label.config(text=data.get("subject", "N/A"))
        coeff = data.get("coefficient", 0.0)
        coeff_label.config(text=str(coeff))
        current_coefficient = float(coeff)
    else:
        messagebox.showerror("Error", response.json().get("error", "Failed to fetch exam details"))
        subject_label.config(text="N/A")
        coeff_label.config(text="0.0")
        current_coefficient = 0.0

def update_exam_modules():
    response = requests.get("https://pfcc.onrender.com/api/exam_modules")
    if response.status_code == 200:
        modules = response.json().get("modules", [])
        cr_exam["values"] = modules
        if modules:
            cr_exam.current(0)
            update_exam_details(None)
        else:
            cr_exam.set("No exams available")
    else:
        messagebox.showerror("Error", response.json().get("error", "Failed to fetch exam modules"))
    Corrections_page.after(5000, update_exam_modules)

# Call update_exam_modules after all labels are defined
update_exam_modules()
cr_exam.bind("<<ComboboxSelected>>", update_exam_details)

tk.Label(Corrections_page, text="Correction", font=("Arial", 14), bg="white").place(x=24, y=230)
cr_entry = tk.Entry(Corrections_page, font=("Arial", 14), bd=2, relief="groove", bg="#FFFFFF", fg="#333333")
cr_entry.place(x=140, y=225, width=114, height=36)

tk.Label(Corrections_page, text="Final grade", font=("Arial", 14), bg="white").place(x=370, y=230)
cr_grade_entry = tk.Entry(Corrections_page, font=("Arial", 14), bd=2, relief="groove", bg="#FFFFFF", fg="#333333", state="readonly")
cr_grade_entry.place(x=490, y=225, width=114, height=36)

def handle_save():
    anonymous_id = cr_anonyme_entry.get().strip()
    exam_name = cr_exam.get().strip()
    try:
        grade = float(cr_entry.get())
        if not (0 <= grade <= 20):
            messagebox.showerror("Error", "Grade must be between 0 and 20")
            return
        if not anonymous_id or not exam_name:
            messagebox.showerror("Error", "Please fill in all required fields (Anonymat and Exam)")
            return
        response = requests.post(
            "https://pfcc.onrender.com/api/grades",
            json={
                "anonymous_id": anonymous_id,
                "exam_name": exam_name,
                "correction": correction,
                "grade": grade,
                "coeff": current_coefficient
            }
        )
        if response.status_code == 200:
            messagebox.showinfo("Success", response.json().get("message", "Grade saved successfully"))
            cr_grade_entry.config(state="normal")
            cr_grade_entry.delete(0, tk.END)
            cr_grade_entry.insert(0, str(grade))  # Display the saved grade
            cr_grade_entry.config(state="readonly")
            # Clear input fields
            cr_anonyme_entry.delete(0, tk.END)
            cr_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", response.json().get("error", "Failed to save grade"))
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number for the grade")

cr_done_btn = tk.Button(Corrections_page, text="Done", font=("Arial", 14), bg="#00B400", fg="white", bd=0, command=handle_save)
cr_done_btn.place(relx=0.97, y=290, width=148, height=27, anchor="e")

def update_entry(data):
    cr_anonyme_entry.delete(0, tk.END)
    cr_anonyme_entry.insert(0, data)

def start_server():
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', 5000))
        server_socket.listen(1)
        print("Server started, listening on port 5000")

        while True:
            client_socket, address = server_socket.accept()
            data = client_socket.recv(1024).decode('utf-8')
            print(f"Received data from {address}: {data}")
            window.after(0, update_entry, data)
            client_socket.close()
    except Exception as e:
        print(f"Server error: {e}")
        messagebox.showerror("Error", f"Failed to start server: {e}")

# Start server in a separate thread
threading.Thread(target=start_server, daemon=True).start()

# Function to get local IP address
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"Error getting IP: {e}")
        return "127.0.0.1"

# Function to create and show QR code window
def show_qr_code():
    local_ip = get_local_ip()
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(local_ip)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_window = tk.Toplevel(window)
    qr_window.title("Mobile App QR Code")
    qr_window.iconbitmap('app-icon.png')
    qr_window.geometry("300x400")
    
    instruction_label = tk.Label(qr_window, text="Open application and scan this code", font=("Arial", 12))
    instruction_label.pack(pady=5)
    
    qr_photo = ImageTk.PhotoImage(qr_img)
    qr_label = tk.Label(qr_window, image=qr_photo)
    qr_label.image = qr_photo
    qr_label.pack(pady=10)
    
    ip_label = tk.Label(qr_window, text=f"Local IP: {local_ip}", font=("Arial", 12))
    ip_label.pack()

mobile_qr = tk.Button(Corrections_page, text="Mobile app", font=("Arial", 14), bg="#5D8BCD", fg="white", bd=0, command=show_qr_code)
mobile_qr.place(relx=0.97, y=250, width=148, height=27, anchor="e")

# About Page /////////////////////////////////////////////////////////////////////////////////////
tk.Label(About_page, text="Faculty of Science and Technology, Ain Temouchent Province",
         font=("Arial", 16), bg="white").place(relx=0.5, y=34, anchor="n")

# Load and place logo
try:
    logo = Image.open("Logo.png")
    logo = logo.resize((80, 80), Image.LANCZOS)
    photo = ImageTk.PhotoImage(logo)
    labellogo = tk.Label(window, image=photo, bg="#FFFFFF")
    labellogo.image = photo
    labellogo.place(relx=1.0, y=8, anchor="ne")
except FileNotFoundError:
    print("Logo.png not found.")

# Show the initial page
show_page("Corrections")

# Start the application
window.mainloop()