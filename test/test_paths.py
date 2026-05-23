import importlib
import sys
from pathlib import Path


def test_get_db_path_defaults_to_user_data_database(monkeypatch, tmp_path, fresh_app_modules):
	home_path = tmp_path / "home"
	monkeypatch.setenv("HOME", str(home_path))
	monkeypatch.delenv("NARC_RECON_DB_PATH", raising=False)
	paths = importlib.import_module("config.paths")

	db_path = paths.get_db_path()

	assert db_path == home_path / "NarcReconData" / "narc_recon.db"
	assert db_path.parent.is_dir()


def test_get_db_path_uses_env_override(monkeypatch, tmp_path, fresh_app_modules):
	home_path = tmp_path / "home"
	config_dir = home_path / "NarcReconData"
	config_dir.mkdir(parents=True)
	(config_dir / "config.env").write_text(
		"NARC_RECON_DB_PATH=/from/config.db\n",
		encoding="utf-8",
	)
	db_path = tmp_path / "nested" / "override.db"
	monkeypatch.setenv("HOME", str(home_path))
	monkeypatch.setenv("NARC_RECON_DB_PATH", str(db_path))
	paths = importlib.import_module("config.paths")

	assert paths.get_db_path() == db_path
	assert db_path.parent.is_dir()


def test_get_db_path_uses_local_config_when_env_missing(monkeypatch, tmp_path, fresh_app_modules):
	home_path = tmp_path / "home"
	configured_db_path = tmp_path / "configured" / "narc_recon.db"
	config_dir = home_path / "NarcReconData"
	config_dir.mkdir(parents=True)
	(config_dir / "config.env").write_text(
		f"NARC_RECON_DB_PATH={configured_db_path}\n",
		encoding="utf-8",
	)
	monkeypatch.setenv("HOME", str(home_path))
	monkeypatch.delenv("NARC_RECON_DB_PATH", raising=False)
	paths = importlib.import_module("config.paths")

	db_path = paths.get_db_path()

	assert db_path == configured_db_path
	assert db_path.parent.is_dir()


def test_get_excel_path_uses_env_override(monkeypatch, tmp_path, fresh_app_modules):
	home_path = tmp_path / "home"
	config_dir = home_path / "NarcReconData"
	config_dir.mkdir(parents=True)
	(config_dir / "config.env").write_text(
		"NARC_RECON_EXCEL_PATH=/from/config.xlsx\n",
		encoding="utf-8",
	)
	excel_path = tmp_path / "override.xlsx"
	monkeypatch.setenv("HOME", str(home_path))
	monkeypatch.setenv("NARC_RECON_EXCEL_PATH", str(excel_path))
	paths = importlib.import_module("config.paths")

	assert paths.get_excel_path() == excel_path


def test_get_excel_path_uses_local_config_when_env_missing(monkeypatch, tmp_path, fresh_app_modules):
	home_path = tmp_path / "home"
	excel_path = tmp_path / "configured.xlsx"
	config_dir = home_path / "NarcReconData"
	config_dir.mkdir(parents=True)
	(config_dir / "config.env").write_text(
		f"NARC_RECON_EXCEL_PATH={excel_path}\n",
		encoding="utf-8",
	)
	monkeypatch.setenv("HOME", str(home_path))
	monkeypatch.delenv("NARC_RECON_EXCEL_PATH", raising=False)
	paths = importlib.import_module("config.paths")

	assert paths.get_excel_path() == excel_path


def test_bundled_resource_paths_use_pyinstaller_resource_directory(monkeypatch, tmp_path, fresh_app_modules):
	monkeypatch.setenv("HOME", str(tmp_path / "home"))
	monkeypatch.delenv("NARC_RECON_EXCEL_PATH", raising=False)
	monkeypatch.setattr(sys, "frozen", True, raising=False)
	monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)

	paths = importlib.import_module("config.paths")

	assert paths.get_excel_path() == tmp_path / "med_sheet.xlsx"
	assert paths.LOGO_PATH == tmp_path / "others" / "logo_nr.png"


def test_bundled_resource_paths_fall_back_to_executable_internal_dir(monkeypatch, tmp_path, fresh_app_modules):
	home_path = tmp_path / "home"
	exe_dir = tmp_path / "dist" / "Narc Recon"
	internal_dir = exe_dir / "_internal"
	(internal_dir / "others").mkdir(parents=True)
	(internal_dir / "med_sheet.xlsx").write_text("", encoding="utf-8")
	(internal_dir / "others" / "logo_nr.png").write_text("", encoding="utf-8")
	empty_meipass = tmp_path / "empty_meipass"
	empty_meipass.mkdir()

	monkeypatch.setenv("HOME", str(home_path))
	monkeypatch.delenv("NARC_RECON_EXCEL_PATH", raising=False)
	monkeypatch.setattr(sys, "frozen", True, raising=False)
	monkeypatch.setattr(sys, "_MEIPASS", str(empty_meipass), raising=False)
	monkeypatch.setattr(sys, "executable", str(exe_dir / "Narc Recon.exe"))

	paths = importlib.import_module("config.paths")

	assert paths.get_excel_path() == internal_dir / "med_sheet.xlsx"
	assert paths.LOGO_PATH == internal_dir / "others" / "logo_nr.png"
