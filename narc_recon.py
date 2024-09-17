import tkinter as tk
from tkinter import ttk, font, messagebox, PhotoImage
from main_page import open_main_page

password_count = 0
def login_try(): #function to count the login tries and close the app if it reaches 3
	global password_count
	password_count += 1

def check_password():
	user_name = user_name_ent.get()
	password = password_ent.get()

	if user_name == "1" and password == "1":
		messagebox.showinfo("Login", "Login successful!")
		window.destroy()  # Close the login window
		open_main_page()  # Open the main page
	else:
		messagebox.showerror("Login", "Invalid username or password")
		user_name_ent.focus_set()
		password_ent.focus_set() #Focus on password after try
		password_ent.delete(0, tk.END)
		login_try()
		if password_count == 3:
			 window.destroy()

window = tk.Tk()
window.title("Narc Recon")
window.configure(bg="#3B4B59")

def sign_in(n):
	check_password()
window.bind('<Return>', sign_in)

#Window setting
window.resizable(False, False) #This stops the user from resizing the screen for the login ui
w = 650 
h = 234
window_width = window.winfo_screenwidth()  # screen centering code from https://stackoverflow.com/questions/14910858/how-to-specify-where-a-tkinter-window-opens
window_height = window.winfo_screenheight()  
x = (window_width/2) - (w/2)
y = (window_height/2) - (h/2)
window.geometry('%dx%d+%d+%d' % (w, h, x, y))
# End of window setting

# Define a font
login_ui_font = font.Font(family="Inter", size=36, weight="bold")

# Define left and right frame
left_frame = tk.Frame(window, width = 350, height = h)
left_frame.grid(row=0, column=0, padx = 53)
left_frame.configure(bg="#3B4B59")

right_frame = tk.Frame(window, width = 300, height = h)
right_frame.grid(row=0, column=1)

# Adding logo to right frame
logo = PhotoImage(file="logo_nr.png")

logo_lbl = tk.Label(right_frame, image = logo)
logo_lbl.grid(row=0,column=0)

# Adding widgets to the left frame

# User name entry widget
user_name_ent = tk.Entry(left_frame, fg = "white", bg ="black", highlightthickness = 0,  width = 30) # Removing the highlightthickness
user_name_ent.grid(row=0, column=0, pady = 2.5)


# Password entry widget 
password_ent = tk.Entry(left_frame, fg = "white", bg = "black", highlightthickness = 0, width = 30, show="*") # Removing the highlightthickness
password_ent.grid(row=1, column=0, pady = 2.5)

login_btn = ttk.Button(left_frame, text = "Sign In", style = 'TButton', command= check_password, padding=(-5, -20))
login_btn.grid(row=2, column=0, pady = 5)


# Running the program
user_name_ent.focus_set()
window.mainloop()

