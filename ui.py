
from tkinter import *
from tkinter import ttk
import tkinter as tk

window = tk.Tk()
window.title("Narcotics Management System")
window.geometry('800x600')

frame = tk.Frame(master=window, width=200, height=200)

greeting = tk.Label(
	text="Welcome back",
	foreground = "white", # Set the text color
	#background = "black", # Set the text background color
	width = 20,
	height = 1
	)

greeting.pack()


user_name = tk.Entry(
	fg = "black",
	bg = "white",
	width = 30	
)

user_name.pack()


password = tk.Entry(
	fg = "black",
	bg = "white",
	width = 30	
	)

password.pack()


login = ttk.Button(
	text = "Sign In",
	style='TButton',
	)

login.pack()


#Runing the program

window.mainloop()
