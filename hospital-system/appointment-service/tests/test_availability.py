from datetime import datetime

from app.utils.availability import fits_doctor_availability


def test_fits_availability():
    slots = [{"weekday": 0, "start": "09:00", "end": "17:00"}]
    start = datetime(2026, 4, 20, 10, 30)  # Monday
    end = datetime(2026, 4, 20, 11, 0)
    assert fits_doctor_availability(start, end, slots) is True


def test_outside_availability():
    slots = [{"weekday": 0, "start": "09:00", "end": "10:00"}]
    start = datetime(2026, 4, 20, 10, 30)
    end = datetime(2026, 4, 20, 11, 0)
    assert fits_doctor_availability(start, end, slots) is False
