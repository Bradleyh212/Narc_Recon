import sqlite3

from db import schema_service


def table_info(cursor, table_name):
	return cursor.execute(f"PRAGMA table_info({table_name})").fetchall()


def table_names(cursor):
	return {
		row[0]
		for row in cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
	}


def test_schema_service_create_narcs_table_creates_current_schema():
	conn = sqlite3.connect(":memory:")
	cursor = conn.cursor()
	service = schema_service.SchemaService(cursor)

	service.create_narcs_table()

	assert table_info(cursor, "narcs") == [
		(0, "din", "TEXT", 0, None, 1),
		(1, "name", "TEXT", 1, None, 0),
		(2, "quantity", "INTEGER", 1, "0", 0),
	]


def test_create_narcs_table_creates_current_schema():
	conn = sqlite3.connect(":memory:")
	cursor = conn.cursor()

	schema_service.create_narcs_table(cursor)
	schema_service.create_narcs_table(cursor)

	assert table_info(cursor, "narcs") == [
		(0, "din", "TEXT", 0, None, 1),
		(1, "name", "TEXT", 1, None, 0),
		(2, "quantity", "INTEGER", 1, "0", 0),
	]


def test_schema_service_create_narcs_details_table_creates_current_schema():
	conn = sqlite3.connect(":memory:")
	cursor = conn.cursor()
	service = schema_service.SchemaService(cursor)

	service.create_narcs_details_table()

	assert table_info(cursor, "narcs_details") == [
		(0, "din", "TEXT", 1, None, 1),
		(1, "upc", "TEXT", 1, None, 2),
		(2, "strength", "TEXT", 0, None, 0),
		(3, "form", "TEXT", 1, None, 0),
		(4, "pack_size", "TEXT", 0, None, 3),
	]
	assert cursor.execute("PRAGMA foreign_key_list(narcs_details)").fetchall() == [
		(0, 0, "narcs", "din", "din", "NO ACTION", "NO ACTION", "NONE")
	]


def test_create_narcs_details_table_creates_current_schema():
	conn = sqlite3.connect(":memory:")
	cursor = conn.cursor()

	schema_service.create_narcs_details_table(cursor)
	schema_service.create_narcs_details_table(cursor)

	assert table_info(cursor, "narcs_details") == [
		(0, "din", "TEXT", 1, None, 1),
		(1, "upc", "TEXT", 1, None, 2),
		(2, "strength", "TEXT", 0, None, 0),
		(3, "form", "TEXT", 1, None, 0),
		(4, "pack_size", "TEXT", 0, None, 3),
	]
	assert cursor.execute("PRAGMA foreign_key_list(narcs_details)").fetchall() == [
		(0, 0, "narcs", "din", "din", "NO ACTION", "NO ACTION", "NONE")
	]


def test_schema_service_create_audit_log_table_creates_current_schema():
	conn = sqlite3.connect(":memory:")
	cursor = conn.cursor()
	service = schema_service.SchemaService(cursor)

	service.create_audit_log_table()

	assert table_info(cursor, "audit_log") == [
		(0, "log_id", "INTEGER", 0, None, 1),
		(1, "din", "TEXT", 0, None, 0),
		(2, "old_qty", "INT", 0, None, 0),
		(3, "new_qty", "INT", 0, None, 0),
		(4, "Updated_By", "VARCHAR(10)", 0, None, 0),
		(5, "Timestamp", "TIMESTAMP", 0, "CURRENT_TIMESTAMP", 0),
		(6, "transaction_type", "TEXT", 0, None, 0),
		(7, "discrepancy", "INT", 0, None, 0),
	]


def test_create_audit_log_table_creates_current_schema():
	conn = sqlite3.connect(":memory:")
	cursor = conn.cursor()

	schema_service.create_audit_log_table(cursor)
	schema_service.create_audit_log_table(cursor)

	assert table_info(cursor, "audit_log") == [
		(0, "log_id", "INTEGER", 0, None, 1),
		(1, "din", "TEXT", 0, None, 0),
		(2, "old_qty", "INT", 0, None, 0),
		(3, "new_qty", "INT", 0, None, 0),
		(4, "Updated_By", "VARCHAR(10)", 0, None, 0),
		(5, "Timestamp", "TIMESTAMP", 0, "CURRENT_TIMESTAMP", 0),
		(6, "transaction_type", "TEXT", 0, None, 0),
		(7, "discrepancy", "INT", 0, None, 0),
	]


def test_schema_service_create_all_catalog_tables_creates_current_tables():
	conn = sqlite3.connect(":memory:")
	cursor = conn.cursor()
	service = schema_service.SchemaService(cursor)

	service.create_all_catalog_tables()

	assert {"narcs", "narcs_details", "audit_log"}.issubset(table_names(cursor))
	assert table_info(cursor, "narcs") == [
		(0, "din", "TEXT", 0, None, 1),
		(1, "name", "TEXT", 1, None, 0),
		(2, "quantity", "INTEGER", 1, "0", 0),
	]
	assert table_info(cursor, "narcs_details") == [
		(0, "din", "TEXT", 1, None, 1),
		(1, "upc", "TEXT", 1, None, 2),
		(2, "strength", "TEXT", 0, None, 0),
		(3, "form", "TEXT", 1, None, 0),
		(4, "pack_size", "TEXT", 0, None, 3),
	]
	assert table_info(cursor, "audit_log") == [
		(0, "log_id", "INTEGER", 0, None, 1),
		(1, "din", "TEXT", 0, None, 0),
		(2, "old_qty", "INT", 0, None, 0),
		(3, "new_qty", "INT", 0, None, 0),
		(4, "Updated_By", "VARCHAR(10)", 0, None, 0),
		(5, "Timestamp", "TIMESTAMP", 0, "CURRENT_TIMESTAMP", 0),
		(6, "transaction_type", "TEXT", 0, None, 0),
		(7, "discrepancy", "INT", 0, None, 0),
	]


def test_schema_service_repeated_calls_remain_idempotent():
	conn = sqlite3.connect(":memory:")
	cursor = conn.cursor()
	service = schema_service.SchemaService(cursor)

	service.create_all_catalog_tables()
	service.create_all_catalog_tables()

	assert {"narcs", "narcs_details", "audit_log"}.issubset(table_names(cursor))
	assert table_info(cursor, "narcs") == [
		(0, "din", "TEXT", 0, None, 1),
		(1, "name", "TEXT", 1, None, 0),
		(2, "quantity", "INTEGER", 1, "0", 0),
	]
