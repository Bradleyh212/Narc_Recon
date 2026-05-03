import sqlite3_functions


def add_to_audit_log(din, old_qty, user, transaction_type):
	return sqlite3_functions.add_to_audit_log(din, old_qty, user, transaction_type)
