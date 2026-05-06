import importlib
import sqlite3

import pytest


def load_auth_service(monkeypatch, tmp_path, fresh_app_modules):
	db_path = tmp_path / "auth-service.db"
	monkeypatch.setenv("NARC_RECON_DB_PATH", str(db_path))
	return importlib.import_module("services.auth_service"), db_path


def make_auth_connection():
	connection = sqlite3.connect(":memory:", isolation_level=None)
	auth_schema = importlib.import_module("db.auth_schema")
	auth_schema.migrate_auth(connection)
	auth_schema.migrate_users(connection)
	return connection


def test_auth_service_uses_local_config_pepper_when_env_missing(monkeypatch, tmp_path, fresh_app_modules):
	home_path = tmp_path / "home"
	config_dir = home_path / "NarcReconData"
	config_dir.mkdir(parents=True)
	(config_dir / "config.env").write_text(
		"NARC_RECON_PEPPER=fake-config-pepper\n",
		encoding="utf-8",
	)
	monkeypatch.setenv("HOME", str(home_path))
	monkeypatch.setenv("NARC_RECON_DB_PATH", str(tmp_path / "auth-service.db"))
	monkeypatch.delenv("NARC_RECON_PEPPER", raising=False)

	auth_service = importlib.import_module("services.auth_service")

	assert auth_service.PEPPER == "fake-config-pepper"


def test_auth_service_env_pepper_overrides_local_config(monkeypatch, tmp_path, fresh_app_modules):
	home_path = tmp_path / "home"
	config_dir = home_path / "NarcReconData"
	config_dir.mkdir(parents=True)
	(config_dir / "config.env").write_text(
		"NARC_RECON_PEPPER=fake-config-pepper\n",
		encoding="utf-8",
	)
	monkeypatch.setenv("HOME", str(home_path))
	monkeypatch.setenv("NARC_RECON_DB_PATH", str(tmp_path / "auth-service.db"))
	monkeypatch.setenv("NARC_RECON_PEPPER", "fake-env-pepper")

	auth_service = importlib.import_module("services.auth_service")

	assert auth_service.PEPPER == "fake-env-pepper"


def test_hash_and_verify_work(monkeypatch, tmp_path, fresh_app_modules):
	auth_service, _ = load_auth_service(monkeypatch, tmp_path, fresh_app_modules)

	hashv = auth_service._hash_secret("correct-password")

	assert "correct-password" not in hashv
	assert auth_service._verify_secret(hashv, "correct-password") is True
	assert auth_service._verify_secret(hashv, "wrong-password") is False


def test_app_account_exists(monkeypatch, tmp_path, fresh_app_modules):
	auth_service, _ = load_auth_service(monkeypatch, tmp_path, fresh_app_modules)
	connection = make_auth_connection()

	assert auth_service.app_account_exists(connection) is False

	auth_service._insert_app_account(connection, " pharmacy ", "secret-password")

	assert auth_service.app_account_exists(connection) is True


def test_seed_from_env_if_needed_creates_account_once(monkeypatch, tmp_path, fresh_app_modules):
	auth_service, _ = load_auth_service(monkeypatch, tmp_path, fresh_app_modules)
	monkeypatch.setenv("NARC_RECON_APP_USER", " pharmacy ")
	monkeypatch.setenv("NARC_RECON_APP_PASSWORD", "secret-password")
	connection = make_auth_connection()

	auth_service.seed_from_env_if_needed(connection)
	auth_service.seed_from_env_if_needed(connection)

	rows = connection.execute("SELECT username, password_hash FROM app_account").fetchall()
	assert len(rows) == 1
	assert rows[0][0] == "pharmacy"
	assert auth_service._verify_secret(rows[0][1], "secret-password") is True


def test_authenticate_app_succeeds_and_updates_last_login(monkeypatch, tmp_path, fresh_app_modules):
	auth_service, db_path = load_auth_service(monkeypatch, tmp_path, fresh_app_modules)
	connection_module = importlib.import_module("db.connection")
	auth_schema = importlib.import_module("db.auth_schema")

	connection = connection_module.get_conn()
	try:
		auth_schema.migrate_auth(connection)
		auth_service._insert_app_account(connection, "pharmacy", "secret-password")
	finally:
		connection.close()

	ok, message = auth_service.authenticate_app("pharmacy", "secret-password")

	assert (ok, message) == (True, "OK")
	connection = sqlite3.connect(db_path)
	try:
		last_login_utc = connection.execute("SELECT last_login_utc FROM app_account").fetchone()[0]
	finally:
		connection.close()
	assert last_login_utc


def test_authenticate_app_fails_for_missing_user(monkeypatch, tmp_path, fresh_app_modules):
	auth_service, _ = load_auth_service(monkeypatch, tmp_path, fresh_app_modules)
	connection_module = importlib.import_module("db.connection")
	auth_schema = importlib.import_module("db.auth_schema")

	connection = connection_module.get_conn()
	try:
		auth_schema.migrate_auth(connection)
	finally:
		connection.close()

	assert auth_service.authenticate_app("missing", "secret-password") == (
		False,
		"Invalid username or password.",
	)


def test_create_initial_app_setup_creates_account_and_initial_pharmacist_user(
	monkeypatch,
	tmp_path,
	fresh_app_modules,
):
	auth_service, _ = load_auth_service(monkeypatch, tmp_path, fresh_app_modules)
	connection = make_auth_connection()

	auth_service.create_initial_app_setup(connection, " pharmacy ", "secret-password", " RPH1 ")

	account = connection.execute("SELECT username, password_hash FROM app_account").fetchone()
	user = connection.execute("SELECT user_id, role, created_at FROM users").fetchone()
	assert account[0] == "pharmacy"
	assert auth_service._verify_secret(account[1], "secret-password") is True
	assert user[0:2] == ("RPH1", "Pharmacist")
	assert user[2]


def test_create_initial_app_setup_rolls_back_on_duplicate_initial_user(
	monkeypatch,
	tmp_path,
	fresh_app_modules,
):
	auth_service, _ = load_auth_service(monkeypatch, tmp_path, fresh_app_modules)
	connection = make_auth_connection()
	connection.execute(
		"INSERT INTO users (user_id, role, created_at) VALUES (?, ?, ?)",
		("RPH1", "Pharmacist", "existing"),
	)

	with pytest.raises(sqlite3.IntegrityError):
		auth_service.create_initial_app_setup(connection, "pharmacy", "secret-password", "RPH1")

	assert connection.execute("SELECT COUNT(*) FROM app_account").fetchone()[0] == 0
	assert connection.execute("SELECT user_id, role, created_at FROM users").fetchall() == [
		("RPH1", "Pharmacist", "existing")
	]
