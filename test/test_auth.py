import importlib
import pytest

# Import the module so we can monkeypatch its PEPPER if needed
authmod = importlib.import_module("src.auth")
_hash_secret = authmod._hash_secret
_verify_secret = authmod._verify_secret

def test_hash_is_not_plaintext_and_has_reasonable_length():
    pwd = "123"
    h = _hash_secret(pwd)
    assert isinstance(h, str)
    assert pwd not in h  # never store plaintext
    assert len(h) > 20   # making sure the hash is not too small


def test_same_password_hashes_differ_due_to_salt():
    pwd = "123"
    h1 = _hash_secret(pwd)
    h2 = _hash_secret(pwd)
    assert h1 != h2      # Argon2 should salt and hash should always be different


def test_verify_correct_password():
    pwd = "correct-horse-battery-staple"
    h = _hash_secret(pwd)
    assert _verify_secret(h, pwd) is True

def test_empty_password():
    # If you ever allow empty passwords, this ensures roundtrip works.
    h = _hash_secret("")
    assert _verify_secret(h, "") is True
    assert _verify_secret(h, " ") is False


def test_unicode_password():
    pwd = "Pässwørd🔒"
    h = _hash_secret(pwd)
    assert _verify_secret(h, pwd) is True
    assert _verify_secret(h, "Pässwørd") is False


def test_blank_spaces():
    h = _hash_secret("123")
    assert _verify_secret(h, "123") is True
    assert _verify_secret(h, "123 ") is False   # testing blank space
