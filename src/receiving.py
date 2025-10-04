def open_receiving_page():
	# Receiving page setup, full-screen, non-resizable window

	# === Standard Library ===
	import tkinter as tk
	import customtkinter as ctk
	from tkinter import ttk, messagebox, simpledialog

	# === Project Modules ===
	from inventory import open_inventory_page
	from filling import open_filling_page
	from reconciliation import open_reconciliation_page
	from report import open_report_page
	from settings import open_settings_page
	from auth import get_conn
	from ui_helpers import create_nav_bar

	# === Database Functions ===
	from sqlite3_functions import (
		find_narcs_upc,
		find_narcs_din,
		find_quantity,
		find_quantity_din,
		show_narcs_table,
		show_audit_log,
		add_to_audit_log,
		user_exists
	)

	# Connect to SQLite database
	con = get_conn()
	cur = con.cursor()

	# Initialize the main Tkinter window
	receiving_window = ctk.CTk()
	receiving_window.title("Narc Recon")

	main_background_color = "#1C1C1C"
	nav_and_header_background_color = "#181818"

	button_color = "#3B4B59"
	button_corner_radius = 20
	button_hover_color="#468189"


	# Initialize the main page Tkinter window
	ctk.set_appearance_mode("dark")
	ctk.set_default_color_theme("dark-blue")
	receiving_window.configure(fg_color=main_background_color)

	w = 1000
	h = 600
	window_width = receiving_window.winfo_screenwidth()
	window_height = receiving_window.winfo_screenheight()
	x = (window_width / 2) - (w / 2)
	y = (window_height / 2) - (h / 2)
	receiving_window.geometry(f'{w}x{h}+{int(x)}+{int(y)}')

	# Disable resizing
	receiving_window.resizable(False, False)

	# Creating the fonts
	header_font = ("Inter", 40)
	font = ("Inter", 30) # Define a font for the Entry widget
	# The size of the text changes the height of the Entry widget

	# Frame setup: header, body, and navigation
	header_frame = tk.Frame(receiving_window, width = w, height = 75, bg = nav_and_header_background_color) # using)
	header_frame.grid(row = 0, column = 0)

	# Configure header_frame columns
	header_frame.columnconfigure(1, weight=1)
	header_frame.grid_propagate(False) # Prevent the header frame from resizing based on its content

	# Navigation frame on the right
	nav_frame = ctk.CTkFrame(header_frame, width=700, height=20, fg_color = nav_and_header_background_color)
	nav_frame.grid(row=0, column=1, sticky="e", pady=20)
	nav_frame.pack_propagate(False) # Prevent the nav frame from resizing based on its content

	body_frame = ctk.CTkFrame(receiving_window, width = 1000, height = 400)
	body_frame.grid(row = 1, column = 0, pady=(60,0))

	body_frame.columnconfigure(0, weight=1)
	body_frame.columnconfigure(1, weight=1)
	body_frame.grid_propagate(False) # Prevent the body frame from resizing based on its content
	body_frame.configure(fg_color=main_background_color)

	left_body_frame = ctk.CTkFrame(body_frame, width = 500, height = 400, corner_radius=20)
	left_body_frame.grid(row = 0, column = 0, sticky="w", padx=(60,0), pady=(0, 200))
	left_body_frame.columnconfigure(0, weight=1) # So column 0 can expand if need, if weight=2 it would expand twice as fast
	left_body_frame.columnconfigure(1, weight=1) # So column 1 can expand if need
	left_body_frame.grid_propagate(False) # Prevent the left_body_frame frame from resizing based on its content

	right_body_frame = ctk.CTkFrame(body_frame, width = 300, height = 400, corner_radius=20)
	right_body_frame.grid(row = 0, column = 1, sticky="e", padx=(0, 60), pady=(0, 200))
	right_body_frame.grid_propagate(False)

	receiving_window.bind('<Return>', lambda event: search_narcs())


	def refresh_page():
		global meds_ent, name_lbl_output, din__med_output, strength_lbl_output, drug_form_output,pack_med_lbl, pack_med_output, qty_med_output, add_qty_ent

		# Title
		page_title = ctk.CTkLabel(header_frame, text="RECEIVING", font=header_font)
		page_title.grid(row=0, column=0, sticky="w", padx=(60,0), pady=(10,5))

		# --- Dropdown Menu + Settings Button ---
		pages = {
			"INVENTORY": open_inventory_page,
			"FILLING": open_filling_page,
			"RECEIVING": open_receiving_page,
			"RECONCILIATION": open_reconciliation_page,
			"REPORT": open_report_page,
			"SETTINGS": open_settings_page
		}

		create_nav_bar(
			receiving_window,
			nav_frame,
			"RECEIVING",
			pages,
			button_color,
			button_corner_radius,
			button_hover_color
		)

		###Left Frame
		meds_ent = ctk.CTkEntry(left_body_frame, placeholder_text = "Enter upc or din", width = 200, font = font, justify="center", corner_radius=20) #upc entry widget
		meds_ent.grid(row = 0, column = 0, sticky="ew", pady=30, padx=10)
		meds_ent.focus()
		meds_ent.bind("<FocusIn>", on_focus_in)
		meds_ent.bind("<FocusOut>", on_focus_out)

		search_btn = ctk.CTkButton(left_body_frame, text = "SEARCH", command=search_narcs, width = 100, fg_color=button_color, corner_radius=button_corner_radius, hover_color=button_hover_color)
		search_btn.grid(row = 0, column = 1, sticky="ew", pady=20, padx=10)

		name_lbl_output = ctk.CTkLabel(left_body_frame, font = font, text="")
		name_lbl_output.grid(row = 2, columnspan=2, pady=(20,0)) # this will be the label to see the output when we enter the upc or din

		din__med_output = ctk.CTkLabel(left_body_frame, font = font, text="")
		din__med_output.grid(row = 3, columnspan=2, pady=(20,0))

		strength_lbl_output = ctk.CTkLabel(left_body_frame, font = font, text="")
		strength_lbl_output.grid(row = 4, columnspan=2, pady=(20,0))

		drug_form_output = ctk.CTkLabel(left_body_frame, font = font, text="")
		drug_form_output.grid(row = 5, columnspan=2, pady=(20,0))

		pack_med_output = ctk.CTkLabel(left_body_frame, font = font, text="")
		pack_med_output.grid(row = 6, columnspan=2, pady=(20,0))


		###Right Frame
		qty_med_lbl = ctk.CTkLabel(right_body_frame, text = "ON HAND", width = 10, font = font)
		qty_med_lbl.grid(row = 1, pady=(30, 0))

		qty_med_output = ctk.CTkLabel(right_body_frame, width = 10, font = font, text="")
		qty_med_output.grid(row = 2, pady=(0, 50))


		add_qty_ent = ctk.CTkEntry(right_body_frame, placeholder_text = "Quantity", font = font, width = 200, justify="center", corner_radius=20)
		add_qty_ent.grid(row = 3, padx=50, pady=(0, 25))

		add_qty_btn = ctk.CTkButton(right_body_frame, text="ADD", command=lambda: add_quantity(add_qty_ent.get(), search_input), fg_color=button_color, corner_radius=button_corner_radius, hover_color=button_hover_color)
		add_qty_btn.grid(row = 4)





	# Function to request a valid user ID
	def ask_user_id():
		while True:
			user_id = simpledialog.askstring("Input", "Please enter your user ID:", parent=receiving_window)

			# If cancelled or closed
			if user_id is None:
				messagebox.showinfo("Cancelled", "Operation cancelled")
				return None  

			# If user exists in DB
			if user_exists(user_id.strip()):
				return user_id.strip()

			# If invalid
			messagebox.showerror("Error", "Please enter a valid user ID")

	# Function to add quantity to a narcotic record
	def add_quantity(amount, inpt):
		# Resolve DIN and user
		if len(inpt) == 12:
			rows = find_narcs_upc(inpt)
			if not rows:
				messagebox.showerror("Error", "Drug not found for this UPC")
				add_qty_ent.focus(); meds_ent.focus()
				return
			din = rows[0][0]
		elif len(inpt) == 8:
			din = inpt
		else:
			messagebox.showerror("Error", "Please enter a valid DIN or UPC")
			add_qty_ent.focus(); meds_ent.focus()
			return

		user_id = ask_user_id()
		if user_id is None:
			return  # user cancelled

		try:
			amt = float(amount)
		except ValueError:
			messagebox.showerror("Error", "Please enter a valid number")
			add_qty_ent.focus(); meds_ent.focus()
			return

		if amt < 0:
			messagebox.showerror("Error", "Please enter a non-negative number")
			add_qty_ent.focus(); meds_ent.focus()
			return

		# Read old qty, update, commit
		current_amount = find_quantity_din(din)
		cur.execute("UPDATE narcs SET quantity = quantity + ? WHERE din = ?", (amt, din))
		con.commit()

		# Refresh UI
		show_narcs_table()
		clear_display_fields()
		refresh_page()
		search_narc_din(din)

		# Audit
		add_to_audit_log(din, current_amount, user_id, "receiving")
		show_audit_log()


	def search_narc_din(din): #function to find the meds in meds.py when refreshing the page
		tup = find_narcs_din(din)
		name_lbl_output.configure(text = tup[0][1])
		din__med_output.configure(text = tup[0][0])
		strength_lbl_output.configure(text = tup[0][4])
		drug_form_output.configure(text = tup[0][5])
		pack_med_output.configure(text = "PACK SIZE " + tup[0][6])
		qty_med_output.configure(text = find_quantity(tup[0][3])) #functions from the meds file to find the qty directly from the database

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
			add_qty_ent.focus()
			meds_ent.focus()
			clear_display_fields()
			return

		if len(tup) == 1:  # Single result, display information
			display_narcotic_info(tup[0])
		elif len(tup) > 1:  # Multiple results, ask for pack size
			select_pack_size(tup)
		else:
			messagebox.showerror("Error", "Drug not found")
			add_qty_ent.focus()
			meds_ent.focus()
			clear_display_fields()

	# Function to display narcotic information
	def display_narcotic_info(narc):
		name_lbl_output.configure(text=narc[1])
		din__med_output.configure(text=narc[0])
		strength_lbl_output.configure(text=narc[4])
		drug_form_output.configure(text=narc[5])
		pack_med_output.configure(text= "PACK SIZE " + narc[6])
		qty_med_output.configure(text=find_quantity(narc[3]))

	# Function to clear the display fields
	def clear_display_fields():
		name_lbl_output.configure(text="")
		din__med_output.configure(text="")
		strength_lbl_output.configure(text="")
		drug_form_output.configure(text="")
		pack_med_output.configure(text="")
		qty_med_output.configure(text="")


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

	def on_focus_in(event):
		meds_ent.configure(border_color="#3B4B59")  # Cyan border on focus

	def on_focus_out(event):
		meds_ent.configure(border_color="#444")     # Neutral gray border when unfocused



	# Initialize the UI and start the Tkinter event loop
	refresh_page()
	receiving_window.mainloop()