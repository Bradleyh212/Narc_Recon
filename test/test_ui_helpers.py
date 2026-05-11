from ui import ui_helpers


class FakeParent:
	def __init__(self):
		self.after_calls = []
		self.destroyed = False

	def after(self, delay, callback):
		self.after_calls.append(delay)
		callback()


class FakeApp:
	page_classes = {"INVENTORY": object, "SETTINGS": object}

	def __init__(self):
		self.shown_pages = []

	def show_page(self, page_name):
		self.shown_pages.append(page_name)


def test_open_nav_choice_routes_settings_through_guard(monkeypatch):
	parent = FakeParent()
	app = FakeApp()
	calls = []

	def fake_guard(window, app):
		calls.append(("guard", window, app))

	monkeypatch.setattr(ui_helpers, "_open_settings_guard", fake_guard)

	ui_helpers.open_nav_choice(parent, "SETTINGS", app=app)

	assert calls == [("guard", parent, app)]
	assert parent.after_calls == []
	assert parent.destroyed is False


def test_open_nav_choice_routes_non_settings_page_through_app():
	parent = FakeParent()
	app = FakeApp()

	ui_helpers.open_nav_choice(parent, "INVENTORY", app=app)

	assert parent.after_calls == [180]
	assert app.shown_pages == ["INVENTORY"]
	assert parent.destroyed is False


def test_open_settings_guard_denies_disallowed_role(monkeypatch):
	parent = FakeParent()
	calls = []
	app = FakeApp()

	monkeypatch.setattr(ui_helpers.simpledialog, "askstring", lambda *args, **kwargs: "tech-1")
	monkeypatch.setattr(ui_helpers.user_service, "get_user_role", lambda conn, user_id: "Technician")
	monkeypatch.setattr(ui_helpers.user_service, "role_allows_settings", lambda role: False)
	monkeypatch.setattr(ui_helpers.messagebox, "showerror", lambda title, message: calls.append((title, message)))

	ui_helpers._open_settings_guard(parent, app=app)

	assert calls == [("Access denied", "Settings are restricted to pharmacists.")]
	assert app.shown_pages == []
	assert parent.after_calls == []
