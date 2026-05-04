import excel_import_service
import schema_service


def initialize_database_from_excel(cursor, connection, excel_path):
	narc_list = excel_import_service.create_narc_list(excel_path)
	schema_service.create_narcs_table(cursor)
	schema_service.create_narcs_details_table(cursor)
	schema_service.create_audit_log_table(cursor)
	excel_import_service.from_excel_to_sql(cursor, narc_list)
	connection.commit()
