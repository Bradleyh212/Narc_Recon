import excel_import_service
from db import schema_service


class CatalogDatabaseService:
	def __init__(self, cursor, connection, excel_path):
		self.cursor = cursor
		self.connection = connection
		self.excel_path = excel_path

	def initialize_from_excel(self):
		narc_list = excel_import_service.create_narc_list(self.excel_path)
		schema_service.create_narcs_table(self.cursor)
		schema_service.create_narcs_details_table(self.cursor)
		schema_service.create_audit_log_table(self.cursor)
		excel_import_service.from_excel_to_sql(self.cursor, narc_list)
		self.connection.commit()


def initialize_database_from_excel(cursor, connection, excel_path):
	return CatalogDatabaseService(cursor, connection, excel_path).initialize_from_excel()
