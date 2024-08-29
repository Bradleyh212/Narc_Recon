import sqlite3 #To use database
con = sqlite3.connect("narcotics_database.db") #Connecting our databse
import pandas as pd
from create_dictionnarie import create_narc_list

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
			pack_size INTEGER
			)

		""")


print()
#print(len(narc_list))
print()
#print(narc_list)

for upc, items in narc_list.items():
		drug_name, din, strength, form, pack_size = items

		cur.execute("""
            INSERT OR REPLACE INTO narcs 
            (upc, drug_name, din, strength, form, pack_size) 
            VALUES (?, ?, ?, ?, ?, ?)
            """, 
            (upc, drug_name, din, strength, form, pack_size))

cur.execute("SELECT * FROM narcs")

items = cur.fetchall()
for item in items:
	print(item)

con.commit()
con.close()

