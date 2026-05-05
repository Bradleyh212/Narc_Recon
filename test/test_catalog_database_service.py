import sqlite3

import pandas as pd

import catalog_database_service


def sample_catalog_df():
	return pd.DataFrame([{
		"DIN": "02248809",
		"Drug Name": "ADDERALL XR",
		"Upc": 663220111026,
		"Strength": "10MG",
		"Form": "CAP",
		"Pack size": 100,
	}])


def write_catalog_excel(tmp_path):
	excel_path = tmp_path / "med_sheet.xlsx"
	sample_catalog_df().to_excel(excel_path, sheet_name="med_sheet", index=False)
	return excel_path


def fetch_table_names(connection):
	return {
		row[0]
		for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
	}


def initialize_catalog(connection, excel_path):
	service = catalog_database_service.CatalogDatabaseService(
		connection.cursor(),
		connection,
		excel_path,
	)
	service.initialize_from_excel()


def test_catalog_database_service_creates_tables(tmp_path):
	connection = sqlite3.connect(":memory:")
	excel_path = write_catalog_excel(tmp_path)

	initialize_catalog(connection, excel_path)

	assert {
		"narcs",
		"narcs_details",
		"audit_log",
	}.issubset(fetch_table_names(connection))


def test_catalog_database_service_imports_catalog_rows(tmp_path):
	connection = sqlite3.connect(":memory:")
	excel_path = write_catalog_excel(tmp_path)

	initialize_catalog(connection, excel_path)

	assert connection.execute("SELECT din, name, quantity FROM narcs").fetchall() == [
		("02248809", "ADDERALL XR", 0)
	]
	assert connection.execute(
		"SELECT din, upc, strength, form, pack_size FROM narcs_details"
	).fetchall() == [
		("02248809", "663220111026", "10MG", "CAP", "100")
	]


def test_catalog_database_service_is_idempotent(tmp_path):
	connection = sqlite3.connect(":memory:")
	excel_path = write_catalog_excel(tmp_path)

	initialize_catalog(connection, excel_path)
	initialize_catalog(connection, excel_path)

	assert connection.execute("SELECT COUNT(*) FROM narcs").fetchone()[0] == 1
	assert connection.execute("SELECT COUNT(*) FROM narcs_details").fetchone()[0] == 1
	assert connection.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0] == 0


def test_catalog_database_service_does_not_reset_existing_quantity(tmp_path):
	connection = sqlite3.connect(":memory:")
	excel_path = write_catalog_excel(tmp_path)

	initialize_catalog(connection, excel_path)
	connection.execute("UPDATE narcs SET quantity = ? WHERE din = ?", (42, "02248809"))
	connection.commit()
	initialize_catalog(connection, excel_path)

	assert connection.execute(
		"SELECT quantity FROM narcs WHERE din = ?",
		("02248809",),
	).fetchone()[0] == 42
