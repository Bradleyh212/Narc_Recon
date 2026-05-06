import sqlite3

from services import reconciliation_service


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


def test_set_inventory_quantity_updates_quantity_and_commits():
	connection = make_inventory_connection(10)
	cursor = connection.cursor()

	reconciliation_service.set_inventory_quantity(cursor, connection, "02248809", 4)

	assert connection.execute("SELECT quantity FROM narcs WHERE din = ?", ("02248809",)).fetchone()[0] == 4


def test_set_inventory_quantity_preserves_current_zero_quantity_behavior():
	connection = make_inventory_connection(10)
	cursor = connection.cursor()

	reconciliation_service.set_inventory_quantity(cursor, connection, "02248809", 0)

	assert connection.execute("SELECT quantity FROM narcs WHERE din = ?", ("02248809",)).fetchone()[0] == 0


def test_set_inventory_quantity_preserves_current_float_quantity_behavior():
	connection = make_inventory_connection(10)
	cursor = connection.cursor()

	reconciliation_service.set_inventory_quantity(cursor, connection, "02248809", 7.5)

	assert connection.execute("SELECT quantity FROM narcs WHERE din = ?", ("02248809",)).fetchone()[0] == 7.5
