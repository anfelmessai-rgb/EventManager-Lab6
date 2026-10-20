from datetime import date
import pytest


@pytest.fixture
def sample_event_dict():
    """Returns a clean dictionary representing a valid event payload."""
    return {
        "title": "DevOps Hackathon",
        "location": "Constantine",
        "capacity": 150,
        "date": date.today()
    }


@pytest.fixture
def sample_participant_dict():
    """Returns a clean dictionary representing a valid participant payload."""
    return {
        "name": "Anfel Messai",
        "email": "anfel@example.com"
    }


@pytest.fixture
def mock_event_store():
    """State & Teardown: Initializes an in-memory list and clears it on teardown."""
    store = []
    yield store
    store.clear()


@pytest.fixture
def prepopulated_event_store(mock_event_store):
    """Chained Fixture: Requests mock_event_store and pre-populates 3 sample events."""
    mock_event_store.extend([
        {"id": 1, "title": "Cybersecurity Workshop", "location": "Constantine", "capacity": 50},
        {"id": 2, "title": "AI Summit", "location": "Algiers", "capacity": 300},
        {"id": 3, "title": "DevOps Bootcamp", "location": "constantine", "capacity": 100},
    ])
    return mock_event_store


@pytest.fixture(autouse=True)
def global_environment_logger():
    """Autouse Fixture: Automatically runs before and after every test function."""
    print("\n[TEST SETUP] Starting test execution...")
    yield
    print("\n[TEST TEARDOWN] Test execution finished.")