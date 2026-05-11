import importlib
import sqlite3
from pathlib import Path


import pytest


@pytest.fixture
def auth_env(monkeypatch, tmp_path, fresh_app_modules):
	db_path = tmp_path / "auth-test.db"
	monkeypatch.setenv("NARC_RECON_DB_PATH", str(db_path))
	connection_module = importlib.import_module("db.connection")
	auth_schema = importlib.import_module("db.auth_schema")
	auth_service = importlib.import_module("services.auth_service")
	yield connection_module, auth_schema, auth_service, db_path


def test_get_conn_uses_temp_database(auth_env):
	connection_module, _, _, db_path = auth_env

	conn = connection_module.get_conn()
	try:
		database_path = conn.execute("PRAGMA database_list").fetchone()[2]
	finally:
		conn.close()

	assert Path(database_path) == db_path


def test_auth_uses_local_config_pepper_when_env_missing(monkeypatch, tmp_path, fresh_app_modules):
	home_path = tmp_path / "home"
	config_dir = home_path / "NarcReconData"
	config_dir.mkdir(parents=True)
	(config_dir / "config.env").write_text(
		"NARC_RECON_PEPPER=fake-config-pepper\n",
		encoding="utf-8",
	)
	monkeypatch.setenv("HOME", str(home_path))
	monkeypatch.setenv("NARC_RECON_DB_PATH", str(tmp_path / "auth-test.db"))
	monkeypatch.delenv("NARC_RECON_PEPPER", raising=False)

	auth_service = importlib.import_module("services.auth_service")

	assert auth_service.PEPPER == "fake-config-pepper"


def test_auth_env_pepper_overrides_local_config(monkeypatch, tmp_path, fresh_app_modules):
	home_path = tmp_path / "home"
	config_dir = home_path / "NarcReconData"
	config_dir.mkdir(parents=True)
	(config_dir / "config.env").write_text(
		"NARC_RECON_PEPPER=fake-config-pepper\n",
		encoding="utf-8",
	)
	monkeypatch.setenv("HOME", str(home_path))
	monkeypatch.setenv("NARC_RECON_DB_PATH", str(tmp_path / "auth-test.db"))
	monkeypatch.setenv("NARC_RECON_PEPPER", "fake-env-pepper")

	auth_service = importlib.import_module("services.auth_service")

	assert auth_service.PEPPER == "fake-env-pepper"


def test_hash_is_not_plaintext_and_has_reasonable_length(auth_env):
	_, _, auth_service, _ = auth_env
	pwd = "123"
	h = auth_service._hash_secret(pwd)

	assert isinstance(h, str)
	assert pwd not in h
	assert len(h) > 20


def test_same_password_hashes_differ_due_to_salt(auth_env):
	_, _, auth_service, _ = auth_env
	pwd = "123"

	h1 = auth_service._hash_secret(pwd)
	h2 = auth_service._hash_secret(pwd)

	assert h1 != h2


def test_verify_correct_password(auth_env):
	_, _, auth_service, _ = auth_env
	pwd = "correct-horse-battery-staple"
	h = auth_service._hash_secret(pwd)

	assert auth_service._verify_secret(h, pwd) is True


def test_empty_password(auth_env):
	_, _, auth_service, _ = auth_env
	h = auth_service._hash_secret("")

	assert auth_service._verify_secret(h, "") is True
	assert auth_service._verify_secret(h, " ") is False


def test_unicode_password(auth_env):
	_, _, auth_service, _ = auth_env
	pwd = "Pässwørd🔒"
	h = auth_service._hash_secret(pwd)

	assert auth_service._verify_secret(h, pwd) is True
	assert auth_service._verify_secret(h, "Pässwørd") is False


def test_blank_spaces(auth_env):
	_, _, auth_service, _ = auth_env
	h = auth_service._hash_secret("123")

	assert auth_service._verify_secret(h, "123") is True
	assert auth_service._verify_secret(h, "123 ") is False


def make_auth_connection(auth_schema):
	conn = sqlite3.connect(":memory:", isolation_level=None)
	auth_schema.migrate_auth(conn)
	auth_schema.migrate_users(conn)
	return conn


def test_create_initial_app_setup_creates_account_and_initial_pharmacist_user(auth_env):
	_, auth_schema, auth_service, _ = auth_env
	conn = make_auth_connection(auth_schema)

	auth_service.create_initial_app_setup(conn, " pharmacy ", "secret-password", " RPH1 ")

	account = conn.execute("SELECT username, password_hash FROM app_account").fetchone()
	user = conn.execute("SELECT user_id, role, created_at FROM users").fetchone()

	assert account[0] == "pharmacy"
	assert "secret-password" not in account[1]
	assert auth_service._verify_secret(account[1], "secret-password") is True
	assert user[0:2] == ("RPH1", "Pharmacist")
	assert user[2]


def test_create_initial_app_setup_rejects_blank_pharmacist_user_id(auth_env):
	_, auth_schema, auth_service, _ = auth_env
	conn = make_auth_connection(auth_schema)

	with pytest.raises(ValueError, match="Initial pharmacist user ID is required."):
		auth_service.create_initial_app_setup(conn, "pharmacy", "secret-password", " ")

	assert conn.execute("SELECT COUNT(*) FROM app_account").fetchone()[0] == 0
	assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0


def test_create_initial_app_setup_rolls_back_app_account_when_initial_user_insert_fails(auth_env):
	_, auth_schema, auth_service, _ = auth_env
	conn = make_auth_connection(auth_schema)
	conn.execute(
		"INSERT INTO users (user_id, role, created_at) VALUES (?, ?, ?)",
		("RPH1", "Pharmacist", "existing"),
	)

	with pytest.raises(sqlite3.IntegrityError):
		auth_service.create_initial_app_setup(conn, "pharmacy", "secret-password", "RPH1")

	assert conn.execute("SELECT COUNT(*) FROM app_account").fetchone()[0] == 0
	assert conn.execute("SELECT user_id, role, created_at FROM users").fetchall() == [
		("RPH1", "Pharmacist", "existing")
	]
