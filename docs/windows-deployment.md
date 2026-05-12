# Narc Recon Windows Deployment

This guide describes the first Windows deployment model for Narc Recon. It is zip/folder based for now, not a full installer.

The app folder can be replaced during updates. The database, config file, and backups must stay outside the app folder.

## Locations

Recommended per-user app install location:

```text
%LOCALAPPDATA%\Programs\Narc Recon\
```

Expected executable:

```text
%LOCALAPPDATA%\Programs\Narc Recon\Narc Recon.exe
```

Recommended data folder:

```text
%USERPROFILE%\NarcReconData\
```

Default database path:

```text
%USERPROFILE%\NarcReconData\narc_recon.db
```

Config file path:

```text
%USERPROFILE%\NarcReconData\config.env
```

Backup folder:

```text
%USERPROFILE%\NarcReconBackups\
```

## Build On Windows

Build the Windows package on a Windows machine:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r src\requirements.txt
pip install pyinstaller
pyinstaller --clean --noconfirm build\narc_recon.spec
```

Expected build output:

```text
dist\Narc Recon\Narc Recon.exe
```

## Install Or Update Locally

From the repository root, run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_windows.ps1
```

The script:

- installs from `dist\Narc Recon\`
- verifies `dist\Narc Recon\Narc Recon.exe` exists
- creates `%LOCALAPPDATA%\Programs\Narc Recon\`
- creates `%USERPROFILE%\NarcReconData\`
- creates `%USERPROFILE%\NarcReconBackups\`
- closes or prompts to stop a running Narc Recon process before replacement
- copies the app to a temporary folder first
- replaces only `%LOCALAPPDATA%\Programs\Narc Recon\`
- creates or updates a Desktop shortcut named `Narc Recon.lnk`
- does not require administrator rights

To install/update and launch the app afterward:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_windows.ps1 -Open
```

## Config File

Create a stable local config file before creating real accounts:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\NarcReconData"
@"
NARC_RECON_DB_PATH=$env:USERPROFILE\NarcReconData\narc_recon.db
NARC_RECON_PEPPER=replace-with-a-long-random-secret
"@ | Set-Content "$env:USERPROFILE\NarcReconData\config.env"
```

Do not use the fake pepper above for real deployment. Choose one long random secret and preserve it. Changing `NARC_RECON_PEPPER` after account creation can break password verification.

Use `NARC_RECON_EXCEL_PATH` only if the initial catalog seed should come from an external Excel file instead of the bundled `med_sheet.xlsx`.

## Zip Package

After building, create a zip from the full output folder:

```powershell
Compress-Archive -Path "dist\Narc Recon\*" -DestinationPath "dist\Narc_Recon_windows.zip" -Force
```

The zip should contain app files only. It must not contain:

- real `narc_recon.db`
- `narc_recon.db-wal`
- `narc_recon.db-shm`
- real `config.env`
- backups
- real secrets

## GitHub Releases

GitHub Releases is a reasonable hosting option for controlled early Windows deployment.

Upload:

- `Narc_Recon_windows.zip`
- release notes
- optional SHA256 checksum

Do not upload database files, `config.env`, backups, or secrets.

## Update Procedure

1. Finish any active workflow in Narc Recon.
2. Close Narc Recon.
3. Run a verified backup:

   ```powershell
   python scripts\backup_db.py
   ```

4. Build or extract the new app version so `dist\Narc Recon\Narc Recon.exe` exists.
5. Run:

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\install_windows.ps1
   ```

6. Launch Narc Recon from the Desktop shortcut or Start menu pin.
7. Run the manual smoke tests below.

## Manual Smoke Tests

Run these on the target Windows workstation account:

- Fresh install opens.
- First-run setup creates app account and initial Pharmacist user.
- Login works after app restart.
- `config.env` is respected.
- Database is created under `%USERPROFILE%\NarcReconData`.
- Inventory search works by DIN and UPC.
- Receiving writes quantity and audit log row.
- Filling writes quantity and audit log row.
- Reconciliation set quantity works for an authorized role.
- Expired quantity workflow works.
- Settings access is denied for non-pharmacist roles.
- Reports export to the user's Downloads folder.
- Backup script creates a verified backup.
- Restore drill works using a copied database and `NARC_RECON_DB_PATH`.
- App update replaces app files without touching `%USERPROFILE%\NarcReconData`.

## What Must Never Be Overwritten

The install/update script must never delete or overwrite:

```text
%USERPROFILE%\NarcReconData\
%USERPROFILE%\NarcReconData\narc_recon.db
%USERPROFILE%\NarcReconData\narc_recon.db-wal
%USERPROFILE%\NarcReconData\narc_recon.db-shm
%USERPROFILE%\NarcReconData\config.env
%USERPROFILE%\NarcReconBackups\
```

## Full Installer

A full Windows installer should wait until the zip/folder deployment has been validated on the target workstation. The first Windows deployment should stay simple: PyInstaller output, zip package, per-user install script, external data folder, and manual smoke tests.
