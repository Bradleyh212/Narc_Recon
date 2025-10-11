from datetime import datetime, UTC
import pytz
import sqlite3
import pandas as pd
from prettytable import PrettyTable
from auth import get_conn

# === Database Connection ===
con = sqlite3.connect("narc_recon.db")
cur = con.cursor()

# === Timezone ===
user_timezone = pytz.timezone('America/Toronto')

# === Create Tables ===

def create_narcs_table():
	cur.execute("""
		CREATE TABLE IF NOT EXISTS narcs (
			din TEXT PRIMARY KEY,
			name TEXT NOT NULL,
			quantity INTEGER NOT NULL DEFAULT 0
		)
	""")

def create_narcs_details_table():
	cur.execute("""
		CREATE TABLE IF NOT EXISTS narcs_details (
			din TEXT NOT NULL,
			upc TEXT NOT NULL,
			strength TEXT,
			form TEXT NOT NULL,
			pack_size TEXT,
			PRIMARY KEY (din, upc, pack_size),
			FOREIGN KEY (din) REFERENCES narcs(din)
		)
	""")

def create_audit_log_table():
	cur.execute("""
		CREATE TABLE IF NOT EXISTS audit_log (
			log_id INTEGER PRIMARY KEY AUTOINCREMENT,
			din TEXT,
			old_qty INT,
			new_qty INT,
			Updated_By VARCHAR(10),
			Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			transaction_type TEXT,
			discrepancy INT
		)
	""")

# === Load Excel and Populate DB ===

def create_narc_list():
	df = pd.read_excel("med_sheet.xlsx", sheet_name="med_sheet")

	upc_list = df["Upc"].fillna(0).apply(lambda x: str(int(x)).zfill(12)).tolist()
	drug_name_list = df["Drug Name"].tolist()
	drug_din_list = df["DIN"].apply(lambda x: str(int(x)).zfill(8)).tolist()
	drug_strength_list = df["Strength"].tolist()
	drug_form_list = df["Form"].tolist()
	drug_pack_size_list = df["Pack size"].fillna(0).astype(int).tolist()

	narc_list = {}
	for i in range(len(upc_list)):
		if upc_list[i] == "000000000000":
			continue
		if drug_din_list[i] not in narc_list:
			narc_list[drug_din_list[i]] = []
		narc_list[drug_din_list[i]].append({
			"name": drug_name_list[i],
			"upc": upc_list[i],
			"strength": drug_strength_list[i],
			"form": drug_form_list[i],
			"pack_size": drug_pack_size_list[i]
		})
	return narc_list

def from_excel_to_sql(narc_list):
	for din, details_list in narc_list.items():
		drug_name = details_list[0]["name"]
		cur.execute("INSERT OR IGNORE INTO narcs (din, name, quantity) VALUES (?, ?, ?)", (din, drug_name, 0))

		for details in details_list:
			cur.execute("""
				INSERT OR IGNORE INTO narcs_details (din, upc, strength, form, pack_size)
				VALUES (?, ?, ?, ?, ?)
			""", (din, details["upc"], details["strength"], details["form"], details["pack_size"]))

# === Query Helpers ===

def find_narcs_upc(upc):
	cur.execute("""
		SELECT n.din, n.name, n.quantity, nd.upc, nd.strength, nd.form, nd.pack_size
		FROM narcs n
		INNER JOIN narcs_details nd ON n.din = nd.din
		WHERE nd.upc = ?
	""", (upc,))
	return cur.fetchall()

def find_narcs_din(din):
	cur.execute("""
		SELECT n.din, n.name, n.quantity, nd.upc, nd.strength, nd.form, nd.pack_size
		FROM narcs n
		INNER JOIN narcs_details nd ON n.din = nd.din
		WHERE nd.din = ?
	""", (din,))
	return cur.fetchall()

def find_quantity(upc):
	cur.execute("SELECT din FROM narcs_details WHERE upc = ?", (upc,))
	din = cur.fetchone()[0]
	return find_quantity_din(din)

def find_quantity_din(din):
	cur.execute("SELECT quantity FROM narcs WHERE din = ?", (din,))
	return cur.fetchone()[0]

# === User Functions ===

def add_user(user_id: str, role: str = "staff"):
	"""Add a new user to the users table."""
	con = get_conn()
	with con:
		con.execute(
			"INSERT INTO users (user_id, role, created_at) VALUES (?, ?, ?)",
			(user_id.strip(), role, datetime.now(UTC).isoformat())
		)

def list_users():
	"""Return all users as (id, user_id, role, created_at)."""
	con = get_conn()
	cur = con.cursor()
	return cur.execute("SELECT id, user_id, role, created_at FROM users ORDER BY id").fetchall()

def list_user_ids():
	conn = get_conn()
	rows = conn.execute("SELECT user_id FROM users").fetchall()
	return [row[0] for row in rows]

def remove_user(user_id: str):
	"""Remove a user by their user_id."""
	con = get_conn()
	with con:
		con.execute("DELETE FROM users WHERE user_id = ?", (user_id.strip(),))

def user_exists(user_id: str) -> bool:
	"""Check if a user already exists."""
	con = get_conn()
	cur = con.cursor()
	row = cur.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id.strip(),)).fetchone()
	return bool(row)

# === Audit Log Functions ===

def add_to_audit_log(din, old_qty, user, transaction_type):
	if not user_exists(user):
		print("Error: Invalid user ID.")
		return

	new_qty = find_quantity_din(din)
	formatted_time = datetime.now(pytz.utc).astimezone(user_timezone).strftime('%Y-%m-%d %H:%M:%S')
	discrepancy = new_qty - old_qty

	cur.execute("""
		INSERT INTO audit_log (din, old_qty, new_qty, Updated_By, Timestamp, transaction_type, discrepancy)
		VALUES (?, ?, ?, ?, ?, ?, ?)
	""", (din, old_qty, new_qty, user, formatted_time, transaction_type, discrepancy))
	con.commit()

def show_audit_log():
	cur.execute("SELECT * FROM audit_log")
	rows = cur.fetchall()

	column_names = [description[0] for description in cur.description]
	table = PrettyTable()
	table.field_names = column_names

	for row in rows:
		table.add_row(row)

	print(table)

def show_narcs_table():
	cur.execute("""
		SELECT n.din, n.name, n.quantity, nd.upc, nd.strength, nd.form, nd.pack_size
		FROM narcs n
		INNER JOIN narcs_details nd ON n.din = nd.din
	""")
	rows = cur.fetchall()

	column_names = [desc[0] for desc in cur.description]
	table = PrettyTable()
	table.field_names = column_names

	for row in rows:
		table.add_row(row)

	# print(table)


def get_audit_log_by_din_and_date(din, start_date, end_date):
	cur.execute("""
		SELECT din, old_qty, new_qty, Updated_By, Timestamp
		FROM audit_log
		WHERE din = ?
		AND date(Timestamp) BETWEEN ? AND ?
		ORDER BY Timestamp ASC
	""", (din, start_date, end_date))
	return cur.fetchall()

# Search for all reconciliation-type audit log entries between start_date and end_date.
def get_reconciliation_log_by_date_range(start_date, end_date):
	# name from narcs; strength from a single row per DIN
	cur.execute("""
		SELECT
			n.name,              -- 0
			nd.strength,         -- 1
			a.din,               -- 2
			a.old_qty,           -- 3
			a.new_qty,           -- 4
			a.discrepancy,       -- 5
			a.Timestamp          -- 6
		FROM audit_log a
		JOIN narcs n ON n.din = a.din
		LEFT JOIN (
			SELECT din, MIN(strength) AS strength
			FROM narcs_details
			GROUP BY din
		) nd ON nd.din = a.din
		WHERE a.transaction_type = 'reconciliation'
		  AND DATE(a.Timestamp) BETWEEN ? AND ?
		ORDER BY
			n.name COLLATE NOCASE,
			nd.strength COLLATE NOCASE,
			a.din,
			a.Timestamp
	""", (start_date, end_date))
	return cur.fetchall()

# === Initialize All Tables and Data ===

narc_list = create_narc_list()
create_narcs_table()
create_narcs_details_table()
create_audit_log_table()
from_excel_to_sql(narc_list)

# === Optional: Show Tables ===
show_narcs_table()
show_audit_log()

con.commit()