import importlib
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"


def test_get_db_path_defaults_to_src_database(monkeypatch, fresh_app_modules):
	monkeypatch.delenv("NARC_RECON_DB_PATH", raising=False)
	paths = importlib.import_module("paths")

	assert paths.get_db_path() == SRC / "narc_recon.db"


def test_get_db_path_uses_env_override(monkeypatch, tmp_path, fresh_app_modules):
	db_path = tmp_path / "override.db"
	monkeypatch.setenv("NARC_RECON_DB_PATH", str(db_path))
	paths = importlib.import_module("paths")

	assert paths.get_db_path() == db_path


def test_get_excel_path_uses_env_override(monkeypatch, tmp_path, fresh_app_modules):
	excel_path = tmp_path / "override.xlsx"
	monkeypatch.setenv("NARC_RECON_EXCEL_PATH", str(excel_path))
	paths = importlib.import_module("paths")

	assert paths.get_excel_path() == excel_path
