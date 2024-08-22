import sqlite3
con = sqlite3.connect("tutorial.db")
import pandas as pd


df = pd.read_excel('Sheet1.xlsx', sheet_name='Sheet1')
upc_list = df['Upc'].fillna(1).astype(int).astype(str).tolist() #transformin to int to removing the float numbers, then going back to string
print(upc_list)

narc_list = {}

for upc in upc_list:
	narc_list[upc] = []

print()
print(narc_list)









