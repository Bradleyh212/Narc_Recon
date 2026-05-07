import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

import customtkinter as ctk

from db.connection import get_conn
from services import filling_service
from services import inventory_service
from services import user_service
from services import workflow_audit_service
from services import workflow_debug_service
from ui.base_page import BasePage
from ui.ui_helpers import create_nav_bar


class FillingPage(BasePage):
	def __init__(self):
		super().__init__()
		self.con = get_conn()
		self.cur = self.con.cursor()
		self.configure_root()
		self.create_shell_frames()
		self.root.bind('<Return>', lambda event: self.search_narcs())

	def run(self):
		self.refresh_page()
		self.root.mainloop()

	def refresh_page(self):
		self.create_title_label("FILLING")
		self.create_nav()
		self.create_filling_widgets()

	def create_nav(self):
		from ui.inventory import open_inventory_page
		from ui.receiving import open_receiving_page
		from ui.reconciliation import open_reconciliation_page
		from ui.report import open_report_page
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
			"FILLING",
			pages,
			self.button_color,
			self.button_corner_radius,
			self.button_hover_color
		)

	def create_filling_widgets(self):
		self.meds_ent = ctk.CTkEntry(
			self.left_body_frame,
			placeholder_text="Enter upc or din",
			width=200,
			font=self.font,
			justify="center",
			corner_radius=20,
		)
		self.meds_ent.grid(row=0, column=0, sticky="ew", pady=30, padx=10)
		self.meds_ent.focus()
		self.meds_ent.bind("<FocusIn>", lambda event: self.on_focus_in(self.meds_ent))
		self.meds_ent.bind("<FocusOut>", lambda event: self.on_focus_out(self.meds_ent))

		search_btn = ctk.CTkButton(
			self.left_body_frame,
			text="SEARCH",
			command=self.search_narcs,
			width=100,
			fg_color=self.button_color,
			corner_radius=self.button_corner_radius,
			hover_color=self.button_hover_color,
		)
		search_btn.grid(row=0, column=1, sticky="ew", pady=20, padx=10)

		self.name_lbl_output = ctk.CTkLabel(self.left_body_frame, font=self.font, text="")
		self.name_lbl_output.grid(row=2, columnspan=2, pady=(20, 0))

		self.din__med_output = ctk.CTkLabel(self.left_body_frame, font=self.font, text="")
		self.din__med_output.grid(row=3, columnspan=2, pady=(20, 0))

		self.strength_lbl_output = ctk.CTkLabel(self.left_body_frame, font=self.font, text="")
		self.strength_lbl_output.grid(row=4, columnspan=2, pady=(20, 0))

		self.drug_form_output = ctk.CTkLabel(self.left_body_frame, font=self.font, text="")
		self.drug_form_output.grid(row=5, columnspan=2, pady=(20, 0))

		self.pack_med_output = ctk.CTkLabel(self.left_body_frame, font=self.font, text="")
		self.pack_med_output.grid(row=6, columnspan=2, pady=(20, 0))

		qty_med_lbl = ctk.CTkLabel(self.right_body_frame, text="ON HAND", width=10, font=self.font)
		qty_med_lbl.grid(row=1, pady=(30, 0))

		self.qty_med_output = ctk.CTkLabel(self.right_body_frame, width=10, font=self.font, text="")
		self.qty_med_output.grid(row=2, pady=(0, 50))

		self.remove_qty_ent = ctk.CTkEntry(
			self.right_body_frame,
			placeholder_text="Quantity",
			font=self.font,
			width=200,
			justify="center",
			corner_radius=20,
		)
		self.remove_qty_ent.grid(row=3, padx=50, pady=(0, 25))

		remove_qty_btn = ctk.CTkButton(
			self.right_body_frame,
			text="FILL",
			command=lambda: self.remove_quantity(self.remove_qty_ent.get(), self.search_input),
			fg_color=self.button_color,
			corner_radius=self.button_corner_radius,
			hover_color=self.button_hover_color,
		)
		remove_qty_btn.grid(row=4)

	def ask_user_id(self):
		while True:
			user_id = simpledialog.askstring("Input", "Please enter your user ID:", parent=self.root)

			# If cancelled or closed
			if user_id is None:
				messagebox.showinfo("Cancelled", "Operation cancelled")
				return None

			# If user exists in DB
			if user_service.user_exists(get_conn(), user_id.strip()):
				return user_id.strip()

			# If invalid
			messagebox.showerror("Error", "Please enter a valid user ID")

	def remove_quantity(self, amount, inpt):
		if len(inpt) == 12:
			rows = inventory_service.find_narcs_by_upc(self.cur, inpt)
			if not rows:
				messagebox.showerror("Error", "Drug not found for this UPC")
				self.remove_qty_ent.focus(); self.meds_ent.focus()
				return
			din = rows[0][0]
		elif len(inpt) == 8:
			din = inpt  # Input is DIN

		else:
			messagebox.showerror("Error", "Please enter a valid DIN or UPC")
			self.remove_qty_ent.focus(); self.meds_ent.focus()
			return

		user_id = self.ask_user_id()
		if user_id is None:
			return  # user cancelled

		try:
			amount = float(amount)
		except ValueError:
			messagebox.showerror("Error", "Please enter a valid number")
			return

		if amount <= 0:
			messagebox.showerror("Error", "Please enter a valid positive quantity to fill")
			return

		# Perform database update and refresh UI
		current_amount = inventory_service.find_quantity_by_din(self.cur, din)

		if amount > current_amount:
			messagebox.showerror("Error", "Not enough stock to remove that quantity")
			return

		filling_service.decrement_inventory_quantity(self.cur, self.con, din, amount)

		workflow_debug_service.show_narcs_table()  # Refresh the narcotic table view
		self.clear_display_fields()
		self.refresh_page()
		self.search_narc_din(din)

		# Log the action to the audit log
		workflow_audit_service.add_to_audit_log(din, current_amount, user_id, "filling")
		workflow_debug_service.show_audit_log()

	def search_narc_din(self, din):
		tup = inventory_service.find_narcs_by_din(self.cur, din)
		self.name_lbl_output.configure(text=tup[0][1])
		self.din__med_output.configure(text=tup[0][0])
		self.strength_lbl_output.configure(text=tup[0][4])
		self.drug_form_output.configure(text=tup[0][5])
		self.pack_med_output.configure(text="PACK SIZE " + tup[0][6])
		self.qty_med_output.configure(text=inventory_service.find_quantity_by_upc(self.cur, tup[0][3]))

	def search_narcs(self):
		self.search_input = self.meds_ent.get()
		self.meds_ent.delete(0, "end")

		if len(self.search_input) == 12:
			tup = inventory_service.find_narcs_by_upc(self.cur, self.search_input)
		elif len(self.search_input) == 8:
			tup = inventory_service.find_narcs_by_din(self.cur, self.search_input)
		else:
			messagebox.showerror("Error", "Drug not found")
			self.remove_qty_ent.focus()
			self.meds_ent.focus()
			self.clear_display_fields()
			return

		if len(tup) == 1:
			self.display_narcotic_info(tup[0])
		elif len(tup) > 1:
			self.select_pack_size(tup)
		else:
			messagebox.showerror("Error", "Drug not found")
			self.remove_qty_ent.focus()
			self.meds_ent.focus()
			self.clear_display_fields()

	def display_narcotic_info(self, narc):
		self.name_lbl_output.configure(text=narc[1])
		self.din__med_output.configure(text=narc[0])
		self.strength_lbl_output.configure(text=narc[4])
		self.drug_form_output.configure(text=narc[5])
		self.pack_med_output.configure(text="PACK SIZE " + narc[6])
		self.qty_med_output.configure(text=inventory_service.find_quantity_by_upc(self.cur, narc[3]))

	def clear_display_fields(self):
		self.name_lbl_output.configure(text="")
		self.din__med_output.configure(text="")
		self.strength_lbl_output.configure(text="")
		self.drug_form_output.configure(text="")
		self.pack_med_output.configure(text="")
		self.qty_med_output.configure(text="")

	def select_pack_size(self, tup):
		choice_window = tk.Toplevel(self.root)
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
			self.display_narcotic_info(selected_pack)
			choice_window.destroy()

		select_btn = tk.Button(choice_window, text="Select", command=on_select_pack_size)
		select_btn.pack()


def open_filling_page():
	FillingPage().run()
