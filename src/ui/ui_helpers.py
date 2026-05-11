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

def get_standalone_pages():
	from ui.inventory import open_inventory_page
	from ui.filling import open_filling_page
	from ui.receiving import open_receiving_page
	from ui.reconciliation import open_reconciliation_page
	from ui.report import open_report_page
	from ui.settings import open_settings_page

	return {
		"INVENTORY": open_inventory_page,
		"FILLING": open_filling_page,
		"RECEIVING": open_receiving_page,
		"RECONCILIATION": open_reconciliation_page,
		"REPORT": open_report_page,
		"SETTINGS": open_settings_page,
	}

def safe_destroy(window):
	try:
		# Cancel all pending .after callbacks
		for after_id in window.tk.call("after", "info"):
			window.after_cancel(after_id)
	except Exception:
		pass
	window.destroy()

def _open_settings_guard(parent_window, app=None, pages=None):
	user_id = simpledialog.askstring("Access required", "Enter your user ID:", parent=parent_window)
	if not user_id:
		return  # user cancelled

	role = user_service.get_user_role(get_conn(), user_id)
	if user_service.role_allows_settings(role):
		# Go to settings like other pages
		if app is not None and "SETTINGS" in app.page_classes:
			parent_window.after(120, lambda: app.show_page("SETTINGS"))
		else:
			fallback_pages = pages or get_standalone_pages()
			parent_window.after(120, lambda: (safe_destroy(parent_window), fallback_pages["SETTINGS"]()))
	else:
		messagebox.showerror("Access denied", "Settings are restricted to pharmacists.")

def open_nav_choice(parent_window, choice, app=None, pages=None):
	if choice == "SETTINGS":
		_open_settings_guard(parent_window, app=app, pages=pages)
		return

	if app is not None and choice in app.page_classes:
		parent_window.after(180, lambda: app.show_page(choice))
		return

	fallback_pages = pages or get_standalone_pages()
	# Delay slightly so the dropdown animation feels smooth
	parent_window.after(180, lambda: (safe_destroy(parent_window), fallback_pages[choice]()))

def create_nav_bar(parent_window, nav_frame, current_page, button_color, button_corner_radius, button_hover_color, app=None, pages=None):
	def on_select_page(choice):
		open_nav_choice(parent_window, choice, app=app, pages=pages)

	page_choices = list(pages.keys()) if pages is not None else list(PAGE_CHOICES)

	page_menu = ctk.CTkOptionMenu(
		nav_frame,
		values=page_choices,
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
		command=lambda: _open_settings_guard(parent_window, app=app, pages=pages)
	)
	settings_btn.grid(row=0, column=1, padx=(10, 60))
