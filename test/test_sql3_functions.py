# test/test_sql3_functions.py
import os, sys, importlib
import sqlite3
import pandas as pd
import pytest

@pytest.fixture(autouse=True)
def temp_db(monkeypatch, tmp_path):
    """Create a fresh, isolated SQLite DB for each test and patch get_conn()."""
    temp_db_path = tmp_path / "temp.db"
    con = sqlite3.connect(temp_db_path)
    cur = con.cursor()

    # --- schema minimal for your tests ---
    cur.executescript("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            role TEXT,
            created_at TEXT
        );

        CREATE TABLE narcs (
            din TEXT PRIMARY KEY,
            name TEXT,
            upc TEXT,
            quantity REAL DEFAULT 0
        );

        CREATE TABLE audit_log (
            din TEXT,
            old_qty REAL,
            new_qty REAL,
            Updated_By TEXT,
            Timestamp TEXT,
            transaction_type TEXT,
            discrepancy REAL
        );
    """)

    # seed users and narcs so quantity lookups & user checks work
    cur.execute("INSERT INTO users (user_id, role, created_at) VALUES (?, ?, ?)",
                ('BHD', 'admin', 'Today'))
    cur.execute("INSERT INTO narcs (din, name, upc, quantity) VALUES (?, ?, ?, ?)",
                ('02248809', 'ADDERALL XR', '663220111026', 0))
    con.commit()

    # Patch sqlite3_functions.get_conn so all DB calls use this temp DB
    monkeypatch.setattr("sqlite3_functions.get_conn", lambda: con)

    # Ensure audit_log starts empty (paranoid clear each test)
    cur.execute("DELETE FROM audit_log")
    con.commit()

    yield

    con.close()

# Make src/ importable as top-level modules ("auth", "sqlite3_functions", etc.)
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(ROOT, "src"))

# Mock DataFrame with the EXACT column names your loader expects
FAKE_DF = pd.DataFrame([{
    "DIN": "02248809",
    "Drug Name": "ADDERALL XR",
    "Upc": 663220111026,
    "Strength": "10MG",
    "Form": "CAP",
    "Pack size": 100,
}])

@pytest.fixture(autouse=True)
def mock_excel(monkeypatch):
    # Ensure import-time read_excel uses the fake sheet
    monkeypatch.setattr("pandas.read_excel", lambda *a, **k: FAKE_DF)

def test_find_narcs_din():
    # Import AFTER mocking so module-level build runs with our fake DF
    sqlite3_functions = importlib.import_module("sqlite3_functions")

    # Adjust expected order/shape to match your function’s return
    assert sqlite3_functions.find_narcs_din("02248809") == [('02248809', 'ADDERALL XR', 0, '663220111026', '10MG', 'CAP', '100')]

def test_find_narcs_upc():
    # Import AFTER mocking so module-level build runs with our fake DF
    sqlite3_functions = importlib.import_module("sqlite3_functions")

    # Adjust expected order/shape to match your function’s return
    assert sqlite3_functions.find_narcs_upc("663220111026") == [('02248809', 'ADDERALL XR', 0, '663220111026', '10MG', 'CAP', '100')]
    assert sqlite3_functions.find_narcs_upc("") == []

def test_find_quantity_din():
    # Import AFTER mocking so module-level build runs with our fake DF
    sqlite3_functions = importlib.import_module("sqlite3_functions")

    assert sqlite3_functions.find_quantity_din("02248809") == 0
    assert sqlite3_functions.find_quantity_din("02248809") != 1 # Testing edge cases
    assert sqlite3_functions.find_quantity_din("02248809") != -1 # Testing edge cases
    assert sqlite3_functions.find_quantity_din("02248809") != 1234 # Testing random value

def test_find_quantity_upc():
    # Import AFTER mocking so module-level build runs with our fake DF
    sqlite3_functions = importlib.import_module("sqlite3_functions")

    assert sqlite3_functions.find_quantity("663220111026") == 0
    assert sqlite3_functions.find_quantity("663220111026") != 1 # Testing edge cases
    assert sqlite3_functions.find_quantity("663220111026") != -1 # Testing edge cases
    assert sqlite3_functions.find_quantity("663220111026") != 4321 # Testing random value

def test_list_users():
    # Import AFTER mocking so module-level build runs with our fake DF
    sqlite3_functions = importlib.import_module("sqlite3_functions")

    assert sqlite3_functions.list_users() == [(1, "BHD", "admin", "Today")]
    assert sqlite3_functions.list_users() != [(1, "Brad", "admin", "Today")]


def test_list_user_ids():
    # Import AFTER mocking so module-level build runs with our fake DF
    sqlite3_functions = importlib.import_module("sqlite3_functions")

    assert sqlite3_functions.list_user_ids() == ["BHD"]

def test_user_exists_true_false():
    # Import AFTER mocking so module-level build runs with our fake DF
    sqlite3_functions = importlib.import_module("sqlite3_functions")
    assert sqlite3_functions.user_exists("BHD") is True
    assert sqlite3_functions.user_exists("NOPE") is False

def test_add_and_remove_user_roundtrip():
    # Import AFTER mocking so module-level build runs with our fake DF
    sqlite3_functions = importlib.import_module("sqlite3_functions")
    sqlite3_functions.add_user("TMP", "staff")
    assert sqlite3_functions.user_exists("TMP") is True
    sqlite3_functions.remove_user("TMP")
    assert sqlite3_functions.user_exists("TMP") is False

# def test_get_audit_log_by_din_and_date():
#     sqlite3_functions = importlib.import_module("sqlite3_functions")
#     # With a fresh temp DB and cleared audit_log, this should be empty
#     assert sqlite3_functions.get_audit_log_by_din_and_date(
#         "02248809", "2025-01-01 21:13:36", "2025-10-09 21:13:36"
#     ) == []
