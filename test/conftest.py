import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
	sys.path.insert(0, str(SRC))


def unload_app_modules():
	for module_name in (
		"auth",
		"config.paths",
		"config.app_config",
		"config",
		"diagnostics.startup_diagnostics",
		"diagnostics",
	):
		sys.modules.pop(module_name, None)


@pytest.fixture
def fresh_app_modules():
	unload_app_modules()
	yield
	unload_app_modules()
