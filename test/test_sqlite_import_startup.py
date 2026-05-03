import importlib

import pandas as pd
import pytest


STARTUP_DF = pd.DataFrame([{
	"DIN": "02248809",
	"Drug Name": "ADDERALL XR",
	"Upc": 663220111026,
	"Strength": "10MG",
	"Form": "CAP",
	"Pack size": 100,
}])


def prepare_startup_env(monkeypatch, tmp_path, debug_value=None):
	db_path = tmp_path / "startup-import-test.db"
	excel_path = tmp_path / "startup_med_sheet.xlsx"
	STARTUP_DF.to_excel(excel_path, sheet_name="med_sheet", index=False)

	monkeypatch.setenv("NARC_RECON_DB_PATH", str(db_path))
	monkeypatch.setenv("NARC_RECON_EXCEL_PATH", str(excel_path))

	if debug_value is None:
		monkeypatch.delenv("NARC_RECON_DEBUG_STARTUP", raising=False)
	else:
		monkeypatch.setenv("NARC_RECON_DEBUG_STARTUP", debug_value)

	return db_path, excel_path


def import_sqlite3_functions(monkeypatch, tmp_path, debug_value=None):
	prepare_startup_env(monkeypatch, tmp_path, debug_value)
	return importlib.import_module("sqlite3_functions")


def table_counts(sqlite3_functions):
	return {
		table: sqlite3_functions.con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
		for table in ("narcs", "narcs_details", "audit_log")
	}


def test_importing_sqlite3_functions_creates_expected_tables(monkeypatch, tmp_path, fresh_app_modules):
	sqlite3_functions = import_sqlite3_functions(monkeypatch, tmp_path)

	rows = sqlite3_functions.con.execute("""
		SELECT name
		FROM sqlite_master
		WHERE type = 'table'
		AND name IN ('narcs', 'narcs_details', 'audit_log')
		ORDER BY name
	""").fetchall()

	assert rows == [("audit_log",), ("narcs",), ("narcs_details",)]


def test_importing_sqlite3_functions_loads_excel_data(monkeypatch, tmp_path, fresh_app_modules):
	sqlite3_functions = import_sqlite3_functions(monkeypatch, tmp_path)

	narc_rows = sqlite3_functions.con.execute("""
		SELECT din, name, quantity
		FROM narcs
		ORDER BY din
	""").fetchall()
	detail_rows = sqlite3_functions.con.execute("""
		SELECT din, upc, strength, form, pack_size
		FROM narcs_details
		ORDER BY din, upc
	""").fetchall()

	assert narc_rows == [("02248809", "ADDERALL XR", 0)]
	assert detail_rows == [("02248809", "663220111026", "10MG", "CAP", "100")]


def test_reloading_sqlite3_functions_does_not_duplicate_imported_rows(monkeypatch, tmp_path, fresh_app_modules):
	sqlite3_functions = import_sqlite3_functions(monkeypatch, tmp_path)
	before = table_counts(sqlite3_functions)

	sqlite3_functions = importlib.reload(sqlite3_functions)
	after = table_counts(sqlite3_functions)

	assert before == {"narcs": 1, "narcs_details": 1, "audit_log": 0}
	assert after == before


@pytest.mark.parametrize("debug_value", [None, "0"])
def test_importing_sqlite3_functions_without_debug_does_not_print_tables(
	monkeypatch,
	tmp_path,
	fresh_app_modules,
	debug_value,
):
	prepare_startup_env(monkeypatch, tmp_path, debug_value)
	print_calls = []
	monkeypatch.setattr("builtins.print", lambda *args, **kwargs: print_calls.append(args))

	importlib.import_module("sqlite3_functions")

	assert print_calls == []


def test_importing_sqlite3_functions_with_debug_triggers_debug_display_path(
	monkeypatch,
	tmp_path,
	fresh_app_modules,
):
	prepare_startup_env(monkeypatch, tmp_path, "1")
	print_calls = []
	monkeypatch.setattr("builtins.print", lambda *args, **kwargs: print_calls.append(args))

	importlib.import_module("sqlite3_functions")

	assert len(print_calls) == 1
