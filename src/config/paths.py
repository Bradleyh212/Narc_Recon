import sys
from pathlib import Path

from config import app_config


APP_DIR = Path(__file__).resolve().parents[1]

def _candidate_resource_dirs():
	candidates = []
	if getattr(sys, "frozen", False):
		meipass = getattr(sys, "_MEIPASS", None)
		if meipass:
			candidates.append(Path(meipass))

		executable = getattr(sys, "executable", None)
		if executable:
			exe_dir = Path(executable).resolve().parent
			candidates.extend([exe_dir / "_internal", exe_dir])

	candidates.append(APP_DIR)

	unique_candidates = []
	for candidate in candidates:
		if candidate not in unique_candidates:
			unique_candidates.append(candidate)
	return unique_candidates


def _resource_dir() -> Path:
	frozen = getattr(sys, "frozen", False)
	for candidate in _candidate_resource_dirs():
		if frozen and candidate == APP_DIR:
			continue
		if candidate.exists():
			return candidate
	return _candidate_resource_dirs()[0]


def get_resource_path(*parts: str) -> Path:
	relative_path = Path(*parts)
	candidates = _candidate_resource_dirs()
	for candidate in candidates:
		if getattr(sys, "frozen", False) and candidate == APP_DIR:
			continue
		resource_path = candidate / relative_path
		if resource_path.exists():
			return resource_path
	return candidates[0] / relative_path


RESOURCE_DIR = _resource_dir()

DEFAULT_DB_PATH = Path.home() / "NarcReconData" / "narc_recon.db"
DEFAULT_EXCEL_PATH = get_resource_path("med_sheet.xlsx")
LOGO_PATH = get_resource_path("others", "logo_nr.png")


def _config_path(name: str, default: Path) -> Path:
	value = app_config.get_config_value(name)
	if value:
		return Path(value).expanduser()
	return default


def get_db_path() -> Path:
	db_path = _config_path("NARC_RECON_DB_PATH", DEFAULT_DB_PATH)
	db_path.parent.mkdir(parents=True, exist_ok=True)
	return db_path


def get_excel_path() -> Path:
	return _config_path("NARC_RECON_EXCEL_PATH", DEFAULT_EXCEL_PATH)
