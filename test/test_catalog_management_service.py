import sqlite3

import pytest

from db import schema_service
from services.catalog_management_service import CatalogManagementService, DuplicateMedicationDetailError


def create_catalog_connection():
	connection = sqlite3.connect(":memory:")
	connection.execute("PRAGMA foreign_keys = ON")
	cursor = connection.cursor()
	schema_service.create_narcs_table(cursor)
	schema_service.create_narcs_details_table(cursor)
	connection.commit()
	return connection


def test_add_medication_inserts_new_narc_and_detail_with_quantity_zero():
	connection = create_catalog_connection()
	service = CatalogManagementService(connection)

	result = service.add_medication(
		name="ADDERALL XR",
		din="2248809",
		upc="663220111026",
		strength="10MG",
		form="CAP",
		pack_size="100",
	)

	assert result == {
		"din": "02248809",
		"upc": "663220111026",
		"pack_size": "100",
		"created_narc": True,
		"updated_name": False,
	}
	assert connection.execute("SELECT din, name, quantity FROM narcs").fetchall() == [
		("02248809", "ADDERALL XR", 0)
	]
	assert connection.execute("SELECT din, upc, strength, form, pack_size FROM narcs_details").fetchall() == [
		("02248809", "663220111026", "10MG", "CAP", "100")
	]


def test_add_medication_preserves_existing_quantity_and_adds_detail_row():
	connection = create_catalog_connection()
	connection.execute(
		"INSERT INTO narcs (din, name, quantity) VALUES (?, ?, ?)",
		("02248809", "ADDERALL XR", 42),
	)
	connection.commit()
	service = CatalogManagementService(connection)

	result = service.add_medication(
		name="ADDERALL XR",
		din="02248809",
		upc="663220111033",
		strength="15MG",
		form="CAP",
		pack_size="100",
	)

	assert result["created_narc"] is False
	assert result["updated_name"] is False
	assert connection.execute("SELECT quantity FROM narcs WHERE din = ?", ("02248809",)).fetchone()[0] == 42
	assert connection.execute("SELECT din, upc, strength, form, pack_size FROM narcs_details").fetchall() == [
		("02248809", "663220111033", "15MG", "CAP", "100")
	]


def test_add_medication_updates_existing_name_without_resetting_quantity():
	connection = create_catalog_connection()
	connection.execute(
		"INSERT INTO narcs (din, name, quantity) VALUES (?, ?, ?)",
		("02248809", "OLD NAME", 17),
	)
	connection.commit()
	service = CatalogManagementService(connection)

	result = service.add_medication(
		name="ADDERALL XR",
		din="02248809",
		upc="663220111033",
		strength="15MG",
		form="CAP",
		pack_size="100",
	)

	assert result["created_narc"] is False
	assert result["updated_name"] is True
	assert connection.execute("SELECT name, quantity FROM narcs WHERE din = ?", ("02248809",)).fetchone() == (
		"ADDERALL XR",
		17,
	)


def test_add_medication_allows_same_din_and_upc_with_different_pack_size():
	connection = create_catalog_connection()
	service = CatalogManagementService(connection)

	service.add_medication("ADDERALL XR", "02248809", "663220111026", "10MG", "CAP", "100")
	service.add_medication("ADDERALL XR", "02248809", "663220111026", "10MG", "CAP", "30")

	assert connection.execute(
		"SELECT din, upc, pack_size FROM narcs_details ORDER BY pack_size"
	).fetchall() == [
		("02248809", "663220111026", "100"),
		("02248809", "663220111026", "30"),
	]


def test_add_medication_rejects_duplicate_detail_without_changing_existing_row():
	connection = create_catalog_connection()
	connection.execute(
		"INSERT INTO narcs (din, name, quantity) VALUES (?, ?, ?)",
		("02248809", "ADDERALL XR", 9),
	)
	connection.execute(
		"INSERT INTO narcs_details (din, upc, strength, form, pack_size) VALUES (?, ?, ?, ?, ?)",
		("02248809", "663220111026", "10MG", "CAP", "100"),
	)
	connection.commit()
	service = CatalogManagementService(connection)

	with pytest.raises(DuplicateMedicationDetailError, match="Medication detail already exists"):
		service.add_medication("CHANGED NAME", "02248809", "663220111026", "10MG", "CAP", "100")

	assert connection.execute("SELECT name, quantity FROM narcs WHERE din = ?", ("02248809",)).fetchone() == (
		"ADDERALL XR",
		9,
	)
	assert connection.execute("SELECT COUNT(*) FROM narcs_details").fetchone()[0] == 1


def test_add_medication_normalizes_blank_optional_values():
	connection = create_catalog_connection()
	service = CatalogManagementService(connection)

	service.add_medication(
		name="ADDERALL XR",
		din="2248809",
		upc="663220111026",
		strength="",
		form="CAP",
		pack_size="",
	)

	assert connection.execute("SELECT strength, pack_size FROM narcs_details").fetchone() == (None, "0")


@pytest.mark.parametrize(
	"kwargs, message",
	[
		({"name": "", "din": "2248809", "upc": "663220111026", "form": "CAP"}, "Drug name is required."),
		({"name": "ADDERALL XR", "din": "", "upc": "663220111026", "form": "CAP"}, "DIN is required."),
		({"name": "ADDERALL XR", "din": "ABC", "upc": "663220111026", "form": "CAP"}, "DIN must be numeric."),
		({"name": "ADDERALL XR", "din": "123456789", "upc": "663220111026", "form": "CAP"}, "DIN must be a numeric value"),
		({"name": "ADDERALL XR", "din": "2248809", "upc": "", "form": "CAP"}, "UPC is required."),
		({"name": "ADDERALL XR", "din": "2248809", "upc": "ABC", "form": "CAP"}, "UPC must be numeric."),
		({"name": "ADDERALL XR", "din": "2248809", "upc": "1234567890123", "form": "CAP"}, "UPC must be a numeric value"),
		({"name": "ADDERALL XR", "din": "2248809", "upc": "663220111026", "form": ""}, "Form is required."),
		({"name": "ADDERALL XR", "din": "2248809", "upc": "663220111026", "form": "CAP", "pack_size": "1.5"}, "Pack size must be a whole number."),
	],
)
def test_add_medication_validates_input(kwargs, message):
	connection = create_catalog_connection()
	service = CatalogManagementService(connection)

	with pytest.raises(ValueError, match=message):
		service.add_medication(**kwargs)

	assert connection.execute("SELECT COUNT(*) FROM narcs").fetchone()[0] == 0
	assert connection.execute("SELECT COUNT(*) FROM narcs_details").fetchone()[0] == 0
