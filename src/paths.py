from pathlib import Path
import os


APP_DIR = Path(__file__).resolve().parent

DEFAULT_DB_PATH = APP_DIR / "narc_recon.db"
DEFAULT_EXCEL_PATH = APP_DIR / "med_sheet.xlsx"
LOGO_PATH = APP_DIR / "others" / "logo_nr.png"


def _env_path(name: str, default: Path) -> Path:
	value = os.environ.get(name)
	if value:
		return Path(value).expanduser()
	return default


def get_db_path() -> Path:
	return _env_path("NARC_RECON_DB_PATH", DEFAULT_DB_PATH)


def get_excel_path() -> Path:
	return _env_path("NARC_RECON_EXCEL_PATH", DEFAULT_EXCEL_PATH)
