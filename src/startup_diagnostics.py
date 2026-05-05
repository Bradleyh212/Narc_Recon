from datetime import datetime, UTC
from pathlib import Path
import os
import sys

import app_config
from paths import get_db_path, get_excel_path


TABLES_TO_COUNT = ("app_account", "users", "narcs", "narcs_details", "audit_log")


def get_startup_log_path() -> Path:
	return Path.home() / "NarcReconData" / "narc_recon_startup.log"


def _fetch_table_names(connection):
	rows = connection.execute("""
		SELECT name
		FROM sqlite_master
		WHERE type = 'table'
		ORDER BY name
	""").fetchall()
	return [row[0] for row in rows]


def _fetch_row_counts(connection):
	table_names = set(_fetch_table_names(connection))
	counts = {}
	for table_name in TABLES_TO_COUNT:
		if table_name not in table_names:
			counts[table_name] = "missing"
			continue
		counts[table_name] = connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
	return table_names, counts


def write_startup_log(connection=None):
	try:
		log_path = get_startup_log_path()
		log_path.parent.mkdir(parents=True, exist_ok=True)

		lines = [
			"=== Narc Recon startup ===",
			f"timestamp_utc={datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}",
			f"pid={os.getpid()}",
			f"sys_frozen={bool(getattr(sys, 'frozen', False))}",
			f"sys_meipass={getattr(sys, '_MEIPASS', '')}",
			f"home={Path.home()}",
			f"db_path={get_db_path()}",
			f"excel_path={get_excel_path()}",
			f"config_path={app_config.get_config_path()}",
			f"config_env_exists={app_config.local_config_exists()}",
			f"narc_recon_db_path_set={bool(os.environ.get('NARC_RECON_DB_PATH'))}",
			f"narc_recon_excel_path_set={bool(os.environ.get('NARC_RECON_EXCEL_PATH'))}",
		]

		if connection is not None:
			try:
				table_names, counts = _fetch_row_counts(connection)
				lines.append("tables=" + ",".join(sorted(table_names)))
				for table_name in TABLES_TO_COUNT:
					lines.append(f"row_count.{table_name}={counts[table_name]}")
			except Exception as exc:
				lines.append(f"table_diagnostics_error={type(exc).__name__}: {exc}")

		with log_path.open("a", encoding="utf-8") as log_file:
			log_file.write("\n".join(lines))
			log_file.write("\n\n")
	except Exception:
		pass
