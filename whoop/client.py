"""WHOOP API client and read-only data endpoints.

`WhoopClient` extends `WhoopAuth` with the WHOOP data endpoints (profile, body
measurement, cycles, recovery, sleep, workouts). See the top-level `whoop`
package docstring for usage examples.

Attributes:
    REQUEST_URL (str): Base URL for v2 data requests.
"""

from __future__ import annotations

from datetime import UTC, datetime, time, timedelta
from typing import Any

from whoop.auth import WhoopAuth

REQUEST_URL = "https://api.prod.whoop.com/developer"


class WhoopClient(WhoopAuth):
    """Make read-only requests to the WHOOP v2 data API.

    Extends `WhoopAuth` with the WHOOP data endpoints. Construct and authenticate
    via `WhoopAuth` (see that class and the package docstring), then call the
    `get_*` methods. Collection endpoints accept ISO date strings and default to a
    trailing seven-day window.

    Raises:
        ValueError: If `start_date` is after `end_date`.
    """

    def __enter__(self) -> WhoopClient:
        """Enter a context manager.

        Returns:
            WhoopClient: A WHOOP client with an active OAuth2Session.
        """
        return self

    def __exit__(self, *_: object) -> None:
        """Exit a context manager by closing the OAuth2 session.

        Args:
            _ (Any): Exception arguments passed when closing context manager.
        """
        self.close()

    ####################################################################################
    # API ENDPOINTS

    def get_activity_mapping(self, activity_v1_id: int) -> dict[str, Any]:
        """Make request to Get V2 UUID for V1 Activity ID endpoint.

        Lookup the V2 UUID for a legacy V1 activity ID. This is useful when
        migrating stored sleep or workout IDs from pre-v2 integrations.

        Returns:
            dict[str, Any]: Response JSON data loaded into an object. Example:
                {
                    "v2_activity_id": "ecfc6a15-4661-442f-a9a4-f160dd7afae8"
                }
        """
        return self._make_request(
            method="GET", url_slug=f"v1/activity-mapping/{activity_v1_id}"
        )

    def get_profile(self) -> dict[str, Any]:
        """Make request to Get Profile endpoint.

        Get the user's basic profile.

        Returns:
            dict[str, Any]: Response JSON data loaded into an object. Example:
                {
                    "user_id": 10129,
                    "email": "jsmith123@whoop.com",
                    "first_name": "John",
                    "last_name": "Smith"
                }
        """
        return self._make_request(method="GET", url_slug="v2/user/profile/basic")

    def get_body_measurement(self) -> dict[str, Any]:
        """Make request to Get Body Measurement endpoint.

        Get the user's body measurements.

        Returns:
            dict[str, Any]: Response JSON data loaded into an object. Example:
                {
                    "height_meter": 1.8288,
                    "weight_kilogram": 90.7185,
                    "max_heart_rate": 200
                }
        """
        return self._make_request(method="GET", url_slug="v2/user/measurement/body")

    def get_cycle_by_id(self, cycle_id: int) -> dict[str, Any]:
        """Make request to Get Cycle By ID endpoint.

        Get the cycle for the specified ID.

        Returns:
            dict[str, Any]: Response JSON data loaded into an object. Example:
                {
                    "id": 93845,
                    "user_id": 10129,
                    "created_at": "2022-04-24T11:25:44.774Z",
                    "updated_at": "2022-04-24T14:25:44.774Z",
                    "start": "2022-04-24T02:25:44.774Z",
                    "end": "2022-04-24T10:25:44.774Z",
                    "timezone_offset": "-05:00",
                    "score_state": "SCORED",
                    "score": {
                        "strain": 5.2951527,
                        "kilojoule": 8288.297,
                        "average_heart_rate": 68,
                        "max_heart_rate": 141
                    }
                }
        """
        return self._make_request(method="GET", url_slug=f"v2/cycle/{cycle_id}")

    def get_cycle_collection(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """Make request to Get Cycle Collection endpoint.

        Get all physiological cycles for a user. Results are sorted by start time in
        descending order.

        Returns:
            list[dict[str, Any]]: Response JSON data loaded into an object. Example:
                [
                    {
                        "id": 93845,
                        "user_id": 10129,
                        "created_at": "2022-04-24T11:25:44.774Z",
                        "updated_at": "2022-04-24T14:25:44.774Z",
                        "start": "2022-04-24T02:25:44.774Z",
                        "end": "2022-04-24T10:25:44.774Z",
                        "timezone_offset": "-05:00",
                        "score_state": "SCORED",
                        "score": {
                            "strain": 5.2951527,
                            "kilojoule": 8288.297,
                            "average_heart_rate": 68,
                            "max_heart_rate": 141
                        }
                    },
                    ...
                ]
        """
        start, end = self._format_dates(start_date, end_date)

        return self._make_paginated_request(
            method="GET",
            url_slug="v2/cycle",
            params={"start": start, "end": end, "limit": 25},
        )

    def get_recovery_for_cycle(self, cycle_id: int) -> dict[str, Any]:
        """Make request to Get Recovery For Cycle endpoint.

        Get the recovery for a cycle.

        Returns:
            dict[str, Any]: Response JSON data loaded into an object. Example:
                {
                    "cycle_id": 93845,
                    "sleep_id": "ee9e6759-2cd8-4317-bc44-0a0bc59a6f1f",
                    "user_id": 10129,
                    "created_at": "2022-04-24T11:25:44.774Z",
                    "updated_at": "2022-04-24T14:25:44.774Z",
                    "score_state": "SCORED",
                    "score": {
                        "user_calibrating": False,
                        "recovery_score": 44,
                        "resting_heart_rate": 64,
                        "hrv_rmssd_milli": 31.813562,
                        "spo2_percentage": 95.6875,
                        "skin_temp_celsius": 33.7
                    }
                }
        """
        return self._make_request(
            method="GET", url_slug=f"v2/cycle/{cycle_id}/recovery"
        )

    def get_sleep_for_cycle(self, cycle_id: int) -> dict[str, Any]:
        """Make request to Get Sleep For Cycle endpoint.

        Get the sleep associated with the specified cycle ID.

        Returns:
            dict[str, Any]: Response JSON data loaded into an object. Example:
                {
                    "id": "5c060dd1-975d-4544-880c-3def81bdfb0d",
                    "cycle_id": 93845,
                    "user_id": 10129,
                    "nap": False,
                    "score_state": "SCORED",
                    "score": {
                        "stage_summary": {},
                        "sleep_needed": {},
                        "respiratory_rate": 16.11328125,
                        "sleep_performance_percentage": 98,
                        "sleep_consistency_percentage": 90,
                        "sleep_efficiency_percentage": 91.69533848
                    }
                }
        """
        return self._make_request(method="GET", url_slug=f"v2/cycle/{cycle_id}/sleep")

    def get_recovery_collection(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """Make request to Get Recovery Collection endpoint.

        Get all recoveries for a user. Results are sorted by start time of the related
        sleep in descending order.

        Returns:
            list[dict[str, Any]]: Response JSON data loaded into an object. Example:
                [
                    {
                        "cycle_id": 93845,
                        "sleep_id": "ee9e6759-2cd8-4317-bc44-0a0bc59a6f1f",
                        "user_id": 10129,
                        "created_at": "2022-04-24T11:25:44.774Z",
                        "updated_at": "2022-04-24T14:25:44.774Z",
                        "score_state": "SCORED",
                        "score": {
                            "user_calibrating": False,
                            "recovery_score": 44,
                            "resting_heart_rate": 64,
                            "hrv_rmssd_milli": 31.813562,
                            "spo2_percentage": 95.6875,
                            "skin_temp_celsius": 33.7
                        }
                    },
                    ...
                ]
        """
        start, end = self._format_dates(start_date, end_date)

        return self._make_paginated_request(
            method="GET",
            url_slug="v2/recovery",
            params={"start": start, "end": end, "limit": 25},
        )

    def get_sleep_by_id(self, sleep_id: str) -> dict[str, Any]:
        """Make request to Get Sleep By ID endpoint.

        Get the sleep for the specified ID.

        Returns:
            dict[str, Any]: Response JSON data loaded into an object. Example:
                {
                    "id": "5c060dd1-975d-4544-880c-3def81bdfb0d",
                    "user_id": 10129,
                    "created_at": "2022-04-24T11:25:44.774Z",
                    "updated_at": "2022-04-24T14:25:44.774Z",
                    "start": "2022-04-24T02:25:44.774Z",
                    "end": "2022-04-24T10:25:44.774Z",
                    "timezone_offset": "-05:00",
                    "nap": False,
                    "score_state": "SCORED",
                    "score": {
                        "stage_summary": {},
                        "sleep_needed": {},
                        "respiratory_rate": 16.11328125,
                        "sleep_performance_percentage": 98,
                        "sleep_consistency_percentage": 90,
                        "sleep_efficiency_percentage": 91.69533848
                    }
                }
        """
        return self._make_request(
            method="GET", url_slug=f"v2/activity/sleep/{sleep_id}"
        )

    def get_sleep_collection(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """Make request to Get Sleep Collection endpoint.

        Get all sleeps for a user. Results are sorted by start time in descending order.

        Returns:
            list[dict[str, Any]]: Response JSON data loaded into an object. Example:
                [
                    {
                        "id": "5c060dd1-975d-4544-880c-3def81bdfb0d",
                        "user_id": 10129,
                        "created_at": "2022-04-24T11:25:44.774Z",
                        "updated_at": "2022-04-24T14:25:44.774Z",
                        "start": "2022-04-24T02:25:44.774Z",
                        "end": "2022-04-24T10:25:44.774Z",
                        "timezone_offset": "-05:00",
                        "nap": False,
                        "score_state": "SCORED",
                        "score": {
                            "stage_summary": {},
                            "sleep_needed": {},
                            "respiratory_rate": 16.11328125,
                            "sleep_performance_percentage": 98,
                            "sleep_consistency_percentage": 90,
                            "sleep_efficiency_percentage": 91.69533848
                        }
                    },
                    ...
                ]
        """
        start, end = self._format_dates(start_date, end_date)

        return self._make_paginated_request(
            method="GET",
            url_slug="v2/activity/sleep",
            params={"start": start, "end": end, "limit": 25},
        )

    def get_sleep_stream(
        self,
        sleep_id: str,
        types: list[str] | tuple[str, ...] | None = None,
    ) -> dict[str, Any]:
        """Make request to Get Sleep Stream endpoint.

        Get raw signal stream data for the specified sleep ID. Pass
        ``types=["sleep_classification"]`` to request sleep-stage classification
        samples; other WHOOP-supported stream types include ``hr``, ``skin_temp``,
        ``board_temp``, ``battery_temp``, and ``charging_status``.

        Returns:
            dict[str, Any]: Response JSON data loaded into an object. Example:
                {
                    "stream": [
                        {
                            "timestamp": "2019-08-24T14:15:22Z",
                            "hr": 0,
                            "skin_temp": 0.0,
                            "board_temp": 0.0,
                            "battery_temp": 0.0,
                            "is_sleeping": True,
                            "is_charging": False
                        }
                    ],
                    "algorithm_version": "string"
                }
        """
        params = {"types": list(types)} if types is not None else None

        return self._make_request(
            method="GET",
            url_slug=f"v2/activity/sleep/{sleep_id}/stream",
            params=params,
        )

    def get_workout_by_id(self, workout_id: str) -> dict[str, Any]:
        """Make request to Get Workout By ID endpoint.

        Get the workout for the specified ID.

        Returns:
            dict[str, Any]: Response JSON data loaded into an object. Example:
                {
                    "id": "ecfc6a15-4661-442f-a9a4-f160dd7afae8",
                    "user_id": 9012,
                    "created_at": "2022-04-24T11:25:44.774Z",
                    "updated_at": "2022-04-24T14:25:44.774Z",
                    "start": "2022-04-24T02:25:44.774Z",
                    "end": "2022-04-24T10:25:44.774Z",
                    "timezone_offset": "-05:00",
                    "sport_id": 1,
                    "score_state": "SCORED",
                    "score": {
                        "strain": 8.2463,
                        "average_heart_rate": 123,
                        "max_heart_rate": 146,
                        "kilojoule": 1569.34033203125,
                        "percent_recorded": 100,
                        "distance_meter": 1772.77035916,
                        "altitude_gain_meter": 46.64384460449,
                        "altitude_change_meter": -0.781372010707855,
                        "zone_duration": {}
                    }
                }
        """
        return self._make_request(
            method="GET", url_slug=f"v2/activity/workout/{workout_id}"
        )

    def get_workout_collection(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """Make request to Get Workout Collection endpoint.

        Get all workouts for a user. Results are sorted by start time in descending
        order.

        Returns:
            list[dict[str, Any]]: Response JSON data loaded into an object. Example:
                [
                    {
                        "id": "ecfc6a15-4661-442f-a9a4-f160dd7afae8",
                        "user_id": 9012,
                        "created_at": "2022-04-24T11:25:44.774Z",
                        "updated_at": "2022-04-24T14:25:44.774Z",
                        "start": "2022-04-24T02:25:44.774Z",
                        "end": "2022-04-24T10:25:44.774Z",
                        "timezone_offset": "-05:00",
                        "sport_id": 1,
                        "score_state": "SCORED",
                        "score": {
                            "strain": 8.2463,
                            "average_heart_rate": 123,
                            "max_heart_rate": 146,
                            "kilojoule": 1569.34033203125,
                            "percent_recorded": 100,
                            "distance_meter": 1772.77035916,
                            "altitude_gain_meter": 46.64384460449,
                            "altitude_change_meter": -0.781372010707855,
                            "zone_duration": {}
                        }
                    },
                    ...
                ]
        """
        start, end = self._format_dates(start_date, end_date)

        return self._make_paginated_request(
            method="GET",
            url_slug="v2/activity/workout",
            params={"start": start, "end": end, "limit": 25},
        )

    ####################################################################################
    # API HELPER METHODS

    def _make_paginated_request(
        self, method: str, url_slug: str, **kwargs: Any
    ) -> list[dict[str, Any]]:
        params = kwargs.pop("params", {})
        response_data: list[dict[str, Any]] = []

        while True:
            response = self._make_request(
                method=method,
                url_slug=url_slug,
                params=params,
                **kwargs,
            )

            response_data += response["records"]

            if next_token := response["next_token"]:
                params["nextToken"] = next_token

            else:
                break

        return response_data

    def _make_request(
        self, method: str, url_slug: str, **kwargs: Any
    ) -> dict[str, Any]:
        response = self.session.request(
            method=method,
            url=f"{REQUEST_URL}/{url_slug}",
            **kwargs,
        )

        response.raise_for_status()

        data: dict[str, Any] = response.json()
        return data

    def _format_dates(
        self, start_date: str | None, end_date: str | None
    ) -> tuple[str, str]:
        # Date-only inputs are interpreted as whole UTC calendar days. Datetime
        # inputs are passed through so callers can request narrower windows.
        today = datetime.now(UTC).date()
        start = self._format_collection_bound(
            start_date,
            default=datetime.combine(today - timedelta(days=6), time.min),
            end_bound=False,
        )
        end = self._format_collection_bound(
            end_date,
            default=datetime.combine(today + timedelta(days=1), time.min),
            end_bound=True,
        )

        if start >= end:
            raise ValueError(f"Start date greater than end date: {start} > {end}")

        return start.isoformat() + "Z", end.isoformat() + "Z"

    @staticmethod
    def _format_collection_bound(
        value: str | None,
        *,
        default: datetime,
        end_bound: bool,
    ) -> datetime:
        if value is None:
            return default

        raw_value = f"{value[:-1]}+00:00" if value.endswith("Z") else value
        parsed = datetime.fromisoformat(raw_value)
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(UTC).replace(tzinfo=None)

        is_datetime = "T" in value or " " in value
        if is_datetime:
            return parsed

        if end_bound:
            return datetime.combine(parsed.date() + timedelta(days=1), time.min)
        return datetime.combine(parsed.date(), time.min)
