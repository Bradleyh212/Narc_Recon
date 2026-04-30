from datetime import datetime, UTC


def normalize_role(role):
	if role is None:
		return ""
	return str(role).strip().lower()


def role_allows_settings(role):
	return normalize_role(role) == "pharmacist"


def role_allows_reconciliation(role):
	return normalize_role(role) in {"pharmacist", "tech"}


def add_user(connection, user_id: str, role: str = "Assistant"):
	"""Add a new user to the users table."""
	with connection:
		connection.execute(
			"INSERT INTO users (user_id, role, created_at) VALUES (?, ?, ?)",
			(user_id.strip(), role, datetime.now(UTC).isoformat())
		)


def get_user_role(connection, user_id):
	"""Return the role for a user_id, or None when the user is missing."""
	row = connection.execute("SELECT role FROM users where user_id = ?", (user_id.strip(),)).fetchone()
	return row[0] if row else None


def list_users(connection):
	"""Return all users as (id, user_id, role, created_at)."""
	cursor = connection.cursor()
	return cursor.execute("SELECT id, user_id, role, created_at FROM users ORDER BY id").fetchall()


def list_user_ids(connection):
	rows = connection.execute("SELECT user_id FROM users").fetchall()
	return [row[0] for row in rows]


def remove_user(connection, user_id: str):
	"""Remove a user by their user_id."""
	with connection:
		connection.execute("DELETE FROM users WHERE user_id = ?", (user_id.strip(),))


def user_exists(connection, user_id: str) -> bool:
	"""Check if a user already exists."""
	cursor = connection.cursor()
	row = cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id.strip(),)).fetchone()
	return bool(row)
