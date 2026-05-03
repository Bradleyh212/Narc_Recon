import inventory_transaction_service


def set_inventory_quantity(cursor, connection, din, quantity):
	return inventory_transaction_service.set_inventory_quantity(cursor, connection, din, quantity)
