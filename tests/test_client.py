"""Tests for whoop.client: data endpoints, pagination, date formatting.

Every endpoint funnels through `_make_request`, which is exercised for real by
patching `session.request` to return a fake response. Synthetic fixtures only.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from whoop import REQUEST_URL, WhoopClient

from . import conftest as fx


def _called_url(mock) -> str:
    return mock.call_args.kwargs["url"]


def _called_params(mock) -> dict:
    return mock.call_args.kwargs.get("params", {})


# --- Single-record endpoints -------------------------------------------------


def test_get_profile(client: WhoopClient, patched_request):
    mock = patched_request(fx.PROFILE)
    result = client.get_profile()

    assert result == fx.PROFILE
    assert _called_url(mock) == f"{REQUEST_URL}/v2/user/profile/basic"


def test_get_body_measurement(client: WhoopClient, patched_request):
    mock = patched_request(fx.BODY)
    result = client.get_body_measurement()

    assert result == fx.BODY
    assert _called_url(mock) == f"{REQUEST_URL}/v2/user/measurement/body"


def test_get_cycle_by_id_integer(client: WhoopClient, patched_request):
    mock = patched_request(fx.CYCLE)
    result = client.get_cycle_by_id(111)

    assert result == fx.CYCLE
    assert _called_url(mock) == f"{REQUEST_URL}/v2/cycle/111"


def test_get_recovery_for_cycle(client: WhoopClient, patched_request):
    mock = patched_request(fx.RECOVERY)
    result = client.get_recovery_for_cycle(111)

    assert result == fx.RECOVERY
    assert _called_url(mock) == f"{REQUEST_URL}/v2/cycle/111/recovery"


def test_get_sleep_by_id_uuid(client: WhoopClient, patched_request):
    mock = patched_request(fx.SLEEP)
    result = client.get_sleep_by_id(fx.SLEEP_UUID)

    assert result == fx.SLEEP
    assert _called_url(mock) == f"{REQUEST_URL}/v2/activity/sleep/{fx.SLEEP_UUID}"


def test_get_workout_by_id_uuid(client: WhoopClient, patched_request):
    mock = patched_request(fx.WORKOUT)
    result = client.get_workout_by_id(fx.WORKOUT_UUID)

    assert result == fx.WORKOUT
    assert _called_url(mock) == f"{REQUEST_URL}/v2/activity/workout/{fx.WORKOUT_UUID}"


# --- Collection endpoints (single page) --------------------------------------


@pytest.mark.parametrize(
    ("method_name", "fixture", "slug"),
    [
        ("get_cycle_collection", fx.CYCLE, "v2/cycle"),
        ("get_recovery_collection", fx.RECOVERY, "v2/recovery"),
        ("get_sleep_collection", fx.SLEEP, "v2/activity/sleep"),
        ("get_workout_collection", fx.WORKOUT, "v2/activity/workout"),
    ],
)
def test_collection_single_page(
    client: WhoopClient, patched_request, method_name, fixture, slug
):
    mock = patched_request(fx.envelope(fixture, next_token=None))
    result = getattr(client, method_name)()

    assert result == [fixture]
    assert _called_url(mock) == f"{REQUEST_URL}/{slug}"
    params = _called_params(mock)
    assert params["limit"] == 25
    assert "start" in params and "end" in params
    # Single page: never advanced the page token.
    assert mock.call_count == 1
    assert "nextToken" not in params


# --- Pagination (multi-page loop) --------------------------------------------


def test_collection_follows_next_token(client: WhoopClient, patched_request):
    first = fx.envelope(fx.CYCLE, next_token="TOKEN")  # noqa: S106
    second = fx.envelope({**fx.CYCLE, "id": 222}, next_token=None)
    mock = patched_request(first, second)

    result = client.get_cycle_collection()

    assert [c["id"] for c in result] == [111, 222]
    assert mock.call_count == 2
    # Second call carried the page token from the first response.
    second_params = mock.call_args_list[1].kwargs["params"]
    assert second_params["nextToken"] == "TOKEN"


# --- _format_dates -----------------------------------------------------------


def test_format_dates_explicit(client: WhoopClient):
    start, end = client._format_dates("2026-04-24", "2026-04-24")

    # Half-open window: start inclusive at midnight, end exclusive at next midnight.
    assert start == "2026-04-24T00:00:00Z"
    assert end == "2026-04-25T00:00:00Z"


def test_format_dates_defaults_live(client: WhoopClient):
    # No freezegun dependency: compute the expected window from the same clock
    # the implementation reads (UTC), so the test never goes stale or flakes near
    # midnight in a non-UTC runner.
    today = datetime.now(timezone.utc).date()
    start, end = client._format_dates(None, None)

    assert start == f"{(today - timedelta(days=6)).isoformat()}T00:00:00Z"
    assert end == f"{(today + timedelta(days=1)).isoformat()}T00:00:00Z"


def test_format_dates_start_after_end_raises(client: WhoopClient):
    with pytest.raises(ValueError, match="Start date greater than end date"):
        client._format_dates("2026-04-25", "2026-04-24")


def test_collection_passes_explicit_dates_through(client: WhoopClient, patched_request):
    mock = patched_request(fx.envelope(fx.SLEEP, next_token=None))
    client.get_sleep_collection(start_date="2026-04-24", end_date="2026-04-24")

    params = _called_params(mock)
    assert params["start"] == "2026-04-24T00:00:00Z"
    assert params["end"] == "2026-04-25T00:00:00Z"


# --- _make_request error propagation -----------------------------------------


def test_make_request_propagates_raise_for_status(client: WhoopClient):
    from unittest.mock import MagicMock

    bad = MagicMock()
    bad.raise_for_status.side_effect = RuntimeError("HTTP 401")
    client.session.request = MagicMock(return_value=bad)

    with pytest.raises(RuntimeError, match="HTTP 401"):
        client.get_profile()
