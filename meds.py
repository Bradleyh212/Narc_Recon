import sqlite3 #To use database
con = sqlite3.connect("narcotics_database.db") #Connecting our databse
import pandas as pd
from other_functions import create_narc_list, show_all_narcs_table

narc_list = create_narc_list()

cur = con.cursor() # Create a cursor

cur.execute("""CREATE TABLE IF NOT EXISTS narcs ( -- Create a table called narcs

/* Added the ""IF NOT EXISTS" constraint to make sure i dont have to
comment out create table (can run multiple time without "table already exist error") */

			upc TEXT PRIMARY KEY, -- storing as text because of leading zero's,
			drug_name TEXT,
			din TEXT, -- storing as text because of leading zero's
			strength TEXT,
			form TEXT,
			pack_size INTEGER,
			Quantity INT NOT NULL DEFAULT 0, --Added the qty part of the table
			Last_Updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, --Create a time_stamp to know when changes are made
			Updated_By VARCHAR(10)
			)

		""")

#Adding the dictionnarie into the database table
for upc, items in narc_list.items():
		drug_name, din, strength, form, pack_size = items

		cur.execute("""
            INSERT OR REPLACE INTO narcs 
            (upc, drug_name, din, strength, form, pack_size) 
            VALUES (?, ?, ?, ?, ?, ?)
            """, 
            (upc, drug_name, din, strength, form, pack_size))

show_all_narcs_table()


def find_quantity(upc):
	cur.execute("SELECT upc FROM narcs")
	qty = cur.fetchone(upc)
	return qty





con.commit()
con.close()

