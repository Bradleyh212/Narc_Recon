#def open_main_page
#main page, will be full screen, not reziable
import tkinter as tk
from tkinter import ttk, font, messagebox
from meds import narc_list, find_quantity, find_narcs_upc, find_narcs_din 
from other_functions import show_narcs_table
from receiving import open_receiving

import sqlite3 #To use database
con = sqlite3.connect("narcotics_database.db") #Connecting our databse
cur = con.cursor() # Create a cursor

main_page_window = tk.Tk()
main_page_window.title("Narc Recon")

#Window setting
w = main_page_window.winfo_screenwidth() 
h = main_page_window.winfo_screenheight()
main_page_window.geometry('%dx%d' % (w, h))


#main_page_window.resizable(False, False) #This stops the user from resizing the screen for the login ui

# Creating the fonts
header_font = font.Font(family="Inter", size=70, weight="normal")
font = font.Font(family="Inter", size=16, weight="normal") # Define a font for the Entry widget

# Creating the frames
header_frame = tk.Frame(main_page_window, width = w, height = 100, bg = "blue") # using the bg to see the frames
header_frame.grid(row = 0, column = 0)
header_frame.grid_propagate(False) # Prevent the header frame from resizing based on its content

body_frame = tk.Frame(main_page_window, width = w, height = h - 100, bg = "red") # using the bg to see the frames
body_frame.grid(row = 1, column = 0, pady = 30)
body_frame.grid_propagate(False) # Prevent the body frame from resizing based on its content

left_body_frame = tk.Frame(body_frame, width = w-500, height = h, bg = "orange")
left_body_frame.grid(row = 0, column = 0)
left_body_frame.grid_propagate(False) # Prevent the left_body_frame frame from resizing based on its content


right_body_frame = tk.Frame(body_frame, width = 500, height = h, bg = "green")
right_body_frame.grid(row = 0, column = 1)
right_body_frame.grid_propagate(False) # Prevent the right_body_frame frame from resizing based on its content

nav_frame = tk.Frame(header_frame, width = 450, height = 100, bg = "purple")
nav_frame.grid(row = 0, column = 1, padx = 550)
nav_frame.grid_propagate(False) # Prevent the nav frame from resizing based on its content


def refresh_page():
	global meds_ent, name_lbl_output, din__med_output, strength_lbl_output, drug_form_output, pack_med_output, qty_med_output, remove_qty_ent

	page_title = tk.Label(header_frame, text = "INVENTORY", fg = "white", bg = "black", font = header_font)
	page_title.grid(row = 0, column = 0, sticky = "w", padx = 30)

	receiving_btn = ttk.Button(nav_frame, text = "RECEIVING", style='TButton', command = lambda : [main_page_window.withdraw(), open_receiving()])
	receiving_btn.grid(row = 0, column = 0, padx = 30, pady = 40) #Used the lambda key word to use 2 functions in 1 button

	#This will be open another page to do the narc reconsiliation where we set the quantity on hand
	reconsiliation_btn = ttk.Button(nav_frame, text = "RECONSILIATION", style='TButton') 
	reconsiliation_btn.grid(row = 0, column = 1)

	log_off_btn = ttk.Button(nav_frame, text = "LOGOUT", style='TButton', command = lambda : [main_page_window.destroy()]) 
	log_off_btn.grid(row = 0, column = 2, padx = 30, ipady=0, ipadx=0)

	meds_ent = tk.Entry(left_body_frame, text = "Enter upc or din", fg = "white", bg = "black", width = 70, font = font, justify="center") #upc entry widget
	meds_ent.grid(row = 0, column = 0, pady = 20, padx = ((w-500)-70)/4)
	meds_ent.focus()

	'''
	search_btn = ttk.Button(main_page_window, text = "Search", style='TButton', command=search_narcs)
	search_btn.pack()

	name__med_lbl = tk.Label(main_page_window, text = "name", bg = "black", fg = "white", width = 20, font = font)
	name__med_lbl.pack(pady = 10)

	name_lbl_output = tk.Label(main_page_window, bg = "black", fg = "red", width = 70, font = font)
	name_lbl_output.pack() # this will be the label to test the output when we enter the upc

	din__med_lbl = tk.Label(main_page_window, text = "din", bg = "black", fg = "white", width = 20, font = font)
	din__med_lbl.pack(pady = 10)

	din__med_output = tk.Label(main_page_window, bg = "black", fg = "red", width = 70, font = font)
	din__med_output.pack()

	strength__med_lbl = tk.Label(main_page_window, text = "strength", bg = "black", fg = "white", width = 20, font = font)
	strength__med_lbl.pack(pady = 10)

	strength_lbl_output = tk.Label(main_page_window, bg = "black", fg = "red", width = 70, font = font)
	strength_lbl_output.pack()

	drug_form_lbl = tk.Label(main_page_window, text = "Form", bg = "black", fg = "white", width = 20, font = font)
	drug_form_lbl.pack(pady = 10)
 
	drug_form_output = tk.Label(main_page_window, bg = "black", fg = "red", width = 70, font = font)
	drug_form_output.pack()

	pack_med_lbl = tk.Label(main_page_window, text = "pack size", bg = "black", fg = "white", width = 20, font = font)
	pack_med_lbl.pack(pady = 10)

	pack_med_output = tk.Label(main_page_window, bg = "black", fg = "red", width = 70, font = font)
	pack_med_output.pack()

	qty_med_lbl = tk.Label(main_page_window, text = "Qty on hand", bg = "black", fg = "white", width = 20, font = font)
	qty_med_lbl.pack(pady = 10)

	qty_med_output = tk.Label(main_page_window, bg = "black", fg = "red", width = 70, font = font)
	qty_med_output.pack()

	remove_qty_ent = ttk.Entry(main_page_window, text = "Fill")
	remove_qty_ent.pack()
	remove_qty_btn = ttk.Button(main_page_window, text = "Fill", style='TButton')
	remove_qty_btn.pack()

	'''



#Running the program
refresh_page()
main_page_window.mainloop()