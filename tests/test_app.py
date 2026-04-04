"""
Unit tests for the ACEest Fitness & Gym Flask API.
Tests endpoints for programs, client profiles, and Swagger documentation.
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_home():
    """Test home endpoint returns 200 and expected message."""
    client = app.test_client()
    res = client.get("/")
    assert res.status_code == 200
    assert b"ACEest Fitness & Gym APP Running" in res.data


def test_get_programs():
    """Test retrieving all programs endpoint."""
    client = app.test_client()
    res = client.get("/programs")
    assert res.status_code == 200
    data = res.get_json()
    assert "Fat Loss (FL)" in data
    assert "Muscle Gain (MG)" in data
    assert "Beginner (BG)" in data


def test_valid_program():
    """Test retrieving a valid program."""
    client = app.test_client()
    res = client.get("/program/Fat Loss (FL)")
    assert res.status_code == 200
    data = res.get_json()
    assert "workout" in data
    assert "diet" in data
    assert "color" in data


def test_invalid_program():
    """Test retrieving an invalid program returns 404."""
    client = app.test_client()
    res = client.get("/program/invalid")
    assert res.status_code == 404
    data = res.get_json()
    assert data["error"] == "Program not found"


def test_client_profile_valid():
    """Test creating a valid client profile."""
    client = app.test_client()
    payload = {
        "name": "John Doe",
        "age": 28,
        "weight": 70,
        "program": "Fat Loss (FL)",
        "adherence": 85
    }
    res = client.post("/client", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["name"] == "John Doe"
    assert data["program"] == "Fat Loss (FL)"
    assert data["calories"] == 70 * 22
    assert data["adherence"] == 85


def test_client_profile_invalid_program():
    """Test creating a client profile with invalid program."""
    client = app.test_client()
    payload = {
        "name": "Jane Doe",
        "age": 25,
        "weight": 60,
        "program": "Invalid Program",
        "adherence": 90
    }
    res = client.post("/client", json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data["error"] == "Invalid program"


def test_swagger_ui_available():
    """Test Swagger API documentation is available."""
    client = app.test_client()
    res = client.get("/swagger.json")
    assert res.status_code == 200

    data = res.get_json()
    assert data["info"]["title"] == "ACEest Fitness & Gym"
    assert (
        data["info"]["description"]
        == "API for accessing fitness programs, workouts, and nutrition plans."
    )
