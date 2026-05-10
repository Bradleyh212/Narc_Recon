import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

import customtkinter as ctk

from db.connection import get_conn
from services import inventory_service
from services import user_service
from ui.base_page import BasePage


class BaseNarcoticPage(BasePage):
	store_search_input = False
	search_error_focus_attr = None

	def __init__(self, app=None, parent=None):
		super().__init__(app=app, parent=parent)
		self.con = get_conn()
		self.cur = self.con.cursor()

	def create_narcotic_search_controls(self):
		self.meds_ent = ctk.CTkEntry(
			self.left_body_frame,
			placeholder_text="Enter upc or din",
			width=200,
			font=self.font,
			justify="center",
			corner_radius=20,
		)
		self.meds_ent.grid(row=0, column=0, sticky="ew", pady=30, padx=10)
		self.meds_ent.focus()
		self.meds_ent.bind("<FocusIn>", lambda event: self.on_focus_in(self.meds_ent))
		self.meds_ent.bind("<FocusOut>", lambda event: self.on_focus_out(self.meds_ent))

		search_btn = ctk.CTkButton(
			self.left_body_frame,
			text="SEARCH",
			command=self.search_narcs,
			width=100,
			fg_color=self.button_color,
			corner_radius=self.button_corner_radius,
			hover_color=self.button_hover_color,
		)
		search_btn.grid(row=0, column=1, sticky="ew", pady=20, padx=10)

	def create_narcotic_display_labels(self):
		self.name_lbl_output = ctk.CTkLabel(self.left_body_frame, font=self.font, text="")
		self.name_lbl_output.grid(row=2, columnspan=2, pady=(20, 0))

		self.din__med_output = ctk.CTkLabel(self.left_body_frame, font=self.font, text="")
		self.din__med_output.grid(row=3, columnspan=2, pady=(20, 0))

		self.strength_lbl_output = ctk.CTkLabel(self.left_body_frame, font=self.font, text="")
		self.strength_lbl_output.grid(row=4, columnspan=2, pady=(20, 0))

		self.drug_form_output = ctk.CTkLabel(self.left_body_frame, font=self.font, text="")
		self.drug_form_output.grid(row=5, columnspan=2, pady=(20, 0))

		self.pack_med_output = ctk.CTkLabel(self.left_body_frame, font=self.font, text="")
		self.pack_med_output.grid(row=6, columnspan=2, pady=(20, 0))

	def create_on_hand_display(
		self,
		label_padx=None,
		label_pady=(30, 0),
		output_padx=None,
		output_pady=(0, 50),
	):
		qty_med_lbl = ctk.CTkLabel(self.right_body_frame, text="ON HAND", width=10, font=self.font)
		label_grid_options = {"row": 1, "pady": label_pady}
		if label_padx is not None:
			label_grid_options["padx"] = label_padx
		qty_med_lbl.grid(**label_grid_options)

		self.qty_med_output = ctk.CTkLabel(self.right_body_frame, width=10, font=self.font, text="")
		output_grid_options = {"row": 2, "pady": output_pady}
		if output_padx is not None:
			output_grid_options["padx"] = output_padx
		self.qty_med_output.grid(**output_grid_options)

	def ask_user_id(self):
		while True:
			user_id = simpledialog.askstring("Input", "Please enter your user ID:", parent=self.root)

			# If cancelled or closed
			if user_id is None:
				messagebox.showinfo("Cancelled", "Operation cancelled")
				return None

			# If user exists in DB
			if user_service.user_exists(get_conn(), user_id.strip()):
				return user_id.strip()

			# If invalid
			messagebox.showerror("Error", "Please enter a valid user ID")

	def search_narcs(self):
		search_input = self.meds_ent.get()
		self.meds_ent.delete(0, "end")

		if self.store_search_input:
			self.search_input = search_input

		if len(search_input) == 12:
			tup = inventory_service.find_narcs_by_upc(self.cur, search_input)
		elif len(search_input) == 8:
			tup = inventory_service.find_narcs_by_din(self.cur, search_input)
		else:
			messagebox.showerror("Error", "Drug not found")
			self.handle_search_error()
			return

		if len(tup) == 1:
			self.display_narcotic_info(tup[0])
		elif len(tup) > 1:
			self.select_pack_size(tup)
		else:
			messagebox.showerror("Error", "Drug not found")
			self.handle_search_error()

	def handle_search_error(self):
		if self.search_error_focus_attr is not None:
			getattr(self, self.search_error_focus_attr).focus()
			self.meds_ent.focus()
		self.clear_display_fields()

	def search_narc_din(self, din):
		tup = inventory_service.find_narcs_by_din(self.cur, din)
		self.name_lbl_output.configure(text=tup[0][1])
		self.din__med_output.configure(text=tup[0][0])
		self.strength_lbl_output.configure(text=tup[0][4])
		self.drug_form_output.configure(text=tup[0][5])
		self.pack_med_output.configure(text="PACK SIZE " + tup[0][6])
		self.qty_med_output.configure(text=inventory_service.find_quantity_by_upc(self.cur, tup[0][3]))

	def display_narcotic_info(self, narc):
		self.name_lbl_output.configure(text=narc[1])
		self.din__med_output.configure(text=narc[0])
		self.strength_lbl_output.configure(text=narc[4])
		self.drug_form_output.configure(text=narc[5])
		self.pack_med_output.configure(text="PACK SIZE " + narc[6])
		self.qty_med_output.configure(text=inventory_service.find_quantity_by_upc(self.cur, narc[3]))

	def clear_display_fields(self):
		self.name_lbl_output.configure(text="")
		self.din__med_output.configure(text="")
		self.strength_lbl_output.configure(text="")
		self.drug_form_output.configure(text="")
		self.pack_med_output.configure(text="")
		self.qty_med_output.configure(text="")

	def select_pack_size(self, tup):
		choice_window = tk.Toplevel(self.root)
		choice_window.title("Choose Pack Size")
		choice_window.geometry("400x100")
		choice_window.wm_attributes("-topmost", True)

		tk.Label(choice_window, text="Choose the pack size:").pack()

		pack_size = tk.StringVar()
		pack_size_dropdown = ttk.Combobox(choice_window, textvariable=pack_size)
		pack_size_dropdown['values'] = [f"{item[6]} units - {item[4]} {item[5]}" for item in tup]
		pack_size_dropdown.pack()

		def on_select_pack_size():
			selected_index = pack_size_dropdown.current()
			selected_pack = tup[selected_index]
			self.display_narcotic_info(selected_pack)
			choice_window.destroy()

		select_btn = tk.Button(choice_window, text="Select", command=on_select_pack_size)
		select_btn.pack()
