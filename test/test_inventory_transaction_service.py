import sqlite3

import inventory_transaction_service


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


def current_quantity(connection):
	return connection.execute("SELECT quantity FROM narcs WHERE din = ?", ("02248809",)).fetchone()[0]


def test_increment_inventory_quantity_updates_quantity_and_commits():
	connection = make_inventory_connection(10)
	cursor = connection.cursor()

	inventory_transaction_service.increment_inventory_quantity(cursor, connection, "02248809", 2.5)

	assert current_quantity(connection) == 12.5


def test_decrement_inventory_quantity_updates_quantity_and_commits():
	connection = make_inventory_connection(10)
	cursor = connection.cursor()

	inventory_transaction_service.decrement_inventory_quantity(cursor, connection, "02248809", 2.5)

	assert current_quantity(connection) == 7.5


def test_set_inventory_quantity_updates_quantity_and_commits():
	connection = make_inventory_connection(10)
	cursor = connection.cursor()

	inventory_transaction_service.set_inventory_quantity(cursor, connection, "02248809", 0)

	assert current_quantity(connection) == 0
