from datetime import datetime
import pytz
import sqlite3
from prettytable import PrettyTable

# Connect to narcotics and audit log databases
con = sqlite3.connect("narcotics_database.db")
cur = con.cursor()

audit_con = sqlite3.connect('audit_log.db')
audit_cur = audit_con.cursor()

# Set the user's timezone (America/Toronto)
user_timezone = pytz.timezone('America/Toronto')

# Create audit log table if it doesn't exist
audit_cur.execute("""
	CREATE TABLE IF NOT EXISTS audit_log (
		log_id INTEGER PRIMARY KEY AUTOINCREMENT,
		din TEXT,
		old_qty INT,
		new_qty INT,
		Updated_By VARCHAR(10),
		Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	)
""")
audit_con.commit()

# Predefined list of valid user IDs
list_user_id = ["Filling"] # Will add user id in pharmacy system only

# Function to add an entry to the audit log
def add_to_audit_log(din, old_qty, user):
	if user not in list_user_id:
		messagebox.showerror("Error", "Please enter a valid user ID")
		return

	# Get the current quantity of the narcotic by DIN
	cur.execute("SELECT quantity FROM narcs WHERE din = ?", (din,))
	new_qty = cur.fetchone()[0]

	# In the add_to_audit_log function
	formatted_time = datetime.now(pytz.utc).astimezone(user_timezone).strftime('%Y-%m-%d %H:%M:%S')

	# Insert the log entry into the audit log table
	audit_cur.execute("""
		INSERT INTO audit_log (din, old_qty, new_qty, Updated_By, Timestamp)
		VALUES (?, ?, ?, ?, ?)
	""", (din, old_qty, new_qty, user, formatted_time))
	
	audit_con.commit()

# Function to display the audit log in a pretty table format
def show_audit_log():
	audit_cur.execute("SELECT * FROM audit_log")
	rows = audit_cur.fetchall()

	# Fetch column names from the database
	column_names = [description[0] for description in audit_cur.description]

	# Create and format the PrettyTable
	table = PrettyTable()
	table.field_names = column_names

	# Add each row to the table
	for row in rows:
		table.add_row(row)

	# Print the table
	print(table)

# Display the audit log

show_audit_log()

