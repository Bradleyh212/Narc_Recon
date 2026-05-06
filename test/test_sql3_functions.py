import importlib
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest


FAKE_DF = pd.DataFrame([{
	"DIN": "02248809",
	"Drug Name": "ADDERALL XR",
	"Upc": 663220111026,
	"Strength": "10MG",
	"Form": "CAP",
	"Pack size": 100,
}])


def prepare_sqlite_env(monkeypatch, tmp_path):
	db_path = tmp_path / "sqlite-functions-test.db"
	excel_path = tmp_path / "med_sheet.xlsx"
	FAKE_DF.to_excel(excel_path, sheet_name="med_sheet", index=False)

	monkeypatch.setenv("NARC_RECON_DB_PATH", str(db_path))
	monkeypatch.setenv("NARC_RECON_EXCEL_PATH", str(excel_path))

	return db_path, excel_path


@pytest.fixture
def sqlite_env(monkeypatch, tmp_path, fresh_app_modules):
	db_path, excel_path = prepare_sqlite_env(monkeypatch, tmp_path)

	sqlite3_functions = importlib.import_module("sqlite3_functions")
	sqlite3_functions.initialize_database_from_excel()

	authmod = importlib.import_module("auth")
	conn = authmod.get_conn()
	try:
		authmod.migrate_users(conn)
		conn.execute(
			"INSERT INTO users (user_id, role, created_at) VALUES (?, ?, ?)",
			("BHD", "admin", "Today"),
		)
	finally:
		conn.close()

	yield sqlite3_functions, db_path, excel_path, authmod


def test_importing_sqlite3_functions_has_no_database_side_effects(monkeypatch, tmp_path, fresh_app_modules):
	db_path, _ = prepare_sqlite_env(monkeypatch, tmp_path)

	sqlite3_functions = importlib.import_module("sqlite3_functions")

	assert not db_path.exists()
	assert not hasattr(sqlite3_functions, "con")
	assert not hasattr(sqlite3_functions, "cur")


def test_sqlite3_functions_wrappers_use_temp_database_after_explicit_initialization(sqlite_env):
	_, db_path, _, authmod = sqlite_env

	conn = authmod.get_conn()
	try:
		database_path = conn.execute("PRAGMA database_list").fetchone()[2]
	finally:
		conn.close()

	assert Path(database_path) == db_path


def test_sqlite3_functions_legacy_wrapper_api_exists(sqlite_env):
	sqlite3_functions, _, _, _ = sqlite_env
	expected_wrappers = [
		"create_narcs_table",
		"create_narcs_details_table",
		"create_audit_log_table",
		"validate_excel_columns",
		"normalize_din",
		"normalize_upc",
		"validate_excel_rows",
		"create_narc_list",
		"from_excel_to_sql",
		"find_narcs_upc",
		"find_narcs_din",
		"find_quantity",
		"find_quantity_din",
		"add_user",
		"get_user_role",
		"list_users",
		"list_user_ids",
		"remove_user",
		"user_exists",
		"add_to_audit_log",
		"show_audit_log",
		"show_narcs_table",
		"get_audit_log_by_din_and_date",
		"get_reconciliation_log_by_date_range",
		"initialize_database_from_excel",
	]

	for wrapper_name in expected_wrappers:
		assert callable(getattr(sqlite3_functions, wrapper_name))


def test_initialize_database_from_excel_explicitly_creates_and_imports_catalog(monkeypatch, tmp_path, fresh_app_modules):
	db_path, _ = prepare_sqlite_env(monkeypatch, tmp_path)
	sqlite3_functions = importlib.import_module("sqlite3_functions")

	sqlite3_functions.initialize_database_from_excel()

	conn = sqlite3.connect(db_path)
	try:
		table_names = {
			row[0]
			for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
		}
		assert {"narcs", "narcs_details", "audit_log"}.issubset(table_names)
		assert conn.execute("SELECT din, name, quantity FROM narcs").fetchall() == [
			("02248809", "ADDERALL XR", 0)
		]
		assert conn.execute(
			"SELECT din, upc, strength, form, pack_size FROM narcs_details"
		).fetchall() == [
			("02248809", "663220111026", "10MG", "CAP", "100")
		]
	finally:
		conn.close()


def test_initialize_database_from_excel_wrapper_is_idempotent(sqlite_env):
	sqlite3_functions, _, _, authmod = sqlite_env

	conn = authmod.get_conn()
	try:
		conn.execute("UPDATE narcs SET quantity = ? WHERE din = ?", (42, "02248809"))
		conn.commit()
	finally:
		conn.close()

	sqlite3_functions.initialize_database_from_excel()

	conn = authmod.get_conn()
	try:
		assert conn.execute(
			"SELECT quantity FROM narcs WHERE din = ?",
			("02248809",),
		).fetchone()[0] == 42
		assert conn.execute("SELECT COUNT(*) FROM narcs").fetchone()[0] == 1
		assert conn.execute("SELECT COUNT(*) FROM narcs_details").fetchone()[0] == 1
	finally:
		conn.close()


def test_sqlite3_functions_inventory_wrappers_return_current_shapes(sqlite_env):
	sqlite3_functions, _, _, _ = sqlite_env

	assert sqlite3_functions.find_narcs_din("02248809") == [
		("02248809", "ADDERALL XR", 0, "663220111026", "10MG", "CAP", "100")
	]
	assert sqlite3_functions.find_narcs_upc("663220111026") == [
		("02248809", "ADDERALL XR", 0, "663220111026", "10MG", "CAP", "100")
	]
	assert sqlite3_functions.find_narcs_upc("") == []
	assert sqlite3_functions.find_quantity_din("02248809") == 0
	assert sqlite3_functions.find_quantity("663220111026") == 0


def test_sqlite3_functions_excel_wrappers_preserve_current_behavior(sqlite_env):
	sqlite3_functions, _, _, _ = sqlite_env

	with pytest.raises(ValueError, match="Missing required Excel columns: Upc"):
		sqlite3_functions.validate_excel_columns(FAKE_DF.drop(columns=["Upc"]))

	assert sqlite3_functions.normalize_din(2248809) == "02248809"
	assert sqlite3_functions.normalize_upc(663220111026) == "663220111026"
	assert sqlite3_functions.normalize_upc(None) == "000000000000"
	assert sqlite3_functions.create_narc_list() == {
		"02248809": [{
			"name": "ADDERALL XR",
			"upc": "663220111026",
			"strength": "10MG",
			"form": "CAP",
			"pack_size": 100,
		}]
	}


def test_sqlite3_functions_user_wrappers_preserve_current_shapes(sqlite_env):
	sqlite3_functions, _, _, _ = sqlite_env

	assert sqlite3_functions.list_users() == [(1, "BHD", "admin", "Today")]
	assert sqlite3_functions.list_user_ids() == ["BHD"]
	assert sqlite3_functions.user_exists("BHD") is True
	assert sqlite3_functions.user_exists("NOPE") is False

	sqlite3_functions.add_user("TMP", "staff")
	assert sqlite3_functions.user_exists("TMP") is True
	sqlite3_functions.remove_user("TMP")
	assert sqlite3_functions.user_exists("TMP") is False


def test_sqlite3_functions_add_to_audit_log_legacy_wrapper_records_current_shape(sqlite_env):
	sqlite3_functions, _, _, authmod = sqlite_env

	conn = authmod.get_conn()
	try:
		conn.execute("UPDATE narcs SET quantity = ? WHERE din = ?", (9, "02248809"))
		conn.commit()
	finally:
		conn.close()

	sqlite3_functions.add_to_audit_log("02248809", 3, "BHD", "expired")

	conn = authmod.get_conn()
	try:
		row = conn.execute("""
			SELECT din, old_qty, new_qty, Updated_By, Timestamp, transaction_type, discrepancy
			FROM audit_log
		""").fetchone()
	finally:
		conn.close()

	assert row[:4] == ("02248809", 3, 9, "BHD")
	datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")
	assert row[5:] == ("expired", 6)


def test_sqlite3_functions_invalid_user_keeps_prior_quantity_update_committed(sqlite_env, capsys):
	sqlite3_functions, _, _, authmod = sqlite_env

	conn = authmod.get_conn()
	try:
		conn.execute("UPDATE narcs SET quantity = ? WHERE din = ?", (6, "02248809"))
		conn.commit()
	finally:
		conn.close()

	sqlite3_functions.add_to_audit_log("02248809", 2, "NOPE", "filling")

	conn = authmod.get_conn()
	try:
		quantity = conn.execute(
			"SELECT quantity FROM narcs WHERE din = ?",
			("02248809",),
		).fetchone()[0]
		audit_rows = conn.execute("SELECT * FROM audit_log").fetchall()
	finally:
		conn.close()

	assert quantity == 6
	assert audit_rows == []
	assert "Error: Invalid user ID." in capsys.readouterr().out
