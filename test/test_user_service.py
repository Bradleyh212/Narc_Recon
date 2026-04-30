import sqlite3

import user_service


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


def test_get_user_role_returns_role_or_none():
	connection = make_users_connection()
	user_service.add_user(connection, "BHD", "admin")

	assert user_service.get_user_role(connection, " BHD ") == "admin"
	assert user_service.get_user_role(connection, "NOPE") is None


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


def test_remove_user_deletes_row_and_user_exists_returns_bool():
	connection = make_users_connection()
	user_service.add_user(connection, "TMP", "staff")

	assert user_service.user_exists(connection, " TMP ") is True

	user_service.remove_user(connection, " TMP ")

	assert user_service.user_exists(connection, "TMP") is False
	assert user_service.list_users(connection) == []
