import sqlite3
con = sqlite3.connect("tutorial.db")

from tkinter import *
from tkinter import ttk
import tkinter as tk

window = tk.Tk()

greeting = tk.Label(text="Hello, Tkinter")

greeting.pack()

window.mainloop()

narc_list = {"upc":["name", "strength" "din",]}

