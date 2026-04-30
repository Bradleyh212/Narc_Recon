import sqlite3

import receiving_service


def make_inventory_connection(quantity=10):
	connection = sqlite3.connect(":memory:")
	connection.execute("""
		CREATE TABLE narcs (
			din TEXT PRIMARY KEY,
			name TEXT NOT NULL,
			quantity INTEGER NOT NULL DEFAULT 0
		)
	""")
	connection.execute(
		"INSERT INTO narcs (din, name, quantity) VALUES (?, ?, ?)",
		("02248809", "ADDERALL XR", quantity),
	)
	return connection


def test_increment_inventory_quantity_updates_quantity_and_commits():
	connection = make_inventory_connection(10)
	cursor = connection.cursor()

	receiving_service.increment_inventory_quantity(cursor, connection, "02248809", 3)

	assert connection.execute("SELECT quantity FROM narcs WHERE din = ?", ("02248809",)).fetchone()[0] == 13


def test_increment_inventory_quantity_preserves_current_float_amount_behavior():
	connection = make_inventory_connection(10)
	cursor = connection.cursor()

	receiving_service.increment_inventory_quantity(cursor, connection, "02248809", 2.5)

	assert connection.execute("SELECT quantity FROM narcs WHERE din = ?", ("02248809",)).fetchone()[0] == 12.5
