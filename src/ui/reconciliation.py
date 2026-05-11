from tkinter import messagebox

import customtkinter as ctk

from db.connection import get_conn
from services import inventory_service
from services import reconciliation_service
from services import user_service
from services import workflow_audit_service
from services import workflow_debug_service
from ui.base_narcotic_page import BaseNarcoticPage
from ui.ui_helpers import create_nav_bar


class ReconciliationPage(BaseNarcoticPage):
	store_search_input = True
	search_error_focus_attr = "set_qty_ent"

	def __init__(self, app, parent):
		super().__init__(app=app, parent=parent)
		self.create_shell_frames()
		self.header_frame.columnconfigure(0, weight=1)
		self.btn_frame = ctk.CTkFrame(self.right_body_frame, fg_color="transparent")
		self.btn_frame.grid(row=4, column=0, pady=(20, 0))
		self.root.bind('<Return>', lambda event: self.search_narcs())

	def run(self):
		self.refresh_page()

	def refresh_page(self):
		self.create_title_label("RECONCILIATION")
		self.create_nav()
		self.create_reconciliation_widgets()

	def create_nav(self):
		create_nav_bar(
			self.root,
			self.nav_frame,
			"RECONCILIATION",
			self.button_color,
			self.button_corner_radius,
			self.button_hover_color,
			app=self.app
		)

	def create_reconciliation_widgets(self):
		self.create_narcotic_search_controls()
		self.create_narcotic_display_labels()
		self.create_on_hand_display()

		self.set_qty_ent = ctk.CTkEntry(
			self.right_body_frame,
			placeholder_text="Quantity",
			font=self.font,
			width=200,
			justify="center",
			corner_radius=20,
		)
		self.set_qty_ent.grid(row=3, padx=50, pady=(0, 25))

		set_qty_btn = ctk.CTkButton(
			self.btn_frame,
			text="SET QUANTITY",
			command=lambda: self.set_quantity(self.set_qty_ent.get(), self.search_input),
			fg_color=self.button_color,
			corner_radius=self.button_corner_radius,
			hover_color=self.button_hover_color,
		)
		set_qty_btn.grid(row=0, column=0, padx=4)

		expired_btn = ctk.CTkButton(
			self.btn_frame,
			text="EXPIRED",
			command=lambda: self.mark_as_expired(self.set_qty_ent.get(), self.search_input),
			fg_color="#B33A3A",
			corner_radius=self.button_corner_radius,
			hover_color="#D64545",
		)
		expired_btn.grid(row=0, column=1, padx=4)

	def set_quantity(self, amount, inpt):
		if len(inpt) == 12:
			rows = inventory_service.find_narcs_by_upc(self.cur, inpt)
			if not rows:
				messagebox.showerror("Error", "Drug not found for this UPC")
				self.set_qty_ent.focus(); self.meds_ent.focus()
				return
			din = rows[0][0]
		elif len(inpt) == 8:
			din = inpt
		else:
			messagebox.showerror("Error", "Please enter a valid DIN or UPC")
			self.set_qty_ent.focus()
			self.meds_ent.focus()
			return

		user_id = self.ask_user_id()
		if user_id is None:
			return  # user cancelled

		role = user_service.get_user_role(get_conn(), user_id)
		if not user_service.role_allows_reconciliation(role):
			messagebox.showerror("Error", f"Permission denied: '{role}' users cannot initiate reconciliations.")
			return

		try:
			# try converting to float instead of int
			amount = float(amount)
		except ValueError:
			messagebox.showerror("Error", "Please enter a valid number")
			self.set_qty_ent.focus()
			self.meds_ent.focus()
			return

		if amount < 0:
			messagebox.showerror("Error", "Please add a positive number")
			self.set_qty_ent.focus()
			self.meds_ent.focus()
			return

		current_amount = inventory_service.find_quantity_by_din(self.cur, din)
		reconciliation_service.set_inventory_quantity(self.cur, self.con, din, amount)

		workflow_debug_service.show_narcs_table()  # Refresh the narcotic table view
		self.clear_display_fields()
		self.refresh_page()
		self.search_narc_din(din)

		# Log the action to the audit log
		workflow_audit_service.add_to_audit_log(din, current_amount, user_id, "reconciliation")
		workflow_debug_service.show_audit_log()

	def mark_as_expired(self, amount, inpt):
		if len(inpt) == 12:
			rows = inventory_service.find_narcs_by_upc(self.cur, inpt)
			if not rows:
				messagebox.showerror("Error", "Drug not found for this UPC")
				self.set_qty_ent.focus(); self.meds_ent.focus()
				return
			din = rows[0][0]
		elif len(inpt) == 8:
			din = inpt
		else:
			messagebox.showerror("Error", "Please enter a valid DIN or UPC")
			self.set_qty_ent.focus()
			self.meds_ent.focus()
			return

		user_id = self.ask_user_id()
		if user_id is None:
			return  # user cancelled

		try:
			expired_qty = float(amount)
		except ValueError:
			messagebox.showerror("Error", "Please enter a valid number")
			return

		current_amount = inventory_service.find_quantity_by_din(self.cur, din)

		if expired_qty <= 0:
			messagebox.showerror("Error", "Expired quantity must be greater than 0")
			return

		if expired_qty > current_amount:
			messagebox.showerror("Error", f"Expired qty ({expired_qty}) cannot exceed current stock ({current_amount})")
			return

		new_amount = current_amount - expired_qty
		reconciliation_service.set_inventory_quantity(self.cur, self.con, din, new_amount)

		workflow_debug_service.show_narcs_table()  # Refresh the narcotic table view
		self.clear_display_fields()
		self.refresh_page()
		self.search_narc_din(din)

		workflow_audit_service.add_to_audit_log(din, current_amount, user_id, "expired")
		workflow_debug_service.show_audit_log()
