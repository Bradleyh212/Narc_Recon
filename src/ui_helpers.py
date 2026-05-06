import customtkinter as ctk
from tkinter import messagebox, simpledialog
from auth import get_conn
from services import user_service

def safe_destroy(window):
	try:
		# Cancel all pending .after callbacks
		for after_id in window.tk.call("after", "info"):
			window.after_cancel(after_id)
	except Exception:
		pass
	window.destroy()

def _open_settings_guard(parent_window):
	from settings import open_settings_page

	user_id = simpledialog.askstring("Access required", "Enter your user ID:", parent=parent_window)
	if not user_id:
		return  # user cancelled

	role = user_service.get_user_role(get_conn(), user_id)
	if user_service.role_allows_settings(role):
		# Go to settings like other pages
		parent_window.after(120, lambda: (safe_destroy(parent_window), open_settings_page()))
	else:
		messagebox.showerror("Access denied", "Settings are restricted to pharmacists.")

def open_nav_choice(parent_window, pages, choice):
	if choice == "SETTINGS":
		_open_settings_guard(parent_window)
		return

	# Delay slightly so the dropdown animation feels smooth
	parent_window.after(180, lambda: (safe_destroy(parent_window), pages[choice]()))

def create_nav_bar(parent_window, nav_frame, current_page, pages, button_color, button_corner_radius, button_hover_color):
	def on_select_page(choice):
		open_nav_choice(parent_window, pages, choice)

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

	# Seperate settins button
	settings_btn = ctk.CTkButton(
		nav_frame,
		text="SETTINGS",
		width=80,
		fg_color=button_color,
		corner_radius=button_corner_radius,
		hover_color=button_hover_color,
		command=lambda: _open_settings_guard(parent_window)
	)
	settings_btn.grid(row=0, column=1, padx=(10, 60))
