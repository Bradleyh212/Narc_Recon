# Narc Recon Manual Restore Drill

This is a non-destructive restore drill for verifying that a Narc Recon SQLite backup can be opened and inspected. It does not restore into the live data folder.

Use this drill before real deployment and after any backup procedure changes.

## Safety Rules

- Close Narc Recon before starting the drill.
- Do not copy the backup into `~/NarcReconData/`.
- Do not overwrite `~/NarcReconData/narc_recon.db`.
- Do not delete `~/NarcReconData/` unless intentionally resetting real local data.
- Use a backup created with the same `NARC_RECON_PEPPER` if you need to test existing login credentials.
- App account password verification depends on the same pepper used when the account was created.

## Restore-Test Folder

Create a temporary restore-test folder:

```bash
mkdir -p "$HOME/NarcReconRestoreTest"
```

Choose a backup file from:

```text
~/NarcReconBackups/
```

Copy the backup into the restore-test folder as `narc_recon.db`:

```bash
cp "/path/to/backup.db" "$HOME/NarcReconRestoreTest/narc_recon.db"
```

## Verify The Copied Database

Run SQLite integrity check:

```bash
sqlite3 "$HOME/NarcReconRestoreTest/narc_recon.db" "PRAGMA integrity_check;"
```

Expected result:

```text
ok
```

Check key table row counts:

```bash
sqlite3 "$HOME/NarcReconRestoreTest/narc_recon.db" \
"SELECT 'app_account', COUNT(*) FROM app_account
 UNION ALL SELECT 'users', COUNT(*) FROM users
 UNION ALL SELECT 'narcs', COUNT(*) FROM narcs
 UNION ALL SELECT 'narcs_details', COUNT(*) FROM narcs_details
 UNION ALL SELECT 'audit_log', COUNT(*) FROM audit_log;"
```

Compare these row counts with the output from `scripts/backup_db.py` when the backup was created.

## Launch Narc Recon Against The Test Copy

Launch the packaged app using the copied test database only:

```bash
NARC_RECON_DB_PATH="$HOME/NarcReconRestoreTest/narc_recon.db" open "/Applications/Narc Recon.app"
```

If macOS reuses an existing app process, close Narc Recon and launch a new instance:

```bash
NARC_RECON_DB_PATH="$HOME/NarcReconRestoreTest/narc_recon.db" open -n "/Applications/Narc Recon.app"
```

Verify:

- App opens.
- Login works.
- Inventory loads.
- Known DIN/UPC searches work.
- Users exist.
- Audit log/report data exists.
- Row counts match the backup output.

## Finish The Drill

Close Narc Recon.

Remove the temporary restore-test folder only after verification, if desired:

```bash
rm -rf "$HOME/NarcReconRestoreTest"
```

Do not remove `~/NarcReconData/` as part of this drill.

## Production Restore

This drill does not perform production restore. A real production restore can overwrite live data and should only be done with Narc Recon closed, a rollback copy of the current live database, and explicit operator approval.
