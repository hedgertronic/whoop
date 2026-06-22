"""Shared fixtures for the WHOOP client test suite.

All values here are synthetic and fabricated. No real WHOOP accounts, tokens,
emails, or biometric data appear anywhere. Every test runs fully offline; the
network is never touched.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from whoop import WhoopClient

CLIENT_ID = "test-client-id"
CLIENT_SECRET = "test-client-secret"  # noqa: S105 (synthetic, not a real secret)
REDIRECT_URI = "https://example.test/callback"

# A synthetic token shaped like an authlib OAuth2 token. Never a real token.
SYNTHETIC_TOKEN: dict[str, Any] = {
    "access_token": "synthetic-access-token",
    "refresh_token": "synthetic-refresh-token",
    "token_type": "bearer",
    "expires_at": 9999999999,
    "scope": "read:profile offline",
}


class FakeResponse:
    """Minimal stand-in for a requests Response object."""

    def __init__(self, payload: Any):
        self._payload = payload

    def raise_for_status(self) -> None:
        """No-op; the real method would raise on a 4xx/5xx status."""

    def json(self) -> Any:
        return self._payload


@pytest.fixture
def unauth_client() -> WhoopClient:
    """A client with no token (authorization flow not yet run)."""
    return WhoopClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)


@pytest.fixture
def client() -> WhoopClient:
    """An authenticated client carrying a synthetic token, no network used."""
    return WhoopClient(
        CLIENT_ID,
        CLIENT_SECRET,
        REDIRECT_URI,
        token=dict(SYNTHETIC_TOKEN),
    )


@pytest.fixture
def patched_request(client: WhoopClient):
    """Patch the session's `request` and let a test queue fake JSON payloads.

    Returns a callable that takes one or more payloads; each becomes the `.json()`
    of a successive `session.request` call, and returns the underlying mock so tests
    can assert on the URL and params passed.
    """
    mock = MagicMock(name="session.request")
    client.session.request = mock

    def queue(*payloads: Any):
        mock.side_effect = [FakeResponse(p) for p in payloads]
        return mock

    return queue


# --- Synthetic v2 fixture shapes (fabricated values, accurate keys) ----------
# v2 detail: cycle & recovery use INTEGER ids; sleep & workout use UUID strings.

PROFILE = {
    "user_id": 12345,
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
}

BODY = {
    "height_meter": 1.8,
    "weight_kilogram": 80.0,
    "max_heart_rate": 190,
}

CYCLE = {
    "id": 111,
    "user_id": 12345,
    "created_at": "2026-04-24T11:25:44.774Z",
    "updated_at": "2026-04-24T14:25:44.774Z",
    "start": "2026-04-24T02:25:44.774Z",
    "end": "2026-04-24T10:25:44.774Z",
    "timezone_offset": "-05:00",
    "score_state": "SCORED",
    "score": {
        "strain": 5.0,
        "kilojoule": 8000.0,
        "average_heart_rate": 60,
        "max_heart_rate": 140,
    },
}

SLEEP_UUID = "5c060dd1-975d-4544-880c-3def81bdfb0d"
WORKOUT_UUID = "a1b2c3d4-0000-4444-8888-1234567890ab"

ACTIVITY_MAPPING = {
    "v2_activity_id": SLEEP_UUID,
}

RECOVERY = {
    "cycle_id": 111,
    "sleep_id": SLEEP_UUID,
    "user_id": 12345,
    "score_state": "SCORED",
    "score": {
        "user_calibrating": False,
        "recovery_score": 50,
        "resting_heart_rate": 60,
        "hrv_rmssd_milli": 30.0,
        "spo2_percentage": 95.0,
        "skin_temp_celsius": 33.0,
    },
}

SLEEP = {
    "id": SLEEP_UUID,
    "user_id": 12345,
    "nap": False,
    "score_state": "SCORED",
    "score": {
        "stage_summary": {},
        "sleep_needed": {},
        "respiratory_rate": 16.0,
        "sleep_performance_percentage": 90,
        "sleep_consistency_percentage": 85,
        "sleep_efficiency_percentage": 90.0,
    },
}

SLEEP_STREAM = {
    "stream": [
        {
            "timestamp": "2026-04-24T02:25:44Z",
            "hr": 55,
            "is_sleeping": True,
        }
    ],
    "algorithm_version": "v1",
}

WORKOUT = {
    "id": WORKOUT_UUID,
    "user_id": 12345,
    "score_state": "SCORED",
    "score": {
        "strain": 8.0,
        "average_heart_rate": 120,
        "max_heart_rate": 150,
        "kilojoule": 1500.0,
    },
}


def envelope(item: Any, next_token: str | None = None) -> dict[str, Any]:
    """Wrap one record in a collection-response envelope."""
    return {"records": [item], "next_token": next_token}
