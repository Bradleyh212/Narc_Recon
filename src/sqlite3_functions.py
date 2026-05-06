"""
Legacy compatibility module.

Production app code should use the focused service modules instead of importing
from this file. This module is kept temporarily for tests and old compatibility
callers while the remaining legacy coverage is migrated.

Do not add new dependencies on this module. Importing it is not neutral: it
opens a database connection and runs catalog initialization at import time.
"""

import os
import pytz
import sqlite3
from prettytable import PrettyTable
from audit_log_service import (
	add_to_audit_log as add_audit_log_entry,
	fetch_audit_log,
	get_audit_log_by_din_and_date as fetch_audit_log_by_din_and_date,
	get_reconciliation_log_by_date_range as fetch_reconciliation_log_by_date_range,
)
from auth import get_conn
import catalog_database_service
from inventory_service import (
	fetch_narcs_table,
	find_narcs_by_din,
	find_narcs_by_upc,
	find_quantity_by_din,
	find_quantity_by_upc,
)
import excel_import_service
from paths import get_db_path, get_excel_path
import schema_service
import user_service

# === Database Connection ===
con = sqlite3.connect(get_db_path())
cur = con.cursor()

# === Timezone ===
user_timezone = pytz.timezone('America/Toronto')

# === Create Tables ===

def create_narcs_table():
	return schema_service.create_narcs_table(cur)

def create_narcs_details_table():
	return schema_service.create_narcs_details_table(cur)

def create_audit_log_table():
	return schema_service.create_audit_log_table(cur)

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
	return user_service.add_user(get_conn(), user_id, role)

def get_user_role(user_id):
	return user_service.get_user_role(get_conn(), user_id)

def list_users():
	return user_service.list_users(get_conn())

def list_user_ids():
	return user_service.list_user_ids(get_conn())

def remove_user(user_id: str):
	return user_service.remove_user(get_conn(), user_id)

def user_exists(user_id: str) -> bool:
	return user_service.user_exists(get_conn(), user_id)

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
	catalog_database_service.initialize_database_from_excel(cur, con, get_excel_path())

	if debug is None:
		debug = should_debug_startup()
	if debug:
		show_narcs_table()
		show_audit_log()


# === Initialize All Tables and Data ===
initialize_database_from_excel()
