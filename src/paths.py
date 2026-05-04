from pathlib import Path
import os
import sys


APP_DIR = Path(__file__).resolve().parent

def _resource_dir() -> Path:
	if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
		return Path(sys._MEIPASS)
	return APP_DIR


RESOURCE_DIR = _resource_dir()

DEFAULT_DB_PATH = Path.home() / "NarcReconData" / "narc_recon.db"
DEFAULT_EXCEL_PATH = RESOURCE_DIR / "med_sheet.xlsx"
LOGO_PATH = RESOURCE_DIR / "others" / "logo_nr.png"


def _env_path(name: str, default: Path) -> Path:
	value = os.environ.get(name)
	if value:
		return Path(value).expanduser()
	return default


def get_db_path() -> Path:
	db_path = _env_path("NARC_RECON_DB_PATH", DEFAULT_DB_PATH)
	db_path.parent.mkdir(parents=True, exist_ok=True)
	return db_path


def get_excel_path() -> Path:
	return _env_path("NARC_RECON_EXCEL_PATH", DEFAULT_EXCEL_PATH)
