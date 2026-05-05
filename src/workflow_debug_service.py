from prettytable import PrettyTable

import audit_log_service
from auth import get_conn
import inventory_service


def show_narcs_table():
	connection = get_conn()
	try:
		column_names, rows = inventory_service.fetch_narcs_table(connection.cursor())
		table = PrettyTable()
		table.field_names = column_names

		for row in rows:
			table.add_row(row)
	finally:
		connection.close()


def show_audit_log():
	connection = get_conn()
	try:
		column_names, rows = audit_log_service.fetch_audit_log(connection.cursor())
		table = PrettyTable()
		table.field_names = column_names

		for row in rows:
			table.add_row(row)

		print(table)
	finally:
		connection.close()
