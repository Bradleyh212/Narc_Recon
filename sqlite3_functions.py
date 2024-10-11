from datetime import datetime
import pytz

import sqlite3
from prettytable import PrettyTable

con = sqlite3.connect("narcotics_database.db")
cur = con.cursor() # Create a cursor

audit_con = sqlite3.connect('audit_log.db')
audit_cur = audit_con.cursor()

def create_narcs_table():
		audit_cur.execute("""CREATE TABLE IF NOT EXISTS audit_log (
	    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
	    din TEXT,
	    odl_qty INT,
	    new_qty INT,
	    Updated_By VARCHAR(10),
	    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	)""")

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

