import importlib
import sqlite3
import sys


def make_diagnostic_connection():
	connection = sqlite3.connect(":memory:")
	connection.execute("CREATE TABLE app_account (id INTEGER PRIMARY KEY, username TEXT)")
	connection.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, user_id TEXT)")
	connection.execute("CREATE TABLE narcs (din TEXT PRIMARY KEY)")
	connection.execute("CREATE TABLE narcs_details (din TEXT, upc TEXT)")
	connection.execute("CREATE TABLE audit_log (log_id INTEGER PRIMARY KEY)")
	connection.execute("INSERT INTO app_account (id, username) VALUES (1, 'pharmacy')")
	connection.execute("INSERT INTO users (id, user_id) VALUES (1, 'RPH1')")
	connection.execute("INSERT INTO narcs (din) VALUES ('02248809')")
	connection.execute("INSERT INTO narcs_details (din, upc) VALUES ('02248809', '663220111026')")
	return connection


def import_startup_diagnostics():
	sys.modules.pop("startup_diagnostics", None)
	return importlib.import_module("startup_diagnostics")


def test_write_startup_log_records_paths_and_table_counts(monkeypatch, tmp_path, fresh_app_modules):
	home_path = tmp_path / "home"
	db_path = tmp_path / "db" / "narc_recon.db"
	excel_path = tmp_path / "med_sheet.xlsx"
	monkeypatch.setenv("HOME", str(home_path))
	monkeypatch.setenv("NARC_RECON_DB_PATH", str(db_path))
	monkeypatch.setenv("NARC_RECON_EXCEL_PATH", str(excel_path))
	config_dir = home_path / "NarcReconData"
	config_dir.mkdir(parents=True)
	(config_dir / "config.env").write_text(
		"NARC_RECON_PEPPER=fake-config-pepper\n",
		encoding="utf-8",
	)
	startup_diagnostics = import_startup_diagnostics()

	startup_diagnostics.write_startup_log(make_diagnostic_connection())

	log_path = home_path / "NarcReconData" / "narc_recon_startup.log"
	log_text = log_path.read_text(encoding="utf-8")

	assert "=== Narc Recon startup ===" in log_text
	assert "timestamp_utc=" in log_text
	assert "pid=" in log_text
	assert "sys_frozen=False" in log_text
	assert f"home={home_path}" in log_text
	assert f"db_path={db_path}" in log_text
	assert f"excel_path={excel_path}" in log_text
	assert f"config_path={config_dir / 'config.env'}" in log_text
	assert "config_env_exists=True" in log_text
	assert "narc_recon_db_path_set=True" in log_text
	assert "narc_recon_excel_path_set=True" in log_text
	assert "row_count.app_account=1" in log_text
	assert "row_count.users=1" in log_text
	assert "row_count.narcs=1" in log_text
	assert "row_count.narcs_details=1" in log_text
	assert "row_count.audit_log=0" in log_text
	assert "NARC_RECON_PEPPER" not in log_text
	assert "fake-config-pepper" not in log_text


def test_write_startup_log_does_not_raise_when_logging_fails(monkeypatch, tmp_path, fresh_app_modules):
	startup_diagnostics = import_startup_diagnostics()
	blocking_directory = tmp_path / "not-a-file"
	blocking_directory.mkdir()
	monkeypatch.setattr(startup_diagnostics, "get_startup_log_path", lambda: blocking_directory)

	startup_diagnostics.write_startup_log(make_diagnostic_connection())
