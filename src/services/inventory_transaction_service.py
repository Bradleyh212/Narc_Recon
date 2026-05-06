class InventoryTransactionService:
	def __init__(self, cursor, connection):
		self.cursor = cursor
		self.connection = connection

	def increment_quantity(self, din, amount):
		self.cursor.execute("UPDATE narcs SET quantity = quantity + ? WHERE din = ?", (amount, din))
		self.connection.commit()

	def decrement_quantity(self, din, amount):
		self.cursor.execute("UPDATE narcs SET quantity = quantity - ? WHERE din = ?", (amount, din))
		self.connection.commit()

	def set_quantity(self, din, quantity):
		self.cursor.execute("UPDATE narcs SET quantity = ? WHERE din = ?", (quantity, din))
		self.connection.commit()


def increment_inventory_quantity(cursor, connection, din, amount):
	return InventoryTransactionService(cursor, connection).increment_quantity(din, amount)


def decrement_inventory_quantity(cursor, connection, din, amount):
	return InventoryTransactionService(cursor, connection).decrement_quantity(din, amount)


def set_inventory_quantity(cursor, connection, din, quantity):
	return InventoryTransactionService(cursor, connection).set_quantity(din, quantity)
