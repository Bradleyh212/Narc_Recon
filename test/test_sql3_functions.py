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


def test_inventory_service_find_narcs_by_din(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env
	inventory_service = importlib.import_module("inventory_service")

	assert inventory_service.find_narcs_by_din(sqlite3_functions.cur, "02248809") == [
		("02248809", "ADDERALL XR", 0, "663220111026", "10MG", "CAP", "100")
	]


def test_inventory_service_find_narcs_by_upc(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env
	inventory_service = importlib.import_module("inventory_service")

	assert inventory_service.find_narcs_by_upc(sqlite3_functions.cur, "663220111026") == [
		("02248809", "ADDERALL XR", 0, "663220111026", "10MG", "CAP", "100")
	]


def test_inventory_service_find_quantity(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env
	inventory_service = importlib.import_module("inventory_service")

	assert inventory_service.find_quantity_by_din(sqlite3_functions.cur, "02248809") == 0
	assert inventory_service.find_quantity_by_upc(sqlite3_functions.cur, "663220111026") == 0


def test_inventory_service_fetch_narcs_table(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env
	inventory_service = importlib.import_module("inventory_service")

	column_names, rows = inventory_service.fetch_narcs_table(sqlite3_functions.cur)

	assert column_names == ["din", "name", "quantity", "upc", "strength", "form", "pack_size"]
	assert rows == [("02248809", "ADDERALL XR", 0, "663220111026", "10MG", "CAP", "100")]


def test_audit_log_service_add_to_audit_log(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env
	audit_log_service = importlib.import_module("audit_log_service")

	sqlite3_functions.cur.execute("UPDATE narcs SET quantity = ? WHERE din = ?", (7, "02248809"))
	sqlite3_functions.con.commit()

	audit_log_service.add_to_audit_log(
		sqlite3_functions.cur,
		sqlite3_functions.con,
		"02248809",
		2,
		"BHD",
		"receiving",
		sqlite3_functions.user_exists,
		sqlite3_functions.find_quantity_din,
		sqlite3_functions.user_timezone,
	)
	column_names, rows = audit_log_service.fetch_audit_log(sqlite3_functions.cur)

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
	assert len(rows) == 1
	assert rows[0][1:5] == ("02248809", 2, 7, "BHD")
	assert rows[0][6:] == ("receiving", 5)


def test_audit_log_service_get_audit_log_by_din_and_date(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env
	audit_log_service = importlib.import_module("audit_log_service")

	sqlite3_functions.cur.execute("""
		INSERT INTO audit_log (din, old_qty, new_qty, Updated_By, Timestamp, transaction_type, discrepancy)
		VALUES (?, ?, ?, ?, ?, ?, ?)
	""", ("02248809", 0, 5, "BHD", "2026-04-30 10:00:00", "receiving", 5))
	sqlite3_functions.cur.execute("""
		INSERT INTO audit_log (din, old_qty, new_qty, Updated_By, Timestamp, transaction_type, discrepancy)
		VALUES (?, ?, ?, ?, ?, ?, ?)
	""", ("02248812", 0, 2, "BHD", "2026-04-30 11:00:00", "receiving", 2))
	sqlite3_functions.con.commit()

	assert audit_log_service.get_audit_log_by_din_and_date(
		sqlite3_functions.cur,
		"02248809",
		"2026-04-30",
		"2026-04-30",
	) == [("02248809", 0, 5, "BHD", "2026-04-30 10:00:00")]


def test_audit_log_service_get_reconciliation_log_by_date_range(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env
	audit_log_service = importlib.import_module("audit_log_service")

	sqlite3_functions.cur.execute("""
		INSERT INTO audit_log (din, old_qty, new_qty, Updated_By, Timestamp, transaction_type, discrepancy)
		VALUES (?, ?, ?, ?, ?, ?, ?)
	""", ("02248809", 10, 8, "BHD", "2026-04-30 10:00:00", "reconciliation", -2))
	sqlite3_functions.cur.execute("""
		INSERT INTO audit_log (din, old_qty, new_qty, Updated_By, Timestamp, transaction_type, discrepancy)
		VALUES (?, ?, ?, ?, ?, ?, ?)
	""", ("02248809", 8, 9, "BHD", "2026-04-30 11:00:00", "receiving", 1))
	sqlite3_functions.con.commit()

	assert audit_log_service.get_reconciliation_log_by_date_range(
		sqlite3_functions.cur,
		"2026-04-30",
		"2026-04-30",
	) == [("ADDERALL XR", "10MG", "02248809", 10, 8, -2, "2026-04-30 10:00:00")]


def test_sqlite3_functions_audit_wrappers_still_work(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env

	sqlite3_functions.cur.execute("UPDATE narcs SET quantity = ? WHERE din = ?", (4, "02248809"))
	sqlite3_functions.con.commit()
	sqlite3_functions.add_to_audit_log("02248809", 1, "BHD", "receiving")

	rows = sqlite3_functions.con.execute("""
		SELECT din, old_qty, new_qty, Updated_By, transaction_type, discrepancy
		FROM audit_log
	""").fetchall()

	assert rows == [("02248809", 1, 4, "BHD", "receiving", 3)]


def test_sqlite3_functions_add_to_audit_log_records_current_audit_shape(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env

	sqlite3_functions.cur.execute("UPDATE narcs SET quantity = ? WHERE din = ?", (9, "02248809"))
	sqlite3_functions.con.commit()
	sqlite3_functions.add_to_audit_log("02248809", 3, "BHD", "expired")

	row = sqlite3_functions.con.execute("""
		SELECT din, old_qty, new_qty, Updated_By, Timestamp, transaction_type, discrepancy
		FROM audit_log
	""").fetchone()

	assert row[:4] == ("02248809", 3, 9, "BHD")
	datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")
	assert row[5:] == ("expired", 6)


def test_sqlite3_functions_add_to_audit_log_invalid_user_does_not_insert(sqlite_env, capsys):
	sqlite3_functions, _, _ = sqlite_env

	sqlite3_functions.cur.execute("UPDATE narcs SET quantity = ? WHERE din = ?", (5, "02248809"))
	sqlite3_functions.con.commit()
	sqlite3_functions.add_to_audit_log("02248809", 1, "NOPE", "receiving")

	rows = sqlite3_functions.con.execute("SELECT * FROM audit_log").fetchall()

	assert rows == []
	assert "Error: Invalid user ID." in capsys.readouterr().out


def test_sqlite3_functions_audit_log_is_visible_from_fresh_connection(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env
	authmod = importlib.import_module("auth")

	sqlite3_functions.cur.execute("UPDATE narcs SET quantity = ? WHERE din = ?", (12, "02248809"))
	sqlite3_functions.con.commit()
	sqlite3_functions.add_to_audit_log("02248809", 4, "BHD", "reconciliation")

	fresh_conn = authmod.get_conn()
	try:
		row = fresh_conn.execute("""
			SELECT din, old_qty, new_qty, Updated_By, Timestamp, transaction_type, discrepancy
			FROM audit_log
		""").fetchone()
	finally:
		fresh_conn.close()

	assert row[:4] == ("02248809", 4, 12, "BHD")
	datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")
	assert row[5:] == ("reconciliation", 8)


def test_workflow_audit_service_preserves_current_audit_behavior(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env
	workflow_audit_service = importlib.import_module("workflow_audit_service")

	sqlite3_functions.cur.execute("UPDATE narcs SET quantity = ? WHERE din = ?", (10, "02248809"))
	sqlite3_functions.con.commit()
	workflow_audit_service.add_to_audit_log("02248809", 6, "BHD", "filling")

	row = sqlite3_functions.con.execute("""
		SELECT din, old_qty, new_qty, Updated_By, Timestamp, transaction_type, discrepancy
		FROM audit_log
	""").fetchone()

	assert row[:4] == ("02248809", 6, 10, "BHD")
	datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")
	assert row[5:] == ("filling", 4)


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


def test_initialize_database_from_excel_creates_expected_tables(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env

	rows = sqlite3_functions.con.execute("""
		SELECT name
		FROM sqlite_master
		WHERE type = 'table'
		AND name IN ('narcs', 'narcs_details', 'audit_log')
		ORDER BY name
	""").fetchall()

	assert rows == [("audit_log",), ("narcs",), ("narcs_details",)]


def test_initialize_database_from_excel_is_idempotent(sqlite_env):
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


def test_validate_excel_columns_missing_required_column_raises(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env
	df = FAKE_DF.drop(columns=["Upc"])

	with pytest.raises(ValueError, match="Missing required Excel columns: Upc"):
		sqlite3_functions.validate_excel_columns(df)


def test_normalize_din_and_upc(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env

	assert sqlite3_functions.normalize_din(2248809) == "02248809"
	assert sqlite3_functions.normalize_upc(663220111026) == "663220111026"
	assert sqlite3_functions.normalize_upc(None) == "000000000000"


def test_validate_excel_rows_reports_blank_upc_and_duplicate_upc(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env
	df = pd.DataFrame([
		{
			"DIN": 2248809,
			"Drug Name": "ADDERALL XR",
			"Upc": 663220111026,
			"Strength": "10MG",
			"Form": "CAP",
			"Pack size": 100,
		},
		{
			"DIN": 2248812,
			"Drug Name": "ADDERALL XR",
			"Upc": 663220111026,
			"Strength": "15MG",
			"Form": "CAP",
			"Pack size": 100,
		},
		{
			"DIN": 2453908,
			"Drug Name": "ACT-BUPRENORPH/NALOXON",
			"Upc": None,
			"Strength": "2MG/0.5MG",
			"Form": "TAB",
			"Pack size": None,
		},
	])

	report = sqlite3_functions.validate_excel_rows(df)

	assert report["blank_upc_count"] == 1
	assert report["blank_upc_rows"] == [4]
	assert report["duplicate_upcs"] == ["663220111026"]
	assert "02248809" not in report["duplicate_dins"]
	assert any("blank UPC" in warning for warning in report["warnings"])
	assert any("Duplicate UPC" in warning for warning in report["warnings"])


def test_create_narc_list_keeps_current_blank_upc_skip_behavior(sqlite_env, monkeypatch, tmp_path):
	sqlite3_functions, _, _ = sqlite_env
	excel_path = tmp_path / "with-blank-upc.xlsx"
	df = pd.DataFrame([
		{
			"DIN": 2248809,
			"Drug Name": "ADDERALL XR",
			"Upc": 663220111026,
			"Strength": "10MG",
			"Form": "CAP",
			"Pack size": 100,
		},
		{
			"DIN": 2453908,
			"Drug Name": "ACT-BUPRENORPH/NALOXON",
			"Upc": None,
			"Strength": "2MG/0.5MG",
			"Form": "TAB",
			"Pack size": None,
		},
	])
	df.to_excel(excel_path, sheet_name="med_sheet", index=False)
	monkeypatch.setenv("NARC_RECON_EXCEL_PATH", str(excel_path))

	narc_list = sqlite3_functions.create_narc_list()

	assert narc_list == {
		"02248809": [{
			"name": "ADDERALL XR",
			"upc": "663220111026",
			"strength": "10MG",
			"form": "CAP",
			"pack_size": 100,
		}]
	}


def test_find_narcs_din(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env

	assert sqlite3_functions.find_narcs_din("02248809") == [
		("02248809", "ADDERALL XR", 0, "663220111026", "10MG", "CAP", "100")
	]


def test_find_narcs_upc(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env

	assert sqlite3_functions.find_narcs_upc("663220111026") == [
		("02248809", "ADDERALL XR", 0, "663220111026", "10MG", "CAP", "100")
	]
	assert sqlite3_functions.find_narcs_upc("") == []


def test_find_quantity_din(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env

	assert sqlite3_functions.find_quantity_din("02248809") == 0
	assert sqlite3_functions.find_quantity_din("02248809") != 1
	assert sqlite3_functions.find_quantity_din("02248809") != -1
	assert sqlite3_functions.find_quantity_din("02248809") != 1234


def test_find_quantity_upc(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env

	assert sqlite3_functions.find_quantity("663220111026") == 0
	assert sqlite3_functions.find_quantity("663220111026") != 1
	assert sqlite3_functions.find_quantity("663220111026") != -1
	assert sqlite3_functions.find_quantity("663220111026") != 4321


def test_list_users(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env

	assert sqlite3_functions.list_users() == [(1, "BHD", "admin", "Today")]
	assert sqlite3_functions.list_users() != [(1, "Brad", "admin", "Today")]


def test_list_user_ids(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env

	assert sqlite3_functions.list_user_ids() == ["BHD"]


def test_user_exists_true_false(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env

	assert sqlite3_functions.user_exists("BHD") is True
	assert sqlite3_functions.user_exists("NOPE") is False


def test_add_and_remove_user_roundtrip(sqlite_env):
	sqlite3_functions, _, _ = sqlite_env

	sqlite3_functions.add_user("TMP", "staff")
	assert sqlite3_functions.user_exists("TMP") is True

	sqlite3_functions.remove_user("TMP")
	assert sqlite3_functions.user_exists("TMP") is False
