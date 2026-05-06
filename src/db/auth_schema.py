def migrate_auth(conn):
	with conn:
		conn.executescript("""
		CREATE TABLE IF NOT EXISTS app_account (
			id INTEGER PRIMARY KEY CHECK (id = 1),
			username TEXT NOT NULL UNIQUE,
			password_hash TEXT NOT NULL,
			last_login_utc TEXT
		);
		""")


def migrate_users(conn):
	with conn:
		conn.executescript("""
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			user_id TEXT NOT NULL UNIQUE,
			role TEXT DEFAULT 'staff',
			created_at TEXT NOT NULL
		);
		""")
