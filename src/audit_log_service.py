from datetime import datetime

import pytz


def create_audit_log_table(cursor):
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS audit_log (
			log_id INTEGER PRIMARY KEY AUTOINCREMENT,
			din TEXT,
			old_qty INT,
			new_qty INT,
			Updated_By VARCHAR(10),
			Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			transaction_type TEXT,
			discrepancy INT
		)
	""")


def local_timestamp(timezone):
	return datetime.now(pytz.utc).astimezone(timezone).strftime('%Y-%m-%d %H:%M:%S')


def add_to_audit_log(
	cursor,
	connection,
	din,
	old_qty,
	user,
	transaction_type,
	user_exists,
	find_quantity_din,
	timezone,
):
	if not user_exists(user):
		print("Error: Invalid user ID.")
		return

	new_qty = find_quantity_din(din)
	formatted_time = local_timestamp(timezone)
	discrepancy = new_qty - old_qty

	cursor.execute("""
		INSERT INTO audit_log (din, old_qty, new_qty, Updated_By, Timestamp, transaction_type, discrepancy)
		VALUES (?, ?, ?, ?, ?, ?, ?)
	""", (din, old_qty, new_qty, user, formatted_time, transaction_type, discrepancy))
	connection.commit()


def fetch_audit_log(cursor):
	cursor.execute("SELECT * FROM audit_log")
	rows = cursor.fetchall()
	column_names = [description[0] for description in cursor.description]
	return column_names, rows


def get_audit_log_by_din_and_date(cursor, din, start_date, end_date):
	cursor.execute("""
		SELECT din, old_qty, new_qty, Updated_By, Timestamp
		FROM audit_log
		WHERE din = ?
		AND date(Timestamp) BETWEEN ? AND ?
		ORDER BY Timestamp ASC
	""", (din, start_date, end_date))
	return cursor.fetchall()


def get_reconciliation_log_by_date_range(cursor, start_date, end_date):
	cursor.execute("""
		SELECT
			n.name,              -- 0
			nd.strength,         -- 1
			a.din,               -- 2
			a.old_qty,           -- 3
			a.new_qty,           -- 4
			a.discrepancy,       -- 5
			a.Timestamp          -- 6
		FROM audit_log a
		JOIN narcs n ON n.din = a.din
		LEFT JOIN (
			SELECT din, MIN(strength) AS strength
			FROM narcs_details
			GROUP BY din
		) nd ON nd.din = a.din
		WHERE a.transaction_type = 'reconciliation'
		  AND DATE(a.Timestamp) BETWEEN ? AND ?
		ORDER BY
			n.name COLLATE NOCASE,
			nd.strength COLLATE NOCASE,
			a.din,
			a.Timestamp
	""", (start_date, end_date))
	return cursor.fetchall()
