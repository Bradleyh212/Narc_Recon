import tkinter as tk
from tkinter import ttk, font, messagebox, PhotoImage
from main_page import open_main_page

# Track the number of failed login attempts
password_count = 0

# Function to handle login attempts and close the window after 3 failed tries
def login_try():
    global password_count
    password_count += 1
    if password_count == 3:
        window.destroy()  # Close the login window after 3 failed attempts

# Function to check username and password validity
def check_password():
    user_name = user_name_ent.get()
    password = password_ent.get()

    # Simple validation: username and password both set to "1"
    if user_name == "1" and password == "1":
        messagebox.showinfo("Login", "Login successful!")
        window.destroy()  # Close the login window
        open_main_page()  # Open the main page
    else:
        # Display error message and clear password entry
        messagebox.showerror("Login", "Invalid username or password")
        password_ent.delete(0, tk.END)
        user_name_ent.focus_set()
        password_ent.focus_set()  # Set focus back to password field
        login_try()  # Count the failed attempt

# Initialize the main Tkinter window
window = tk.Tk()
window.title("Narc Recon")
window.configure(bg="#3B4B59")
window.resizable(False, False)  # Disable resizing for the login UI


w, h = 650, 234
window_width = window.winfo_screenwidth()
window_height = window.winfo_screenheight()
x = (window_width / 2) - (w / 2)
y = (window_height / 2) - (h / 2)
window.geometry(f'{w}x{h}+{int(x)}+{int(y)}')

# Define font for the UI
login_ui_font = font.Font(family="Inter", size=36, weight="bold")

# Function to handle pressing "Enter" key for login
def sign_in(event=None):
    check_password()
window.bind('<Return>', sign_in)  # Bind "Enter" key to the sign-in process


# Left and right frames for the UI layout
left_frame = tk.Frame(window, width=350, height=h, bg="#3B4B59")
left_frame.grid(row=0, column=0, padx=53)

right_frame = tk.Frame(window, width=300, height=h)
right_frame.grid(row=0, column=1)

# Add logo to the right frame
logo = PhotoImage(file="logo_nr.png")
logo_lbl = tk.Label(right_frame, image=logo)
logo_lbl.grid(row=0, column=0)


# Adding widgets to the left frame
# Username entry widget
user_name_ent = tk.Entry(left_frame, fg="white", bg="black", highlightthickness=0, width=30)
user_name_ent.grid(row=0, column=0, pady=2.5)

# Password entry widget
password_ent = tk.Entry(left_frame, fg="white", bg="black", highlightthickness=0, width=30, show="*")
password_ent.grid(row=1, column=0, pady=2.5)

# Login button
login_btn = ttk.Button(left_frame, text="Sign In", command=check_password, , padding=(-5, -20))
login_btn.grid(row=2, column=0, pady=5)


# Set focus to the username entry widget on start
user_name_ent.focus_set()

# Start the Tkinter main event loop
window.mainloop()