import sqlite3
from prettytable import PrettyTable


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

def show_audit_log():
    audit_cur.execute("SELECT * FROM audit_log")
    rows = audit_cur.fetchall()

    column_names = []
    for description in audit_cur.description:
        column_names.append(description[0])


    table = PrettyTable()

    table.field_names = column_names

    for row in rows:
        table.add_row(row)

    print(table)

print(show_audit_log())