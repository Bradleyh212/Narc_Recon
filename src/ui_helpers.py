import customtkinter as ctk
from tkinter import messagebox

def safe_destroy(window):
	try:
		# Cancel all pending .after callbacks
		for after_id in window.tk.call("after", "info"):
			window.after_cancel(after_id)
	except Exception:
		pass
	window.destroy()

def create_nav_bar(parent_window, nav_frame, current_page, pages, button_color, button_corner_radius, button_hover_color):
	"""
	Create a consistent navigation bar with a dropdown for page switching and a Settings button.
	"""

	def on_select_page(choice):
		# Delay slightly so the dropdown animation feels smooth
		parent_window.after(180, lambda: (safe_destroy(parent_window), pages[choice]()))

	page_menu = ctk.CTkOptionMenu(
		nav_frame,
		values=list(pages.keys()),
		command=on_select_page,
		fg_color=button_color,
		button_color=button_color,
		corner_radius=20
		)
	page_menu._text_label.configure(padx=15)  # keeps text nicely centered
	page_menu.grid(row=0, column=0, padx=(10, 10))
	page_menu.set(current_page)  # highlight current page