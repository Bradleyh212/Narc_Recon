import sqlite3
con = sqlite3.connect("tutorial.db")
import pandas as pd

narc_list = {}
df = pd.read_excel("Sheet1.xlsx", sheet_name="Sheet1")
upc_list = df["Upc"].fillna(1).apply(lambda x: str(int(x)).zfill(12)).tolist()
#print(upc_list)

drug_name_list = df["Drug Name"].tolist()
#print(drug_name_list)



for i in range(len(upc_list)):
	narc_list[upc_list[i]] = [drug_name_list[i]]




print()
print(narc_list)



