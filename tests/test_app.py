import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
INITIAL_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities = copy.deepcopy(INITIAL_ACTIVITIES)
    yield
    app_module.activities = copy.deepcopy(INITIAL_ACTIVITIES)


def activity_url(activity_name: str) -> str:
    return f"/activities/{quote(activity_name)}"


def test_get_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_signup_for_activity():
    response = client.post(f"{activity_url('Chess Club')}/signup", params={"email": "test@mergington.edu"})

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up test@mergington.edu for Chess Club"}
    assert "test@mergington.edu" in app_module.activities["Chess Club"]["participants"]


def test_signup_for_activity_already_registered():
    response = client.post(f"{activity_url('Chess Club')}/signup", params={"email": "michael@mergington.edu"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_for_invalid_activity():
    response = client.post(f"{activity_url('Nonexistent Club')}/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant():
    response = client.delete(f"{activity_url('Programming Class')}/participants", params={"email": "emma@mergington.edu"})

    assert response.status_code == 200
    assert response.json() == {"message": "Removed emma@mergington.edu from Programming Class"}
    assert "emma@mergington.edu" not in app_module.activities["Programming Class"]["participants"]


def test_remove_nonexistent_participant():
    response = client.delete(f"{activity_url('Programming Class')}/participants", params={"email": "missing@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
