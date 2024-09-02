import sqlite3 #To use database
con = sqlite3.connect("narcotics_database.db") #Connecting our databse
import pandas as pd

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

def show_all_narcs_table():
	cur.execute("SELECT * FROM narcs ORDER BY name ASC")
	items = cur.fetchall()
	'''print("Upc          | Name|") #WILL DO LATE FOR BETTER FORMATTING
				print("------         ---------"             )'''
	for i in range(len(items)):
		print(f"{items[i][0]} | {items[i][1]}| {items[i][2]} | {items[i][3]} | {items[i][4]} | {items[i][5]} | {items[i][6]} | {items[i][7]}| {items[i][8]}")
