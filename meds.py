import sqlite3
con = sqlite3.connect("tutorial.db")


narc_list = {"upc":["Sandoz-Amphetamine Xr", "5mg", "02457288", "ER Cap", "100"]} #example of first medication

print(narc_list["upc"])


