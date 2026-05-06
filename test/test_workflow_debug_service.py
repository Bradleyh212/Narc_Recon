import sqlite3

from services import workflow_debug_service


def create_inventory_connection():
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
	connection.execute(
		"INSERT INTO narcs (din, name, quantity) VALUES (?, ?, ?)",
		("02248809", "ADDERALL XR", 3),
	)
	connection.execute(
		"""
		INSERT INTO narcs_details (din, upc, strength, form, pack_size)
		VALUES (?, ?, ?, ?, ?)
		""",
		("02248809", "663220111026", "10MG", "CAP", "100"),
	)
	connection.commit()
	return connection


def create_audit_connection():
	connection = sqlite3.connect(":memory:")
	connection.execute("""
		CREATE TABLE audit_log (
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
	connection.execute(
		"""
		INSERT INTO audit_log (
			din, old_qty, new_qty, Updated_By, Timestamp, transaction_type, discrepancy
		)
		VALUES (?, ?, ?, ?, ?, ?, ?)
		""",
		("02248809", 1, 3, "BHD", "2026-05-05 10:00:00", "receiving", 2),
	)
	connection.commit()
	return connection


def test_show_narcs_table_does_not_print_output(monkeypatch, capsys):
	connection = create_inventory_connection()
	monkeypatch.setattr(workflow_debug_service, "get_conn", lambda: connection)

	workflow_debug_service.show_narcs_table()

	assert capsys.readouterr().out == ""


def test_show_audit_log_prints_prettytable_output(monkeypatch, capsys):
	connection = create_audit_connection()
	monkeypatch.setattr(workflow_debug_service, "get_conn", lambda: connection)

	workflow_debug_service.show_audit_log()

	output = capsys.readouterr().out
	assert "log_id" in output
	assert "02248809" in output
	assert "receiving" in output


def test_workflow_debug_service_does_not_import_sqlite3_functions():
	assert not hasattr(workflow_debug_service, "sqlite3_functions")
