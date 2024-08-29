def open_main_page():
	#main page, will be full screen, not reziable
	import tkinter as tk
	from tkinter import ttk, font, messagebox
	from meds import narc_list, find_quantity # importing the list of narcs and the function for qtyfrom the file meds.py

	import sqlite3 #To use database
	con = sqlite3.connect("narcotics_database.db") #Connecting our databse
	cur = con.cursor() # Create a cursor

	main_page_window = tk.Tk()
	main_page_window.title("Narcotics Management System")

	#Window setting	
	w = main_page_window.winfo_screenwidth() 
	h = main_page_window.winfo_screenheight()

	main_page_window.geometry('%dx%d' % (w, h))

	#main_page_window.state('zoomed') #setting window to full screen before stopping the resizable to false

	main_page_window.resizable(False, False) #This stops the user from resizing the screen for the login ui


	#end of main_page_window setting
	def search(search):
		search_meds_by_upc()
	main_page_window.bind('<Return>', search)


	def search_meds_by_upc(): #function to find the meds in meds.py
		upc = upc_ent.get()
		if upc in narc_list:
			med_info = narc_list[upc]
			name_lbl_output.config(text = med_info[0])
			din__med_output.config(text = med_info[1])
			strength_lbl_output.config(text = med_info[2])
			drug_form_output.config(text = med_info[3])
			pack_med_output.config(text = med_info[4])
			qty_med_output.config(text = find_quantity(upc))

		else:
			messagebox.showerror("Error", "UPC not found")


	# Define a font for the Entry widget
	font = font.Font(family="Inter", size=16, weight="normal")

	upc_ent = tk.Entry(main_page_window, text = "Enter upc", fg = "black", bg = "white", width = 70, font = font, justify="center") #upc entry widget
	upc_ent.pack(pady = 20)
	upc_ent.focus()

	search_btn = ttk.Button(main_page_window, text = "Search", style='TButton', command=search_meds_by_upc)
	search_btn.pack()

	name__med_lbl = tk.Label(main_page_window, text = "name", bg = "white", fg = "black", width = 20, font = font)
	name__med_lbl.pack(pady = 10)

	name_lbl_output = tk.Label(main_page_window, bg = "white", fg = "red", width = 70, font = font)
	name_lbl_output.pack() # this will be the label to test the output when we enter the upc

	din__med_lbl = tk.Label(main_page_window, text = "din", bg = "white", fg = "black", width = 20, font = font)
	din__med_lbl.pack(pady = 10)

	din__med_output = tk.Label(main_page_window, bg = "white", fg = "red", width = 70, font = font)
	din__med_output.pack()

	strength__med_lbl = tk.Label(main_page_window, text = "strength", bg = "white", fg = "black", width = 20, font = font)
	strength__med_lbl.pack(pady = 10)

	strength_lbl_output = tk.Label(main_page_window, bg = "white", fg = "red", width = 70, font = font)
	strength_lbl_output.pack()

	drug_form_lbl = tk.Label(main_page_window, text = "Form", bg = "white", fg = "black", width = 20, font = font)
	drug_form_lbl.pack(pady = 10)

	drug_form_output = tk.Label(main_page_window, bg = "white", fg = "red", width = 70, font = font)
	drug_form_output.pack()

	pack_med_lbl = tk.Label(main_page_window, text = "pack size", bg = "white", fg = "black", width = 20, font = font)
	pack_med_lbl.pack(pady = 10)

	pack_med_output = tk.Label(main_page_window, bg = "white", fg = "red", width = 70, font = font)
	pack_med_output.pack()

	qty_med_lbl = tk.Label(main_page_window, text = "Qty on hand", bg = "white", fg = "black", width = 20, font = font)
	qty_med_lbl.pack(pady = 10)

	qty_med_output = tk.Label(main_page_window, bg = "white", fg = "red", width = 70, font = font)
	qty_med_output.pack()



	#Running the program

	main_page_window.mainloop()
