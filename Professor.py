#professors.py
import sys
import tkinter as tk
from tkinter import ttk
import socket
import qrcode
import threading
from PIL import Image, ImageTk
import requests
from db_connector import get_exam_options, fetch_exam_modules, fetch_exam_details,save_grade,get_db_connection


# Create the main window
window = tk.Tk()
window.title("Professor Window")
window_width = 800
window_height = 500
window.resizable(True, True)  # Allow resizing
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
    if len(sys.argv) < 2:  # Only expecting script name + correction
        print("Usage: python professor.py <correction>")
        return 1  # Default value if no argument provided
    try:
        correction = int(sys.argv[1])  # correction is the first argument after script name
        return correction
    except ValueError:
        print("Error: <correction> must be an integer (1, 2, or 3)")
        return 1  # Default value if invalid

# Get correction value
correction = get_correction()


# GUI setup for Corrections page
tk.Label(Corrections_page, text="Option", font=("Arial", 14), bg="white").place(x=24, y=30)


cr_option = ttk.Combobox(Corrections_page, state="readonly")
cr_option.place(x=135, y=26, width=237, height=36)

options = requests.get("https://pfcc.onrender.com/api/exam_options").json()["exam_options"]
cr_option["values"] = options


tk.Label(Corrections_page, text="Anonymat", font=("Arial", 14), bg="white").place(x=24, y=90)
cr_anonyme_entry = tk.Entry(Corrections_page, font=("Arial", 14), bd=2, relief="groove", bg="#FFFFFF", fg="#333333")
cr_anonyme_entry.place(x=135, y=84, width=114, height=36)



# Separator line
separator = tk.Frame(Corrections_page, bg="#D9D9D9", height=2)
separator.place(x=100, y=155, width=560)

tk.Label(Corrections_page, text="Exam :", font=("Arial", 14, "bold"), bg="white").place(x=24, y=140)

# Store coefficient globally to use in save_grades
current_coefficient = 0.0

def update_exam_details(event):
    global current_coefficient
    selected_exam = cr_exam.get()
    response = requests.get(f"https://pfcc.onrender.com/api/exam_details/{selected_exam}")
    data = response.json()
    subject_label.config(text=data["subject"])
    coeff_label.config(text=str(data["coefficient"]))
    current_coefficient = data["coefficient"]

tk.Label(Corrections_page, text="Exam", font=("Arial", 14), bg="white").place(x=264, y=90)
cr_exam = ttk.Combobox(Corrections_page, state="readonly")
cr_exam.place(x=325, y=84, width=95, height=36)

exam_modules = requests.get("https://pfcc.onrender.com/api/exam_modules").json()["modules"]
cr_exam["values"] = exam_modules

tk.Label(Corrections_page, text="Subject :", font=("Arial", 14), bg="white").place(x=24, y=180)
subject_label = tk.Label(Corrections_page, text="", font=("Arial", 14), bg="white")
subject_label.place(x=140, y=180)

tk.Label(Corrections_page, text="Coeffs :", font=("Arial", 14), bg="white").place(x=370, y=180)
coeff_label = tk.Label(Corrections_page, text="", font=("Arial", 14), bg="white")
coeff_label.place(x=490, y=180)


tk.Label(Corrections_page, text="Correction", font=("Arial", 14), bg="white").place(x=24, y=230)
cr_entry = tk.Entry(Corrections_page, font=("Arial", 14), bd=2, relief="groove", bg="#FFFFFF", fg="#333333",
                      state="normal")
cr_entry.place(x=140, y=225, width=114, height=36)


tk.Label(Corrections_page, text="Finale grade", font=("Arial", 14), bg="white").place(x=370, y=230)
cr_grade_entry = tk.Entry(Corrections_page, font=("Arial", 14), bd=2, relief="groove", bg="#FFFFFF", fg="#333333", state="readonly")
cr_grade_entry.place(x=490, y=225, width=114, height=36)



def handle_save():
    anonymous_id = cr_anonyme_entry.get()
    exam_name = cr_exam.get()
    coeff = coeff_label.cget("text")
    try:
        grade = float(cr_entry.get())
        if 0 <= grade <= 20:
            response = requests.post(
                "https://pfcc.onrender.com/api/grades",
                json={"anonymous_id": anonymous_id, "exam_name": exam_name, "correction": correction, "grade": grade, "coeff": coeff}
            )
            if response.status_code == 200:
                # جلب الدرجة النهائية من الـ API إذا لزم الأمر
                cr_grade_entry.config(state="normal")
                cr_grade_entry.delete(0, tk.END)
                cr_grade_entry.insert(0, "تم الحفظ")  # يمكن تحسين هذا لجلب الدرجة النهائية
                cr_grade_entry.config(state="readonly")
            else:
                print(response.json()["message"])
        else:
            print("Error: Grade must be between 0 and 20")
    except ValueError:
        print("Error: Please enter a valid number for the grade")

cr_done_btn = tk.Button(Corrections_page, text="Done", font=("Arial", 14), bg="#00B400", fg="white", bd=0, command=handle_save)
cr_done_btn.place(relx=0.97, y=290, width=148, height=27, anchor="e")

def update_entry(data):
    cr_anonyme_entry.delete(0, tk.END)
    cr_anonyme_entry.insert(0, data)

def start_server():
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

# Start server and GUI
threading.Thread(target=start_server, daemon=True).start()

# Function to get local IP address
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connect to a known external server (Google DNS)
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"Error getting IP: {e}")
        return "127.0.0.1"  # Fallback to localhost

# Function to create and show QR code window
def show_qr_code():
    # Get local IP
        local_ip = get_local_ip()
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(local_ip)
        qr.make(fit=True)
        
        # Generate QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Create a new window
        qr_window = tk.Toplevel(window)
        qr_window.title("Mobile App QR Code")
        qr_window.geometry("300x400")
        
        # Add label with instructions
        instruction_label = tk.Label(qr_window, text="Open application and scan this code", font=("Arial", 12))
        instruction_label.pack(pady=5)
        
        # Convert QR code image to Tkinter-compatible format
        qr_photo = ImageTk.PhotoImage(qr_img)
        
        # Display QR code
        qr_label = tk.Label(qr_window, image=qr_photo)
        qr_label.image = qr_photo  # Keep a reference to avoid garbage collection
        qr_label.pack(pady=10)
        
        # Display IP address text
        ip_label = tk.Label(qr_window, text=f"Local IP: {local_ip}", font=("Arial", 12))
        ip_label.pack()
        


# Add Mobile QR button (fixed command parameter)
mobile_qr = tk.Button(Corrections_page, text="Mobile app", font=("Arial", 14), bg="#5D8BCD", fg="white", bd=0, command=show_qr_code)  # Removed quotes around show_qr_code
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
    labellogo.image = photo  # Keep a reference to avoid garbage collection
    labellogo.place(relx=1.0, y=8, anchor="ne")
except FileNotFoundError:
    print("Logo.png not found.")

# Show the initial page
show_page("Corrections")

# Start the application
window.mainloop()