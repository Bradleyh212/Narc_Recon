import sqlite3

from services import user_service


def test_normalize_role_strips_and_lowercases_role_values():
	assert user_service.normalize_role(" Pharmacist ") == "pharmacist"
	assert user_service.normalize_role("Tech") == "tech"
	assert user_service.normalize_role(None) == ""


def test_role_allows_settings_accepts_pharmacist_case_insensitively():
	assert user_service.role_allows_settings("Pharmacist") is True
	assert user_service.role_allows_settings("pharmacist") is True
	assert user_service.role_allows_settings(" pharmacist ") is True
	assert user_service.role_allows_settings("Tech") is False
	assert user_service.role_allows_settings(None) is False


def test_role_allows_reconciliation_accepts_existing_roles_case_insensitively():
	assert user_service.role_allows_reconciliation("Pharmacist") is True
	assert user_service.role_allows_reconciliation("pharmacist") is True
	assert user_service.role_allows_reconciliation("Tech") is True
	assert user_service.role_allows_reconciliation("tech") is True
	assert user_service.role_allows_reconciliation("Technician") is False
	assert user_service.role_allows_reconciliation(None) is False


def make_users_connection():
	connection = sqlite3.connect(":memory:")
	connection.execute("""
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			user_id TEXT NOT NULL UNIQUE,
			role TEXT DEFAULT 'staff',
			created_at TEXT NOT NULL
		)
	""")
	return connection


def test_add_user_preserves_current_insert_behavior():
	connection = make_users_connection()

	user_service.add_user(connection, " TMP ", "Pharmacist")

	row = connection.execute("SELECT user_id, role, created_at FROM users").fetchone()
	assert row[0:2] == ("TMP", "Pharmacist")
	assert "T" in row[2]
	assert row[2].endswith("+00:00")


def test_user_service_add_user_preserves_current_insert_behavior():
	connection = make_users_connection()
	service = user_service.UserService(connection)

	service.add_user(" TMP ", "Pharmacist")

	row = connection.execute("SELECT user_id, role, created_at FROM users").fetchone()
	assert row[0:2] == ("TMP", "Pharmacist")
	assert "T" in row[2]
	assert row[2].endswith("+00:00")


def test_get_user_role_returns_role_or_none():
	connection = make_users_connection()
	user_service.add_user(connection, "BHD", "admin")

	assert user_service.get_user_role(connection, " BHD ") == "admin"
	assert user_service.get_user_role(connection, "NOPE") is None


def test_user_service_get_user_role_returns_role_or_none():
	connection = make_users_connection()
	service = user_service.UserService(connection)
	service.add_user("BHD", "admin")

	assert service.get_user_role(" BHD ") == "admin"
	assert service.get_user_role("NOPE") is None


def test_list_users_returns_current_shape_ordered_by_id():
	connection = make_users_connection()
	connection.execute(
		"INSERT INTO users (user_id, role, created_at) VALUES (?, ?, ?)",
		("BHD", "admin", "Today"),
	)
	connection.execute(
		"INSERT INTO users (user_id, role, created_at) VALUES (?, ?, ?)",
		("TMP", "staff", "Tomorrow"),
	)

	assert user_service.list_users(connection) == [
		(1, "BHD", "admin", "Today"),
		(2, "TMP", "staff", "Tomorrow"),
	]


def test_user_service_list_users_returns_current_shape_ordered_by_id():
	connection = make_users_connection()
	service = user_service.UserService(connection)
	connection.execute(
		"INSERT INTO users (user_id, role, created_at) VALUES (?, ?, ?)",
		("BHD", "admin", "Today"),
	)
	connection.execute(
		"INSERT INTO users (user_id, role, created_at) VALUES (?, ?, ?)",
		("TMP", "staff", "Tomorrow"),
	)

	assert service.list_users() == [
		(1, "BHD", "admin", "Today"),
		(2, "TMP", "staff", "Tomorrow"),
	]


def test_list_user_ids_returns_current_shape():
	connection = make_users_connection()
	connection.execute(
		"INSERT INTO users (user_id, role, created_at) VALUES (?, ?, ?)",
		("BHD", "admin", "Today"),
	)
	connection.execute(
		"INSERT INTO users (user_id, role, created_at) VALUES (?, ?, ?)",
		("TMP", "staff", "Tomorrow"),
	)

	assert user_service.list_user_ids(connection) == ["BHD", "TMP"]


def test_user_service_list_user_ids_returns_current_shape():
	connection = make_users_connection()
	service = user_service.UserService(connection)
	connection.execute(
		"INSERT INTO users (user_id, role, created_at) VALUES (?, ?, ?)",
		("BHD", "admin", "Today"),
	)
	connection.execute(
		"INSERT INTO users (user_id, role, created_at) VALUES (?, ?, ?)",
		("TMP", "staff", "Tomorrow"),
	)

	assert service.list_user_ids() == ["BHD", "TMP"]


def test_remove_user_deletes_row_and_user_exists_returns_bool():
	connection = make_users_connection()
	user_service.add_user(connection, "TMP", "staff")

	assert user_service.user_exists(connection, " TMP ") is True

	user_service.remove_user(connection, " TMP ")

	assert user_service.user_exists(connection, "TMP") is False
	assert user_service.list_users(connection) == []


def test_user_service_remove_user_deletes_row_and_user_exists_returns_bool():
	connection = make_users_connection()
	service = user_service.UserService(connection)
	service.add_user("TMP", "staff")

	assert service.user_exists(" TMP ") is True

	service.remove_user(" TMP ")

	assert service.user_exists("TMP") is False
	assert service.list_users() == []
