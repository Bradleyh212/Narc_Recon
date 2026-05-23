# Narc Recon Windows Deployment

This is the supported Windows release flow for the current zip/folder deployment model.

The pharmacy user should be able to download `Narc_Recon_windows_release.zip`, extract it, run `install_windows.ps1`, and land in Narc Recon first-run setup without copying assets or editing files by hand.

## Release Layout

The release zip contains:

```text
install_windows.ps1
dist\Narc Recon\
docs\windows-deployment.md
scripts\install_windows.ps1
```

The root `install_windows.ps1` is the script users should run after extracting the zip. The copy under `scripts\` is included so the same script also works from a repository checkout.

## Installed Locations

Per-user app install location:

```text
%LOCALAPPDATA%\Programs\Narc Recon\
```

Executable:

```text
%LOCALAPPDATA%\Programs\Narc Recon\Narc Recon.exe
```

Data folder:

```text
%USERPROFILE%\NarcReconData\
```

Default database path:

```text
%USERPROFILE%\NarcReconData\narc_recon.db
```

Config file:

```text
%USERPROFILE%\NarcReconData\config.env
```

Backup folder:

```text
%USERPROFILE%\NarcReconBackups\
```

## Build On Windows

Build the PyInstaller folder on a Windows machine:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r src\requirements.txt
pip install pyinstaller
pyinstaller --clean --noconfirm build\narc_recon.spec
```

Expected build output:

```text
dist\Narc Recon\Narc Recon.exe
```

The spec bundles these required resources:

```text
med_sheet.xlsx
others\logo_nr.png
others\logo_nr.ico
```

## Package The Release Zip

After the PyInstaller build succeeds, run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\package_windows_release.ps1
```

Expected release artifact:

```text
dist\Narc_Recon_windows_release.zip
```

The packaging script verifies the executable and bundled resources, refuses to package `narc_recon.db`, SQLite sidecar files, or `config.env`, and stages the simple release layout before zipping it.

## Install From The Release Zip

On the pharmacy workstation:

1. Extract `Narc_Recon_windows_release.zip`.
2. Open PowerShell in the extracted folder.
3. Run:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\install_windows.ps1
   ```

The installer:

- installs from `dist\Narc Recon\`
- creates `%LOCALAPPDATA%\Programs\Narc Recon\`
- creates `%USERPROFILE%\NarcReconData\`
- creates `%USERPROFILE%\NarcReconBackups\`
- creates `%USERPROFILE%\NarcReconData\config.env` only if it is missing
- never overwrites an existing `config.env`
- never deletes or overwrites `%USERPROFILE%\NarcReconData\narc_recon.db`
- refuses to install from or replace an app folder that contains `narc_recon.db`, SQLite sidecar files, or `config.env`
- closes or prompts to stop a running Narc Recon process before replacing app files
- replaces only the app install folder
- creates or updates the Desktop shortcut `Narc Recon.lnk`
- launches Narc Recon by default
- does not require administrator rights

Use `-NoOpen` when you need to install or update without launching afterward:

```powershell
powershell -ExecutionPolicy Bypass -File .\install_windows.ps1 -NoOpen
```

## First-Run Setup

On a fresh workstation, the installer creates `config.env` with:

```text
NARC_RECON_DB_PATH=%USERPROFILE%\NarcReconData\narc_recon.db
NARC_RECON_PEPPER=<generated-secret>
```

The generated pepper must be preserved after accounts are created. The installer never changes it once `config.env` exists.

When Narc Recon launches and no app account exists, first-run setup opens. Create the pharmacy app account and the initial Pharmacist user there. The database is created under `%USERPROFILE%\NarcReconData\`.

Use `NARC_RECON_EXCEL_PATH` only if a deployment intentionally needs an external Excel catalog file instead of the bundled `med_sheet.xlsx`.

## Update Procedure

1. Finish any active workflow in Narc Recon.
2. Close Narc Recon, or let the installer prompt to close it.
3. Confirm there is a current backup.
4. Extract the new `Narc_Recon_windows_release.zip`.
5. Run:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\install_windows.ps1
   ```

6. Run the smoke tests below.

The update replaces app files only. It must not touch `%USERPROFILE%\NarcReconData\` or `%USERPROFILE%\NarcReconBackups\`.

## GitHub Releases

Upload:

- `dist\Narc_Recon_windows_release.zip`
- release notes
- optional SHA256 checksum

Do not upload database files, `config.env`, backups, or secrets.

## Manual Smoke Tests

Run these on the target Windows workstation account:

- Fresh install opens without manual asset copying.
- Logo renders on the login window.
- First-run setup creates the app account and initial Pharmacist user.
- Login works after app restart.
- `config.env` is respected and remains unchanged after rerunning the installer.
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

The install/update flow must never delete or overwrite:

```text
%USERPROFILE%\NarcReconData\
%USERPROFILE%\NarcReconData\narc_recon.db
%USERPROFILE%\NarcReconData\narc_recon.db-wal
%USERPROFILE%\NarcReconData\narc_recon.db-shm
%USERPROFILE%\NarcReconData\config.env
%USERPROFILE%\NarcReconBackups\
```

## Full Installer

A full Windows installer can wait until the zip deployment has been validated on the target workstation. The current release flow is intentionally simple: PyInstaller folder, release zip, per-user install script, external data folder, and manual smoke tests.
