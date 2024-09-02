def open_main_page():
	#main page, will be full screen, not reziable
	import tkinter as tk
	from tkinter import ttk, font, messagebox
	from meds import narc_list, find_quantity, find_narcs_upc, find_narcs_din # importing the list of narcs and the function for qtyfrom the file meds.py

	import sqlite3 #To use database
	con = sqlite3.connect("narcotics_database.db") #Connecting our databse
	cur = con.cursor() # Create a cursor

	main_page_window = tk.Tk()
	main_page_window.title("Narc Recon")

	#Window setting
	w = main_page_window.winfo_screenwidth() 
	h = main_page_window.winfo_screenheight()

	main_page_window.geometry('%dx%d' % (w, h))

	#main_page_window.state('zoomed') #setting window to full screen before stopping the resizable to false

	main_page_window.resizable(False, False) #This stops the user from resizing the screen for the login ui


	#end of main_page_window setting
	def search(search):
		search_narcs()
	main_page_window.bind('<Return>', search)


	def search_narcs(): #function to find the meds in meds.py
		search_input = meds_ent.get()
		if len(search_input) == 12:
			tup = find_narcs_upc(search_input)
		elif len(search_input) == 8:
			tup = find_narcs_din(search_input)
		else:
			messagebox.showerror("Error", "Drug not found")
			return

		if len(tup) == 1:
#There will always be only 1 tuple in the list when looking with upc, will but another constraint, "if len(din) > 1" when lookin with din
			name_lbl_output.config(text = tup[0][1])
			din__med_output.config(text = tup[0][0])
			strength_lbl_output.config(text = tup[0][4])
			drug_form_output.config(text = tup[0][5])
			pack_med_output.config(text = tup[0][6])
			qty_med_output.config(text = find_quantity(search_input)) #functions from the meds file to find the qty directly from the database
		elif len(tup) > 1:
			#I will output a choice for which pack size they want
			choice_windw = tk.Toplevel(main_page_window)
			choice_windw.title("Choose Pack Size")
			#Creating the place and the size of the window
			w = 400 
			h = 100

			window_width = choice_windw.winfo_screenwidth()  # screen centering code from https://stackoverflow.com/questions/14910858/how-to-specify-where-a-tkinter-window-opens
			window_height = choice_windw.winfo_screenheight()

			x = (window_width/2) - (w/2)
			y = (window_height/2) - (h/0.1)
			choice_windw.geometry('%dx%d+%d+%d' % (w, h, x, y))

			choice_windw.wm_attributes("-topmost", True) #Will keep the choice_windw on top
			tk.Label(choice_windw, text="Choose the pack size:").pack()

			pack_size = tk.StringVar()
			pack_size_dropdown = ttk.Combobox(choice_windw, textvariable=pack_size)
			pack_size_dropdown['values'] = [f"{item[6]} units - {item[4]} {item[5]}" for item in tup]
			pack_size_dropdown.pack()
		else:
			messagebox.showerror("Error", "Drug not found")


	# Define a font for the Entry widget
	font = font.Font(family="Inter", size=16, weight="normal")

	meds_ent = tk.Entry(main_page_window, text = "Enter upc or din", fg = "black", bg = "white", width = 70, font = font, justify="center") #upc entry widget
	meds_ent.pack(pady = 20)
	meds_ent.focus()

	search_btn = ttk.Button(main_page_window, text = "Search", style='TButton', command=search_narcs)
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
