#import sqlite3
#con = sqlite3.connect("tutorial.db")
import pandas as pd

narc_list = {}
df = pd.read_excel("Sheet1.xlsx", sheet_name="Sheet1")
upc_list = df["Upc"].fillna(1).apply(lambda x: str(int(x)).zfill(12)).tolist() #make the upc list, also fill the first numbers with zero
#print(upc_list)

def strip_spaces(list):
	for i in list:
		i = i.strip()

drug_name_list = df["Drug Name"].tolist()

#strip_spaces(drug_name_list)

drug_din_list = df["DIN"].apply(lambda x: str(int(x)).zfill(8)).tolist() #make the din list, also fill the first numbers with zero
#print(drug_din_list)

drug_stregth_list = df["Strength"].tolist()
#print(drug_stregth_list)

drug_pack_size_list = df["Pack size"].fillna(1).astype(int).tolist()
#print(drug_pack_size_list)


for i in range(len(upc_list)):
		narc_list[upc_list[i]] = [drug_name_list[i], drug_din_list[i], drug_stregth_list[i], drug_pack_size_list[i]]

cleaned_narc_list = {} # creating a new list without the spaces from the excel sheet (maybe i will manually remove the spaces later on)
for key, value in narc_list.items():
    cleaned_values = []
    for item in value:
        if type(item) == str:
            cleaned_values.append(item.replace("\t", "").strip())
        else:
            cleaned_values.append(item)
    cleaned_narc_list[key] = cleaned_values



print()
print(len(cleaned_narc_list))
print()
print(cleaned_narc_list)



