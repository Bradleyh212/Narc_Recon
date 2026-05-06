from datetime import datetime
import sqlite3

import pytz

from services import audit_log_service


class CommitTrackingConnection:
	def __init__(self, connection):
		self.connection = connection
		self.commit_count = 0

	def commit(self):
		self.commit_count += 1
		self.connection.commit()


def make_audit_connection():
	connection = sqlite3.connect(":memory:")
	connection.execute("""
		CREATE TABLE narcs (
			din TEXT PRIMARY KEY,
			name TEXT NOT NULL,
			quantity INTEGER NOT NULL DEFAULT 0
		)
	""")
	connection.execute("""
		CREATE TABLE narcs_details (
			din TEXT NOT NULL,
			upc TEXT NOT NULL,
			strength TEXT,
			form TEXT NOT NULL,
			pack_size TEXT,
			PRIMARY KEY (din, upc, pack_size),
			FOREIGN KEY (din) REFERENCES narcs(din)
		)
	""")
	audit_log_service.AuditLogService(connection.cursor()).create_table()
	connection.execute(
		"INSERT INTO narcs (din, name, quantity) VALUES (?, ?, ?)",
		("02248809", "ADDERALL XR", 7),
	)
	connection.execute(
		"INSERT INTO narcs_details (din, upc, strength, form, pack_size) VALUES (?, ?, ?, ?, ?)",
		("02248809", "663220111026", "10MG", "CAP", "100"),
	)
	return connection


def user_exists(user):
	return user == "BHD"


def find_quantity_din(connection):
	return lambda din: connection.execute("SELECT quantity FROM narcs WHERE din = ?", (din,)).fetchone()[0]


def test_audit_log_service_add_entry_preserves_current_insert_shape_and_commit_timing():
	connection = make_audit_connection()
	tracking_connection = CommitTrackingConnection(connection)
	service = audit_log_service.AuditLogService(connection.cursor(), tracking_connection)

	service.add_entry(
		"02248809",
		2,
		"BHD",
		"receiving",
		user_exists,
		find_quantity_din(connection),
		pytz.timezone("America/Toronto"),
	)

	row = connection.execute("""
		SELECT din, old_qty, new_qty, Updated_By, Timestamp, transaction_type, discrepancy
		FROM audit_log
	""").fetchone()

	assert row[:4] == ("02248809", 2, 7, "BHD")
	datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")
	assert row[5:] == ("receiving", 5)
	assert tracking_connection.commit_count == 1


def test_audit_log_service_add_entry_invalid_user_does_not_insert_or_commit(capsys):
	connection = make_audit_connection()
	tracking_connection = CommitTrackingConnection(connection)
	service = audit_log_service.AuditLogService(connection.cursor(), tracking_connection)

	service.add_entry(
		"02248809",
		2,
		"NOPE",
		"receiving",
		user_exists,
		find_quantity_din(connection),
		pytz.timezone("America/Toronto"),
	)

	assert connection.execute("SELECT * FROM audit_log").fetchall() == []
	assert tracking_connection.commit_count == 0
	assert "Error: Invalid user ID." in capsys.readouterr().out


def test_audit_log_service_fetch_all_returns_current_shape():
	connection = make_audit_connection()
	connection.execute("""
		INSERT INTO audit_log (din, old_qty, new_qty, Updated_By, Timestamp, transaction_type, discrepancy)
		VALUES (?, ?, ?, ?, ?, ?, ?)
	""", ("02248809", 0, 5, "BHD", "2026-04-30 10:00:00", "receiving", 5))
	service = audit_log_service.AuditLogService(connection.cursor())

	column_names, rows = service.fetch_all()

	assert column_names == [
		"log_id",
		"din",
		"old_qty",
		"new_qty",
		"Updated_By",
		"Timestamp",
		"transaction_type",
		"discrepancy",
	]
	assert rows == [(1, "02248809", 0, 5, "BHD", "2026-04-30 10:00:00", "receiving", 5)]


def test_audit_log_service_get_by_din_and_date_returns_current_shape():
	connection = make_audit_connection()
	connection.execute("""
		INSERT INTO audit_log (din, old_qty, new_qty, Updated_By, Timestamp, transaction_type, discrepancy)
		VALUES (?, ?, ?, ?, ?, ?, ?)
	""", ("02248809", 0, 5, "BHD", "2026-04-30 10:00:00", "receiving", 5))
	connection.execute("""
		INSERT INTO audit_log (din, old_qty, new_qty, Updated_By, Timestamp, transaction_type, discrepancy)
		VALUES (?, ?, ?, ?, ?, ?, ?)
	""", ("02248812", 0, 2, "BHD", "2026-04-30 11:00:00", "receiving", 2))
	service = audit_log_service.AuditLogService(connection.cursor())

	assert service.get_by_din_and_date("02248809", "2026-04-30", "2026-04-30") == [
		("02248809", 0, 5, "BHD", "2026-04-30 10:00:00")
	]


def test_audit_log_service_get_reconciliation_by_date_range_returns_current_shape():
	connection = make_audit_connection()
	connection.execute("""
		INSERT INTO audit_log (din, old_qty, new_qty, Updated_By, Timestamp, transaction_type, discrepancy)
		VALUES (?, ?, ?, ?, ?, ?, ?)
	""", ("02248809", 10, 8, "BHD", "2026-04-30 10:00:00", "reconciliation", -2))
	connection.execute("""
		INSERT INTO audit_log (din, old_qty, new_qty, Updated_By, Timestamp, transaction_type, discrepancy)
		VALUES (?, ?, ?, ?, ?, ?, ?)
	""", ("02248809", 8, 9, "BHD", "2026-04-30 11:00:00", "receiving", 1))
	service = audit_log_service.AuditLogService(connection.cursor())

	assert service.get_reconciliation_by_date_range("2026-04-30", "2026-04-30") == [
		("ADDERALL XR", "10MG", "02248809", 10, 8, -2, "2026-04-30 10:00:00")
	]
