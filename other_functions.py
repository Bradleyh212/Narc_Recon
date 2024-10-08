import sqlite3 #To use database
con = sqlite3.connect("narcotics_database.db") #Connecting our databse
import pandas as pd
from prettytable import PrettyTable

cur = con.cursor() # Create a cursor


def create_narc_list():	
	df = pd.read_excel("Sheet1.xlsx", sheet_name="Sheet1")

	upc_list = df["Upc"].fillna(0).apply(lambda x: str(int(x)).zfill(12)).tolist()
	#print(upc_list)
	drug_name_list = df["Drug Name"].tolist()
	#print(drug_name_list)

	drug_din_list = df["DIN"].apply(lambda x: str(int(x)).zfill(8)).tolist() #make the din list, also fill the first numbers with zero
	#print(drug_din_list)mm

	drug_stregth_list = df["Strength"].tolist()
	#print(drug_stregth_list)

	drug_form_list = df["Form"].tolist()
	#print(drug_form_list)

	drug_pack_size_list = df["Pack size"].fillna(0).astype(int).tolist()
	#print(drug_pack_size_list)

	narc_list = {}
	for i in range(len(upc_list)):
		if (upc_list[i]=="000000000000"):
			pass
		else:
			if drug_din_list[i] not in narc_list:
				narc_list[drug_din_list[i]] = []
			# Append the details for the UPC to the DIN entry
			narc_list[drug_din_list[i]].append({
				"name": drug_name_list[i],
				"upc": upc_list[i],
				"strength": drug_stregth_list[i],
				"form": drug_form_list[i],
				"pack_size": drug_pack_size_list[i]
			})
	return narc_list

def show_narcs_table():
	cur.execute("""
	SELECT n.din, n.name, n.quantity, nd.upc, nd.strength, nd.form, nd.pack_size
	FROM narcs n
	INNER JOIN narcs_details  nd ON n.din = nd.din
	""")

	rows = cur.fetchall()

	column_names = []
	for description in cur.description:
		column_names.append(description[0])


	table = PrettyTable()

	table.field_names = column_names

	for row in rows:
		table.add_row(row)

	print(table)



'''add_qty_ent = tk.Entry(main_page_window, fg = "white", bg = "black", width = 70, font = font, justify="center")
add_qty_ent.pack()

add_btn = ttk.Button(main_page_window, text = "Add Quantity", style='TButton', command=lambda: add_quantity(add_qty_ent.get(), meds_ent.get()))
add_btn.pack()'''




con.commit()







