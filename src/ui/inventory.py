from tkinter import messagebox

from services import inventory_service
from ui.base_narcotic_page import BaseNarcoticPage
from ui.ui_helpers import create_nav_bar


class InventoryPage(BaseNarcoticPage):
	def __init__(self):
		super().__init__()
		self.configure_root()
		self.create_shell_frames()
		self.root.bind('<Return>', lambda event: self.search_narcs())

	def run(self):
		self.refresh_page()
		self.root.mainloop()

	def refresh_page(self):
		self.create_title_label("INVENTORY")
		self.create_nav()
		self.create_inventory_widgets()

	def create_nav(self):
		from ui.filling import open_filling_page
		from ui.receiving import open_receiving_page
		from ui.reconciliation import open_reconciliation_page
		from ui.report import open_report_page
		from ui.settings import open_settings_page

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
			"INVENTORY",
			pages,
			self.button_color,
			self.button_corner_radius,
			self.button_hover_color
		)

	def create_inventory_widgets(self):
		self.create_narcotic_search_controls()
		self.create_narcotic_display_labels()
		self.create_on_hand_display(
			label_padx=(80, 0),
			label_pady=(30, 15),
			output_padx=(80, 0),
			output_pady=(0, 50),
		)

	def search_narcs(self):
		search_input = self.meds_ent.get()
		self.meds_ent.delete(0, "end")

		if len(search_input) == 12:
			tup = inventory_service.find_narcs_by_upc(self.cur, search_input)
		elif len(search_input) == 8:
			tup = inventory_service.find_narcs_by_din(self.cur, search_input)
		else:
			messagebox.showerror("Error", "Drug not found")
			self.clear_display_fields()
			return

		if len(tup) == 1:
			self.display_narcotic_info(tup[0])
		elif len(tup) > 1:
			self.select_pack_size(tup)
		else:
			messagebox.showerror("Error", "Drug not found")
			self.clear_display_fields()


def open_inventory_page():
	InventoryPage().run()
