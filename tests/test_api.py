import copy
from fastapi.testclient import TestClient
import pytest

from src import app as app_module

client = TestClient(app_module.app)

# Keep a baseline copy to restore between tests
BASELINE_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Restore baseline before each test to keep tests isolated
    app_module.activities = copy.deepcopy(BASELINE_ACTIVITIES)
    yield


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)


def test_signup_and_reflects_in_activity():
    activity = "Chess Club"
    email = "newperson@example.com"

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body["message"]

    # Check activity now contains the new participant
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert email in data[activity]["participants"]


def test_signup_already_signed_up_returns_400():
    activity = "Chess Club"
    email = "already@taken.com"

    # First signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200

    # Second signup should fail
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 400


def test_unregister_existing_participant():
    activity = "Chess Club"
    # Use an existing participant from baseline
    email = "michael@mergington.edu"

    resp = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200
    body = resp.json()
    assert "Removed" in body["message"]

    # Verify participant removed
    resp = client.get("/activities")
    data = resp.json()
    assert email not in data[activity]["participants"]


def test_unregister_nonexistent_returns_404():
    activity = "Chess Club"
    email = "not@here.com"

    resp = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 404
