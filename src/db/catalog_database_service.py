from db import schema_service
from services import excel_import_service


class CatalogDatabaseService:
	def __init__(self, cursor, connection, excel_path):
		self.cursor = cursor
		self.connection = connection
		self.excel_path = excel_path

	def create_catalog_tables(self):
		schema_service.create_narcs_table(self.cursor)
		schema_service.create_narcs_details_table(self.cursor)
		schema_service.create_audit_log_table(self.cursor)

	def catalog_row_counts(self):
		narcs_count = self.cursor.execute("SELECT COUNT(*) FROM narcs").fetchone()[0]
		narcs_details_count = self.cursor.execute("SELECT COUNT(*) FROM narcs_details").fetchone()[0]
		return narcs_count, narcs_details_count

	def catalog_is_initialized(self):
		narcs_count, narcs_details_count = self.catalog_row_counts()
		return narcs_count > 0 and narcs_details_count > 0

	def catalog_is_empty(self):
		narcs_count, narcs_details_count = self.catalog_row_counts()
		return narcs_count == 0 and narcs_details_count == 0

	def import_from_excel(self):
		narc_list = excel_import_service.create_narc_list(self.excel_path)
		excel_import_service.from_excel_to_sql(self.cursor, narc_list)

	def initialize_from_excel(self):
		self.create_catalog_tables()
		self.import_from_excel()
		self.connection.commit()

	def initialize_for_startup(self):
		self.create_catalog_tables()
		if self.catalog_is_initialized():
			self.connection.commit()
			return
		if not self.catalog_is_empty():
			raise RuntimeError("Catalog tables are partially initialized; startup will not repair them automatically.")
		self.import_from_excel()
		self.connection.commit()


def initialize_database_from_excel(cursor, connection, excel_path):
	return CatalogDatabaseService(cursor, connection, excel_path).initialize_from_excel()


def initialize_catalog_for_startup(cursor, connection, excel_path):
	return CatalogDatabaseService(cursor, connection, excel_path).initialize_for_startup()
