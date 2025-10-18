# settings.py
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from sqlite3_functions import add_user, remove_user, list_users, user_exists
from ui_helpers import create_nav_bar

def open_settings_page():
	# === Window Setup ===
	settings_window = ctk.CTk()
	settings_window.title("Narc Recon")

	main_background_color = "#1C1C1C"
	nav_and_header_background_color = "#181818"

	button_color = "#3B4B59"
	button_corner_radius = 20
	button_hover_color = "#468189"

	ctk.set_appearance_mode("dark")
	ctk.set_default_color_theme("dark-blue")
	settings_window.configure(fg_color=main_background_color)

	w, h = 1000, 600
	screen_w = settings_window.winfo_screenwidth()
	screen_h = settings_window.winfo_screenheight()
	x = (screen_w / 2) - (w / 2)
	y = (screen_h / 2) - (h / 2)
	settings_window.geometry(f"{w}x{h}+{int(x)}+{int(y)}")
	settings_window.resizable(False, False)

	# === Frames ===
	header_frame = tk.Frame(settings_window, width=w, height=75, bg=nav_and_header_background_color)
	header_frame.grid(row=0, column=0, sticky="ew")
	header_frame.columnconfigure(0, weight=1)
	header_frame.columnconfigure(1, weight=1)
	header_frame.grid_propagate(False)

	# Navigation frame
	nav_frame = ctk.CTkFrame(header_frame, width=700, height=20, fg_color=nav_and_header_background_color)
	nav_frame.grid(row=0, column=1, sticky="e", pady=20)
	nav_frame.pack_propagate(False)

	body_frame = ctk.CTkFrame(settings_window, width=1000, height=500, fg_color=main_background_color)
	body_frame.grid(row=1, column=0, pady=(40, 0))
	body_frame.columnconfigure(0, weight=1)
	body_frame.columnconfigure(1, weight=1)
	body_frame.grid_propagate(False)

	left_body_frame = ctk.CTkFrame(body_frame, width=500, height=400, corner_radius=20)
	left_body_frame.grid(row=0, column=0, sticky="nsew", padx=(60, 20), pady=(0, 40))
	left_body_frame.grid_propagate(False)

	right_body_frame = ctk.CTkFrame(body_frame, width=400, height=400, corner_radius=20)
	right_body_frame.grid(row=0, column=1, sticky="nsew", padx=(20, 60), pady=(0, 40))
	right_body_frame.grid_propagate(False)

	# === Title ===
	header_font = ("Inter", 40)
	page_title = ctk.CTkLabel(header_frame, text="SETTINGS", font=header_font)
	page_title.grid(row=0, column=0, sticky="w", padx=(60, 0), pady=(10, 5))

	# === Navigation ===
	from inventory import open_inventory_page
	from filling import open_filling_page
	from receiving import open_receiving_page
	from reconciliation import open_reconciliation_page
	from report import open_report_page

	pages = {
		"INVENTORY": open_inventory_page,
		"FILLING": open_filling_page,
		"RECEIVING": open_receiving_page,
		"RECONCILIATION": open_reconciliation_page,
		"REPORT": open_report_page,
		"SETTINGS": open_settings_page
	}
	
	create_nav_bar(
		settings_window,
		nav_frame,
		"SETTINGS",
		pages,
		button_color,
		button_corner_radius,
		button_hover_color
	)

	# === User List ===
	user_listbox = tk.Listbox(left_body_frame, font=("Inter", 14), height=16, width=40)
	user_listbox.pack(padx=20, pady=20, fill="both", expand=True)

	def refresh_user_list():
		user_listbox.delete(0, "end")
		for row in list_users():
			user_listbox.insert("end", f"{row[1]} ({row[2]})")  # user_id (role)

	refresh_user_list()

	# === Controls (Right Panel) ===
	ctk.CTkLabel(right_body_frame, text="User ID", font=("Inter", 18)).pack(pady=(30, 5))
	user_id_entry = ctk.CTkEntry(right_body_frame, width=250, corner_radius=20)
	user_id_entry.pack(pady=5)

	ctk.CTkLabel(right_body_frame, text="Role", font=("Inter", 18)).pack(pady=(20, 5))
	role_entry = ctk.CTkEntry(right_body_frame, width=250, corner_radius=20, placeholder_text="e.g. Pharmacist, Technician, Assistant")
	role_entry.pack(pady=5)

	def add_user_handler():
		uid = user_id_entry.get().strip()
		role = role_entry.get().strip() or "staff"
		if not uid:
			messagebox.showerror("Error", "User ID cannot be empty")
			return
		if user_exists(uid):
			messagebox.showerror("Error", f"User '{uid}' already exists")
			return
		add_user(uid, role)
		messagebox.showinfo("Success", f"User '{uid}' added with role '{role}'")
		user_id_entry.delete(0, "end")
		role_entry.delete(0, "end")
		refresh_user_list()

	def remove_user_handler():
		try:
			selected = user_listbox.get(user_listbox.curselection())
			uid = selected.split(" ")[0]
		except:
			messagebox.showerror("Error", "Select a user to remove")
			return
		remove_user(uid)
		messagebox.showinfo("Success", f"User '{uid}' removed")
		refresh_user_list()

	# Buttons
	add_btn = ctk.CTkButton(right_body_frame, text="Add User", command=add_user_handler,
							fg_color=button_color, hover_color=button_hover_color, corner_radius=20)
	add_btn.pack(pady=(30, 10))

	remove_btn = ctk.CTkButton(right_body_frame, text="Remove Selected", command=remove_user_handler,
							   fg_color="#B33A3A", hover_color="#D64545", corner_radius=20)
	remove_btn.pack(pady=10)

	settings_window.mainloop()