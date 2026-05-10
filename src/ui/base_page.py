import tkinter as tk

import customtkinter as ctk


class BasePage:
	main_background_color = "#1C1C1C"
	nav_and_header_background_color = "#181818"
	button_color = "#3B4B59"
	button_corner_radius = 20
	button_hover_color = "#468189"
	window_width = 1000
	window_height = 600
	header_font = ("Inter", 40)
	font = ("Inter", 30)

	def __init__(self, app=None, parent=None):
		self.app = app
		self.is_standalone = app is None
		if self.is_standalone:
			self.root = ctk.CTk()
			self.root.title("Narc Recon")
		else:
			self.root = app.root
		self.parent = parent if parent is not None else self.root

	def configure_root(self):
		ctk.set_appearance_mode("dark")
		ctk.set_default_color_theme("dark-blue")
		self.root.configure(fg_color=self.main_background_color)
		self.center_window()
		self.root.resizable(False, False)

	def center_window(self):
		window_width = self.root.winfo_screenwidth()
		window_height = self.root.winfo_screenheight()
		x = (window_width / 2) - (self.window_width / 2)
		y = (window_height / 2) - (self.window_height / 2)
		self.root.geometry(f'{self.window_width}x{self.window_height}+{int(x)}+{int(y)}')

	def create_shell_frames(self):
		self.header_frame = tk.Frame(
			self.parent,
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

		self.body_frame = ctk.CTkFrame(self.parent, width=1000, height=400)
		self.body_frame.grid(row=1, column=0, pady=(60, 0))
		self.body_frame.columnconfigure(0, weight=1)
		self.body_frame.columnconfigure(1, weight=1)
		self.body_frame.grid_propagate(False)
		self.body_frame.configure(fg_color=self.main_background_color)

		self.left_body_frame = ctk.CTkFrame(self.body_frame, width=500, height=400, corner_radius=20)
		self.left_body_frame.grid(row=0, column=0, sticky="w", padx=(60, 0), pady=(0, 200))
		self.left_body_frame.columnconfigure(0, weight=1)
		self.left_body_frame.columnconfigure(1, weight=1)
		self.left_body_frame.grid_propagate(False)

		self.right_body_frame = ctk.CTkFrame(self.body_frame, width=300, height=400, corner_radius=20)
		self.right_body_frame.grid(row=0, column=1, sticky="e", padx=(0, 60), pady=(0, 200))
		self.right_body_frame.grid_propagate(False)

	def create_title_label(self, title):
		page_title = ctk.CTkLabel(self.header_frame, text=title, font=self.header_font)
		page_title.grid(row=0, column=0, sticky="w", padx=(60, 0), pady=(10, 5))
		return page_title

	def on_focus_in(self, widget):
		widget.configure(border_color="#3B4B59")

	def on_focus_out(self, widget):
		widget.configure(border_color="#444")
