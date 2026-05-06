class InventoryReadService:
	def __init__(self, cursor):
		self.cursor = cursor

	def find_narcs_by_upc(self, upc):
		self.cursor.execute("""
			SELECT n.din, n.name, n.quantity, nd.upc, nd.strength, nd.form, nd.pack_size
			FROM narcs n
			INNER JOIN narcs_details nd ON n.din = nd.din
			WHERE nd.upc = ?
		""", (upc,))
		return self.cursor.fetchall()

	def find_narcs_by_din(self, din):
		self.cursor.execute("""
			SELECT n.din, n.name, n.quantity, nd.upc, nd.strength, nd.form, nd.pack_size
			FROM narcs n
			INNER JOIN narcs_details nd ON n.din = nd.din
			WHERE nd.din = ?
		""", (din,))
		return self.cursor.fetchall()

	def find_quantity_by_upc(self, upc):
		self.cursor.execute("SELECT din FROM narcs_details WHERE upc = ?", (upc,))
		din = self.cursor.fetchone()[0]
		return self.find_quantity_by_din(din)

	def find_quantity_by_din(self, din):
		self.cursor.execute("SELECT quantity FROM narcs WHERE din = ?", (din,))
		return self.cursor.fetchone()[0]

	def fetch_narcs_table(self):
		self.cursor.execute("""
			SELECT n.din, n.name, n.quantity, nd.upc, nd.strength, nd.form, nd.pack_size
			FROM narcs n
			INNER JOIN narcs_details nd ON n.din = nd.din
		""")
		rows = self.cursor.fetchall()
		column_names = [desc[0] for desc in self.cursor.description]
		return column_names, rows


def find_narcs_by_upc(cursor, upc):
	return InventoryReadService(cursor).find_narcs_by_upc(upc)


def find_narcs_by_din(cursor, din):
	return InventoryReadService(cursor).find_narcs_by_din(din)


def find_quantity_by_upc(cursor, upc):
	return InventoryReadService(cursor).find_quantity_by_upc(upc)


def find_quantity_by_din(cursor, din):
	return InventoryReadService(cursor).find_quantity_by_din(din)


def fetch_narcs_table(cursor):
	return InventoryReadService(cursor).fetch_narcs_table()
