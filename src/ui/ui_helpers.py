import customtkinter as ctk
from tkinter import messagebox, simpledialog
from db.connection import get_conn
from services import user_service

PAGE_CHOICES = (
	"INVENTORY",
	"FILLING",
	"RECEIVING",
	"RECONCILIATION",
	"REPORT",
	"SETTINGS",
)

def _open_settings_guard(parent_window, app):
	user_id = simpledialog.askstring("Access required", "Enter your user ID:", parent=parent_window)
	if not user_id:
		return  # user cancelled

	role = user_service.get_user_role(get_conn(), user_id)
	if user_service.role_allows_settings(role):
		# Go to settings like other pages
		parent_window.after(120, lambda: app.show_page("SETTINGS"))
	else:
		messagebox.showerror("Access denied", "Settings are restricted to pharmacists.")

def open_nav_choice(parent_window, choice, app):
	if choice == "SETTINGS":
		_open_settings_guard(parent_window, app=app)
		return

	# Delay slightly so the dropdown animation feels smooth
	parent_window.after(180, lambda: app.show_page(choice))

def create_nav_bar(parent_window, nav_frame, current_page, button_color, button_corner_radius, button_hover_color, app):
	def on_select_page(choice):
		open_nav_choice(parent_window, choice, app=app)

	page_menu = ctk.CTkOptionMenu(
		nav_frame,
		values=list(PAGE_CHOICES),
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
		command=lambda: _open_settings_guard(parent_window, app=app)
	)
	settings_btn.grid(row=0, column=1, padx=(10, 60))
