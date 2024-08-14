#main page, will be full screen, not reziable
from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import font
from tkinter import messagebox

window = tk.Tk()
window.title("Narcotics Management System")

window.resizable(False, False) #This stops the user from resizing the screen for the login ui

#Window setting
w = window.winfo_screenwidth() 
h = window.winfo_screenheight()

#end of window setting

# Define a font

#Running the program

window.mainloop()

