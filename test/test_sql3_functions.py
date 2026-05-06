import importlib
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


@pytest.fixture
def sqlite_env(monkeypatch, tmp_path, fresh_app_modules):
	db_path = tmp_path / "sqlite-functions-test.db"
	excel_path = tmp_path / "med_sheet.xlsx"
	FAKE_DF.to_excel(excel_path, sheet_name="med_sheet", index=False)

	monkeypatch.setenv("NARC_RECON_DB_PATH", str(db_path))
	monkeypatch.setenv("NARC_RECON_EXCEL_PATH", str(excel_path))

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

	sqlite3_functions = importlib.import_module("sqlite3_functions")
	yield sqlite3_functions, db_path, excel_path


def test_sqlite3_functions_uses_temp_database(sqlite_env):
	sqlite3_functions, db_path, _ = sqlite_env

	database_path = sqlite3_functions.con.execute("PRAGMA database_list").fetchone()[2]

	assert Path(database_path) == db_path


def test_sqlite3_functions_legacy_wrapper_api_exists(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env
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


def test_sqlite3_functions_inventory_wrappers_return_current_shapes(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env

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
	sqlite3_functions, _, _ = sqlite_env

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
	sqlite3_functions, _, _ = sqlite_env

	assert sqlite3_functions.list_users() == [(1, "BHD", "admin", "Today")]
	assert sqlite3_functions.list_user_ids() == ["BHD"]
	assert sqlite3_functions.user_exists("BHD") is True
	assert sqlite3_functions.user_exists("NOPE") is False

	sqlite3_functions.add_user("TMP", "staff")
	assert sqlite3_functions.user_exists("TMP") is True
	sqlite3_functions.remove_user("TMP")
	assert sqlite3_functions.user_exists("TMP") is False


def test_initialize_database_from_excel_wrapper_is_idempotent(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env

	before = {
		table: sqlite3_functions.con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
		for table in ("narcs", "narcs_details", "audit_log")
	}

	sqlite3_functions.initialize_database_from_excel()

	after = {
		table: sqlite3_functions.con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
		for table in ("narcs", "narcs_details", "audit_log")
	}

	assert after == before


def test_sqlite3_functions_add_to_audit_log_legacy_wrapper_records_current_shape(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env
	authmod = importlib.import_module("auth")

	sqlite3_functions.cur.execute("UPDATE narcs SET quantity = ? WHERE din = ?", (9, "02248809"))
	sqlite3_functions.con.commit()
	sqlite3_functions.add_to_audit_log("02248809", 3, "BHD", "expired")

	fresh_conn = authmod.get_conn()
	try:
		row = fresh_conn.execute("""
			SELECT din, old_qty, new_qty, Updated_By, Timestamp, transaction_type, discrepancy
			FROM audit_log
		""").fetchone()
	finally:
		fresh_conn.close()

	assert row[:4] == ("02248809", 3, 9, "BHD")
	datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")
	assert row[5:] == ("expired", 6)


def test_sqlite3_functions_invalid_user_keeps_prior_quantity_update_committed(sqlite_env, capsys):
	sqlite3_functions, _, _ = sqlite_env
	authmod = importlib.import_module("auth")

	sqlite3_functions.cur.execute("UPDATE narcs SET quantity = ? WHERE din = ?", (6, "02248809"))
	sqlite3_functions.con.commit()
	sqlite3_functions.add_to_audit_log("02248809", 2, "NOPE", "filling")

	fresh_conn = authmod.get_conn()
	try:
		quantity = fresh_conn.execute(
			"SELECT quantity FROM narcs WHERE din = ?",
			("02248809",),
		).fetchone()[0]
		audit_rows = fresh_conn.execute("SELECT * FROM audit_log").fetchall()
	finally:
		fresh_conn.close()

	assert quantity == 6
	assert audit_rows == []
	assert "Error: Invalid user ID." in capsys.readouterr().out
