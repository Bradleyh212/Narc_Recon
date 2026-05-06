import sqlite3

import customtkinter as ctk
from tkinter import messagebox

from services import auth_service


def create_account_window(conn):
	# GUI for first-run account creation
	class SetupWindow(ctk.CTk):
		def __init__(self):
			super().__init__()
			self.title("Narc Recon • First-Run Setup")
			self.resizable(False, False)

			ctk.set_appearance_mode("dark")
			ctk.set_default_color_theme("dark-blue")

			w, h = 420, 350
			sel_width = self.winfo_screenwidth()
			self_height = self.winfo_screenheight()
			x = (sel_width / 2) - (w / 2)
			y = (self_height / 2) - (h / 2)
			self.geometry(f'{w}x{h}+{int(x)}+{int(y)}')

			ctk.CTkLabel(self, text="Create Pharmacy Account", font=("Arial", 18, "bold")).pack(pady=10)

			self.username = ctk.CTkEntry(self, width=100, height=35, placeholder_text="Username (e.g., pharmacy)", corner_radius=20)
			self.username.pack(padx=20, pady=(10, 6), fill="x")

			self.pharmacist_user_id = ctk.CTkEntry(self, width=100, height=35, placeholder_text="Initial pharmacist user ID", corner_radius=20)
			self.pharmacist_user_id.pack(padx=20, pady=6, fill="x")

			self.pw = ctk.CTkEntry(self, width=100, height=35, placeholder_text="Password", show="*", corner_radius=20)
			self.pw.pack(padx=20, pady=6, fill="x")

			self.pw2 = ctk.CTkEntry(self, width=100, height=35, placeholder_text="Confirm password", show="*", corner_radius=20)
			self.pw2.pack(padx=20, pady=6, fill="x")

			self.show_var = ctk.BooleanVar(value=False)
			self.show_btn = ctk.CTkCheckBox(self, text="Show password", variable=self.show_var, command=self._toggle_show, corner_radius=20)
			self.show_btn.pack(padx=20, pady=4, anchor="w")

			self.create_btn = ctk.CTkButton(self, text="Create Account", command=self._create, corner_radius=20)
			self.create_btn.pack(pady=14)

		def _toggle_show(self):
			ch = "" if self.show_var.get() else "*"
			self.pw.configure(show=ch)
			self.pw2.configure(show=ch)

		def _create(self):
			u = self.username.get().strip()
			pharmacist_user_id = self.pharmacist_user_id.get().strip()
			p1 = self.pw.get()
			p2 = self.pw2.get()
			if not u or not p1:
				messagebox.showerror("Error", "Username and password are required.")
				return
			if not pharmacist_user_id:
				messagebox.showerror("Error", "Initial pharmacist user ID is required.")
				return
			if p1 != p2:
				messagebox.showerror("Error", "Passwords do not match.")
				return
			try:
				auth_service.create_initial_app_setup(conn, u, p1, pharmacist_user_id)
				messagebox.showinfo("Success", "Pharmacy account and initial pharmacist user created. Please log in.")
				self.destroy()
			except ValueError as e:
				messagebox.showerror("Error", str(e))
			except sqlite3.IntegrityError as e:
				messagebox.showerror("Error", f"Failed to create account: {e}")

	app = SetupWindow()
	app.mainloop()
