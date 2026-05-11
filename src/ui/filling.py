from tkinter import messagebox

import customtkinter as ctk

from services import filling_service
from services import inventory_service
from services import workflow_audit_service
from services import workflow_debug_service
from ui.base_narcotic_page import BaseNarcoticPage
from ui.ui_helpers import create_nav_bar


class FillingPage(BaseNarcoticPage):
	store_search_input = True
	search_error_focus_attr = "remove_qty_ent"

	def __init__(self, app=None, parent=None):
		super().__init__(app=app, parent=parent)
		if self.is_standalone:
			self.configure_root()
		self.create_shell_frames()
		self.root.bind('<Return>', lambda event: self.search_narcs())

	def run(self):
		self.refresh_page()
		if self.is_standalone:
			self.root.mainloop()

	def refresh_page(self):
		self.create_title_label("FILLING")
		self.create_nav()
		self.create_filling_widgets()

	def create_nav(self):
		create_nav_bar(
			self.root,
			self.nav_frame,
			"FILLING",
			self.button_color,
			self.button_corner_radius,
			self.button_hover_color,
			app=self.app
		)

	def create_filling_widgets(self):
		self.create_narcotic_search_controls()
		self.create_narcotic_display_labels()
		self.create_on_hand_display()

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
