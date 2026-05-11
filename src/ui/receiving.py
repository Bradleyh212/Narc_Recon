from tkinter import messagebox

import customtkinter as ctk

from services import inventory_service
from services import receiving_service
from services import workflow_audit_service
from services import workflow_debug_service
from ui.base_narcotic_page import BaseNarcoticPage
from ui.ui_helpers import create_nav_bar


class ReceivingPage(BaseNarcoticPage):
	store_search_input = True
	search_error_focus_attr = "add_qty_ent"

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
		self.create_title_label("RECEIVING")
		self.create_nav()
		self.create_receiving_widgets()

	def create_nav(self):
		create_nav_bar(
			self.root,
			self.nav_frame,
			"RECEIVING",
			self.button_color,
			self.button_corner_radius,
			self.button_hover_color,
			app=self.app
		)

	def create_receiving_widgets(self):
		self.create_narcotic_search_controls()
		self.create_narcotic_display_labels()
		self.create_on_hand_display()

		self.add_qty_ent = ctk.CTkEntry(
			self.right_body_frame,
			placeholder_text="Quantity",
			font=self.font,
			width=200,
			justify="center",
			corner_radius=20,
		)
		self.add_qty_ent.grid(row=3, padx=50, pady=(0, 25))

		add_qty_btn = ctk.CTkButton(
			self.right_body_frame,
			text="ADD",
			command=lambda: self.add_quantity(self.add_qty_ent.get(), self.search_input),
			fg_color=self.button_color,
			corner_radius=self.button_corner_radius,
			hover_color=self.button_hover_color,
		)
		add_qty_btn.grid(row=4)

	def add_quantity(self, amount, inpt):
		# Resolve DIN and user
		if len(inpt) == 12:
			rows = inventory_service.find_narcs_by_upc(self.cur, inpt)
			if not rows:
				messagebox.showerror("Error", "Drug not found for this UPC")
				self.add_qty_ent.focus(); self.meds_ent.focus()
				return
			din = rows[0][0]
		elif len(inpt) == 8:
			din = inpt
		else:
			messagebox.showerror("Error", "Please enter a valid DIN or UPC")
			self.add_qty_ent.focus(); self.meds_ent.focus()
			return

		user_id = self.ask_user_id()
		if user_id is None:
			return  # user cancelled

		try:
			amt = float(amount)
		except ValueError:
			messagebox.showerror("Error", "Please enter a valid number")
			self.add_qty_ent.focus(); self.meds_ent.focus()
			return

		if amt < 0:
			messagebox.showerror("Error", "Please enter a non-negative number")
			self.add_qty_ent.focus(); self.meds_ent.focus()
			return

		# Read old qty, update, commit
		current_amount = inventory_service.find_quantity_by_din(self.cur, din)
		receiving_service.increment_inventory_quantity(self.cur, self.con, din, amt)

		# Refresh UI
		workflow_debug_service.show_narcs_table()
		self.clear_display_fields()
		self.refresh_page()
		self.search_narc_din(din)

		# Audit
		workflow_audit_service.add_to_audit_log(din, current_amount, user_id, "receiving")
		workflow_debug_service.show_audit_log()
