import inventory_transaction_service


def increment_inventory_quantity(cursor, connection, din, amount):
	return inventory_transaction_service.increment_inventory_quantity(cursor, connection, din, amount)
