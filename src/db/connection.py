import sqlite3

from config.paths import get_db_path


DB_PATH = get_db_path()


def get_conn():
	conn = sqlite3.connect(DB_PATH, timeout=10, isolation_level=None)
	conn.execute("PRAGMA foreign_keys = ON;")
	conn.execute("PRAGMA journal_mode = WAL;")
	return conn
