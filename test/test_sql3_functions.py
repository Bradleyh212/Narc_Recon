# test/test_sql3_functions.py
import os, sys, importlib
import pandas as pd
import pytest

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