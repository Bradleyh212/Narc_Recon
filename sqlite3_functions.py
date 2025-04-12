from datetime import datetime
import pytz

import sqlite3
import pandas as pd
from prettytable import PrettyTable


con = sqlite3.connect("narcotics_database.db")
cur = con.cursor() # Create a cursor

audit_con = sqlite3.connect('audit_log.db')
audit_cur = audit_con.cursor()

def create_narcs_table():
	cur.execute("""CREATE TABLE IF NOT EXISTS narcs ( -- Create a table called narcs

	/* Added the ""IF NOT EXISTS" constraint to make sure i dont have to
	comment out create table (can run multiple time without "table already exist error") */

		din TEXT PRIMARY KEY, -- storing as text because of leading zero's,
		name TEXT NOT NULL,
		quantity INTEGER NOT NULL DEFAULT 0
	)
	""")

def create_narcs_details_table():
	cur.execute("""CREATE TABLE IF NOT EXISTS narcs_details (
		din TEXT NOT NULL, -- storing as text because of leading zero's,
		upc TEXT NOT NULL, -- storing as text because of leading zero's,
		strength TEXT,
		form TEXT NOT NULL,
		pack_size TEXT,
		PRIMARY KEY (din, upc, pack_size),
		FOREIGN KEY (din) REFERENCES drugs(din)
	)""")

def from_excel_to_sql():
	for din, details_list in narc_list.items():
		# Adding to narcs table
		drug_name = details_list[0]["name"]  # Assuming all entries under the same DIN have the same name
		cur.execute("INSERT OR IGNORE INTO narcs (din, name, quantity) VALUES (?, ?, ?)", (din, drug_name, 0))
		
		# Adding to narcs_details table
		for details in details_list:
			cur.execute("""
			INSERT OR IGNORE INTO narcs_details (din, upc, strength, form, pack_size)
			VALUES (?, ?, ?, ?, ?)
			""", (din, details["upc"], details["strength"], details["form"], details["pack_size"]))

def find_narcs_upc(upc):
	cur.execute("""
	SELECT n.din, n.name, n.quantity, nd.upc, nd.strength, nd.form, nd.pack_size
	FROM narcs n
	INNER JOIN narcs_details  nd ON n.din = nd.din WHERE nd.upc = ?""", (upc,))
	tup = cur.fetchall()
	return tup

def find_narcs_din(din):
	cur.execute("""
	SELECT n.din, n.name, n.quantity, nd.upc, nd.strength, nd.form, nd.pack_size
	FROM narcs n
	INNER JOIN narcs_details  nd ON n.din = nd.din WHERE nd.din = ?""", (din,))
	tup = cur.fetchall()
	return tup

def find_quantity(upc):
	cur.execute("SELECT * FROM narcs_details WHERE upc = ?", (upc, ))
	din = cur.fetchone()[0] #Used index 0 as it is the index for the din in the table narc_details
	cur.execute("SELECT * FROM narcs WHERE din = ?", (din, ))
	qty = cur.fetchone()[2] #Used index 2 as it is the index for the din in the table narcs
	return qty

def find_quantity_din(din):
	cur.execute("SELECT * FROM narcs WHERE din = ?", (din, ))
	qty = cur.fetchone()[2] #Used index 2 as it is the index for the din in the table narcs
	return qty

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

def create_narc_list():	
	df = pd.read_excel("med_sheet.xlsx", sheet_name="med_sheet")

	upc_list = df["Upc"].fillna(0).apply(lambda x: str(int(x)).zfill(12)).tolist()
	#print(upc_list)
	drug_name_list = df["Drug Name"].tolist()
	#print(drug_name_list)

	drug_din_list = df["DIN"].apply(lambda x: str(int(x)).zfill(8)).tolist() #make the din list, also fill the first numbers with zero
	# print(drug_din_list)

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

narc_list = create_narc_list()
create_narcs_table()
create_narcs_details_table()
from_excel_to_sql()

show_narcs_table()


con.commit()
audit_con.commit()


