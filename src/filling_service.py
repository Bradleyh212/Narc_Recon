def decrement_inventory_quantity(cursor, connection, din, amount):
	cursor.execute("UPDATE narcs SET quantity = quantity - ? WHERE din = ?", (amount, din))
	connection.commit()
