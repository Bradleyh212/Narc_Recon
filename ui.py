
from tkinter import *
from tkinter import ttk
import tkinter as tk

window = tk.Tk()
window.title("Narcotics Management System")
window.geometry('800x600')

greeting = tk.Label(
	text="Welcome back",
	foreground = "white", # Set the text color
	#background = "black", # Set the text background color
	width = 20,
	height = 1
	)

user_name = tk.Entry(
	fg = "black",
	bg = "white",
	width = 30	
)

password = tk.Entry(
	fg = "black",
	bg = "white",
	width = 30	
	)


login = tk.Button(
	text = "Sign In",
	bg = "black",
	fg = "white",
	width = 20,
	height = 15
	)

greeting.pack()

user_name.pack()

password.pack()

login.pack()


#Runing the program

window.mainloop()
