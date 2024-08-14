
from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import font
from tkinter import messagebox


def check_password():
	user_name = user_name_ent.get()
	password = password_ent.get()

	if user_name == "Test1" and password == "1234":
		messagebox.showinfo("Login", "Login successful!")
	else:
		messagebox.showerror("Login", "Invalid username or password")
		password_ent.delete(0, tk.END)

window = tk.Tk()
window.title("Narcotics Management System")

window.resizable(False, False) #This stops the user from resizing the screen for the login ui

#Window setting
w = 550 
h = 500

window_width = window.winfo_screenwidth()  # screen centering code from https://stackoverflow.com/questions/14910858/how-to-specify-where-a-tkinter-window-opens
window_height = window.winfo_screenheight()

x = (window_width/2) - (w/2)
y = (window_height/2) - (h/2)

window.geometry('%dx%d+%d+%d' % (w, h, x, y))

#end of window settin

# Define a font
login_ui_font = font.Font(family="Inter", size=36, weight="bold")

login_lbl = tk.Label(text = "Login", relief = RAISED, width = 0, font = login_ui_font) #login label
login_lbl.pack(pady=50)


user_name_ent = tk.Entry(fg = "black", bg = "white", width = 30) #user name entry widget
user_name_ent.pack(pady=12)


password_ent = tk.Entry(fg = "black", bg = "white", width = 30, show="*") #password name entry widget
password_ent.pack(pady=12)


login_btn = ttk.Button(text = "Sign In", style='TButton', command=check_password)
login_btn.pack()


#Running the program

window.mainloop()

