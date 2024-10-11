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

list_user_id = ["AZ"]

#This function will only be use when receiving and when doing
def add_to_audit_log(din, old, new, user): #Takes the din, the old qty, new qty and the user_id, and updates the audit log
    if user not in list_user_id:
        messagebox.showerror("Error", "Please enter a valid user ID")
    else :
        cur.execute("INSERT INTO audit_log values (?, ?, ?, ?)", (din, old, new, user))
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
    
show_audit_log()