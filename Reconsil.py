import sqlite3
con = sqlite3.connect("tutorial.db")

from tkinter import *
from tkinter import ttk
import tkinter as tk

window = tk.Tk()

greeting = tk.Label(text="Hello, Tkinter")

greeting.pack()

#window.mainloop()

narc_list = {"upc":["Sandoz-Amphetamine Xr", "5mg", "02457288", "ER Cap", "100"]} #example of first medication

print(narc_list["upc"])

