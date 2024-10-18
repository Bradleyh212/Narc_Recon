####################
# Need to add a way to print the audit_log based on time
####################
def open_reconciliation_page():
	# Reconsilation page setup, full-screen, non-resizable window
	import tkinter as tk
	from tkinter import ttk, font, messagebox, simpledialog
	from main_page import open_main_page
	from receiving import open_receiving
	from audit_log_database import add_to_audit_log, show_audit_log, list_user_id
	from sqlite3_functions import find_narcs_upc, find_narcs_din, find_quantity, show_narcs_table, find_quantity_din
	import sqlite3

	import sqlite3 #To use database
	# Connect to SQLite database
	con = sqlite3.connect("narcotics_database.db")
	cur = con.cursor()

	# Initialize the main Tkinter window
	reconciliation_window = tk.Tk()
	reconciliation_window.title("Narc Recon")

	# Set window size to full screen
	w = reconciliation_window.winfo_screenwidth()
	h = reconciliation_window.winfo_screenheight()
	reconciliation_window.geometry(f'{w}x{h}')

	# Set background color and disable resizing
	main_background_color = "#3B4B59"
	reconciliation_window.configure(bg=main_background_color)
	reconciliation_window.resizable(False, False)

	# Creating the fonts
	header_font = font.Font(family="Inter", size=70, weight="normal")
	font = font.Font(family="Inter", size=30, weight="normal") # Define a font for the Entry widget
	# The size of the text changes the height of the Entry widget

	# Frame setup: header, body, and navigation
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
	nav_frame.grid(row = 0, column = 1, padx = 390)
	nav_frame.grid_propagate(False) # Prevent the nav frame from resizing based on its content

	picture_frame = tk.Frame(right_body_frame, width = 200, height = 200, bg = "Black")
	picture_frame.grid(padx = 150, pady = 100)
	picture_frame.grid_propagate(False) # Prevent the picture frame from resizing based on its content

	def refresh_page():
		global meds_ent, name_lbl_output, din__med_output, strength_lbl_output, drug_form_output, pack_med_output, qty_med_output, set_qty_ent

		page_title = tk.Label(header_frame, text = "RECONCILIATION", fg = "white", font = header_font)
		page_title.grid(row = 0, column = 0, sticky = "w", padx = 30)

		home_btn = ttk.Button(nav_frame, text = "HOME", style='TButton', command = lambda : [reconciliation_window.destroy(), open_main_page()], padding=(-5, -20))
		home_btn.grid(row = 0, column = 0, padx = 6, pady = 40) #Used the lambda key word to use 2 functions in 1 button

		receiving_btn = ttk.Button(nav_frame, text = "RECEIVING", style='TButton', command = lambda : [reconciliation_window.destroy(), open_receiving()], padding=(-5, -20))
		receiving_btn.grid(row = 0, column = 1, padx = 6) #Used the lambda key word to use 2 functions in 1 button

		#This will be open another page to do the narc reconciliation where we set the quantity on hand
		reconciliation_btn = ttk.Button(nav_frame, text = "RECONCILIATION", style='TButton', padding=(-5, -20))
		reconciliation_btn.grid(row = 0, column = 2, padx = 6)

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

		set_qty_ent = ttk.Entry(right_body_frame, font = font, width = 8)
		set_qty_ent.grid(row = 3, pady = 30)

		add_btn = ttk.Button(right_body_frame, text = "SET QUANTITY", style='TButton', padding=(-5, -20), command=lambda: set_quantity(set_qty_ent.get(), search_input))
		add_btn.grid(row = 4)

	def search(search):
		search_narcs()
	reconciliation_window.bind('<Return>', search)

	# Function to request a valid user ID
	def ask_user_id():
		while True:
			user_id = simpledialog.askstring("Input", "Please enter your user ID:", parent=reconciliation_window)
			if user_id is None:  # Cancel or close
				messagebox.showinfo("Cancelled", "Operation cancelled")
				return None
			if user_id in list_user_id:  # Valid user ID
				return user_id
			else:
				messagebox.showerror("Error", "Please enter a valid user ID")

	def set_quantity(amount, input): #This is the function to set the new quantity when doing the reconsiliation
		if len(input) == 12:
			din = find_narcs_upc(input)[0][0]
			user_id = ask_user_id()
			if user_id not in list_user_id: # In case the user press the cancel button
				return
		elif len(input) == 8:
			din = input
			user_id = ask_user_id()
			if user_id not in list_user_id: # In case the user press the cancel button
				return
		else:
			messagebox.showerror("Error", "Please enter a valid DIN or UPC")
			set_qty_ent.focus()
			meds_ent.focus()
			return

		if int(amount) < 0:
			messagebox.showerror("Error", "PLease add a positive integer")
			set_qty_ent.focus()
			meds_ent.focus()
			return

		# Perform database update and refresh UI
		current_amount = find_quantity_din(din)
		cur.execute("UPDATE narcs SET quantity = ? WHERE din = ?", (amount, din))
		con.commit()

		show_narcs_table()  # Refresh the narcotic table view
		refresh_page()
		search_narc_din(din)

		# Log the action to the audit log
		add_to_audit_log(din, current_amount, user_id)
		show_audit_log()


	def search_narc(upc): #function to find the meds in meds.py when refreshing the page
		tup = find_narcs_upc(upc)
		name_lbl_output.config(text = tup[0][1])
		din__med_output.config(text = tup[0][0])
		strength_lbl_output.config(text = tup[0][4])
		drug_form_output.config(text = tup[0][5])
		pack_med_output.config(text = tup[0][6])
		qty_med_output.config(text = find_quantity(tup[0][3])) #functions from the meds file to find the qty directly from the database

	def search_narc_din(din): #function to find the meds in meds.py when refreshing the page
		tup = find_narcs_din(din)
		name_lbl_output.config(text = tup[0][1])
		din__med_output.config(text = tup[0][0])
		strength_lbl_output.config(text = tup[0][4])
		drug_form_output.config(text = tup[0][5])
		pack_med_output.config(text = tup[0][6])
		qty_med_output.config(text = find_quantity(tup[0][3])) #functions from the meds file to find the qty directly from the database

	def search_narcs():
		global search_input
		search_input = meds_ent.get()  # Get the input from entry field
		meds_ent.delete(0, "end")  # Clear the entry field

		if len(search_input) == 12:
			tup = find_narcs_upc(search_input)
		elif len(search_input) == 8:
			tup = find_narcs_din(search_input)
		else:
			messagebox.showerror("Error", "Drug not found")
			set_qty_ent.focus()
			meds_ent.focus()
			clear_display_fields()
			return

		if len(tup) == 1:  # Single result, display information
			display_narcotic_info(tup[0])
		elif len(tup) > 1:  # Multiple results, ask for pack size
			select_pack_size(tup)
		else:
			messagebox.showerror("Error", "Drug not found")
			set_qty_ent.focus()
			meds_ent.focus()
			clear_display_fields()

	# Function to display narcotic information
	def display_narcotic_info(narc):
		name_lbl_output.config(text=narc[1])
		din__med_output.config(text=narc[0])
		strength_lbl_output.config(text=narc[4])
		drug_form_output.config(text=narc[5])
		pack_med_output.config(text=narc[6])
		qty_med_output.config(text=find_quantity(narc[3]))

	# Function to clear the display fields
	def clear_display_fields():
		name_lbl_output.config(text="")
		din__med_output.config(text="")
		strength_lbl_output.config(text="")
		drug_form_output.config(text="")
		pack_med_output.config(text="")
		qty_med_output.config(text="")

	# Function to handle pack size selection when multiple results are found
	def select_pack_size(tup):
		choice_window = tk.Toplevel(receiving_window)
		choice_window.title("Choose Pack Size")
		choice_window.geometry("400x100")
		choice_window.wm_attributes("-topmost", True)

		tk.Label(choice_window, text="Choose the pack size:").pack()

		pack_size = tk.StringVar()
		pack_size_dropdown = ttk.Combobox(choice_window, textvariable=pack_size)
		pack_size_dropdown['values'] = [f"{item[6]} units - {item[4]} {item[5]}" for item in tup]
		pack_size_dropdown.pack()

		def on_select_pack_size():
			selected_index = pack_size_dropdown.current()
			selected_pack = tup[selected_index]
			display_narcotic_info(selected_pack)
			choice_window.destroy()

		select_btn = tk.Button(choice_window, text="Select", command=on_select_pack_size)
		select_btn.pack()

	def on_entry_click(event): # When the med entry widget is clicked remove the text
		"""Remove placeholder when entry is clicked."""
		if meds_ent.get() == 'Enter DIN or UPC':
			meds_ent.delete(0, "end")  # Delete all the text in the entry

	def on_focusout(event): # When the med entry widget is un-clicked add the text back
		"""Re-add placeholder if entry is empty when focus is lost."""
		if meds_ent.get() == '':
			meds_ent.insert(0, 'Enter DIN or UPC')


	#Running the program
	refresh_page()
	reconciliation_window.mainloop()