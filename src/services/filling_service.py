from services import inventory_transaction_service


def decrement_inventory_quantity(cursor, connection, din, amount):
	return inventory_transaction_service.decrement_inventory_quantity(cursor, connection, din, amount)
