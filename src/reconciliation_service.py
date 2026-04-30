def set_inventory_quantity(cursor, connection, din, quantity):
	cursor.execute("UPDATE narcs SET quantity = ? WHERE din = ?", (quantity, din))
	connection.commit()
