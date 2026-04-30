from collections import Counter
from datetime import datetime, UTC
import os
import pytz
import sqlite3
import pandas as pd
from prettytable import PrettyTable
from audit_log_service import (
	add_to_audit_log as add_audit_log_entry,
	create_audit_log_table as create_audit_log_table_schema,
	fetch_audit_log,
	get_audit_log_by_din_and_date as fetch_audit_log_by_din_and_date,
	get_reconciliation_log_by_date_range as fetch_reconciliation_log_by_date_range,
)
from auth import get_conn
from inventory_service import (
	fetch_narcs_table,
	find_narcs_by_din,
	find_narcs_by_upc,
	find_quantity_by_din,
	find_quantity_by_upc,
)
from paths import get_db_path, get_excel_path

# === Database Connection ===
con = sqlite3.connect(get_db_path())
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
	return create_audit_log_table_schema(cur)

# === Load Excel and Populate DB ===

REQUIRED_EXCEL_COLUMNS = ("Drug Name", "DIN", "Strength", "Form", "Upc", "Pack size")


def validate_excel_columns(df):
	missing_columns = [column for column in REQUIRED_EXCEL_COLUMNS if column not in df.columns]
	if missing_columns:
		raise ValueError("Missing required Excel columns: " + ", ".join(missing_columns))


def normalize_din(value):
	return str(int(value)).zfill(8)


def normalize_upc(value):
	if pd.isna(value):
		value = 0
	return str(int(value)).zfill(12)


def validate_excel_rows(df):
	validate_excel_columns(df)

	blank_upc_rows = []
	normalized_upcs = []
	normalized_dins = []
	warnings = []

	for row_number, (_, row) in enumerate(df.iterrows(), start=2):
		try:
			upc = normalize_upc(row["Upc"])
			if upc == "000000000000":
				blank_upc_rows.append(row_number)
			else:
				normalized_upcs.append(upc)
		except (TypeError, ValueError):
			warnings.append(f"Row {row_number} has an invalid UPC value.")

		try:
			normalized_dins.append(normalize_din(row["DIN"]))
		except (TypeError, ValueError):
			warnings.append(f"Row {row_number} has an invalid DIN value.")

	duplicate_upcs = sorted(upc for upc, count in Counter(normalized_upcs).items() if count > 1)
	duplicate_dins = sorted(din for din, count in Counter(normalized_dins).items() if count > 1)

	if blank_upc_rows:
		warnings.append(f"{len(blank_upc_rows)} row(s) have blank UPC values and will be skipped.")
	if duplicate_upcs:
		warnings.append("Duplicate UPC values found: " + ", ".join(duplicate_upcs))

	return {
		"blank_upc_count": len(blank_upc_rows),
		"blank_upc_rows": blank_upc_rows,
		"duplicate_upcs": duplicate_upcs,
		"duplicate_dins": duplicate_dins,
		"warnings": warnings,
	}


def create_narc_list():
	df = pd.read_excel(get_excel_path(), sheet_name="med_sheet")
	validate_excel_columns(df)

	upc_list = df["Upc"].apply(normalize_upc).tolist()
	drug_name_list = df["Drug Name"].tolist()
	drug_din_list = df["DIN"].apply(normalize_din).tolist()
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
	return find_narcs_by_upc(cur, upc)

def find_narcs_din(din):
	return find_narcs_by_din(cur, din)

def find_quantity(upc):
	return find_quantity_by_upc(cur, upc)

def find_quantity_din(din):
	return find_quantity_by_din(cur, din)

# === User Functions ===

def add_user(user_id: str, role: str = "Assistant"):
	"""Add a new user to the users table."""
	con = get_conn()
	with con:
		con.execute(
			"INSERT INTO users (user_id, role, created_at) VALUES (?, ?, ?)",
			(user_id.strip(), role, datetime.now(UTC).isoformat())
		)

def get_user_role(user_id):
	"""Add a new user to the users table."""
	con = get_conn()
	row = con.execute("SELECT role FROM users where user_id = ?", (user_id.strip(),)).fetchone()
	return row[0] if row else None

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
	return add_audit_log_entry(
		cur,
		con,
		din,
		old_qty,
		user,
		transaction_type,
		user_exists,
		find_quantity_din,
		user_timezone,
	)

def show_audit_log():
	column_names, rows = fetch_audit_log(cur)
	table = PrettyTable()
	table.field_names = column_names

	for row in rows:
		table.add_row(row)

	print(table)

def show_narcs_table():
	column_names, rows = fetch_narcs_table(cur)
	table = PrettyTable()
	table.field_names = column_names

	for row in rows:
		table.add_row(row)

	# print(table)


def get_audit_log_by_din_and_date(din, start_date, end_date):
	return fetch_audit_log_by_din_and_date(cur, din, start_date, end_date)

# Search for all reconciliation-type audit log entries between start_date and end_date.
def get_reconciliation_log_by_date_range(start_date, end_date):
	return fetch_reconciliation_log_by_date_range(cur, start_date, end_date)

def should_debug_startup():
	return os.environ.get("NARC_RECON_DEBUG_STARTUP") == "1"


def initialize_database_from_excel(debug=None):
	narc_list = create_narc_list()
	create_narcs_table()
	create_narcs_details_table()
	create_audit_log_table()
	from_excel_to_sql(narc_list)

	if debug is None:
		debug = should_debug_startup()
	if debug:
		show_narcs_table()
		show_audit_log()

	con.commit()


# === Initialize All Tables and Data ===
initialize_database_from_excel()
