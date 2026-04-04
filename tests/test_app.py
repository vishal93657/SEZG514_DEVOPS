import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_home():
    client = app.test_client()
    res = client.get("/")
    assert res.status_code == 200

def test_get_programs():
    client = app.test_client()
    res = client.get("/programs")
    assert res.status_code == 200

def test_valid_program():
    client = app.test_client()
    res = client.get("/program/Fat Loss (FL)")
    assert res.status_code == 200

def test_invalid_program():
    client = app.test_client()
    res = client.get("/program/invalid")
    assert res.status_code == 404