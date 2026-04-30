import importlib
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
