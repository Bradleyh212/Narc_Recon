# Narc Recon

Narc Recon is a Python desktop application for controlled-substance and narcotic inventory reconciliation in a pharmacy setting. It supports local pharmacy workflows for inventory lookup, receiving, filling, reconciliation, expired quantity handling, reporting, and staff/user management while tracking inventory changes in an audit log.

This project does not claim regulatory compliance by itself. It is intended for controlled local deployment after pharmacy-specific testing, backup validation, and operational review.

## Current Status

- Local desktop application built with Python and CustomTkinter.
- SQLite database stored outside the app bundle by default at `~/NarcReconData/narc_recon.db`.
- Normal startup uses SQLite after the initial catalog seed.
- macOS packaging/install workflow is supported.
- Windows packaging is planned for future deployment work.
- Intended for controlled, local pharmacy use after proper testing.

## Features

- Inventory search by DIN or UPC.
- Receiving workflow to increase inventory.
- Filling workflow to decrease inventory.
- Reconciliation workflow to set quantity.
- Expired quantity workflow.
- Audit log tracking for inventory changes.
- PDF report generation.
- User management and role checks.
- First-run setup with an initial `Pharmacist` user.
- Local config file support for stable Finder/Dock launches.

## Architecture Overview

```text
src/
  config/
  db/
  diagnostics/
  services/
  ui/
  narc_recon.pyw
```

- `src/config/`: local config and path resolution.
- `src/db/`: database connection, schema, auth schema, and catalog startup initialization.
- `src/diagnostics/`: startup diagnostic logging.
- `src/services/`: inventory, inventory transactions, users, audit log, auth, and Excel import services.
- `src/ui/`: CustomTkinter UI, including `AppRouter`, page classes, shared base pages, login, and first-run setup.
- `src/narc_recon.pyw`: desktop app entry point.

The main UI uses a single-root router in `src/ui/app_router.py`. Main pages are router-hosted:

- Inventory
- Receiving
- Filling
- Reconciliation
- Report
- Settings

Shared UI behavior lives in `BasePage` and `BaseNarcoticPage`.

## Local Data And Config

Narc Recon keeps app data outside the source tree and outside the packaged app bundle.

Default database path:

```text
~/NarcReconData/narc_recon.db
```

Local config path:

```text
~/NarcReconData/config.env
```

Startup diagnostic log:

```text
~/NarcReconData/narc_recon_startup.log
```

Do not store production database files in the repository.

Example `config.env` with fake values:

```bash
NARC_RECON_DB_PATH=/Users/example/NarcReconData/narc_recon.db
NARC_RECON_PEPPER=replace-with-a-long-random-secret
```

Optional external Excel catalog path:

```bash
NARC_RECON_EXCEL_PATH=/Users/example/NarcReconData/med_sheet.xlsx
```

Environment variables override values in `config.env`.

## Development Setup

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r src/requirements.txt
python3 -m pytest -q
```

Launching from source may vary by platform. On macOS/Linux, this is the usual source launch command:

```bash
python3 src/narc_recon.pyw
```

Use a test database path when developing against disposable data:

```bash
export NARC_RECON_DB_PATH="/tmp/narc_recon_test.db"
```

## macOS Build And Install

Use the local install/update script:

```bash
scripts/install_mac.sh
```

The script:

- builds with PyInstaller using `build/narc_recon.spec`
- installs to `/Applications/Narc Recon.app`
- keeps app data in `~/NarcReconData/`
- does not delete database files
- may request administrator permission for the `/Applications` install step

After install, open the app manually:

```bash
open "/Applications/Narc Recon.app"
```

To build and open immediately:

```bash
scripts/install_mac.sh --open
```

## Windows Build And Install

Windows deployment is currently zip/folder based, not a full installer. Build on Windows with PyInstaller, then install from the local build output:

```powershell
pyinstaller --clean --noconfirm build\narc_recon.spec
powershell -ExecutionPolicy Bypass -File scripts\install_windows.ps1
```

The Windows install script installs to:

```text
%LOCALAPPDATA%\Programs\Narc Recon\
```

It keeps data outside the app folder:

```text
%USERPROFILE%\NarcReconData\
```

See [docs/windows-deployment.md](docs/windows-deployment.md) for the full Windows build, install, update, and smoke-test checklist.

## Testing

Run automated tests:

```bash
python3 -m pytest -q
```

Manual smoke tests before release:

- first-run setup
- login
- inventory search by DIN and UPC
- receiving
- filling
- reconciliation
- expired quantity
- report export
- settings/user management
- app close/reopen with persisted quantities and audit rows

## Backup

Create a verified SQLite backup with:

```bash
python3 scripts/backup_db.py
```

By default, backups are written to:

```text
~/NarcReconBackups/
```

The script resolves the database path using the same config rules as the app, uses SQLite's backup API, runs `PRAGMA integrity_check`, and prints row counts for the required tables. It is backup-only; restore should be tested manually before pharmacy deployment.

Run the non-destructive restore drill in [docs/restore-drill.md](docs/restore-drill.md) before any real deployment or production restore. The drill uses `~/NarcReconRestoreTest/` and must not overwrite `~/NarcReconData/narc_recon.db`.

## Never Commit

Do not commit:

- `*.db`
- `*.db-wal`
- `*.db-shm`
- `__pycache__/`
- `*.pyc`
- `.DS_Store`
- `~$*.xlsx`
- real `config.env`
- real secrets
- generated pharmacy PDFs
- production backups

## Deployment Notes

- Use a stable `~/NarcReconData/config.env` for packaged app launches.
- Set and preserve `NARC_RECON_PEPPER` before creating real accounts.
- Back up SQLite with the app closed when practical, using `python3 scripts/backup_db.py`.
- Test restore before pharmacy deployment.
- Keep app data outside the app bundle.
- Do not overwrite or delete `~/NarcReconData/` during app updates.
- Run a full manual smoke test on the target workstation account.

## Roadmap

- Windows deployment validation and optional full installer.
- Optional admin Excel import tooling.
- Production deployment checklist.
