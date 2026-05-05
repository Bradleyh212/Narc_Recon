class SchemaService:
	def __init__(self, cursor):
		self.cursor = cursor

	def create_narcs_table(self):
		self.cursor.execute("""
			CREATE TABLE IF NOT EXISTS narcs (
				din TEXT PRIMARY KEY,
				name TEXT NOT NULL,
				quantity INTEGER NOT NULL DEFAULT 0
			)
		""")

	def create_narcs_details_table(self):
		self.cursor.execute("""
			CREATE TABLE IF NOT EXISTS narcs_details (
				din TEXT NOT NULL,
				upc TEXT NOT NULL,
				strength TEXT,
				form TEXT NOT NULL,
				pack_size TEXT,
				PRIMARY KEY (din, upc, pack_size),
				FOREIGN KEY (din) REFERENCES narcs(din)
			)
		""")

	def create_audit_log_table(self):
		self.cursor.execute("""
			CREATE TABLE IF NOT EXISTS audit_log (
				log_id INTEGER PRIMARY KEY AUTOINCREMENT,
				din TEXT,
				old_qty INT,
				new_qty INT,
				Updated_By VARCHAR(10),
				Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				transaction_type TEXT,
				discrepancy INT
			)
		""")

	def create_all_catalog_tables(self):
		self.create_narcs_table()
		self.create_narcs_details_table()
		self.create_audit_log_table()


def create_narcs_table(cursor):
	return SchemaService(cursor).create_narcs_table()


def create_narcs_details_table(cursor):
	return SchemaService(cursor).create_narcs_details_table()


def create_audit_log_table(cursor):
	return SchemaService(cursor).create_audit_log_table()
