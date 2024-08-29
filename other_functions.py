import pandas as pd # Importing to read excel file

def create_narc_list():
	narc_list = {}
	for i in range(len(upc_list)):
		narc_list[upc_list[i]] = [drug_name_list[i], drug_din_list[i], drug_stregth_list[i], drug_form_list[i], drug_pack_size_list[i]]
	return narc_list

df = pd.read_excel("Sheet1.xlsx", sheet_name="Sheet1")

#make the upc list, also fill the first numbers with zero
upc_list = df["Upc"].fillna(1).apply(lambda x: str(int(x)).zfill(12)).tolist()
#print(upc_list)

drug_name_list = df["Drug Name"].tolist()
#print(drug_name_list)

drug_din_list = df["DIN"].apply(lambda x: str(int(x)).zfill(8)).tolist() #make the din list, also fill the first numbers with zero
#print(drug_din_list)

drug_stregth_list = df["Strength"].tolist()
#print(drug_stregth_list)

drug_form_list = df["Form"].tolist()
#print(drug_form_list)

drug_pack_size_list = df["Pack size"].fillna(1).astype(int).tolist()
#print(drug_pack_size_list)


def show_all_narcs_table():
	cur.execute("SELECT * FROM narcs")
	items = cur.fetchall()
	for i in range(len(items)):
		print(f"{items[i][0]} | {items[i][1]} | {items[i][2]} | {items[i][3]} | {items[i][4]} | {items[i][5]}")
