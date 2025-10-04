#!/usr/bin/env python3
import subprocess, sys # To update the app at lunch if possible

def update_code():
	try:
		subprocess.run(["git", "pull", "origin", "main"], check=True)
		print("Code updated.")
	except subprocess.CalledProcessError as e:
		print(f"Git pull failed: {e}")

def install_requirements():
	try:
		print("Installing requirements...")
		subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
		print("All requirements installed.")
	except subprocess.CalledProcessError as e:
		print(f"Error installing requirements: {e}")
		sys.exit(1)

update_code()
install_requirements()

from auth import get_conn, migrate_auth, migrate_users, seed_from_env_if_needed, app_account_exists, create_account_window
import login

if __name__ == "__main__":
	# DB connection + migrations
	conn = get_conn()
	migrate_auth(conn)
	migrate_users(conn)

	# If no account exists
	if not app_account_exists(conn):
		# Try env var seeding
		seed_from_env_if_needed(conn)
		# If still no account, show Create Account window
		if not app_account_exists(conn):
			create_account_window(conn)

	conn.close()

	# Launch login screen
	login.main()
