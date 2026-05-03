# Narc Recon PyInstaller Build Guide

This guide creates a repeatable desktop build for the current Narc Recon app without changing runtime behavior.

## Entry Point

Use:

```bash
src/narc_recon.pyw
```

The PyInstaller spec is:

```bash
build/narc_recon.spec
```

## Production Data Policy

Do not bundle a live production database.

The production SQLite database must live outside the app bundle and be configured with:

```bash
NARC_RECON_DB_PATH="/path/to/narc_recon.db"
```

The build must not include:

- `*.db`
- `*.db-wal`
- `*.db-shm`

SQLite WAL mode may create `-wal` and `-shm` files beside the database. Treat all three as runtime data, not application assets.

## Create A Virtual Environment

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Install dependencies:

```bash
python -m pip install -r src/requirements.txt
```

Packaging note: `login.py` imports `PIL.Image`. If Pillow is not already installed as a transitive dependency, install it explicitly:

```bash
python -m pip install Pillow
```

## Required Environment Variables For Smoke Testing

Set these before launching the packaged app:

```bash
export NARC_RECON_DB_PATH="/absolute/path/to/test-or-production/narc_recon.db"
export NARC_RECON_PEPPER="a-long-random-secret-kept-outside-git"
```

Optional, when the Excel file is external instead of the bundled default:

```bash
export NARC_RECON_EXCEL_PATH="/absolute/path/to/med_sheet.xlsx"
```

Do not enable development update behavior in production:

```bash
unset NARC_RECON_DEV_UPDATE
```

## Build Command

From the project root, with the virtual environment active:

```bash
pyinstaller --clean --noconfirm build/narc_recon.spec
```

Expected output:

```bash
dist/Narc Recon/
```

The executable will be inside that output folder. The exact file extension depends on the operating system.

On macOS, the spec also creates an app bundle when run on macOS:

```bash
dist/Narc Recon.app
```

On Windows, the expected executable is:

```bash
dist/Narc Recon/Narc Recon.exe
```

## Bundled Files

The spec bundles:

- `src/med_sheet.xlsx`
- `src/others/logo_nr.png`

The spec also uses these desktop icon files when they exist:

- `src/others/logo_nr.ico` for Windows `.exe` builds
- `src/others/logo_nr.icns` for macOS `.app` builds

At the moment, the project only includes `src/others/logo_nr.png`. Generate the platform icon files from that source image before release, then commit the generated `.ico` and/or `.icns` after visually approving them.

## Generate Desktop Icons

Create a Windows `.ico` from the PNG:

```bash
python - <<'PY'
from pathlib import Path
from PIL import Image

source = Path("src/others/logo_nr.png")
target = Path("src/others/logo_nr.ico")

image = Image.open(source).convert("RGBA")
image.save(
    target,
    sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
)
PY
```

Create a macOS `.icns` on macOS:

```bash
mkdir -p build/icon.iconset
sips -z 16 16 src/others/logo_nr.png --out build/icon.iconset/icon_16x16.png
sips -z 32 32 src/others/logo_nr.png --out build/icon.iconset/icon_16x16@2x.png
sips -z 32 32 src/others/logo_nr.png --out build/icon.iconset/icon_32x32.png
sips -z 64 64 src/others/logo_nr.png --out build/icon.iconset/icon_32x32@2x.png
sips -z 128 128 src/others/logo_nr.png --out build/icon.iconset/icon_128x128.png
sips -z 256 256 src/others/logo_nr.png --out build/icon.iconset/icon_128x128@2x.png
sips -z 256 256 src/others/logo_nr.png --out build/icon.iconset/icon_256x256.png
sips -z 512 512 src/others/logo_nr.png --out build/icon.iconset/icon_256x256@2x.png
sips -z 512 512 src/others/logo_nr.png --out build/icon.iconset/icon_512x512.png
sips -z 1024 1024 src/others/logo_nr.png --out build/icon.iconset/icon_512x512@2x.png
iconutil -c icns build/icon.iconset -o src/others/logo_nr.icns
rm -rf build/icon.iconset
```

If either icon file is missing, the packaged app still builds, but it uses the operating system or PyInstaller default icon for that platform.

## Packaging-Relevant Dependencies

Current `src/requirements.txt` includes:

- `pandas`
- `openpyxl`
- `prettytable`
- `pyinstaller`
- `reportlab`
- `pytz`
- `customtkinter`
- `argon2-cffi`

Also verify `Pillow` is installed for `PIL.Image`.

## Files That Must Not Be Committed

Do not commit:

- `dist/`
- PyInstaller generated work output, except the committed spec file
- temporary iconset folders like `build/icon.iconset/`
- `*.db`
- `*.db-wal`
- `*.db-shm`
- `.env`
- production secrets
- production backups
- generated pharmacy PDFs
- Excel lock files like `~$*.xlsx`

## Smoke Test The Packaged App

Use a test database path first.

1. Set `NARC_RECON_DB_PATH` to a test database location outside `dist/`.
2. Set `NARC_RECON_PEPPER`.
3. Launch the packaged app.
4. Create the first-run account if needed.
5. Log in.
6. Confirm the logo appears.
7. Confirm Inventory opens.
8. Search by DIN and UPC.
9. Receive a small quantity with a valid user ID.
10. Fill a smaller quantity with a valid user ID.
11. Reconcile with an authorized role.
12. Mark expired quantity.
13. Confirm audit rows are written with expected transaction types:
    - `receiving`
    - `filling`
    - `reconciliation`
    - `expired`
14. Confirm Settings access is blocked for non-pharmacist roles.
15. Export an inventory PDF and confirm it appears in Downloads.
16. Close and reopen the app.
17. Confirm catalog rows did not duplicate and quantities/audit rows persisted.
18. On macOS, drag `dist/Narc Recon.app` to Applications, launch it, and use Dock `Options > Keep in Dock` if the workstation needs a persistent launcher.
19. On Windows, copy the full `dist/Narc Recon/` folder to the install location, create a desktop shortcut to `Narc Recon.exe`, and pin the running app to the taskbar if needed.

## Deployment Notes

- Keep the production database external and backed up.
- Keep `NARC_RECON_PEPPER` stable after creating production login credentials.
- Keep `med_sheet.xlsx` closed while testing startup/import behavior.
- Test the packaged app on the target workstation account, not only on the development machine.
- Run `pytest` before building:

```bash
pytest
```
