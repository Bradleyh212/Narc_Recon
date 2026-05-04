import sqlite3

import inventory_service


def make_inventory_connection():
	connection = sqlite3.connect(":memory:")
	connection.execute("""
		CREATE TABLE narcs (
			din TEXT PRIMARY KEY,
			name TEXT NOT NULL,
			quantity INTEGER NOT NULL DEFAULT 0
		)
	""")
	connection.execute("""
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
	connection.execute(
		"INSERT INTO narcs (din, name, quantity) VALUES (?, ?, ?)",
		("02248809", "ADDERALL XR", 12),
	)
	connection.execute(
		"INSERT INTO narcs_details (din, upc, strength, form, pack_size) VALUES (?, ?, ?, ?, ?)",
		("02248809", "663220111026", "10MG", "CAP", "100"),
	)
	return connection


def make_read_service():
	connection = make_inventory_connection()
	return inventory_service.InventoryReadService(connection.cursor())


def expected_narc_row():
	return ("02248809", "ADDERALL XR", 12, "663220111026", "10MG", "CAP", "100")


def test_inventory_read_service_find_narcs_by_din_returns_current_shape():
	service = make_read_service()

	assert service.find_narcs_by_din("02248809") == [expected_narc_row()]


def test_inventory_read_service_find_narcs_by_upc_returns_current_shape():
	service = make_read_service()

	assert service.find_narcs_by_upc("663220111026") == [expected_narc_row()]


def test_inventory_read_service_find_quantity_by_din_returns_current_shape():
	service = make_read_service()

	assert service.find_quantity_by_din("02248809") == 12


def test_inventory_read_service_find_quantity_by_upc_returns_current_shape():
	service = make_read_service()

	assert service.find_quantity_by_upc("663220111026") == 12


def test_inventory_read_service_fetch_narcs_table_returns_current_shape():
	service = make_read_service()

	column_names, rows = service.fetch_narcs_table()

	assert column_names == ["din", "name", "quantity", "upc", "strength", "form", "pack_size"]
	assert rows == [expected_narc_row()]
