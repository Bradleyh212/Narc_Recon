from ui import ui_helpers


class FakeParent:
	def __init__(self):
		self.after_calls = []
		self.destroyed = False

	def after(self, delay, callback):
		self.after_calls.append(delay)
		callback()

	def destroy(self):
		self.destroyed = True


class FakeApp:
	page_classes = {"INVENTORY": object, "SETTINGS": object}

	def __init__(self):
		self.shown_pages = []

	def show_page(self, page_name):
		self.shown_pages.append(page_name)


def test_open_nav_choice_routes_settings_through_guard(monkeypatch):
	parent = FakeParent()
	calls = []

	def fake_guard(window, app=None, pages=None):
		calls.append(("guard", window, app, pages))

	monkeypatch.setattr(ui_helpers, "_open_settings_guard", fake_guard)

	ui_helpers.open_nav_choice(parent, "SETTINGS")

	assert calls == [("guard", parent, None, None)]
	assert parent.after_calls == []
	assert parent.destroyed is False


def test_open_nav_choice_routes_non_settings_page_through_app():
	parent = FakeParent()
	app = FakeApp()

	ui_helpers.open_nav_choice(parent, "INVENTORY", app=app)

	assert parent.after_calls == [180]
	assert app.shown_pages == ["INVENTORY"]
	assert parent.destroyed is False


def test_open_nav_choice_keeps_standalone_fallback(monkeypatch):
	parent = FakeParent()
	calls = []
	pages = {"INVENTORY": lambda: calls.append("opened")}

	monkeypatch.setattr(ui_helpers, "safe_destroy", lambda window: calls.append(("destroy", window)))

	ui_helpers.open_nav_choice(parent, "INVENTORY", pages=pages)

	assert parent.after_calls == [180]
	assert calls == [("destroy", parent), "opened"]
