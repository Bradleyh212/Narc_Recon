import sqlite3

import pandas as pd
import pytest

import excel_import_service


def sample_excel_df():
	return pd.DataFrame([
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


def test_validate_excel_columns_missing_required_column_raises():
	df = sample_excel_df().drop(columns=["Upc"])

	with pytest.raises(ValueError, match="Missing required Excel columns: Upc"):
		excel_import_service.validate_excel_columns(df)


def test_normalize_din_and_upc():
	assert excel_import_service.normalize_din(2248809) == "02248809"
	assert excel_import_service.normalize_upc(663220111026) == "663220111026"
	assert excel_import_service.normalize_upc(None) == "000000000000"


def test_validate_excel_rows_reports_current_warning_shape():
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

	report = excel_import_service.validate_excel_rows(df)

	assert report == {
		"blank_upc_count": 1,
		"blank_upc_rows": [4],
		"duplicate_upcs": ["663220111026"],
		"duplicate_dins": [],
		"warnings": [
			"1 row(s) have blank UPC values and will be skipped.",
			"Duplicate UPC values found: 663220111026",
		],
	}


def test_create_narc_list_accepts_explicit_excel_path_and_preserves_shape(tmp_path):
	excel_path = tmp_path / "med_sheet.xlsx"
	sample_excel_df().to_excel(excel_path, sheet_name="med_sheet", index=False)

	narc_list = excel_import_service.create_narc_list(excel_path)

	assert narc_list == {
		"02248809": [{
			"name": "ADDERALL XR",
			"upc": "663220111026",
			"strength": "10MG",
			"form": "CAP",
			"pack_size": 100,
		}]
	}


def test_from_excel_to_sql_uses_insert_or_ignore_behavior():
	conn = sqlite3.connect(":memory:")
	cursor = conn.cursor()
	cursor.execute("""
		CREATE TABLE narcs (
			din TEXT PRIMARY KEY,
			name TEXT NOT NULL,
			quantity INTEGER NOT NULL DEFAULT 0
		)
	""")
	cursor.execute("""
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
	narc_list = {
		"02248809": [{
			"name": "ADDERALL XR",
			"upc": "663220111026",
			"strength": "10MG",
			"form": "CAP",
			"pack_size": 100,
		}]
	}

	excel_import_service.from_excel_to_sql(cursor, narc_list)
	excel_import_service.from_excel_to_sql(cursor, narc_list)

	assert cursor.execute("SELECT din, name, quantity FROM narcs").fetchall() == [
		("02248809", "ADDERALL XR", 0)
	]
	assert cursor.execute("SELECT din, upc, strength, form, pack_size FROM narcs_details").fetchall() == [
		("02248809", "663220111026", "10MG", "CAP", "100")
	]
