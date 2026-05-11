import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
	sys.path.insert(0, str(SRC))


def unload_app_modules():
	for module_name in (
		"db.auth_schema",
		"db.catalog_database_service",
		"db.connection",
		"db.schema_service",
		"db",
		"config.paths",
		"config.app_config",
		"config",
		"diagnostics.startup_diagnostics",
		"diagnostics",
		"services.auth_service",
	):
		sys.modules.pop(module_name, None)
	services_pkg = sys.modules.get("services")
	if services_pkg is not None and hasattr(services_pkg, "auth_service"):
		delattr(services_pkg, "auth_service")


@pytest.fixture
def fresh_app_modules():
	unload_app_modules()
	yield
	unload_app_modules()
