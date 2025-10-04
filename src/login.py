import tkinter as tk
import customtkinter
from tkinter import ttk, font, messagebox, PhotoImage
from inventory import open_inventory_page
from customtkinter import CTkImage
from PIL import Image
from auth import authenticate_app


def main():
	# Track the number of failed login attempts
	global password_count
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
		ok, msg = authenticate_app(user_name, password)

		# Simple validation: username and password both set to "1"
		if ok: 
			messagebox.showinfo("Login", "Login successful!")
			window.withdraw()  # Close the login window
			open_inventory_page()  # Open the main page
		else:
			# Display error message and clear password entry
			messagebox.showerror("Login", "Invalid username or password")
			# flash_error()
			password_ent.delete(0, tk.END)
			user_name_ent.focus_set()
			password_ent.focus_set()  # Set focus back to password field
			login_try()  # Count the failed attempt

	# def flash_error():
	#     password_ent.configure(border_color="red")
	#     user_name_ent.configure(border_color="red")
	#     window.after(1000, lambda: (
	#         password_ent.configure(border_color="gray"),
	#         user_name_ent.configure(border_color="gray")
	#     ))

	# Initialize the main Tkinter window
	customtkinter.set_appearance_mode("dark")
	customtkinter.set_default_color_theme("dark-blue")

	window = customtkinter.CTk()
	window.title("Narc Recon")
	window.resizable(False, False)  # Disable resizing for the login UI


	w, h = 565, 234
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
	left_frame = customtkinter.CTkFrame(window, width=300, height=h)
	left_frame.grid(row=0, column=0)

	right_frame = customtkinter.CTkFrame(window, width=300, height=h)
	right_frame.grid(row=0, column=1)

	# Load the image using PIL, then convert to CTkImage
	logo_image = Image.open("others/logo_nr.png")
	logo = CTkImage(light_image=logo_image, dark_image=logo_image, size=(250, 234))  
	logo_lbl = customtkinter.CTkLabel(right_frame, image=logo, text='')
	logo_lbl.grid(row=0, column=0)


	# Adding widgets to the left frame
	# Username entry widget
	user_name_ent = customtkinter.CTkEntry(left_frame, width=275, height=35, placeholder_text = "Username", corner_radius=20)
	user_name_ent.grid(row=0, column=0, pady=(53, 0), padx=20)

	# Password entry widget
	password_ent = customtkinter.CTkEntry(left_frame, width=275, height=35, show="*", placeholder_text = "Password", corner_radius=20)
	password_ent.grid(row=1, column=0, pady=(10, 24))

	# Login button
	login_btn = customtkinter.CTkButton(left_frame, text="Login", command=check_password, corner_radius=20)
	login_btn.grid(row=2, column=0, pady=(0, 53))

	# Set focus to the username entry widget on start
	user_name_ent.focus_set()

	# Start the Tkinter main event loop
	window.mainloop()