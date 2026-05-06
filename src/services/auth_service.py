import os
from datetime import datetime, timezone

from argon2 import PasswordHasher

from config import app_config
from db import connection


PEPPER = app_config.get_config_value("NARC_RECON_PEPPER", "dev-pepper-change-me")
ph = PasswordHasher()


def _now_iso():
	return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _hash_secret(secret: str) -> str:
	return ph.hash(secret + PEPPER)


def _verify_secret(hashv: str, secret: str) -> bool:
	try:
		return ph.verify(hashv, secret + PEPPER)
	except Exception:
		return False


def app_account_exists(conn) -> bool:
	row = conn.execute("SELECT COUNT(*) FROM app_account").fetchone()
	return bool(row and row[0] > 0)


def seed_from_env_if_needed(conn):
	# safe, one-time seeding WITHOUT hard-coding creds
	if app_account_exists(conn):
		return
	u = os.environ.get("NARC_RECON_APP_USER")
	p = os.environ.get("NARC_RECON_APP_PASSWORD")
	if u and p:
		with conn:
			conn.execute(
				"INSERT INTO app_account(id, username, password_hash) VALUES (1, ?, ?)",
				(u.strip(), _hash_secret(p))
			)


def authenticate_app(username: str, password: str) -> tuple[bool, str]:
	conn = connection.get_conn()
	row = conn.execute("SELECT id, password_hash FROM app_account WHERE username=?", (username,)).fetchone()
	if not row:
		return False, "Invalid username or password."
	ok = _verify_secret(row[1], password)
	if ok:
		conn.execute("UPDATE app_account SET last_login_utc=? WHERE id=1", (_now_iso(),))
		return True, "OK"
	return False, "Invalid username or password."


def _insert_app_account(conn, username: str, password: str):
	# inserts the single pharmacy account (id must be 1)
	with conn:
		conn.execute(
			"INSERT INTO app_account (id, username, password_hash) VALUES (1, ?, ?)",
			(username.strip(), _hash_secret(password))
		)


def create_initial_app_setup(conn, username: str, password: str, pharmacist_user_id: str):
	username = username.strip()
	pharmacist_user_id = pharmacist_user_id.strip()

	if not username or not password:
		raise ValueError("Username and password are required.")
	if not pharmacist_user_id:
		raise ValueError("Initial pharmacist user ID is required.")

	try:
		conn.execute("BEGIN")
		conn.execute(
			"INSERT INTO app_account (id, username, password_hash) VALUES (1, ?, ?)",
			(username, _hash_secret(password))
		)
		conn.execute(
			"INSERT INTO users (user_id, role, created_at) VALUES (?, ?, ?)",
			(pharmacist_user_id, "Pharmacist", _now_iso())
		)
		conn.commit()
	except Exception:
		conn.rollback()
		raise
