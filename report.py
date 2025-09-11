def open_report_page():
	# Main page setup, full-screen, non-resizable window

	# === Standard Library ===
	import os
	import tkinter as tk
	import customtkinter as ctk
	from tkinter import ttk, messagebox, simpledialog

	# === External Libraries ===
	from reportlab.lib import colors
	from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

	# === Project Modules ===
	from inventory import open_inventory_page
	from filling import open_filling_page
	from receiving import open_receiving_page
	from reconciliation import open_reconciliation_page
	from settings import open_settings_page
	from auth import get_conn
	from ui_helpers import create_nav_bar

	# === Database Functions ===
	from sqlite3_functions import (
		get_audit_log_by_din_and_date,
		get_reconciliation_log_by_date_range,
		find_narcs_upc,
		find_narcs_din,
		find_quantity,
		find_quantity_din,
		show_narcs_table,
		add_to_audit_log,
		show_audit_log,
	)

	# Connect to SQLite database
	con = get_conn()
	cur = con.cursor()


	report_window = ctk.CTk()
	report_window.title("Narc Recon")

	main_background_color = "#1C1C1C"
	nav_and_header_background_color = "#181818"

	button_color = "#3B4B59"
	button_corner_radius = 20
	button_hover_color="#468189"

	style = ttk.Style(report_window)

	# macOS fix: aqua ignores heading anchor; clam respects it
	try:
		style.theme_use("clam")
	except Exception:
		pass



	# Initialize the main page Tkinter window
	ctk.set_appearance_mode("dark")
	ctk.set_default_color_theme("dark-blue")
	report_window.configure(fg_color=main_background_color)

	w = 1000
	h = 600
	window_width = report_window.winfo_screenwidth()
	window_height = report_window.winfo_screenheight()
	x = (window_width / 2) - (w / 2)
	y = (window_height / 2) - (h / 2)
	report_window.geometry(f'{w}x{h}+{int(x)}+{int(y)}')

	# Disable resizing
	report_window.resizable(False, False)

	# Creating the fonts
	header_font = ("Inter", 40)
	font = ("Inter", 20) # Define a font for the Entry widget
	# The size of the text changes the height of the Entry widget

	# Frame setup: header, body, and navigation
	header_frame = tk.Frame(report_window, width = w, height = 75, bg = nav_and_header_background_color)
	header_frame.grid(row = 0, column = 0)

	# Configure header_frame columns
	header_frame.columnconfigure(1, weight=1)
	header_frame.grid_propagate(False) # Prevent the header frame from resizing based on its content

	# Navigation frame on the right
	nav_frame = ctk.CTkFrame(header_frame, width=700, height=20, fg_color = nav_and_header_background_color)
	nav_frame.grid(row=0, column=1, sticky="e", pady=20)
	nav_frame.pack_propagate(False) # Prevent the nav frame from resizing based on its content


	body_frame = ctk.CTkFrame(report_window, width = 1000, height = 525)
	body_frame.grid(row = 1, column = 0, pady=(0,0))

	body_frame.columnconfigure(0, weight=1)
	body_frame.grid_propagate(False) # Prevent the body frame from resizing based on its content
	body_frame.configure(fg_color=main_background_color)


	search_frame = ctk.CTkFrame(body_frame, width = 1000, height = 150, fg_color = main_background_color)
	search_frame.grid(row = 0, column = 0, pady=25, padx=(100, 0))
	search_frame.grid_propagate(False)


	# # Add table to display the report
	columns = ("med_name", "din", "qty")
	report_table = ttk.Treeview(body_frame, columns=columns, show="headings", height=12)
	report_table.grid(row=1, column=0, padx=50, pady=(0, 10))

	# Attach vertical scrollbar
	scrollbar = ttk.Scrollbar(body_frame, orient="vertical", command=report_table.yview)
	report_table.configure(yscrollcommand=scrollbar.set)

	# Place widgets side by side
	report_table.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nsew")
	scrollbar.grid(row=1, column=1, sticky="ns")

	# Define headings
	report_table.heading("med_name", text="Medication Name", anchor="w")  # w = west (left align)
	report_table.heading("din", text="DIN", anchor="w")
	report_table.heading("qty", text="Current Quantity", anchor="e")

	# Set column widths + alignment
	report_table.column("med_name", width=300, anchor="w")
	report_table.column("din", width=100, anchor="w")
	report_table.column("qty", width=100, anchor="e")


	def refresh_page():
		global date_ent, date_ent_1, din_ent

		# Title
		page_title = ctk.CTkLabel(header_frame, text="REPORT", font=header_font)
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
			report_window,
			nav_frame,
			"REPORT",
			pages,
			button_color,
			button_corner_radius,
			button_hover_color
		)

		date_ent = ctk.CTkEntry(search_frame, placeholder_text = "yyyy-mm-dd", width = 150, font = font, justify="center") #upc entry widget
		date_ent.grid(row = 0, column = 0)
		date_ent.focus()

		to_lbl = ctk.CTkLabel(search_frame, text="to", width = 30, font = font, justify="center")
		to_lbl.grid(row = 0, column = 1, padx=10)

		date_ent_1 = ctk.CTkEntry(search_frame, placeholder_text = "yyyy-mm-dd", width = 150, font = font, justify="center") #upc entry widget
		date_ent_1.grid(row = 0, column = 2, padx=(0, 10))

		din_ent = ctk.CTkEntry(search_frame, width = 150, font = font, justify="center", placeholder_text="Enter din") #upc entry widget
		din_ent.grid(row = 0, column = 3, padx=(0, 20))

		create_audit_report_btn = ctk.CTkButton(search_frame, text = "CREATE AUDIT REPORT", command=create_audit_report, fg_color=button_color, corner_radius=button_corner_radius, hover_color=button_hover_color)
		create_audit_report_btn.grid(row = 0, column = 4, pady=30)

		recon_report_btn = ctk.CTkButton(search_frame, text="CREATE RECONCILIATION REPORT", command=create_reconciliation_report, fg_color=button_color, corner_radius=button_corner_radius, hover_color=button_hover_color)
		recon_report_btn.grid(row=1, column=4)

		load_report_data()

		# PDF export button
		export_btn = ctk.CTkButton(body_frame, text="EXPORT TO PDF", command=export_to_pdf, fg_color=button_color, corner_radius=button_corner_radius, hover_color=button_hover_color)
		export_btn.grid(row=3, column=0)




	def load_report_data():
		report_table.delete(*report_table.get_children())  # Clear old data

		# Read alphabetically by med name (A→Z), then by DIN
		cur.execute("""
			SELECT name, din, quantity
			FROM narcs
			ORDER BY name COLLATE NOCASE, din
		""")
		rows = cur.fetchall()

		for row in rows:
			report_table.insert("", "end", values=row)

	def export_to_pdf():
		data = [("Medication Name", "DIN", "Current Qty")]

		for child in report_table.get_children():
			row = report_table.item(child)['values']
			data.append(row)

		# Get user's Downloads folder
		downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
		pdf_path = os.path.join(downloads_path, "narcotics_report.pdf")

		pdf = SimpleDocTemplate(pdf_path)
		table = Table(data)

		# Style
		style = TableStyle([
			("BACKGROUND", (0, 0), (-1, 0), colors.grey),
			("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
			("ALIGN", (0, 0), (-1, -1), "CENTER"),
			("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
			("BOTTOMPADDING", (0, 0), (-1, 0), 12),
			("GRID", (0, 0), (-1, -1), 1, colors.black),
		])
		table.setStyle(style)

		pdf.build([table])
		messagebox.showinfo("Success", f"PDF report saved to:\n{pdf_path}")

	def create_audit_report():
		start_date = date_ent.get().strip()
		end_date = date_ent_1.get().strip()
		din = din_ent.get().strip()

		if not start_date or not end_date or not din:
			messagebox.showerror("Input Error", "Please enter both dates and a DIN.")
			return

		from sqlite3_functions import get_audit_log_by_din_and_date
		rows = get_audit_log_by_din_and_date(din, start_date, end_date)

		if not rows:
			messagebox.showinfo("No Data", "No audit log entries found for the given DIN and date range.")
			return

		# Build PDF data
		data = [("DIN", "OLD QUANTITY", "NEW QUANTITY", "Timestamp")]
		for row in rows:
			data.append(row)

		# Save to Downloads folder
		downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
		filename = f"audit_log_{din}_{start_date}_to_{end_date}.pdf"
		pdf_path = os.path.join(downloads_path, filename)

		pdf = SimpleDocTemplate(pdf_path)
		table = Table(data)

		# Style the table
		style = TableStyle([
			("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
			("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
			("ALIGN", (0, 0), (-1, -1), "CENTER"),
			("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
			("BOTTOMPADDING", (0, 0), (-1, 0), 12),
			("GRID", (0, 0), (-1, -1), 1, colors.black),
		])
		table.setStyle(style)

		# Build and save the PDF
		pdf.build([table])
		messagebox.showinfo("Audit Report Created", f"PDF saved to:\n{pdf_path}")

	def create_reconciliation_report():
		start_date = date_ent.get().strip()
		end_date   = date_ent_1.get().strip()
		if not start_date or not end_date:
			messagebox.showerror("Input Error", "Please enter both start and end dates.")
			return

		rows = get_reconciliation_log_by_date_range(start_date, end_date)
		if not rows:
			messagebox.showinfo("No Data", "No reconciliation entries found for the given date range.")
			return

		# rows already in order: (name, strength, din, old_qty, new_qty, discrepancy, timestamp)
		data = [("Name", "Strength", "DIN", "Old Qty", "New Qty", "Discrepancy", "Timestamp")]
		data.extend(rows)

		downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
		pdf_path = os.path.join(downloads_path, f"reconciliation_report_{start_date}_to_{end_date}.pdf")

		pdf = SimpleDocTemplate(pdf_path)
		table = Table(data)
		table.setStyle(TableStyle([
			("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
			("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
			("ALIGN", (0, 0), (-1, -1), "CENTER"),
			("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
			("BOTTOMPADDING", (0, 0), (-1, 0), 12),
			("GRID", (0, 0), (-1, -1), 1, colors.black),
		]))
		pdf.build([table])
		messagebox.showinfo("Reconciliation Report Created", f"PDF saved to:\n{pdf_path}")

	# Initialize the UI and start the Tkinter event loop
	refresh_page()
	report_window.mainloop()