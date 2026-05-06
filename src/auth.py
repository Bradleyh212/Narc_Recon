# auth.py	# tabs for indentation
from db import auth_schema
from db import connection
from services import auth_service

DB_PATH = connection.DB_PATH
PEPPER = auth_service.PEPPER
ph = auth_service.ph

def _now_iso():
	return auth_service._now_iso()

def _hash_secret(secret: str) -> str:
	return auth_service._hash_secret(secret)

def _verify_secret(hashv: str, secret: str) -> bool:
	return auth_service._verify_secret(hashv, secret)

def get_conn():
	return connection.get_conn()

def migrate_auth(conn):
	return auth_schema.migrate_auth(conn)

def migrate_users(conn):
	return auth_schema.migrate_users(conn)

def app_account_exists(conn) -> bool:
	return auth_service.app_account_exists(conn)

def seed_from_env_if_needed(conn):
	return auth_service.seed_from_env_if_needed(conn)

def authenticate_app(username: str, password: str) -> tuple[bool, str]:
	return auth_service.authenticate_app(username, password)

def _insert_app_account(conn, username: str, password: str):
	return auth_service._insert_app_account(conn, username, password)

def create_initial_app_setup(conn, username: str, password: str, pharmacist_user_id: str):
	return auth_service.create_initial_app_setup(conn, username, password, pharmacist_user_id)

def create_account_window(conn):
	from ui import first_run_setup

	return first_run_setup.create_account_window(conn)
