from collections import Counter

import pandas as pd


REQUIRED_EXCEL_COLUMNS = ("Drug Name", "DIN", "Strength", "Form", "Upc", "Pack size")


def validate_excel_columns(df):
	missing_columns = [column for column in REQUIRED_EXCEL_COLUMNS if column not in df.columns]
	if missing_columns:
		raise ValueError("Missing required Excel columns: " + ", ".join(missing_columns))


def normalize_din(value):
	return str(int(value)).zfill(8)


def normalize_upc(value):
	if pd.isna(value):
		value = 0
	return str(int(value)).zfill(12)


class ExcelImportService:
	def __init__(self, excel_path=None, sheet_name="med_sheet"):
		self.excel_path = excel_path
		self.sheet_name = sheet_name

	def validate_columns(self, df):
		return validate_excel_columns(df)

	def validate_rows(self, df):
		self.validate_columns(df)

		blank_upc_rows = []
		normalized_upcs = []
		normalized_dins = []
		warnings = []

		for row_number, (_, row) in enumerate(df.iterrows(), start=2):
			try:
				upc = normalize_upc(row["Upc"])
				if upc == "000000000000":
					blank_upc_rows.append(row_number)
				else:
					normalized_upcs.append(upc)
			except (TypeError, ValueError):
				warnings.append(f"Row {row_number} has an invalid UPC value.")

			try:
				normalized_dins.append(normalize_din(row["DIN"]))
			except (TypeError, ValueError):
				warnings.append(f"Row {row_number} has an invalid DIN value.")

		duplicate_upcs = sorted(upc for upc, count in Counter(normalized_upcs).items() if count > 1)
		duplicate_dins = sorted(din for din, count in Counter(normalized_dins).items() if count > 1)

		if blank_upc_rows:
			warnings.append(f"{len(blank_upc_rows)} row(s) have blank UPC values and will be skipped.")
		if duplicate_upcs:
			warnings.append("Duplicate UPC values found: " + ", ".join(duplicate_upcs))

		return {
			"blank_upc_count": len(blank_upc_rows),
			"blank_upc_rows": blank_upc_rows,
			"duplicate_upcs": duplicate_upcs,
			"duplicate_dins": duplicate_dins,
			"warnings": warnings,
		}

	def create_narc_list(self):
		df = pd.read_excel(self.excel_path, sheet_name=self.sheet_name)
		self.validate_columns(df)

		upc_list = df["Upc"].apply(normalize_upc).tolist()
		drug_name_list = df["Drug Name"].tolist()
		drug_din_list = df["DIN"].apply(normalize_din).tolist()
		drug_strength_list = df["Strength"].tolist()
		drug_form_list = df["Form"].tolist()
		drug_pack_size_list = df["Pack size"].fillna(0).astype(int).tolist()

		narc_list = {}
		for i in range(len(upc_list)):
			if upc_list[i] == "000000000000":
				continue
			if drug_din_list[i] not in narc_list:
				narc_list[drug_din_list[i]] = []
			narc_list[drug_din_list[i]].append({
				"name": drug_name_list[i],
				"upc": upc_list[i],
				"strength": drug_strength_list[i],
				"form": drug_form_list[i],
				"pack_size": drug_pack_size_list[i]
			})
		return narc_list

	def import_to_sql(self, cursor, narc_list):
		for din, details_list in narc_list.items():
			drug_name = details_list[0]["name"]
			cursor.execute("INSERT OR IGNORE INTO narcs (din, name, quantity) VALUES (?, ?, ?)", (din, drug_name, 0))

			for details in details_list:
				cursor.execute("""
					INSERT OR IGNORE INTO narcs_details (din, upc, strength, form, pack_size)
					VALUES (?, ?, ?, ?, ?)
				""", (din, details["upc"], details["strength"], details["form"], details["pack_size"]))


def validate_excel_rows(df):
	return ExcelImportService().validate_rows(df)


def create_narc_list(excel_path, sheet_name="med_sheet"):
	return ExcelImportService(excel_path, sheet_name).create_narc_list()


def from_excel_to_sql(cursor, narc_list):
	return ExcelImportService().import_to_sql(cursor, narc_list)
