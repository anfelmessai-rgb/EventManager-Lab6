import datetime
from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.database import get_db
from app.main import app
from app.schemas import EventCreate, EventUpdate
from app.routers.events import (
    filter_events_by_location,
    filter_events_by_title,
    create_event,
    list_events,
    get_event,
    update_event,
    delete_event,
)


# ==========================================
# 1. Happy Path Tests
# ==========================================
def test_valid_event_instantiation(sample_event_dict):
    event = EventCreate(**sample_event_dict)
    assert event.title == sample_event_dict["title"]
    assert event.capacity == sample_event_dict["capacity"]
    assert event.location == sample_event_dict["location"]


def test_successful_filtering_using_prepopulated_store(prepopulated_event_store):
    filtered_by_loc = filter_events_by_location(prepopulated_event_store, "constantine")
    assert len(filtered_by_loc) == 2
    filtered_by_title = filter_events_by_title(prepopulated_event_store, "workshop")
    assert len(filtered_by_title) == 1
    assert filtered_by_title[0]["id"] == 1


# ==========================================
# 2. Boundary Value Tests
# ==========================================
def test_boundary_capacity_min(sample_event_dict):
    sample_event_dict["capacity"] = 1
    event = EventCreate(**sample_event_dict)
    assert event.capacity == 1


def test_boundary_capacity_max(sample_event_dict):
    sample_event_dict["capacity"] = 10000
    event = EventCreate(**sample_event_dict)
    assert event.capacity == 10000


def test_boundary_title_length_min(sample_event_dict):
    sample_event_dict["title"] = "Sec"
    event = EventCreate(**sample_event_dict)
    assert event.title == "Sec"


# ==========================================
# 3. Negative Tests
# ==========================================
def test_negative_short_title_raises_validation_error(sample_event_dict):
    sample_event_dict["title"] = "AB"
    with pytest.raises(ValidationError):
        EventCreate(**sample_event_dict)


def test_negative_zero_capacity_raises_validation_error(sample_event_dict):
    sample_event_dict["capacity"] = 0
    with pytest.raises(ValidationError):
        EventCreate(**sample_event_dict)


def test_negative_negative_capacity_raises_validation_error(sample_event_dict):
    sample_event_dict["capacity"] = -10
    with pytest.raises(ValidationError):
        EventCreate(**sample_event_dict)


def test_negative_exceeded_capacity_raises_validation_error(sample_event_dict):
    sample_event_dict["capacity"] = 10001
    with pytest.raises(ValidationError):
        EventCreate(**sample_event_dict)


# ==========================================
# 4. Mock Endpoint & Database Tests (100% Coverage)
# ==========================================
def test_create_event_endpoint_mock(sample_event_dict):
    mock_db = MagicMock()
    event = EventCreate(**sample_event_dict)
    res = create_event(event, mock_db)
    assert mock_db.add.called
    assert mock_db.commit.called


def test_create_event_past_date_raises_http_error():
    mock_db = MagicMock()
    event = EventCreate(
        title="Old Event",
        location="Algiers",
        capacity=100,
        date=datetime.date(2000, 1, 1),
    )
    with pytest.raises(HTTPException):
        create_event(event, mock_db)


def test_list_events_endpoint_mock():
    mock_db = MagicMock()
    mock_query = mock_db.query.return_value
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value.all.return_value = []
    res = list_events(title="DevOps", location="Constantine", db=mock_db)
    assert res == []


def test_get_event_endpoint_mock():
    mock_db = MagicMock()
    mock_event = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_event
    res = get_event(1, mock_db)
    assert res == mock_event


def test_get_event_not_found_mock():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException):
        get_event(999, mock_db)


def test_update_event_endpoint_mock():
    mock_db = MagicMock()
    mock_event = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_event
    res = update_event(1, EventUpdate(title="Updated Title"), mock_db)
    assert mock_db.commit.called


def test_update_event_not_found_mock():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException):
        update_event(999, EventUpdate(title="Title"), mock_db)


def test_update_event_past_date_raises_http_error():
    mock_db = MagicMock()
    mock_event = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_event
    with pytest.raises(HTTPException):
        update_event(1, EventUpdate(date=datetime.date(2000, 1, 1)), mock_db)


def test_delete_event_endpoint_mock():
    mock_db = MagicMock()
    mock_event = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_event
    delete_event(1, mock_db)
    assert mock_db.delete.called


def test_delete_event_not_found_mock():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException):
        delete_event(999, mock_db)


def test_get_db_coverage():
    db_gen = get_db()
    db = next(db_gen)
    assert db is not None
    try:
        next(db_gen)
    except StopIteration:
        pass


def test_main_root_endpoint_coverage():
    for route in app.routes:
        if getattr(route, "path", None) == "/":
            func = getattr(route, "endpoint", None)
            if func and callable(func):
                func()