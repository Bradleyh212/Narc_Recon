import sqlite3 #To use database
con = sqlite3.connect("narcotics_database.db") #Connecting our databse
import pandas as pd #Importint to read excel file

cur = con.cursor() # Create a cursor

cur.execute("""CREATE TABLE IF NOT EXISTS narcs ( -- Create a table called narcs

/* Added the ""IF NOT EXISTS" constraint to make sure i dont have to
comment out create table (can run multiple time without "table already exist error") */
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug_name TEXT NOT NULL,
            din TEXT NOT NULL, -- storing as text because of leading zero's
            strength TEXT NOT NULL,
            form TEXT NOT NULL UNIQUE,
            upc TEXT NOT NULL, -- storing as text because of leading zero's
            pack_size INTEGER NOT NULL
            )

        """)

#ur.executemany()

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

narc_list = create_narc_list()


print()
print(len(narc_list))
print()
print(narc_list)



