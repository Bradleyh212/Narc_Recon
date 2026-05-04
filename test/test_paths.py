import importlib
import sys
from pathlib import Path


def test_get_db_path_defaults_to_user_data_database(monkeypatch, tmp_path, fresh_app_modules):
	home_path = tmp_path / "home"
	monkeypatch.setenv("HOME", str(home_path))
	monkeypatch.delenv("NARC_RECON_DB_PATH", raising=False)
	paths = importlib.import_module("paths")

	db_path = paths.get_db_path()

	assert db_path == home_path / "NarcReconData" / "narc_recon.db"
	assert db_path.parent.is_dir()


def test_get_db_path_uses_env_override(monkeypatch, tmp_path, fresh_app_modules):
	db_path = tmp_path / "nested" / "override.db"
	monkeypatch.setenv("NARC_RECON_DB_PATH", str(db_path))
	paths = importlib.import_module("paths")

	assert paths.get_db_path() == db_path
	assert db_path.parent.is_dir()


def test_get_excel_path_uses_env_override(monkeypatch, tmp_path, fresh_app_modules):
	excel_path = tmp_path / "override.xlsx"
	monkeypatch.setenv("NARC_RECON_EXCEL_PATH", str(excel_path))
	paths = importlib.import_module("paths")

	assert paths.get_excel_path() == excel_path


def test_bundled_resource_paths_use_pyinstaller_resource_directory(monkeypatch, tmp_path, fresh_app_modules):
	monkeypatch.delenv("NARC_RECON_EXCEL_PATH", raising=False)
	monkeypatch.setattr(sys, "frozen", True, raising=False)
	monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)

	paths = importlib.import_module("paths")

	assert paths.get_excel_path() == tmp_path / "med_sheet.xlsx"
	assert paths.LOGO_PATH == tmp_path / "others" / "logo_nr.png"
