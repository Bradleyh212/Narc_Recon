import pytz

from db.connection import get_conn
from services import audit_log_service
from services import inventory_service
from services import user_service


def add_to_audit_log(din, old_qty, user, transaction_type):
	connection = get_conn()
	try:
		cursor = connection.cursor()
		return audit_log_service.add_to_audit_log(
			cursor,
			connection,
			din,
			old_qty,
			user,
			transaction_type,
			lambda user_id: user_service.user_exists(connection, user_id),
			lambda narc_din: inventory_service.find_quantity_by_din(cursor, narc_din),
			pytz.timezone("America/Toronto"),
		)
	finally:
		connection.close()
