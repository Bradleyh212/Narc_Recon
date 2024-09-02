import sqlite3 #To use database
con = sqlite3.connect("narcotics_database.db") #Connecting our databse
import pandas as pd
from other_functions import create_narc_list, show_narcs_table

narc_list = create_narc_list()

cur = con.cursor() # Create a cursor

cur.execute("""CREATE TABLE IF NOT EXISTS narcs ( -- Create a table called narcs

/* Added the ""IF NOT EXISTS" constraint to make sure i dont have to
comment out create table (can run multiple time without "table already exist error") */

	din TEXT PRIMARY KEY, -- storing as text because of leading zero's,
	name TEXT NOT NULL,
	quantity INTEGER NOT NULL DEFAULT 0
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS narcs_details (
	din TEXT NOT NULL, -- storing as text because of leading zero's,
	upc TEXT NOT NULL, -- storing as text because of leading zero's,
	strength TEXT,
	form TEXT NOT NULL,
	pack_size TEXT,
	PRIMARY KEY (din, upc, pack_size),
	FOREIGN KEY (din) REFERENCES drugs(din)
)
""")

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



def find_narcs_upcs(upc):
	cur.execute("""
	SELECT n.din, n.name, n.quantity, nd.upc, nd.strength, nd.form, nd.pack_size
	FROM narcs n
	INNER JOIN narcs_details  nd ON n.din = nd.din WHERE nd.upc = ?""", (upc,))
	tup = cur.fetchall()
	return tup

print(find_narcs_upcs("63691082762"))


def find_quantity(upc):
	cur.execute("SELECT * FROM narcs WHERE upc = upc")
	qty = cur.fetchone()[6] #Used index 6 as it is the index for the qty in the table
	return qty

#show_narcs_table()


con.commit()

