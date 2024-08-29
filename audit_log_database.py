import sqlite3

audit_con = sqlite3.connect('audit_log.db')

audit_cur = audit_con.cursor()

audit_cur.execute("""CREATE TABLE IF NOT EXISTS audit_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    din TEXT,
    odl_qty INT,
    new_qty INT,
    Updated_By VARCHAR(10),
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	)""")

audit_con.commit()