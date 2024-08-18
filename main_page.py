#main page, will be full screen, not reziable
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
from meds import narc_list 

main_page_window = tk.Tk()
main_page_window.title("Narcotics Management System")

#Window setting
main_page_window.state('zoomed') #setting window to full screen before stopping the resizable to false

#main_page_window.resizable(False, False) #This stops the user from resizing the screen for the login ui


#end of main_page_window setting

def search_meds():
	upc = upc_ent.get()
	if upc in narc_list:
		med_info = narc_list[upc]
		name_lbl_output.config(text = med_info[0])


# Define a font for the Entry widget
font = font.Font(family="Inter", size=16, weight="normal")

upc_ent = tk.Entry(fg = "black", bg = "white", width = 70, font = font) #upc entry widget
upc_ent.pack(pady = 20)

search_btn = ttk.Button(text = "Search", style='TButton', command=search_meds)
search_btn.pack()



name_lbl_output = tk.Label(text = "Allo", bg = "white", fg = "red", width = 70, font = font)
name_lbl_output.pack() # this will be the label to test the output when we enter the upc






#Running the program

main_page_window.mainloop()
