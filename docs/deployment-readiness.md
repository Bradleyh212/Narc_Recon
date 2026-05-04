# Narc Recon Deployment Readiness

This checklist is for a small pharmacy desktop deployment of Narc Recon. It focuses on safe data handling, audit continuity, packaging, and manual release checks.

## 1. Production Database Path Recommendation

Do not store the production database inside the application source directory or app bundle.

Recommended production setup:

- If `NARC_RECON_DB_PATH` is not set, Narc Recon uses `~/NarcReconData/narc_recon.db`.
- Use `NARC_RECON_DB_PATH` only when a deployment needs an explicit writable, backed-up location outside the app bundle/source folder.
- Use a per-pharmacy shared local path only if one workstation owns access at a time and backups are reliable.
- Prefer a location with restricted filesystem permissions so regular users cannot casually edit or delete the database.

Default local path:

```bash
~/NarcReconData/narc_recon.db
```

Explicit override example:

```bash
NARC_RECON_DB_PATH="/Users/shared/NarcRecon/narc_recon.db"
```

Also keep the Excel catalog path explicit if the packaged app does not ship `med_sheet.xlsx` beside the source files:

```bash
NARC_RECON_EXCEL_PATH="/Users/shared/NarcRecon/med_sheet.xlsx"
```

## 2. SQLite Backup Procedure

SQLite may create companion files when WAL mode is active:

- `narc_recon.db`
- `narc_recon.db-wal`
- `narc_recon.db-shm`

Warning: do not copy only `narc_recon.db` while the app is open. Recent committed data may still involve WAL state.

Preferred backup procedure:

1. Close Narc Recon on all workstations.
2. Confirm no staff member is using the app.
3. Copy all existing database files:
   - `narc_recon.db`
   - `narc_recon.db-wal`, if present
   - `narc_recon.db-shm`, if present
4. Store the backup with a timestamp, for example:
   - `narc_recon_2026-05-03_1800.db`
5. Verify the copied backup opens in SQLite.
6. Confirm key tables exist:
   - `narcs`
   - `narcs_details`
   - `audit_log`
   - `users`
   - `app_account`

Minimum backup frequency:

- Before first deployment.
- Before every app update.
- Daily while in active use.
- Immediately before any manual database maintenance.

## 3. Restore Procedure

Use restore only while Narc Recon is closed.

1. Close Narc Recon on all workstations.
2. Move the current database files into a dated rollback folder:
   - `narc_recon.db`
   - `narc_recon.db-wal`, if present
   - `narc_recon.db-shm`, if present
3. Copy the backup database files into the production database directory.
4. Confirm the restored main file name matches `NARC_RECON_DB_PATH`.
5. Start Narc Recon.
6. Log in.
7. Verify:
   - Inventory opens.
   - Known DIN/UPC searches work.
   - Recent audit rows are present.
   - User list is intact.
8. If validation fails, close the app and restore the rollback copy.

## 4. Required Environment Variables

Required for production:

```bash
NARC_RECON_PEPPER="a-long-random-secret-kept-outside-git"
```

Optional database override:

```bash
NARC_RECON_DB_PATH="/path/to/narc_recon.db"
```

If this override is not set, Narc Recon creates and uses `~/NarcReconData/narc_recon.db`.

Recommended when the Excel file is external to the app bundle:

```bash
NARC_RECON_EXCEL_PATH="/path/to/med_sheet.xlsx"
```

Optional first-run account seeding:

```bash
NARC_RECON_APP_USER="admin-username"
NARC_RECON_APP_PASSWORD="temporary-setup-password"
```

Development-only flags:

```bash
NARC_RECON_DEV_UPDATE="1"
NARC_RECON_DEBUG_STARTUP="1"
```

Do not enable development-only flags in production unless intentionally troubleshooting.

Important:

- Set `NARC_RECON_PEPPER` before creating the production login account.
- Keep the pepper stable. Changing it after account creation can prevent existing passwords from verifying.
- Do not store production secrets in git.
- On fresh first-run setup, create the initial pharmacist staff user ID when prompted. This creates the first `users` row with role `Pharmacist` so Settings access is available without a hardcoded default user.

## 5. Manual QA Checklist Before Release

Run these checks against a copied test database before touching production data.

Login and startup:

- First-run account creation works.
- First-run setup requires an initial pharmacist user ID.
- The initial pharmacist user can open Settings.
- Existing login works.
- Invalid password is rejected.
- App opens Inventory after login.
- Restarting the app does not duplicate catalog rows.

Inventory:

- Search by DIN.
- Search by UPC.
- Invalid DIN/UPC shows the expected error.
- Multiple pack sizes can be selected correctly.

Receiving:

- Receive by DIN.
- Receive by UPC.
- Invalid user ID is rejected.
- Invalid quantity is rejected.
- Negative quantity is rejected.
- Quantity increases correctly.
- Audit row is written with transaction type `receiving`.

Filling:

- Fill by DIN.
- Fill by UPC.
- Zero quantity is rejected.
- Negative quantity is rejected.
- Quantity greater than stock is rejected.
- Quantity decreases correctly.
- Audit row is written with transaction type `filling`.

Reconciliation:

- Authorized role can set quantity.
- Unauthorized role is denied.
- Negative quantity is rejected.
- Quantity is set correctly.
- Audit row is written with transaction type `reconciliation`.

Expired quantity:

- Expired quantity greater than stock is rejected.
- Valid expired quantity reduces stock.
- Audit row is written with transaction type `expired`.

Reports:

- Inventory PDF exports to Downloads.
- Audit report exports for a known DIN/date range.
- Reconciliation report exports for a known date range.
- Empty report ranges show the expected no-data message.

Settings:

- Settings button prompts for user ID.
- Settings dropdown also prompts for user ID.
- `Pharmacist` and `pharmacist` roles are accepted.
- Non-pharmacist role is denied.
- Add user works.
- Remove user works.

## 6. Packaging Checklist For PyInstaller

Before packaging:

- Run full tests with `pytest`.
- Freeze and record dependency versions used for the build.
- Confirm `Pillow` is available, because `login.py` imports `PIL.Image`.
- Confirm the app starts from a clean terminal environment with production env vars set.

PyInstaller checklist:

- Use `src/narc_recon.pyw` as the entry point.
- Bundle required data files listed below.
- Test the packaged app on the target OS account, not only from the dev machine.
- Confirm write access to `NARC_RECON_DB_PATH`.
- Confirm PDF export to Downloads.
- Confirm the app can read `NARC_RECON_EXCEL_PATH`.
- Confirm the logo displays on the login screen.
- Confirm first-run setup works from the packaged app.

Do not depend on `NARC_RECON_DEV_UPDATE=1` in packaged production builds.

## 7. Files That Must Be Bundled

Application assets:

- `src/med_sheet.xlsx`, unless `NARC_RECON_EXCEL_PATH` points to an external managed file.
- `src/others/logo_nr.png`

Python modules under `src/` must be included by the packaged app.

If using external paths instead of bundled files:

- Document the deployed Excel path.
- Document the deployed database path.
- Confirm those files survive app updates.

## 8. Files That Must Never Be Committed

Never commit:

- `*.db`
- `*.db-wal`
- `*.db-shm`
- `.env`
- Excel lock files like `~$*.xlsx`
- Production backups
- Production credentials
- Production pepper/secrets
- Generated PDFs containing pharmacy data

The current `.gitignore` should continue excluding runtime database files and Excel lock files.

## 9. Known Deployment Risks

Database location:

- The default DB path is inside `src/`. That is not suitable for a packaged production app unless the folder is writable and backed up.

SQLite backup:

- WAL mode means backup procedures must account for `-wal` and `-shm` files or use a SQLite-safe backup.

Secrets:

- `NARC_RECON_PEPPER` must be set and retained. Losing or changing it can break password verification.

Settings access:

- Settings permissions are role-gated by user ID prompt. This is not the same as password re-authentication.

Audit integrity:

- Audit logs are stored in SQLite. Anyone with direct filesystem write access to the DB can potentially alter them outside the app.

Packaging:

- There is no committed PyInstaller spec yet.
- Dependency versions are not pinned.
- The app depends on local files and environment variables that must be configured carefully.

Excel catalog:

- Startup imports the Excel catalog. The production Excel file must be present, readable, and not locked by Excel.

## 10. What Can Wait Until After First Controlled Deployment

These items should not block a controlled deployment if backup, audit, login, and packaging checks pass:

- Further service refactoring.
- Removing `sqlite3_functions.py` import-time initialization.
- Changing audit internals.
- Redesigning database connection ownership.
- Changing report styling.
- UI layout polish.
- Replacing debug console output.
- Adding advanced import previews or import logs.

For first deployment, prioritize a controlled rollout with known users, verified backups, and daily audit review.
