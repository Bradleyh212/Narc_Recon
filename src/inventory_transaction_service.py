def increment_inventory_quantity(cursor, connection, din, amount):
	cursor.execute("UPDATE narcs SET quantity = quantity + ? WHERE din = ?", (amount, din))
	connection.commit()


def decrement_inventory_quantity(cursor, connection, din, amount):
	cursor.execute("UPDATE narcs SET quantity = quantity - ? WHERE din = ?", (amount, din))
	connection.commit()


def set_inventory_quantity(cursor, connection, din, quantity):
	cursor.execute("UPDATE narcs SET quantity = ? WHERE din = ?", (quantity, din))
	connection.commit()
