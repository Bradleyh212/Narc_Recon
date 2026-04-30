def find_narcs_by_upc(cursor, upc):
	cursor.execute("""
		SELECT n.din, n.name, n.quantity, nd.upc, nd.strength, nd.form, nd.pack_size
		FROM narcs n
		INNER JOIN narcs_details nd ON n.din = nd.din
		WHERE nd.upc = ?
	""", (upc,))
	return cursor.fetchall()


def find_narcs_by_din(cursor, din):
	cursor.execute("""
		SELECT n.din, n.name, n.quantity, nd.upc, nd.strength, nd.form, nd.pack_size
		FROM narcs n
		INNER JOIN narcs_details nd ON n.din = nd.din
		WHERE nd.din = ?
	""", (din,))
	return cursor.fetchall()


def find_quantity_by_upc(cursor, upc):
	cursor.execute("SELECT din FROM narcs_details WHERE upc = ?", (upc,))
	din = cursor.fetchone()[0]
	return find_quantity_by_din(cursor, din)


def find_quantity_by_din(cursor, din):
	cursor.execute("SELECT quantity FROM narcs WHERE din = ?", (din,))
	return cursor.fetchone()[0]


def fetch_narcs_table(cursor):
	cursor.execute("""
		SELECT n.din, n.name, n.quantity, nd.upc, nd.strength, nd.form, nd.pack_size
		FROM narcs n
		INNER JOIN narcs_details nd ON n.din = nd.din
	""")
	rows = cursor.fetchall()
	column_names = [desc[0] for desc in cursor.description]
	return column_names, rows
