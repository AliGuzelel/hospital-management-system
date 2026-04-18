from unittest.mock import MagicMock

import pytest

from app.services.consumer import handle_message


@pytest.mark.asyncio
async def test_handle_appointment_created_logs():
    class CM:
        async def __aenter__(self):
            return None

        async def __aexit__(self, exc_type, exc, tb):
            return False

    message = MagicMock()
    message.body = b'{"event":"appointment_created","appointment_id":1,"patient_id":2,"doctor_id":3}'
    message.process = MagicMock(return_value=CM())

    await handle_message(message)
    message.process.assert_called_once()
