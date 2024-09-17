def open_reconciliation_page():
	#main page, will be full screen, not reziable
	import tkinter as tk
	from tkinter import ttk, font, messagebox
	from meds import narc_list, find_quantity, find_narcs_upc, find_narcs_din 
	from other_functions import show_narcs_table
	from main_page import open_main_page
	from receiving import open_receiving

	import sqlite3 #To use database
	con = sqlite3.connect("narcotics_database.db") #Connecting our databse
	cur = con.cursor() # Create a cursor

	reconciliation_window = tk.Tk()
	reconciliation_window.title("Narc Recon")

	#Window setting
	w = reconciliation_window.winfo_screenwidth() 
	h = reconciliation_window.winfo_screenheight()
	reconciliation_window.geometry('%dx%d' % (w, h))

	main_background_color = "#3B4B59"

	reconciliation_window.resizable(False, False) #This stops the user from resizing the screen for the login ui



	def search(search):
		search_narcs()
	reconciliation_window.bind('<Return>', search)

	def search_narcs(): #function to find the meds in meds.py
		meds_ent.focus_set()
		search_input = meds_ent.get()
		meds_ent.delete(0, "end")
		if len(search_input) == 12:
			tup = find_narcs_upc(search_input)
		elif len(search_input) == 8:
			tup = find_narcs_din(search_input)
		else:
			messagebox.showerror("Error", "Drug not found")
			name_lbl_output.config(text = "")
			din__med_output.config(text = "")
			strength_lbl_output.config(text = "")
			drug_form_output.config(text = "")
			pack_med_output.config(text = "")
			qty_med_output.config(text = "") 
			remove_qty_ent.focus_set() #This brings the focus out of the med entry
			meds_ent.focus_set() # This brings back the focus to med entry
			return

		if len(tup) == 1:
	#There will always be only 1 tuple in the list when looking with upc, will but another constraint, "if len(din) > 1" when lookin with din
			name_lbl_output.config(text = tup[0][1])
			din__med_output.config(text = tup[0][0])
			strength_lbl_output.config(text = tup[0][4])
			drug_form_output.config(text = tup[0][5])
			pack_med_output.config(text = tup[0][6])
			qty_med_output.config(text = find_quantity(tup[0][3])) #functions from the meds file to find the qty directly from the database
		elif len(tup) > 1:
			#I will output a choice for which pack size they want
			choice_windw = tk.Toplevel(reconciliation_window)
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

			def on_select_pack_size():
				global selected_pack
				selected_index = pack_size_dropdown.current()
				selected_pack = tup[selected_index]
				name_lbl_output.config(text=selected_pack[1])
				din__med_output.config(text=selected_pack[0])
				strength_lbl_output.config(text=selected_pack[4])
				drug_form_output.config(text=selected_pack[5])
				pack_med_output.config(text=selected_pack[6])
				qty_med_output.config(text=find_quantity(selected_pack[3]))
				print(selected_pack)
				choice_windw.destroy()

			select_btn = tk.Button(choice_windw, text="Select", command=on_select_pack_size)
			select_btn.pack()
		else:
			messagebox.showerror("Error", "Drug not found")
			name_lbl_output.config(text = "")
			din__med_output.config(text = "")
			strength_lbl_output.config(text = "")
			drug_form_output.config(text = "")
			pack_med_output.config(text = "")
			qty_med_output.config(text = "") 
			remove_qty_ent.focus_set() #This brings the focus out of the med entry
			meds_ent.focus_set() # This brings back the focus to med entry


	# Creating the fonts
	header_font = font.Font(family="Inter", size=70, weight="normal")
	font = font.Font(family="Inter", size=30, weight="normal") # Define a font for the Entry widget
	# The size of the text changes the height of the Entry widget

	# Creating the frames
	header_frame = tk.Frame(reconciliation_window, width = w, height = 100, bg = main_background_color) # using the bg to see the frames
	header_frame.grid(row = 0, column = 0)
	header_frame.grid_propagate(False) # Prevent the header frame from resizing based on its content

	body_frame = tk.Frame(reconciliation_window, width = w, height = h - 100, bg = main_background_color) # using the bg to see the frames
	body_frame.grid(row = 1, column = 0, pady = 30)
	body_frame.grid_propagate(False) # Prevent the body frame from resizing based on its content

	left_body_frame = tk.Frame(body_frame, width = w-500, height = h, bg = main_background_color)
	left_body_frame.grid(row = 0, column = 0)
	left_body_frame.grid_propagate(False) # Prevent the left_body_frame frame from resizing based on its content

	search_frame = tk.Frame(left_body_frame, width = w-500, height = 150, bg = main_background_color)
	search_frame.grid(row = 0, column = 0)
	search_frame.grid_propagate(False)

	name_din_frame = tk.Frame(left_body_frame, width = w-500, height = 150, bg = main_background_color)
	name_din_frame.grid(row = 1, column = 0, pady = 30)
	name_din_frame.grid_propagate(False)

	strength_form_frame = tk.Frame(left_body_frame, width = w-500, height = 150, bg = main_background_color)
	strength_form_frame.grid(row = 2, column = 0, pady = 30)
	strength_form_frame.grid_propagate(False)

	pack_med_frame = tk.Frame(left_body_frame, width = w-500, height = 150, bg = main_background_color)
	pack_med_frame.grid(row = 3, column = 0, pady = 30)
	pack_med_frame.grid_propagate(False)

	right_body_frame = tk.Frame(body_frame, width = 500, height = h, bg = main_background_color, bd = 5, relief = "raised")
	right_body_frame.grid(row = 0, column = 1)
	right_body_frame.grid_propagate(False)


	nav_frame = tk.Frame(header_frame, width = 450, height = 100, bg = main_background_color)
	nav_frame.grid(row = 0, column = 1, padx = 550)
	nav_frame.grid_propagate(False) # Prevent the nav frame from resizing based on its content

	picture_frame = tk.Frame(right_body_frame, width = 200, height = 200, bg = "Black")
	picture_frame.grid(padx = 150, pady = 100)
	picture_frame.grid_propagate(False) # Prevent the picture frame from resizing based on its content


	def on_entry_click(event): # When the med entry widget is clicked remove the text
		"""Remove placeholder when entry is clicked."""
		if meds_ent.get() == 'Enter DIN or UPC':
			meds_ent.delete(0, "end")  # Delete all the text in the entry

	def on_focusout(event): # When the med entry widget is un-clicked add the text back
		"""Re-add placeholder if entry is empty when focus is lost."""
		if meds_ent.get() == '':
			meds_ent.insert(0, 'Enter DIN or UPC')

	def refresh_page():
		global meds_ent, name_lbl_output, din__med_output, strength_lbl_output, drug_form_output, pack_med_output, qty_med_output, remove_qty_ent

		page_title = tk.Label(header_frame, text = "RECONCILIATION", fg = "white", font = header_font)
		page_title.grid(row = 0, column = 0, sticky = "w", padx = 30)

		home_btn = ttk.Button(nav_frame, text = "HOME", style='TButton', command = lambda : [reconciliation_window.destroy(), open_main_page()], padding=(-5, -20))
		home_btn.grid(row = 0, column = 0, padx = 6, pady = 40) #Used the lambda key word to use 2 functions in 1 button

		receiving_btn = ttk.Button(nav_frame, text = "RECEIVING", style='TButton', command = lambda : [reconciliation_window.destroy(), open_receiving()], padding=(-5, -20))
		receiving_btn.grid(row = 0, column = 1, padx = 6) #Used the lambda key word to use 2 functions in 1 button

		#This will be open another page to do the narc reconsiliation where we set the quantity on hand
		reconsiliation_btn = ttk.Button(nav_frame, text = "RECONSILIATION", style='TButton', padding=(-5, -20))
		reconsiliation_btn.grid(row = 0, column = 2, padx = 6)

		log_off_btn = ttk.Button(nav_frame, text = "LOGOUT", style='TButton', command = lambda : [reconciliation_window.destroy()], padding=(-5, -20)) 
		log_off_btn.grid(row = 0, column = 3, padx = 6)



		meds_ent = ttk.Entry(search_frame, text = "Enter upc or din", width = 35, font = font, justify="center") #upc entry widget
		meds_ent.grid(row = 0, column = 0, padx = 30, pady = 50)
		meds_ent.focus()
		meds_ent.bind('<FocusIn>', on_entry_click)
		meds_ent.bind('<FocusOut>', on_focusout)

		search_btn = ttk.Button(search_frame, text = "SEARCH", style='TButton', command=search_narcs, padding=(-5, -20)) #The padding is to remove the space around the button
		search_btn.grid(row = 0, column = 1)

		name_lbl_output = tk.Label(name_din_frame, bg = "black", fg = "White", width = 30, font = font)
		name_lbl_output.grid(row = 0, column = 0, padx = 30) # this will be the label to see the output when we enter the upc or din

		din__med_output = tk.Label(name_din_frame, bg = "black", fg = "red", width = 12, font = font)
		din__med_output.grid(row = 0, column = 1, padx =75, pady = 30)

		strength_lbl_output = tk.Label(strength_form_frame, bg = "black", fg = "red", width = 30, font = font)
		strength_lbl_output.grid(row = 0, column = 0, padx = 30)

		drug_form_output = tk.Label(strength_form_frame, bg = "black", fg = "red", width = 12, font = font)
		drug_form_output.grid(row = 0, column = 1, padx =75, pady = 30)


		pack_med_lbl = tk.Label(pack_med_frame, bg = "black", text = "PACK SIZE", fg = "white", width = 15, font = font)
		pack_med_lbl.grid(row = 0, column = 0, padx = 30, pady = 30)
		pack_med_output = tk.Label(pack_med_frame, bg = "black", fg = "blue", width = 15, font = font)
		pack_med_output.grid(row = 0, column = 1)


		med_picture = tk.Label(picture_frame, text = "PICTURE", bg = "black", fg = "white", width = 10, font = font)
		med_picture.grid(pady = 75)

		qty_med_lbl = tk.Label(right_body_frame, text = "ON HAND", bg = "black", fg = "white", width = 10, font = font)
		qty_med_lbl.grid(row = 1)

		qty_med_output = tk.Label(right_body_frame, bg = "black", fg = "red", width = 10, font = font)
		qty_med_output.grid(row = 2)


		remove_qty_ent = ttk.Entry(right_body_frame, text = "FILL", font = font, width = 8)
		remove_qty_ent.grid(row = 3, pady = 30)

		remove_qty_btn = ttk.Button(right_body_frame, text = "Fill", style='TButton', padding=(-5, -20))
		remove_qty_btn.grid(row = 4)



	#Running the program
	refresh_page()
	reconciliation_window.mainloop()