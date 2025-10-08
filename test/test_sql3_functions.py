# test/test_sql3_functions.py
import os, sys, importlib
import sqlite3
import pandas as pd
import pytest

@pytest.fixture(autouse=True)
def temp_db(monkeypatch, tmp_path):
    """Create a temporary in-memory or file-based SQLite DB for tests."""
    temp_db_path = tmp_path / "temp.db"
    con = sqlite3.connect(temp_db_path)
    cur = con.cursor()

    # Create only the minimal table needed for your test
    cur.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            role TEXT,
            created_at TEXT
        )
    """)
    cur.execute("INSERT INTO users (user_id, role, created_at) VALUES (?, ?, ?)", ('BHD', 'admin', "Today"))
    con.commit()

    # Patch get_conn() so it returns this temporary connection
    monkeypatch.setattr("sqlite3_functions.get_conn", lambda: con)

    yield  # runs the test

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