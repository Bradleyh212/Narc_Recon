# settings.py
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from db.connection import get_conn
from services.catalog_management_service import CatalogManagementService, DuplicateMedicationDetailError
from services import user_service
from ui.base_page import BasePage
from ui.ui_helpers import create_nav_bar


class SettingsPage(BasePage):
	def __init__(self, app, parent):
		super().__init__(app=app, parent=parent)
		self.create_settings_shell_frames()

	def run(self):
		self.create_title_label("SETTINGS")
		self.create_nav()
		self.create_user_list()
		self.refresh_user_list()
		self.create_controls()

	def create_settings_shell_frames(self):
		self.header_frame = tk.Frame(
			self.parent,
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
			self.parent,
			width=1000,
			height=500,
			fg_color=self.main_background_color,
		)
		self.body_frame.grid(row=1, column=0, pady=(25, 0))
		self.body_frame.columnconfigure(0, weight=1)
		self.body_frame.columnconfigure(1, weight=1)
		self.body_frame.grid_propagate(False)

		self.left_body_frame = ctk.CTkFrame(self.body_frame, width=500, height=460, corner_radius=20)
		self.left_body_frame.grid(row=0, column=0, sticky="nsew", padx=(60, 20), pady=(0, 20))
		self.left_body_frame.columnconfigure(0, weight=1)
		self.left_body_frame.columnconfigure(1, weight=1)
		self.left_body_frame.grid_propagate(False)

		self.right_body_frame = ctk.CTkFrame(self.body_frame, width=400, height=460, corner_radius=20)
		self.right_body_frame.grid(row=0, column=1, sticky="nsew", padx=(20, 60), pady=(0, 20))
		self.right_body_frame.columnconfigure(0, weight=0)
		self.right_body_frame.columnconfigure(1, weight=1)
		self.right_body_frame.grid_propagate(False)

	def create_nav(self):
		create_nav_bar(
			self.root,
			self.nav_frame,
			"SETTINGS",
			self.button_color,
			self.button_corner_radius,
			self.button_hover_color,
			app=self.app,
		)

	def create_user_list(self):
		ctk.CTkLabel(self.left_body_frame, text="Users", font=("Inter", 20)).grid(
			row=0,
			column=0,
			columnspan=2,
			pady=(20, 8),
		)
		self.user_listbox = tk.Listbox(self.left_body_frame, font=("Inter", 14), height=9, width=40)
		self.user_listbox.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 12), sticky="ew")

	def refresh_user_list(self):
		self.user_listbox.delete(0, "end")
		for row in user_service.list_users(get_conn()):
			self.user_listbox.insert("end", f"{row[1]} ({row[2]})")  # user_id (role)

	def create_controls(self):
		self.create_user_controls()
		self.create_medication_controls()

	def create_user_controls(self):
		ctk.CTkLabel(self.left_body_frame, text="User ID", font=("Inter", 16)).grid(
			row=2,
			column=0,
			columnspan=2,
			pady=(4, 4),
		)
		self.user_id_entry = ctk.CTkEntry(self.left_body_frame, width=250, corner_radius=20)
		self.user_id_entry.grid(row=3, column=0, columnspan=2, pady=(0, 8))

		ctk.CTkLabel(self.left_body_frame, text="Role", font=("Inter", 16)).grid(
			row=4,
			column=0,
			columnspan=2,
			pady=(4, 4),
		)
		self.role_entry = ctk.CTkEntry(
			self.left_body_frame,
			width=250,
			corner_radius=20,
			placeholder_text="e.g. Pharmacist, Technician, Assistant",
		)
		self.role_entry.grid(row=5, column=0, columnspan=2, pady=(0, 10))

		add_btn = ctk.CTkButton(
			self.left_body_frame,
			text="Add User",
			command=self.add_user_handler,
			fg_color=self.button_color,
			hover_color=self.button_hover_color,
			corner_radius=20,
		)
		add_btn.grid(row=6, column=0, padx=(40, 8), pady=(8, 0), sticky="ew")

		remove_btn = ctk.CTkButton(
			self.left_body_frame,
			text="Remove Selected",
			command=self.remove_user_handler,
			fg_color="#B33A3A",
			hover_color="#D64545",
			corner_radius=20,
		)
		remove_btn.grid(row=6, column=1, padx=(8, 40), pady=(8, 0), sticky="ew")

	def create_medication_controls(self):
		ctk.CTkLabel(self.right_body_frame, text="Add Medication", font=("Inter", 20)).grid(
			row=0,
			column=0,
			columnspan=2,
			pady=(20, 12),
		)

		self.medication_entries = {}
		fields = [
			("Drug Name", "name", "e.g. ADDERALL XR"),
			("DIN", "din", "8 digits"),
			("UPC", "upc", "12 digits"),
			("Strength", "strength", "Optional"),
			("Form", "form", "e.g. TAB, CAP"),
			("Pack Size", "pack_size", "Optional"),
		]
		for row_number, (label_text, field_name, placeholder) in enumerate(fields, start=1):
			ctk.CTkLabel(self.right_body_frame, text=label_text, font=("Inter", 14), anchor="w").grid(
				row=row_number,
				column=0,
				padx=(28, 8),
				pady=5,
				sticky="w",
			)
			entry = ctk.CTkEntry(
				self.right_body_frame,
				width=215,
				corner_radius=20,
				placeholder_text=placeholder,
			)
			entry.grid(row=row_number, column=1, padx=(0, 28), pady=5, sticky="ew")
			self.medication_entries[field_name] = entry

		add_medication_btn = ctk.CTkButton(
			self.right_body_frame,
			text="Add Medication",
			command=self.add_medication_handler,
			fg_color=self.button_color,
			hover_color=self.button_hover_color,
			corner_radius=20,
		)
		add_medication_btn.grid(row=7, column=0, columnspan=2, padx=80, pady=(16, 0), sticky="ew")

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

	def add_medication_handler(self):
		values = {
			field_name: entry.get()
			for field_name, entry in self.medication_entries.items()
		}
		connection = None
		try:
			connection = get_conn()
			result = CatalogManagementService(connection).add_medication(**values)
		except DuplicateMedicationDetailError as exc:
			messagebox.showerror("Duplicate medication detail", str(exc))
		except ValueError as exc:
			messagebox.showerror("Invalid medication", str(exc))
		except Exception as exc:
			messagebox.showerror("Error", f"Unable to add medication: {exc}")
		else:
			if result["created_narc"]:
				message = f"Medication '{values['name'].strip()}' added."
			else:
				message = "Medication detail added."
				if result["updated_name"]:
					message += " Existing catalog name updated."
			messagebox.showinfo("Success", message)
			self.clear_medication_entries()
		finally:
			if connection is not None:
				connection.close()

	def clear_medication_entries(self):
		for entry in self.medication_entries.values():
			entry.delete(0, "end")

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
