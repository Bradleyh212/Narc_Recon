
from tkinter import *
from tkinter import ttk
import tkinter as tk

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

for i in range(3):
	window.columnconfigure(i, weight=1, minsize=75)
	window.rowconfigure(i, weight=1, minsize=50)

	for j in range(3):
		frame = tk.Frame(
			master = window,
			relief = tk.RAISED,
			borderwidth = 1,
			padx = 75

			)
		frame.grid(row = i, column = j, padx = 2)
		label = tk.Label(master = frame, text = f"{i} x {j}")
		label.pack()



"""
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
"""

#Runing the program

window.mainloop()
