"""
Legacy compatibility shim.

Production app code should use the focused service modules instead of importing
from this file. This module is kept temporarily for old compatibility callers
while the remaining legacy facade usage is retired.

Importing this module is intentionally passive: it does not open a database
connection, create tables, or import the Excel catalog.
"""

import os

import pytz
from prettytable import PrettyTable

from auth import get_conn
from db import catalog_database_service
from db import schema_service
from config.paths import get_excel_path
from services import audit_log_service
from services import excel_import_service
from services import inventory_service
from services import user_service


user_timezone = pytz.timezone("America/Toronto")
REQUIRED_EXCEL_COLUMNS = excel_import_service.REQUIRED_EXCEL_COLUMNS


def _with_connection(callback):
	connection = get_conn()
	try:
		return callback(connection)
	finally:
		connection.close()


def _with_cursor(callback):
	return _with_connection(lambda connection: callback(connection.cursor(), connection))


def create_narcs_table():
	return _with_cursor(lambda cursor, _connection: schema_service.create_narcs_table(cursor))


def create_narcs_details_table():
	return _with_cursor(lambda cursor, _connection: schema_service.create_narcs_details_table(cursor))


def create_audit_log_table():
	return _with_cursor(lambda cursor, _connection: schema_service.create_audit_log_table(cursor))


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
	def import_rows(cursor, connection):
		excel_import_service.from_excel_to_sql(cursor, narc_list)
		connection.commit()

	return _with_cursor(import_rows)


def find_narcs_upc(upc):
	return _with_cursor(lambda cursor, _connection: inventory_service.find_narcs_by_upc(cursor, upc))


def find_narcs_din(din):
	return _with_cursor(lambda cursor, _connection: inventory_service.find_narcs_by_din(cursor, din))


def find_quantity(upc):
	return _with_cursor(lambda cursor, _connection: inventory_service.find_quantity_by_upc(cursor, upc))


def find_quantity_din(din):
	return _with_cursor(lambda cursor, _connection: inventory_service.find_quantity_by_din(cursor, din))


def add_user(user_id: str, role: str = "Assistant"):
	return _with_connection(lambda connection: user_service.add_user(connection, user_id, role))


def get_user_role(user_id):
	return _with_connection(lambda connection: user_service.get_user_role(connection, user_id))


def list_users():
	return _with_connection(user_service.list_users)


def list_user_ids():
	return _with_connection(user_service.list_user_ids)


def remove_user(user_id: str):
	return _with_connection(lambda connection: user_service.remove_user(connection, user_id))


def user_exists(user_id: str) -> bool:
	return _with_connection(lambda connection: user_service.user_exists(connection, user_id))


def add_to_audit_log(din, old_qty, user, transaction_type):
	def write_audit_entry(cursor, connection):
		return audit_log_service.add_to_audit_log(
			cursor,
			connection,
			din,
			old_qty,
			user,
			transaction_type,
			lambda user_id: user_service.user_exists(connection, user_id),
			lambda narc_din: inventory_service.find_quantity_by_din(cursor, narc_din),
			user_timezone,
		)

	return _with_cursor(write_audit_entry)


def show_audit_log():
	def print_audit_table(cursor, _connection):
		column_names, rows = audit_log_service.fetch_audit_log(cursor)
		table = PrettyTable()
		table.field_names = column_names

		for row in rows:
			table.add_row(row)

		print(table)

	return _with_cursor(print_audit_table)


def show_narcs_table():
	def build_narcs_table(cursor, _connection):
		column_names, rows = inventory_service.fetch_narcs_table(cursor)
		table = PrettyTable()
		table.field_names = column_names

		for row in rows:
			table.add_row(row)

	return _with_cursor(build_narcs_table)


def get_audit_log_by_din_and_date(din, start_date, end_date):
	return _with_cursor(
		lambda cursor, _connection: audit_log_service.get_audit_log_by_din_and_date(
			cursor,
			din,
			start_date,
			end_date,
		)
	)


def get_reconciliation_log_by_date_range(start_date, end_date):
	return _with_cursor(
		lambda cursor, _connection: audit_log_service.get_reconciliation_log_by_date_range(
			cursor,
			start_date,
			end_date,
		)
	)


def should_debug_startup():
	return os.environ.get("NARC_RECON_DEBUG_STARTUP") == "1"


def initialize_database_from_excel(debug=None):
	def initialize(cursor, connection):
		catalog_database_service.initialize_database_from_excel(cursor, connection, get_excel_path())

	return_value = _with_cursor(initialize)

	if debug is None:
		debug = should_debug_startup()
	if debug:
		show_narcs_table()
		show_audit_log()

	return return_value
