import sqlite3
con = sqlite3.connect("tutorial.db")

from tkinter import *
from tkinter import ttk
import tkinter as tk

window = tk.Tk()
window.title("Narcotics Management System")
window.geometry('800x600')

greeting = tk.Label(
	text="Narc Management System",
	foreground = "white", # Set the text color
	background = "black", # Set the text background color
	width = 20,
	height = 1

	)

#user_name = 

login = tk.Button(
	text = "Sign In",
	bg = "orange",
	fg = "black"

	)

greeting.pack()


narc_list = {"upc":["Sandoz-Amphetamine Xr", "5mg", "02457288", "ER Cap", "100"]} #example of first medication

print(narc_list["upc"])




#Runing the program

window.mainloop()
