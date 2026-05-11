from ui.base_narcotic_page import BaseNarcoticPage
from ui.ui_helpers import create_nav_bar


class InventoryPage(BaseNarcoticPage):
	def __init__(self, app=None, parent=None):
		super().__init__(app=app, parent=parent)
		if self.is_standalone:
			self.configure_root()
		self.create_shell_frames()
		self.root.bind('<Return>', lambda event: self.search_narcs())

	def run(self):
		self.refresh_page()
		if self.is_standalone:
			self.root.mainloop()

	def refresh_page(self):
		self.create_title_label("INVENTORY")
		self.create_nav()
		self.create_inventory_widgets()

	def create_nav(self):
		create_nav_bar(
			self.root,
			self.nav_frame,
			"INVENTORY",
			self.button_color,
			self.button_corner_radius,
			self.button_hover_color,
			app=self.app
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

def open_inventory_page():
	InventoryPage().run()
