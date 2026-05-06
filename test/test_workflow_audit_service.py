import importlib
import sys
from datetime import datetime

import pytest


@pytest.fixture(autouse=True)
def unload_workflow_audit_service():
	sys.modules.pop("services.workflow_audit_service", None)
	yield
	sys.modules.pop("services.workflow_audit_service", None)


def load_workflow_audit_service(monkeypatch, tmp_path, fresh_app_modules):
	db_path = tmp_path / "workflow-audit.db"
	monkeypatch.setenv("NARC_RECON_DB_PATH", str(db_path))
	sys.modules.pop("services.workflow_audit_service", None)

	auth = importlib.import_module("auth")
	schema_service = importlib.import_module("db.schema_service")

	connection = auth.get_conn()
	try:
		auth.migrate_users(connection)
		schema_service.SchemaService(connection.cursor()).create_all_catalog_tables()
		connection.execute(
			"INSERT INTO users (user_id, role, created_at) VALUES (?, ?, ?)",
			("BHD", "Pharmacist", "Today"),
		)
		connection.execute(
			"INSERT INTO narcs (din, name, quantity) VALUES (?, ?, ?)",
			("02248809", "ADDERALL XR", 2),
		)
		connection.execute(
			"""
			INSERT INTO narcs_details (din, upc, strength, form, pack_size)
			VALUES (?, ?, ?, ?, ?)
			""",
			("02248809", "663220111026", "10MG", "CAP", "100"),
		)
		connection.commit()
	finally:
		connection.close()

	return importlib.import_module("services.workflow_audit_service"), auth, db_path


def update_quantity(auth, quantity):
	connection = auth.get_conn()
	try:
		connection.execute("UPDATE narcs SET quantity = ? WHERE din = ?", (quantity, "02248809"))
		connection.commit()
	finally:
		connection.close()


def fetch_audit_row(auth):
	connection = auth.get_conn()
	try:
		return connection.execute("""
			SELECT din, old_qty, new_qty, Updated_By, Timestamp, transaction_type, discrepancy
			FROM audit_log
		""").fetchone()
	finally:
		connection.close()


def test_workflow_audit_service_valid_insert_records_current_audit_shape(monkeypatch, tmp_path, fresh_app_modules):
	workflow_audit_service, auth, _ = load_workflow_audit_service(monkeypatch, tmp_path, fresh_app_modules)
	update_quantity(auth, 10)

	workflow_audit_service.add_to_audit_log("02248809", 6, "BHD", "filling")

	row = fetch_audit_row(auth)
	assert row[:4] == ("02248809", 6, 10, "BHD")
	datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")
	assert row[5:] == ("filling", 4)


def test_workflow_audit_service_reads_new_quantity_after_committed_update_and_fresh_connection_sees_row(
	monkeypatch,
	tmp_path,
	fresh_app_modules,
):
	workflow_audit_service, auth, _ = load_workflow_audit_service(monkeypatch, tmp_path, fresh_app_modules)
	update_quantity(auth, 12)

	workflow_audit_service.add_to_audit_log("02248809", 4, "BHD", "reconciliation")

	row = fetch_audit_row(auth)
	assert row[:4] == ("02248809", 4, 12, "BHD")
	datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")
	assert row[5:] == ("reconciliation", 8)


def test_workflow_audit_service_invalid_user_inserts_no_row_and_keeps_quantity_update_committed(
	monkeypatch,
	tmp_path,
	fresh_app_modules,
	capsys,
):
	workflow_audit_service, auth, _ = load_workflow_audit_service(monkeypatch, tmp_path, fresh_app_modules)
	update_quantity(auth, 6)

	workflow_audit_service.add_to_audit_log("02248809", 2, "NOPE", "receiving")

	connection = auth.get_conn()
	try:
		quantity = connection.execute(
			"SELECT quantity FROM narcs WHERE din = ?",
			("02248809",),
		).fetchone()[0]
		audit_rows = connection.execute("SELECT * FROM audit_log").fetchall()
	finally:
		connection.close()

	assert quantity == 6
	assert audit_rows == []
	assert "Error: Invalid user ID." in capsys.readouterr().out
