import sqlite3

from db import auth_schema


def table_columns(connection, table_name):
	return {
		row[1]: row
		for row in connection.execute(f"PRAGMA table_info({table_name})")
	}


def test_migrate_auth_creates_app_account_table_with_expected_columns():
	connection = sqlite3.connect(":memory:")

	auth_schema.migrate_auth(connection)

	columns = table_columns(connection, "app_account")
	assert set(columns) == {"id", "username", "password_hash", "last_login_utc"}
	assert columns["id"][2] == "INTEGER"
	assert columns["id"][5] == 1
	assert columns["username"][2] == "TEXT"
	assert columns["username"][3] == 1
	assert columns["password_hash"][2] == "TEXT"
	assert columns["password_hash"][3] == 1
	assert columns["last_login_utc"][2] == "TEXT"


def test_migrate_users_creates_users_table_with_expected_columns():
	connection = sqlite3.connect(":memory:")

	auth_schema.migrate_users(connection)

	columns = table_columns(connection, "users")
	assert set(columns) == {"id", "user_id", "role", "created_at"}
	assert columns["id"][2] == "INTEGER"
	assert columns["id"][5] == 1
	assert columns["user_id"][2] == "TEXT"
	assert columns["user_id"][3] == 1
	assert columns["role"][2] == "TEXT"
	assert columns["role"][4] == "'staff'"
	assert columns["created_at"][2] == "TEXT"
	assert columns["created_at"][3] == 1


def test_auth_schema_migrations_are_idempotent():
	connection = sqlite3.connect(":memory:")

	auth_schema.migrate_auth(connection)
	auth_schema.migrate_users(connection)
	auth_schema.migrate_auth(connection)
	auth_schema.migrate_users(connection)

	table_names = {
		row[0]
		for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
	}
	assert {"app_account", "users"}.issubset(table_names)
