from __future__ import annotations

from datetime import datetime
from typing import Any


def _to_minutes(hhmm: str) -> int:
    hour, minute = hhmm.split(":")
    return int(hour) * 60 + int(minute)


def fits_doctor_availability(start: datetime, end: datetime, slots: list[dict[str, Any]]) -> bool:
    if start.date() != end.date():
        return False

    weekday = start.weekday()
    start_m = start.hour * 60 + start.minute
    end_m = end.hour * 60 + end.minute
    if end_m <= start_m:
        return False

    for raw in slots:
        try:
            if int(raw.get("weekday", -1)) != weekday:
                continue
            sm = _to_minutes(str(raw["start"]))
            em = _to_minutes(str(raw["end"]))
        except (KeyError, ValueError, TypeError):
            continue
        if sm <= start_m and end_m <= em:
            return True
    return False
