#!/usr/bin/env python3
"""Create and verify a non-destructive SQLite backup for Narc Recon."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


REQUIRED_TABLES = ("app_account", "users", "narcs", "narcs_details", "audit_log")


class BackupError(Exception):
	pass


def add_src_to_path() -> None:
	root_dir = Path(__file__).resolve().parents[1]
	src_dir = root_dir / "src"
	if str(src_dir) not in sys.path:
		sys.path.insert(0, str(src_dir))


def resolve_db_path(cli_db_path: str | None) -> Path:
	if cli_db_path:
		return Path(cli_db_path).expanduser().resolve()

	add_src_to_path()
	from config.paths import get_db_path

	return get_db_path().expanduser().resolve()


def default_output_dir() -> Path:
	return Path.home() / "NarcReconBackups"


def unique_backup_path(output_dir: Path) -> Path:
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	base_path = output_dir / f"narc_recon_backup_{timestamp}.db"
	if not base_path.exists():
		return base_path

	for suffix in range(1, 1000):
		candidate = output_dir / f"narc_recon_backup_{timestamp}_{suffix}.db"
		if not candidate.exists():
			return candidate

	raise BackupError("Could not find a unique backup filename.")


def create_backup(source_db_path: Path, backup_path: Path) -> None:
	if not source_db_path.is_file():
		raise BackupError(f"Source database does not exist: {source_db_path}")
	if backup_path.exists():
		raise BackupError(f"Refusing to overwrite existing backup: {backup_path}")

	source_uri = f"file:{source_db_path}?mode=ro"
	source = sqlite3.connect(source_uri, uri=True, timeout=10)
	destination = sqlite3.connect(backup_path)
	try:
		source.backup(destination)
	finally:
		destination.close()
		source.close()


def table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
	row = connection.execute(
		"SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
		(table_name,),
	).fetchone()
	return row is not None


def verify_backup(backup_path: Path) -> tuple[str, dict[str, int]]:
	connection = sqlite3.connect(backup_path)
	try:
		integrity_rows = [row[0] for row in connection.execute("PRAGMA integrity_check").fetchall()]
		integrity_result = "ok" if integrity_rows == ["ok"] else "; ".join(integrity_rows)
		if integrity_result != "ok":
			raise BackupError(f"Backup integrity check failed: {integrity_result}")

		missing_tables = [table for table in REQUIRED_TABLES if not table_exists(connection, table)]
		if missing_tables:
			raise BackupError(f"Backup is missing required table(s): {', '.join(missing_tables)}")

		row_counts = {}
		for table in REQUIRED_TABLES:
			row_counts[table] = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
		return integrity_result, row_counts
	finally:
		connection.close()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Create and verify a non-destructive backup of the Narc Recon SQLite database.",
	)
	parser.add_argument(
		"--output-dir",
		default=None,
		help="Directory for the backup file. Defaults to ~/NarcReconBackups/.",
	)
	parser.add_argument(
		"--db-path",
		default=None,
		help="Specific database path to back up. Defaults to the app's configured database path.",
	)
	parser.add_argument(
		"--quiet",
		action="store_true",
		help="Reduce output while still printing the backup path and integrity result.",
	)
	return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
	args = parse_args(argv)

	try:
		db_path = resolve_db_path(args.db_path)
		output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else default_output_dir()
		output_dir.mkdir(parents=True, exist_ok=True)
		backup_path = unique_backup_path(output_dir)

		if not args.quiet:
			print("Narc Recon SQLite backup")
			print("Tip: close Narc Recon before backup for the simplest operational procedure.")
			print(f"Source database: {db_path}")
			print(f"Backup directory: {output_dir}")

		create_backup(db_path, backup_path)
		integrity_result, row_counts = verify_backup(backup_path)

		print(f"Backup created: {backup_path}")
		print(f"Integrity check: {integrity_result}")

		print("Row counts:")
		for table, count in row_counts.items():
			print(f"  {table}: {count}")

		return 0
	except (BackupError, OSError, sqlite3.Error) as exc:
		print(f"Error: {exc}", file=sys.stderr)
		return 1


if __name__ == "__main__":
	raise SystemExit(main())
