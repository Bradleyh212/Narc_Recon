import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
	sys.path.insert(0, str(SRC))


def unload_app_modules():
	sqlite_module = sys.modules.get("sqlite3_functions")
	if sqlite_module is not None:
		con = getattr(sqlite_module, "con", None)
		if con is not None:
			try:
				con.close()
			except Exception:
				pass

	for module_name in ("sqlite3_functions", "auth", "paths"):
		sys.modules.pop(module_name, None)


@pytest.fixture
def fresh_app_modules():
	unload_app_modules()
	yield
	unload_app_modules()
