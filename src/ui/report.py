import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

import customtkinter as ctk
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from db.connection import get_conn
from services import audit_log_service
from ui.base_page import BasePage
from ui.ui_helpers import create_nav_bar


class ReportPage(BasePage):
	def __init__(self):
		super().__init__()
		self.con = get_conn()
		self.cur = self.con.cursor()
		self.font = ("Inter", 20)
		self.configure_root()
		self.configure_table_style()
		self.create_report_shell_frames()
		self.create_report_table()

	def run(self):
		self.refresh_page()
		self.root.mainloop()

	def configure_table_style(self):
		self.style = ttk.Style(self.root)

		# macOS fix: aqua ignores heading anchor; clam respects it
		try:
			self.style.theme_use("clam")
		except Exception:
			pass

	def create_report_shell_frames(self):
		self.header_frame = tk.Frame(
			self.root,
			width=self.window_width,
			height=75,
			bg=self.nav_and_header_background_color,
		)
		self.header_frame.grid(row=0, column=0)
		self.header_frame.columnconfigure(1, weight=1)
		self.header_frame.grid_propagate(False)

		self.nav_frame = ctk.CTkFrame(
			self.header_frame,
			width=700,
			height=20,
			fg_color=self.nav_and_header_background_color,
		)
		self.nav_frame.grid(row=0, column=1, sticky="e", pady=20)
		self.nav_frame.pack_propagate(False)

		self.body_frame = ctk.CTkFrame(self.root, width=1000, height=525)
		self.body_frame.grid(row=1, column=0, pady=(0, 0))
		self.body_frame.columnconfigure(0, weight=1)
		self.body_frame.grid_propagate(False)
		self.body_frame.configure(fg_color=self.main_background_color)

		self.search_frame = ctk.CTkFrame(
			self.body_frame,
			width=1000,
			height=150,
			fg_color=self.main_background_color,
		)
		self.search_frame.grid(row=0, column=0, pady=25, padx=(100, 0))
		self.search_frame.grid_propagate(False)

	def create_report_table(self):
		columns = ("med_name", "din", "qty")
		self.report_table = ttk.Treeview(self.body_frame, columns=columns, show="headings", height=12)
		self.report_table.grid(row=1, column=0, padx=50, pady=(0, 10))

		# Attach vertical scrollbar
		scrollbar = ttk.Scrollbar(self.body_frame, orient="vertical", command=self.report_table.yview)
		self.report_table.configure(yscrollcommand=scrollbar.set)

		# Place widgets side by side
		self.report_table.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nsew")
		scrollbar.grid(row=1, column=1, sticky="ns")

		# Define headings
		self.report_table.heading("med_name", text="Medication Name", anchor="w")
		self.report_table.heading("din", text="DIN", anchor="w")
		self.report_table.heading("qty", text="Current Quantity", anchor="e")

		# Set column widths + alignment
		self.report_table.column("med_name", width=300, anchor="w")
		self.report_table.column("din", width=100, anchor="w")
		self.report_table.column("qty", width=100, anchor="e")

	def refresh_page(self):
		self.create_title_label("REPORT")
		self.create_nav()
		self.create_search_controls()
		self.load_report_data()

		# PDF export button
		export_btn = ctk.CTkButton(
			self.body_frame,
			text="EXPORT TO PDF",
			command=self.export_to_pdf,
			fg_color=self.button_color,
			corner_radius=self.button_corner_radius,
			hover_color=self.button_hover_color,
		)
		export_btn.grid(row=3, column=0)

	def create_nav(self):
		from ui.inventory import open_inventory_page
		from ui.filling import open_filling_page
		from ui.receiving import open_receiving_page
		from ui.reconciliation import open_reconciliation_page
		from ui.settings import open_settings_page

		pages = {
			"INVENTORY": open_inventory_page,
			"FILLING": open_filling_page,
			"RECEIVING": open_receiving_page,
			"RECONCILIATION": open_reconciliation_page,
			"REPORT": open_report_page,
			"SETTINGS": open_settings_page
		}

		create_nav_bar(
			self.root,
			self.nav_frame,
			"REPORT",
			pages,
			self.button_color,
			self.button_corner_radius,
			self.button_hover_color
		)

	def create_search_controls(self):
		self.date_ent = ctk.CTkEntry(
			self.search_frame,
			placeholder_text="yyyy-mm-dd",
			width=150,
			font=self.font,
			justify="center",
		)
		self.date_ent.grid(row=0, column=0)
		self.date_ent.focus()

		to_lbl = ctk.CTkLabel(self.search_frame, text="to", width=30, font=self.font, justify="center")
		to_lbl.grid(row=0, column=1, padx=10)

		self.date_ent_1 = ctk.CTkEntry(
			self.search_frame,
			placeholder_text="yyyy-mm-dd",
			width=150,
			font=self.font,
			justify="center",
		)
		self.date_ent_1.grid(row=0, column=2, padx=(0, 10))

		self.din_ent = ctk.CTkEntry(
			self.search_frame,
			width=150,
			font=self.font,
			justify="center",
			placeholder_text="Enter din",
		)
		self.din_ent.grid(row=0, column=3, padx=(0, 20))

		create_audit_report_btn = ctk.CTkButton(
			self.search_frame,
			text="CREATE AUDIT REPORT",
			command=self.create_audit_report,
			fg_color=self.button_color,
			corner_radius=self.button_corner_radius,
			hover_color=self.button_hover_color,
		)
		create_audit_report_btn.grid(row=0, column=4, pady=30)

		recon_report_btn = ctk.CTkButton(
			self.search_frame,
			text="CREATE RECONCILIATION REPORT",
			command=self.create_reconciliation_report,
			fg_color=self.button_color,
			corner_radius=self.button_corner_radius,
			hover_color=self.button_hover_color,
		)
		recon_report_btn.grid(row=1, column=4)

	def load_report_data(self):
		self.report_table.delete(*self.report_table.get_children())

		# Read alphabetically by med name (A-Z), then by DIN
		self.cur.execute("""
			SELECT name, din, quantity
			FROM narcs
			ORDER BY name COLLATE NOCASE, din
		""")
		rows = self.cur.fetchall()

		for row in rows:
			self.report_table.insert("", "end", values=row)

	def export_to_pdf(self):
		data = [("Medication Name", "DIN", "Current Qty")]

		for child in self.report_table.get_children():
			row = self.report_table.item(child)['values']
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

	def create_audit_report(self):
		start_date = self.date_ent.get().strip()
		end_date = self.date_ent_1.get().strip()
		din = self.din_ent.get().strip()

		if not start_date or not end_date or not din:
			messagebox.showerror("Input Error", "Please enter both dates and a DIN.")
			return

		rows = audit_log_service.get_audit_log_by_din_and_date(self.cur, din, start_date, end_date)

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

	def create_reconciliation_report(self):
		start_date = self.date_ent.get().strip()
		end_date = self.date_ent_1.get().strip()
		if not start_date or not end_date:
			messagebox.showerror("Input Error", "Please enter both start and end dates.")
			return

		rows = audit_log_service.get_reconciliation_log_by_date_range(self.cur, start_date, end_date)
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


def open_report_page():
	ReportPage().run()
