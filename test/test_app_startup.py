import importlib.machinery
import importlib.util
import sqlite3
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINT = ROOT / "src" / "narc_recon.pyw"

STARTUP_DF = pd.DataFrame([{
	"DIN": "02248809",
	"Drug Name": "ADDERALL XR",
	"Upc": 663220111026,
	"Strength": "10MG",
	"Form": "CAP",
	"Pack size": 100,
}])


def load_narc_recon_module():
	loader = importlib.machinery.SourceFileLoader("narc_recon_startup_test", str(ENTRYPOINT))
	spec = importlib.util.spec_from_loader(loader.name, loader)
	module = importlib.util.module_from_spec(spec)
	loader.exec_module(module)
	return module


def prepare_startup_env(monkeypatch, tmp_path):
	db_path = tmp_path / "fresh-startup.db"
	excel_path = tmp_path / "med_sheet.xlsx"
	STARTUP_DF.to_excel(excel_path, sheet_name="med_sheet", index=False)

	monkeypatch.setenv("NARC_RECON_DB_PATH", str(db_path))
	monkeypatch.setenv("NARC_RECON_EXCEL_PATH", str(excel_path))
	monkeypatch.setenv("NARC_RECON_APP_USER", "startup-admin")
	monkeypatch.setenv("NARC_RECON_APP_PASSWORD", "startup-password")

	return db_path


def fetch_table_names(connection):
	return {
		row[0]
		for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
	}


def test_startup_initialization_creates_auth_and_catalog_tables_on_fresh_database(
	monkeypatch,
	tmp_path,
	fresh_app_modules,
):
	db_path = prepare_startup_env(monkeypatch, tmp_path)
	narc_recon = load_narc_recon_module()

	narc_recon.initialize_startup_database()

	connection = sqlite3.connect(db_path)
	try:
		assert {
			"app_account",
			"users",
			"narcs",
			"narcs_details",
			"audit_log",
		}.issubset(fetch_table_names(connection))
		assert connection.execute("SELECT COUNT(*) FROM app_account").fetchone()[0] == 1
		assert connection.execute("SELECT din, name, quantity FROM narcs").fetchall() == [
			("02248809", "ADDERALL XR", 0)
		]
		assert connection.execute(
			"SELECT din, upc, strength, form, pack_size FROM narcs_details"
		).fetchall() == [
			("02248809", "663220111026", "10MG", "CAP", "100")
		]
		assert connection.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0] == 0
	finally:
		connection.close()


def test_startup_initialization_is_idempotent_and_does_not_reset_existing_quantity(
	monkeypatch,
	tmp_path,
	fresh_app_modules,
):
	db_path = prepare_startup_env(monkeypatch, tmp_path)
	narc_recon = load_narc_recon_module()

	narc_recon.initialize_startup_database()
	connection = sqlite3.connect(db_path)
	try:
		connection.execute("UPDATE narcs SET quantity = ? WHERE din = ?", (42, "02248809"))
		connection.commit()
	finally:
		connection.close()

	narc_recon.initialize_startup_database()

	connection = sqlite3.connect(db_path)
	try:
		assert connection.execute("SELECT quantity FROM narcs WHERE din = ?", ("02248809",)).fetchone()[0] == 42
		assert connection.execute("SELECT COUNT(*) FROM narcs").fetchone()[0] == 1
		assert connection.execute("SELECT COUNT(*) FROM narcs_details").fetchone()[0] == 1
	finally:
		connection.close()


def test_startup_initialization_skips_excel_when_catalog_already_exists(
	monkeypatch,
	tmp_path,
	fresh_app_modules,
):
	db_path = prepare_startup_env(monkeypatch, tmp_path)
	excel_path = tmp_path / "med_sheet.xlsx"
	narc_recon = load_narc_recon_module()

	narc_recon.initialize_startup_database()
	excel_path.unlink()
	connection = sqlite3.connect(db_path)
	try:
		connection.execute("UPDATE narcs SET quantity = ? WHERE din = ?", (42, "02248809"))
		connection.commit()
	finally:
		connection.close()

	narc_recon.initialize_startup_database()

	connection = sqlite3.connect(db_path)
	try:
		assert connection.execute("SELECT quantity FROM narcs WHERE din = ?", ("02248809",)).fetchone()[0] == 42
		assert connection.execute("SELECT COUNT(*) FROM narcs").fetchone()[0] == 1
		assert connection.execute("SELECT COUNT(*) FROM narcs_details").fetchone()[0] == 1
	finally:
		connection.close()
