# auth.py	# tabs for indentation
import os, sqlite3
from datetime import datetime, timezone
from argon2 import PasswordHasher
import customtkinter as ctk
from tkinter import messagebox
import app_config
from paths import get_db_path

DB_PATH = get_db_path()
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

def get_conn():
	conn = sqlite3.connect(DB_PATH, timeout=10, isolation_level=None)
	conn.execute("PRAGMA foreign_keys = ON;")
	conn.execute("PRAGMA journal_mode = WAL;")
	return conn

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
	conn = get_conn()
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

def create_account_window(conn):
	# GUI for first-run account creation
	class SetupWindow(ctk.CTk):
		def __init__(self):
			super().__init__()
			self.title("Narc Recon • First-Run Setup")
			self.resizable(False, False)

			ctk.set_appearance_mode("dark")
			ctk.set_default_color_theme("dark-blue")

			w, h = 420, 350
			sel_width = self.winfo_screenwidth()
			self_height = self.winfo_screenheight()
			x = (sel_width / 2) - (w / 2)
			y = (self_height / 2) - (h / 2)
			self.geometry(f'{w}x{h}+{int(x)}+{int(y)}')

			ctk.CTkLabel(self, text="Create Pharmacy Account", font=("Arial", 18, "bold")).pack(pady=10)

			self.username = ctk.CTkEntry(self, width=100, height=35, placeholder_text="Username (e.g., pharmacy)", corner_radius=20)
			self.username.pack(padx=20, pady=(10, 6), fill="x")

			self.pharmacist_user_id = ctk.CTkEntry(self, width=100, height=35, placeholder_text="Initial pharmacist user ID", corner_radius=20)
			self.pharmacist_user_id.pack(padx=20, pady=6, fill="x")

			self.pw = ctk.CTkEntry(self, width=100, height=35, placeholder_text="Password", show="*", corner_radius=20)
			self.pw.pack(padx=20, pady=6, fill="x")

			self.pw2 = ctk.CTkEntry(self, width=100, height=35, placeholder_text="Confirm password", show="*", corner_radius=20)
			self.pw2.pack(padx=20, pady=6, fill="x")

			self.show_var = ctk.BooleanVar(value=False)
			self.show_btn = ctk.CTkCheckBox(self, text="Show password", variable=self.show_var, command=self._toggle_show, corner_radius=20)
			self.show_btn.pack(padx=20, pady=4, anchor="w")

			self.create_btn = ctk.CTkButton(self, text="Create Account", command=self._create, corner_radius=20)
			self.create_btn.pack(pady=14)

		def _toggle_show(self):
			ch = "" if self.show_var.get() else "*"
			self.pw.configure(show=ch)
			self.pw2.configure(show=ch)

		def _create(self):
			u = self.username.get().strip()
			pharmacist_user_id = self.pharmacist_user_id.get().strip()
			p1 = self.pw.get()
			p2 = self.pw2.get()
			if not u or not p1:
				messagebox.showerror("Error", "Username and password are required.")
				return
			if not pharmacist_user_id:
				messagebox.showerror("Error", "Initial pharmacist user ID is required.")
				return
			if p1 != p2:
				messagebox.showerror("Error", "Passwords do not match.")
				return
			try:
				create_initial_app_setup(conn, u, p1, pharmacist_user_id)
				messagebox.showinfo("Success", "Pharmacy account and initial pharmacist user created. Please log in.")
				self.destroy()
			except ValueError as e:
				messagebox.showerror("Error", str(e))
			except sqlite3.IntegrityError as e:
				messagebox.showerror("Error", f"Failed to create account: {e}")

	app = SetupWindow()
	app.mainloop()
