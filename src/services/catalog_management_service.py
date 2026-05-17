from services.excel_import_service import normalize_din, normalize_upc


class DuplicateMedicationDetailError(ValueError):
	pass


class CatalogManagementService:
	def __init__(self, connection):
		self.connection = connection

	def add_medication(self, name, din, upc, strength=None, form=None, pack_size=None):
		medication = self._normalize_medication(name, din, upc, strength, form, pack_size)
		cursor = self.connection.cursor()
		started_transaction = not self.connection.in_transaction

		if started_transaction:
			self.connection.execute("BEGIN")

		try:
			existing_narc = cursor.execute(
				"SELECT name FROM narcs WHERE din = ?",
				(medication["din"],),
			).fetchone()

			if self._detail_exists(cursor, medication["din"], medication["upc"], medication["pack_size"]):
				raise DuplicateMedicationDetailError("Medication detail already exists for this DIN, UPC, and pack size.")

			created_narc = existing_narc is None
			updated_name = False

			if created_narc:
				cursor.execute(
					"INSERT INTO narcs (din, name, quantity) VALUES (?, ?, ?)",
					(medication["din"], medication["name"], 0),
				)
			elif existing_narc[0] != medication["name"]:
				cursor.execute(
					"UPDATE narcs SET name = ? WHERE din = ?",
					(medication["name"], medication["din"]),
				)
				updated_name = True

			cursor.execute(
				"""
				INSERT INTO narcs_details (din, upc, strength, form, pack_size)
				VALUES (?, ?, ?, ?, ?)
				""",
				(
					medication["din"],
					medication["upc"],
					medication["strength"],
					medication["form"],
					medication["pack_size"],
				),
			)

			if started_transaction:
				self.connection.commit()
		except Exception:
			if started_transaction:
				self.connection.rollback()
			raise

		return {
			"din": medication["din"],
			"upc": medication["upc"],
			"pack_size": medication["pack_size"],
			"created_narc": created_narc,
			"updated_name": updated_name,
		}

	def _normalize_medication(self, name, din, upc, strength, form, pack_size):
		return {
			"name": self._required_text(name, "Drug name"),
			"din": self._identifier(din, "DIN", normalize_din, 8),
			"upc": self._identifier(upc, "UPC", normalize_upc, 12),
			"strength": self._optional_text(strength),
			"form": self._required_text(form, "Form"),
			"pack_size": self._pack_size(pack_size),
		}

	def _detail_exists(self, cursor, din, upc, pack_size):
		row = cursor.execute(
			"""
			SELECT 1
			FROM narcs_details
			WHERE din = ? AND upc = ? AND pack_size = ?
			""",
			(din, upc, pack_size),
		).fetchone()
		return row is not None

	def _required_text(self, value, field_name):
		text = self._optional_text(value)
		if text is None:
			raise ValueError(f"{field_name} is required.")
		return text

	def _optional_text(self, value):
		if value is None:
			return None
		text = str(value).strip()
		return text or None

	def _identifier(self, value, field_name, normalizer, width):
		text = self._required_text(value, field_name)
		try:
			normalized = normalizer(text)
		except (TypeError, ValueError):
			raise ValueError(f"{field_name} must be numeric.") from None
		if len(normalized) != width or not normalized.isdigit() or normalized == "0" * width:
			raise ValueError(f"{field_name} must be a numeric value with at most {width} digits.")
		return normalized

	def _pack_size(self, value):
		text = self._optional_text(value)
		if text is None:
			return "0"
		try:
			pack_size = int(text)
		except (TypeError, ValueError):
			raise ValueError("Pack size must be a whole number.") from None
		if pack_size < 0:
			raise ValueError("Pack size must be zero or greater.")
		return str(pack_size)


def add_medication(connection, name, din, upc, strength=None, form=None, pack_size=None):
	return CatalogManagementService(connection).add_medication(name, din, upc, strength, form, pack_size)
