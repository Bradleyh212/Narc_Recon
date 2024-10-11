from datetime import datetime
import pytz

import sqlite3
from prettytable import PrettyTable

con = sqlite3.connect("narcotics_database.db")
cur = con.cursor() # Create a cursor


audit_con = sqlite3.connect('audit_log.db')
audit_cur = audit_con.cursor()

user_timezone = pytz.timezone('America/Toronto') # This is to set the current time zone

audit_cur.execute("""CREATE TABLE IF NOT EXISTS audit_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    din TEXT,
    odl_qty INT,
    new_qty INT,
    Updated_By VARCHAR(10),
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	)""")

audit_con.commit()

list_user_id = ["AZ", "Remove"]

#This function will only be use when receiving and when doing
def add_to_audit_log(din, old, user): #Takes the din, the old qty, new qty and the user_id, and updates the audit log
    if user not in list_user_id:
        messagebox.showerror("Error", "Please enter a valid user ID")
    else :
        cur.execute("SELECT quantity FROM narcs WHERE din = ?", (din, ))
        new_amount = cur.fetchone()[0]

        current_time_utc = datetime.now(pytz.utc)
        current_time_local = current_time_utc.astimezone(user_timezone)

        # Format the converted time as a string for SQLite (e.g., '2024-10-11 03:42:04')
        formatted_time = current_time_local.strftime('%Y-%m-%d %H:%M:%S')
        
        audit_cur.execute("INSERT INTO audit_log (din, odl_qty, new_qty, Updated_By, Timestamp) values (?, ?, ?, ?, ?)", (din, old, new_amount, user, formatted_time))
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