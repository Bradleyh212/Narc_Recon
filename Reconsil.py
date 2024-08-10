
from tkinter import *
from tkinter import ttk
import tkinter as tk

window = tk.Tk()
window.title("Narcotics Management System")
window.geometry('800x600')

frame = tk.Frame(master=window, width=200, height=200, bg="white")
frame.pack()

greeting = tk.Label(
	master=frame,
	text="Welcome back",
	foreground = "white", # Set the text color
	#background = "black", # Set the text background color
	width = 20,
	height = 1
	)

greeting.pack()


user_name = tk.Entry(
	master=frame,
	fg = "black",
	bg = "white",
	width = 30	
)

user_name.pack()


password = tk.Entry(
	master=frame,
	fg = "black",
	bg = "white",
	width = 30	
	)

password.pack()


login = ttk.Button(
	master=frame,
	text = "Sign In",
	style='TButton',
	)

login.pack()


#Runing the program

window.mainloop()
