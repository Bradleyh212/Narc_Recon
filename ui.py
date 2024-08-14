
from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import font

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

window.columnconfigure(0, minsize=400)
window.rowconfigure(0, minsize=250)

# Define a font
login_ui_font = font.Font(family="Inter", size=18, weight="bold")

login_lbl = tk.Label(text = "Login", relief = RAISED, width = 30, font = login_ui_font) #login label
login_lbl.grid(row=0, column=0)


user_name = tk.Entry(fg = "black", bg = "white", width = 30) #user name entry widget
user_name.grid(row = 2, column = 0)


password = tk.Entry(fg = "black", bg = "white", width = 30) #password name entry widget
password.grid(row = 3, column = 0)


login = ttk.Button(text = "Sign In", style='TButton')
login.grid(row = 4, column = 0)


#Running the program

window.mainloop()
