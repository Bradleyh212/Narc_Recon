import sqlite3 #To use database
con = sqlite3.connect("narcotics_database.db") #Connecting our databse
import pandas as pd
from other_functions import create_narc_list, show_narcs_table
from sqlite3_functions import create_narcs_table, create_narcs_details_table, from_excel_to_sql, find_narcs_upc, find_narcs_din, find_quantity

narc_list = create_narc_list()

cur = con.cursor() # Create a cursor

create_narcs_table() #Creating table for the meds
create_narcs_details_table() #Creating a detailed table for the meds
from_excel_to_sql() # Importing all the excel data into the sql database

con.commit()

