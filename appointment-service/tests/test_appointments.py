from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

@patch("app.services.appointment_service.httpx.get")
@patch("app.services.appointment_service.publish_event_sync")
def test_book_cancel(mock_publish, mock_get):
    mock_get.return_value.status_code = 200
    book = client.post("/appointments", json={"patient_id":1,"doctor_id":1,"date_time":"2026-04-01T10:00:00Z"})
    assert book.status_code == 200
    cancel = client.delete(f"/appointments/{book.json()['id']}")
    assert cancel.status_code == 200
