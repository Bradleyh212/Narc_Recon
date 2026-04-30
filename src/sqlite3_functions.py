from datetime import datetime, UTC
import os
import pytz
import sqlite3
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
import excel_import_service
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

REQUIRED_EXCEL_COLUMNS = excel_import_service.REQUIRED_EXCEL_COLUMNS


def validate_excel_columns(df):
	return excel_import_service.validate_excel_columns(df)


def normalize_din(value):
	return excel_import_service.normalize_din(value)


def normalize_upc(value):
	return excel_import_service.normalize_upc(value)


def validate_excel_rows(df):
	return excel_import_service.validate_excel_rows(df)


def create_narc_list():
	return excel_import_service.create_narc_list(get_excel_path())

def from_excel_to_sql(narc_list):
	return excel_import_service.from_excel_to_sql(cur, narc_list)

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
