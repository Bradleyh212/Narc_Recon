import importlib
from pathlib import Path


import pytest


@pytest.fixture
def auth_env(monkeypatch, tmp_path, fresh_app_modules):
	db_path = tmp_path / "auth-test.db"
	monkeypatch.setenv("NARC_RECON_DB_PATH", str(db_path))
	authmod = importlib.import_module("auth")
	yield authmod, db_path


def test_get_conn_uses_temp_database(auth_env):
	authmod, db_path = auth_env

	conn = authmod.get_conn()
	try:
		database_path = conn.execute("PRAGMA database_list").fetchone()[2]
	finally:
		conn.close()

	assert Path(database_path) == db_path


def test_hash_is_not_plaintext_and_has_reasonable_length(auth_env):
	authmod, _ = auth_env
	pwd = "123"
	h = authmod._hash_secret(pwd)

	assert isinstance(h, str)
	assert pwd not in h
	assert len(h) > 20


def test_same_password_hashes_differ_due_to_salt(auth_env):
	authmod, _ = auth_env
	pwd = "123"

	h1 = authmod._hash_secret(pwd)
	h2 = authmod._hash_secret(pwd)

	assert h1 != h2


def test_verify_correct_password(auth_env):
	authmod, _ = auth_env
	pwd = "correct-horse-battery-staple"
	h = authmod._hash_secret(pwd)

	assert authmod._verify_secret(h, pwd) is True


def test_empty_password(auth_env):
	authmod, _ = auth_env
	h = authmod._hash_secret("")

	assert authmod._verify_secret(h, "") is True
	assert authmod._verify_secret(h, " ") is False


def test_unicode_password(auth_env):
	authmod, _ = auth_env
	pwd = "Pässwørd🔒"
	h = authmod._hash_secret(pwd)

	assert authmod._verify_secret(h, pwd) is True
	assert authmod._verify_secret(h, "Pässwørd") is False


def test_blank_spaces(auth_env):
	authmod, _ = auth_env
	h = authmod._hash_secret("123")

	assert authmod._verify_secret(h, "123") is True
	assert authmod._verify_secret(h, "123 ") is False
