from pathlib import Path
import os


SUPPORTED_CONFIG_KEYS = {"NARC_RECON_DB_PATH", "NARC_RECON_EXCEL_PATH", "NARC_RECON_PEPPER"}


def get_config_path() -> Path:
	return Path.home() / "NarcReconData" / "config.env"


def _strip_optional_quotes(value: str) -> str:
	if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
		return value[1:-1]
	return value


def read_local_config(config_path=None):
	config_path = Path(config_path) if config_path is not None else get_config_path()
	config = {}

	try:
		lines = config_path.read_text(encoding="utf-8").splitlines()
	except FileNotFoundError:
		return config

	for line in lines:
		line = line.strip()
		if not line or line.startswith("#"):
			continue
		if line.startswith("export "):
			line = line[len("export "):].strip()
		if "=" not in line:
			continue

		key, value = line.split("=", 1)
		key = key.strip()
		if key not in SUPPORTED_CONFIG_KEYS:
			continue
		config[key] = _strip_optional_quotes(value.strip())

	return config


def get_config_value(key, default=None):
	env_value = os.environ.get(key)
	if env_value:
		return env_value

	config_value = read_local_config().get(key)
	if config_value:
		return config_value

	return default


def local_config_exists() -> bool:
	return get_config_path().is_file()
