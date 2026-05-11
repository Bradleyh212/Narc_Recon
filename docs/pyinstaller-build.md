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

The production SQLite database must live outside the app bundle. If `NARC_RECON_DB_PATH` is not set, Narc Recon defaults to:

```bash
~/NarcReconData/narc_recon.db
```

Use `NARC_RECON_DB_PATH` only when a deployment needs an explicit database location:

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

## Environment Variables For Smoke Testing

When launching from Terminal, you can override the database path for smoke testing:

```bash
export NARC_RECON_DB_PATH="/absolute/path/to/test-or-production/narc_recon.db"
```

If no override is set, the packaged app uses `~/NarcReconData/narc_recon.db`. This matters for Finder and Dock launches because macOS apps opened that way do not inherit Terminal environment variables.

For stable Finder/Dock launches, create a local config file:

```bash
mkdir -p "$HOME/NarcReconData"
chmod 700 "$HOME/NarcReconData"
cat > "$HOME/NarcReconData/config.env" <<'EOF'
NARC_RECON_DB_PATH=/Users/example/NarcReconData/narc_recon.db
NARC_RECON_EXCEL_PATH=/Users/example/NarcReconData/med_sheet.xlsx
NARC_RECON_PEPPER=replace-with-a-long-random-secret
EOF
chmod 600 "$HOME/NarcReconData/config.env"
```

Config priority is:

1. Environment variables
2. `~/NarcReconData/config.env`
3. Safe defaults

Set the pepper before creating test or production login credentials:

```bash
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

## macOS Local Install/Update Script

For local macOS development and testing, finish any active Narc Recon workflow, then use:

```bash
scripts/install_mac.sh
```

The script builds with the existing PyInstaller spec:

```bash
pyinstaller --clean --noconfirm build/narc_recon.spec
```

Then it installs the built app to the standard macOS Applications folder:

```bash
/Applications/Narc Recon.app
```

First-time install behavior:

- creates `~/NarcReconData/` if it does not exist
- asks for administrator permission only for the `/Applications` install step
- copies `dist/Narc Recon.app` into `/Applications/Narc Recon.app`
- prints the recommended database and pepper environment variables
- prints the command to open the installed app

Update behavior:

- rebuilds the app first
- stops before changing the installed app if the build fails
- gracefully closes Narc Recon before replacing the app bundle
- uses `pkill` only as a fallback if a Narc Recon process is still running
- copies the new app bundle to a temporary path first
- replaces only `/Applications/Narc Recon.app`
- leaves `~/NarcReconData/` untouched
- does not delete or overwrite `*.db`, `*.db-wal`, or `*.db-shm` files

The script does not open the app by default. After install/update, open it manually:

```bash
open "/Applications/Narc Recon.app"
```

To explicitly open the app after installing, use:

```bash
scripts/install_mac.sh --open
```

The `--open` option uses `open -n` so macOS starts a new app instance instead of activating an existing one.

The database should live outside the app bundle so app updates do not replace pharmacy data:

```bash
export NARC_RECON_PEPPER="<set-a-real-secret>"
```

The default database path is already `~/NarcReconData/narc_recon.db`. Set `NARC_RECON_DB_PATH` only when intentionally using another database location.

The script does not modify the Dock. Add `/Applications/Narc Recon.app` to the Dock once; future script runs replace the app at the same path, so the Dock item continues pointing to the updated app.

To uninstall the app bundle:

```bash
sudo rm -rf "/Applications/Narc Recon.app"
```

Do not remove `~/NarcReconData/` unless you intentionally want to delete local database files and supporting data.

## Bundled Files

The spec bundles:

- `src/med_sheet.xlsx`
- `src/others/logo_nr.png`

The spec also uses these desktop icon files when they exist:

- `src/others/logo_nr.ico` for Windows `.exe` builds
- `src/others/logo_nr.icns` for macOS `.app` builds

At the moment, the project includes `src/others/logo_nr.png` and `src/others/logo_nr.icns`. Windows icon support still needs `src/others/logo_nr.ico` generated from the approved PNG before a Windows release.

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
- `Pillow`

## Files That Must Not Be Committed

Do not commit:

- `dist/`
- PyInstaller generated work output, except the committed spec file
- temporary iconset folders like `build/icon.iconset/`
- temporary macOS installer app bundles like `/Applications/.Narc Recon.app.tmp.*`
- temporary macOS installer backup app bundles like `/Applications/.Narc Recon.app.backup.*`
- `*.db`
- `*.db-wal`
- `*.db-shm`
- `.env`
- production secrets
- production backups
- generated pharmacy PDFs
- Excel lock files like `~$*.xlsx`
- `__pycache__/`
- `*.pyc`
- `.DS_Store`

## Smoke Test The Packaged App

Use a test database path first.

1. Confirm the app is using either the default database path `~/NarcReconData/narc_recon.db` or an explicit `NARC_RECON_DB_PATH` test location outside `dist/`.
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
- Keep `med_sheet.xlsx` closed while testing initial catalog seed or import behavior.
- Test the packaged app on the target workstation account, not only on the development machine.
- Run `pytest` before building:

```bash
pytest
```
