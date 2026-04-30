import importlib.machinery
import importlib.util
from pathlib import Path


def load_startup_module(monkeypatch):
	monkeypatch.delenv("NARC_RECON_DEV_UPDATE", raising=False)
	module_path = Path(__file__).resolve().parents[1] / "src" / "narc_recon.pyw"
	loader = importlib.machinery.SourceFileLoader("narc_recon_startup_test", str(module_path))
	spec = importlib.util.spec_from_loader(loader.name, loader)
	module = importlib.util.module_from_spec(spec)
	loader.exec_module(module)
	return module


def test_should_run_dev_update_defaults_to_false(monkeypatch):
	module = load_startup_module(monkeypatch)

	assert module.should_run_dev_update() is False


def test_should_run_dev_update_requires_explicit_flag(monkeypatch):
	module = load_startup_module(monkeypatch)

	monkeypatch.setenv("NARC_RECON_DEV_UPDATE", "1")
	assert module.should_run_dev_update() is True

	monkeypatch.setenv("NARC_RECON_DEV_UPDATE", "true")
	assert module.should_run_dev_update() is False
