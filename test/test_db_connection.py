import importlib
from pathlib import Path


def load_connection_module(monkeypatch, tmp_path, fresh_app_modules):
	db_path = tmp_path / "connection-test.db"
	monkeypatch.setenv("NARC_RECON_DB_PATH", str(db_path))
	return importlib.import_module("db.connection"), db_path


def test_get_conn_uses_temp_database(monkeypatch, tmp_path, fresh_app_modules):
	connection_module, db_path = load_connection_module(monkeypatch, tmp_path, fresh_app_modules)

	conn = connection_module.get_conn()
	try:
		database_path = conn.execute("PRAGMA database_list").fetchone()[2]
	finally:
		conn.close()

	assert Path(database_path) == db_path


def test_get_conn_enables_foreign_keys(monkeypatch, tmp_path, fresh_app_modules):
	connection_module, _ = load_connection_module(monkeypatch, tmp_path, fresh_app_modules)

	conn = connection_module.get_conn()
	try:
		foreign_keys_enabled = conn.execute("PRAGMA foreign_keys").fetchone()[0]
	finally:
		conn.close()

	assert foreign_keys_enabled == 1


def test_get_conn_sets_wal_journal_mode(monkeypatch, tmp_path, fresh_app_modules):
	connection_module, _ = load_connection_module(monkeypatch, tmp_path, fresh_app_modules)

	conn = connection_module.get_conn()
	try:
		journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
	finally:
		conn.close()

	assert journal_mode.lower() == "wal"
