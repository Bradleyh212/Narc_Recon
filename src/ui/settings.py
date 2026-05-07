# settings.py
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from db.connection import get_conn
from services import user_service
from ui.base_page import BasePage
from ui.ui_helpers import create_nav_bar


class SettingsPage(BasePage):
	def __init__(self):
		super().__init__()
		self.configure_root()
		self.create_settings_shell_frames()

	def run(self):
		self.create_title_label("SETTINGS")
		self.create_nav()
		self.create_user_list()
		self.refresh_user_list()
		self.create_controls()
		self.root.mainloop()

	def create_settings_shell_frames(self):
		self.header_frame = tk.Frame(
			self.root,
			width=self.window_width,
			height=75,
			bg=self.nav_and_header_background_color,
		)
		self.header_frame.grid(row=0, column=0, sticky="ew")
		self.header_frame.columnconfigure(0, weight=1)
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

		self.body_frame = ctk.CTkFrame(
			self.root,
			width=1000,
			height=500,
			fg_color=self.main_background_color,
		)
		self.body_frame.grid(row=1, column=0, pady=(40, 0))
		self.body_frame.columnconfigure(0, weight=1)
		self.body_frame.columnconfigure(1, weight=1)
		self.body_frame.grid_propagate(False)

		self.left_body_frame = ctk.CTkFrame(self.body_frame, width=500, height=400, corner_radius=20)
		self.left_body_frame.grid(row=0, column=0, sticky="nsew", padx=(60, 20), pady=(0, 40))
		self.left_body_frame.grid_propagate(False)

		self.right_body_frame = ctk.CTkFrame(self.body_frame, width=400, height=400, corner_radius=20)
		self.right_body_frame.grid(row=0, column=1, sticky="nsew", padx=(20, 60), pady=(0, 40))
		self.right_body_frame.grid_propagate(False)

	def create_nav(self):
		from ui.inventory import open_inventory_page
		from ui.filling import open_filling_page
		from ui.receiving import open_receiving_page
		from ui.reconciliation import open_reconciliation_page
		from ui.report import open_report_page

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
			"SETTINGS",
			pages,
			self.button_color,
			self.button_corner_radius,
			self.button_hover_color
		)

	def create_user_list(self):
		self.user_listbox = tk.Listbox(self.left_body_frame, font=("Inter", 14), height=16, width=40)
		self.user_listbox.pack(padx=20, pady=20, fill="both", expand=True)

	def refresh_user_list(self):
		self.user_listbox.delete(0, "end")
		for row in user_service.list_users(get_conn()):
			self.user_listbox.insert("end", f"{row[1]} ({row[2]})")  # user_id (role)

	def create_controls(self):
		ctk.CTkLabel(self.right_body_frame, text="User ID", font=("Inter", 18)).pack(pady=(30, 5))
		self.user_id_entry = ctk.CTkEntry(self.right_body_frame, width=250, corner_radius=20)
		self.user_id_entry.pack(pady=5)

		ctk.CTkLabel(self.right_body_frame, text="Role", font=("Inter", 18)).pack(pady=(20, 5))
		self.role_entry = ctk.CTkEntry(
			self.right_body_frame,
			width=250,
			corner_radius=20,
			placeholder_text="e.g. Pharmacist, Technician, Assistant",
		)
		self.role_entry.pack(pady=5)

		# Buttons
		add_btn = ctk.CTkButton(
			self.right_body_frame,
			text="Add User",
			command=self.add_user_handler,
			fg_color=self.button_color,
			hover_color=self.button_hover_color,
			corner_radius=20,
		)
		add_btn.pack(pady=(30, 10))

		remove_btn = ctk.CTkButton(
			self.right_body_frame,
			text="Remove Selected",
			command=self.remove_user_handler,
			fg_color="#B33A3A",
			hover_color="#D64545",
			corner_radius=20,
		)
		remove_btn.pack(pady=10)

	def add_user_handler(self):
		uid = self.user_id_entry.get().strip()
		role = self.role_entry.get().strip() or "staff"
		if not uid:
			messagebox.showerror("Error", "User ID cannot be empty")
			return
		if user_service.user_exists(get_conn(), uid):
			messagebox.showerror("Error", f"User '{uid}' already exists")
			return
		user_service.add_user(get_conn(), uid, role)
		messagebox.showinfo("Success", f"User '{uid}' added with role '{role}'")
		self.user_id_entry.delete(0, "end")
		self.role_entry.delete(0, "end")
		self.refresh_user_list()

	def remove_user_handler(self):
		try:
			selected = self.user_listbox.get(self.user_listbox.curselection())
			uid = selected.split(" ")[0]
		except:
			messagebox.showerror("Error", "Select a user to remove")
			return
		user_service.remove_user(get_conn(), uid)
		messagebox.showinfo("Success", f"User '{uid}' removed")
		self.refresh_user_list()


def open_settings_page():
	SettingsPage().run()
