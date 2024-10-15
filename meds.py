# Page to create the meds in the SQLite database
import sqlite3
import pandas as pd
from sqlite3_functions import (
    create_narcs_table,
    create_narcs_details_table,
    from_excel_to_sql,
    find_narcs_upc,
    find_narcs_din,
    find_quantity
)

# Connect to the SQLite database
con = sqlite3.connect("narcotics_database.db")
cur = con.cursor()

# Create tables for storing narcotics data
create_narcs_table()  # Main table for meds
create_narcs_details_table()  # Detailed table for meds

# Import data from Excel into the SQL database
from_excel_to_sql()

# Commit the changes to the database
con.commit()

# Optionally, you may want to close the connection afterward if no further actions are needed
con.close()