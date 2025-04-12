def open_report_page():
	# Main page setup, full-screen, non-resizable window
	import tkinter as tk
	from tkinter import ttk, font, messagebox, simpledialog
	from main_page import open_main_page
	from receiving import open_receiving
	from reconciliation import open_reconciliation_page
	from audit_log_database import add_to_audit_log, show_audit_log, list_user_id, get_audit_log_by_din_and_date
	from sqlite3_functions import find_narcs_upc, find_narcs_din, find_quantity, show_narcs_table, find_quantity_din
	import sqlite3

	from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
	from reportlab.lib import colors

	import os # to let us export file to download folder directly

	# Connect to SQLite database
	con = sqlite3.connect("narcotics_database.db")
	cur = con.cursor()

	report_window = tk.Tk()
	report_window.title("Narc Recon")

	# Set window size to full screena
	w = report_window.winfo_screenwidth()
	h = report_window.winfo_screenheight()
	report_window.geometry(f'{w}x{h}')

	# Set background color and disable resizing
	main_background_color = "#3B4B59"
	nav_background_color = "black"
	report_window.configure(bg=main_background_color)
	report_window.resizable(False, False)

	# Creating the fonts
	header_font = font.Font(family="Inter", size=40, weight="normal")
	font = font.Font(family="Inter", size=20, weight="normal") # Define a font for the Entry widget
	# The size of the text changes the height of the Entry widget

	# Frame setup: header, body, and navigation
	header_frame = tk.Frame(report_window, width = w, height = 100, bg = nav_background_color) # using the bg to see the frames
	header_frame.grid(row = 0, column = 0)
	header_frame.grid_propagate(False) # Prevent the header frame from resizing based on its content

	body_frame = tk.Frame(report_window, width = w, height = h - 100, bg = main_background_color) # using the bg to see the frames
	body_frame.grid(row = 1, column = 0, pady = 30)
	body_frame.grid_propagate(False) # Prevent the body frame from resizing based on its content

	search_frame = tk.Frame(body_frame, width = w-300, height = 150, bg = main_background_color)
	search_frame.grid(row = 0, column = 0)
	search_frame.grid_propagate(False)

	nav_frame = tk.Frame(header_frame, width = 550, height = 100, bg = nav_background_color)
	nav_frame.grid(row = 0, column = 1, padx = 600)
	nav_frame.grid_propagate(False) # Prevent the nav frame from resizing based on its content

	# Add table to display the report
	columns = ("med_name", "din", "qty")
	report_table = ttk.Treeview(body_frame, columns=columns, show="headings", height=20)
	report_table.grid(row=1, column=0, padx=30)

	# Define headings
	report_table.heading("med_name", text="Medication Name")
	report_table.heading("din", text="DIN")
	report_table.heading("qty", text="Current Quantity")

	# Set column widths
	report_table.column("med_name", width=400)
	report_table.column("din", width=150)
	report_table.column("qty", width=200)

	def refresh_page():
			global date_ent, date_ent_1, din_ent

			page_title = tk.Label(header_frame, text = "REPORT", fg = "white", bg = "black", font = header_font)
			page_title.grid(row = 0, column = 0, sticky = "w", padx = 30)

			home_btn = ttk.Button(nav_frame, text = "HOME", style='TButton', command = lambda : [report_window.destroy(), open_main_page()])
			home_btn.grid(row = 0, column = 0, padx = 3, pady = 40) #Used the lambda key word to use 2 functions in 1 button

			receiving_btn = ttk.Button(nav_frame, text = "RECEIVING", style='TButton', command = lambda : [report_window.destroy(), open_receiving()])
			receiving_btn.grid(row = 0, column = 1, padx = 3) #Used the lambda key word to use 2 functions in 1 button

			#This will be open another page to do the narc reconciliation where we set the quantity on hand
			reconciliation_btn = ttk.Button(nav_frame, text = "RECONCILIATION", style='TButton', command = lambda : [report_window.destroy(), open_reconciliation_page()])
			reconciliation_btn.grid(row = 0, column = 2, padx = 3)

			#This will be open another page to do the report where we get the previous reconciliation
			report_btn = ttk.Button(nav_frame, text = "REPORT", style='TButton')
			report_btn.grid(row = 0, column = 3, padx = 3)

			log_off_btn = ttk.Button(nav_frame, text = "LOGOUT", style='TButton', command = lambda : [report_window.destroy()]) 
			log_off_btn.grid(row = 0, column = 4, padx = 3)

			date_ent = ttk.Entry(search_frame, width = 15, font = font, justify="center") #upc entry widget
			date_ent.grid(row = 0, column = 0, padx = 15, pady = 50)
			date_ent.focus()

			date_ent_1 = ttk.Entry(search_frame, text = 'Enter date in format yyyy-mm-dd', width = 15, font = font, justify="center") #upc entry widget
			date_ent_1.grid(row = 0, column = 1, padx = 15, pady = 50)

			# date_ent_1.bind('<FocusIn>', on_entry_click)
			# date_ent_1.bind('<FocusOut>', on_focusout)

			din_ent = ttk.Entry(search_frame, width = 15, font = font, justify="center") #upc entry widget
			din_ent.grid(row = 0, column = 2, padx = 15, pady = 50)

			create_audit_report_btn = ttk.Button(search_frame, style='TButton', text = "CREATE AUDIT REPORT", command=create_audit_report)
			create_audit_report_btn.grid(row = 0, column = 3, padx = 15, pady = 50)

			load_report_data()

			# PDF export button
			export_btn = ttk.Button(body_frame, text="EXPORT TO PDF", style='TButton', command=export_to_pdf)
			export_btn.grid(row=2, column=0, pady=20)

	def on_entry_click(event): # When the med entry widget is clicked remove the text
		"""Remove placeholder when entry is clicked."""
		if date_ent_1.get() == 'Enter date in format yyyy-mm-dd':
			date_ent_1.delete(0, "end")  # Delete all the text in the entry

	def on_focusout(event): # When the med entry widget is un-clicked add the text back
		"""Re-add placeholder if entry is empty when focus is lost."""
		if date_ent_1.get() == '':
			date_ent_1.insert(0, 'Enter date in format yyyy-mm-dd')


	def load_report_data():
		report_table.delete(*report_table.get_children())  # Clear old data

		cur.execute("SELECT name, din, quantity FROM narcs")  # Adjust if needed
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

		from audit_log_database import get_audit_log_by_din_and_date
		rows = get_audit_log_by_din_and_date(start_date, end_date, din)

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


	# Initialize the UI and start the Tkinter event loop
	refresh_page()
	report_window.mainloop()