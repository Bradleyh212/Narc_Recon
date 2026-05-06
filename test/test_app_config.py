import importlib


def import_app_config():
	return importlib.import_module("config.app_config")


def test_read_local_config_parses_supported_key_value_lines(tmp_path):
	app_config = import_app_config()
	config_path = tmp_path / "config.env"
	config_path.write_text("""
		# local Narc Recon config
		NARC_RECON_DB_PATH=~/NarcReconData/custom.db
		NARC_RECON_EXCEL_PATH="/tmp/med sheet.xlsx"
		export NARC_RECON_PEPPER='fake-local-secret'
		IGNORED_KEY=value
		malformed line
	""", encoding="utf-8")

	assert app_config.read_local_config(config_path) == {
		"NARC_RECON_DB_PATH": "~/NarcReconData/custom.db",
		"NARC_RECON_EXCEL_PATH": "/tmp/med sheet.xlsx",
		"NARC_RECON_PEPPER": "fake-local-secret",
	}


def test_get_config_value_uses_environment_before_config_file(monkeypatch, tmp_path):
	home_path = tmp_path / "home"
	config_dir = home_path / "NarcReconData"
	config_dir.mkdir(parents=True)
	(config_dir / "config.env").write_text(
		"NARC_RECON_DB_PATH=/from/config.db\n",
		encoding="utf-8",
	)
	monkeypatch.setenv("HOME", str(home_path))
	monkeypatch.setenv("NARC_RECON_DB_PATH", "/from/env.db")
	app_config = import_app_config()

	assert app_config.get_config_value("NARC_RECON_DB_PATH") == "/from/env.db"


def test_get_config_value_uses_config_file_before_default(monkeypatch, tmp_path):
	home_path = tmp_path / "home"
	config_dir = home_path / "NarcReconData"
	config_dir.mkdir(parents=True)
	(config_dir / "config.env").write_text(
		"NARC_RECON_EXCEL_PATH=/from/config.xlsx\n",
		encoding="utf-8",
	)
	monkeypatch.setenv("HOME", str(home_path))
	monkeypatch.delenv("NARC_RECON_EXCEL_PATH", raising=False)
	app_config = import_app_config()

	assert app_config.get_config_value("NARC_RECON_EXCEL_PATH", "/default.xlsx") == "/from/config.xlsx"


def test_get_config_value_uses_default_when_env_and_config_are_missing(monkeypatch, tmp_path):
	monkeypatch.setenv("HOME", str(tmp_path / "home"))
	monkeypatch.delenv("NARC_RECON_DB_PATH", raising=False)
	app_config = import_app_config()

	assert app_config.get_config_value("NARC_RECON_DB_PATH", "/default.db") == "/default.db"
