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


def test_open_nav_choice_routes_settings_through_guard(monkeypatch):
	parent = FakeParent()
	calls = []
	pages = {"SETTINGS": lambda: calls.append("opened")}

	monkeypatch.setattr(ui_helpers, "_open_settings_guard", lambda window: calls.append(("guard", window)))

	ui_helpers.open_nav_choice(parent, pages, "SETTINGS")

	assert calls == [("guard", parent)]
	assert parent.after_calls == []
	assert parent.destroyed is False


def test_open_nav_choice_opens_non_settings_page(monkeypatch):
	parent = FakeParent()
	calls = []
	pages = {"INVENTORY": lambda: calls.append("opened")}

	monkeypatch.setattr(ui_helpers, "safe_destroy", lambda window: calls.append(("destroy", window)))

	ui_helpers.open_nav_choice(parent, pages, "INVENTORY")

	assert parent.after_calls == [180]
	assert calls == [("destroy", parent), "opened"]
