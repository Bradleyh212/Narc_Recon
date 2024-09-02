import sqlite3 #To use database
con = sqlite3.connect("narcotics_database.db") #Connecting our databse
import pandas as pd
from other_functions import create_narc_list, show_all_narcs_table

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


#Adding the dictionnarie into the database table
for upc, items in narc_list.items():
		drug_name, din, strength, form, pack_size = items

		cur.execute("""
            INSERT OR REPLACE INTO narcs 
            (upc, drug_name, din, strength, form, pack_size) 
            VALUES (?, ?, ?, ?, ?, ?)
            """, 
            (upc, drug_name, din, strength, form, pack_size))

show_all_narcs_table() # From other functions file to to show by name ascending (A to Z) 


def find_quantity(upc):
	cur.execute("SELECT * FROM narcs WHERE upc = upc")
	qty = cur.fetchone()[6] #Used index 6 as it is the index for the qty in the table
	return qty


con.commit()

