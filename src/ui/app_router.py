import customtkinter as ctk

from ui.base_page import BasePage
from ui.inventory import InventoryPage


class AppRouter:
	page_classes = {
		"INVENTORY": InventoryPage,
	}

	def __init__(self, initial_page="INVENTORY"):
		self.root = ctk.CTk()
		self.root.title("Narc Recon")
		self.configure_root()
		self.create_page_container()
		self.current_page = None
		self.show_page(initial_page)

	def configure_root(self):
		ctk.set_appearance_mode("dark")
		ctk.set_default_color_theme("dark-blue")
		self.root.configure(fg_color=BasePage.main_background_color)
		self.center_window()
		self.root.resizable(False, False)

	def center_window(self):
		window_width = self.root.winfo_screenwidth()
		window_height = self.root.winfo_screenheight()
		x = (window_width / 2) - (BasePage.window_width / 2)
		y = (window_height / 2) - (BasePage.window_height / 2)
		self.root.geometry(f'{BasePage.window_width}x{BasePage.window_height}+{int(x)}+{int(y)}')

	def create_page_container(self):
		self.page_container = ctk.CTkFrame(
			self.root,
			width=BasePage.window_width,
			height=BasePage.window_height,
			fg_color=BasePage.main_background_color,
		)
		self.page_container.grid(row=0, column=0)
		self.page_container.grid_propagate(False)

	def show_page(self, page_name):
		page_class = self.page_classes[page_name]
		for widget in self.page_container.winfo_children():
			widget.destroy()
		self.current_page = page_class(app=self, parent=self.page_container)
		self.current_page.run()

	def run(self):
		self.root.mainloop()
