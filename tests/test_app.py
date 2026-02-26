from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client() -> TestClient:
    return TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities_state():
    original_activities = deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original_activities)


def test_get_activities_returns_expected_structure(client: TestClient):
    expected_keys = {"description", "schedule", "max_participants", "participants"}

    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert expected_keys.issubset(payload["Chess Club"].keys())


def test_signup_adds_participant_successfully(client: TestClient):
    activity_name = "Chess Club"
    new_email = "new.student@mergington.edu"

    response = client.post("/activities/Chess%20Club/signup", params={"email": new_email})

    assert response.status_code == 200
    payload = response.json()
    assert "message" in payload
    assert new_email in app_module.activities[activity_name]["participants"]


def test_signup_returns_404_for_unknown_activity(client: TestClient):
    response = client.post("/activities/Unknown Club/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    payload = response.json()
    assert "detail" in payload


def test_signup_returns_400_for_duplicate_participant(client: TestClient):
    activity_name = "Chess Club"
    existing_email = app_module.activities[activity_name]["participants"][0]

    response = client.post("/activities/Chess%20Club/signup", params={"email": existing_email})

    assert response.status_code == 400
    payload = response.json()
    assert "detail" in payload


def test_signup_returns_422_when_email_is_missing(client: TestClient):
    response = client.post("/activities/Chess%20Club/signup")

    assert response.status_code == 422
    payload = response.json()
    assert "detail" in payload
