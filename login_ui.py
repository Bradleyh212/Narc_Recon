import tkinter as tk
from tkinter import ttk, font, messagebox
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
		password_ent.delete(0, tk.END)
		login_try()
		print(password_count)
		if password_count >= 3:
			window.destroy()


window = tk.Tk()
window.title("Narc Recon")

#Window setting
window.resizable(False, False) #This stops the user from resizing the screen for the login ui

def sign_in(sign_in):
		check_password()
window.bind('<Return>', sign_in)


w = 550 
h = 500

window_width = window.winfo_screenwidth()  # screen centering code from https://stackoverflow.com/questions/14910858/how-to-specify-where-a-tkinter-window-opens
window_height = window.winfo_screenheight()

x = (window_width/2) - (w/2)
y = (window_height/2) - (h/2)

window.geometry('%dx%d+%d+%d' % (w, h, x, y))

#end of window setting

# Define a font
login_ui_font = font.Font(family="Inter", size=36, weight="bold")

login_lbl = tk.Label(text = "Login", relief = tk.RAISED, width = 0, font = login_ui_font) #login label
login_lbl.pack(pady=50)


user_name_ent = tk.Entry(fg = "black", bg = "white", width = 30) #user name entry widget
user_name_ent.pack(pady=12)


password_ent = tk.Entry(fg = "black", bg = "white", width = 30, show="*") #password name entry widget
password_ent.pack(pady=12)


login_btn = ttk.Button(text = "Sign In", style='TButton', command=check_password)
login_btn.pack()


#Running the program

window.mainloop()

