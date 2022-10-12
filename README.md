# WHOOP for Python <!-- omit in toc -->

Tools for acquiring and analyzing Whoop API data.

WHOOP is a wearable strap for monitoring sleep, activity, and workouts. Learn more about WHOOP at https://www.whoop.com.

WHOOP API documentation can be found at https://developer.whoop.com/api.

## Contents <!-- omit in toc -->

- [Installation](#installation)
- [Getting Started](#getting-started)
- [API Requests](#api-requests)
  - [Get Profile](#get-profile)
  - [Get Body Measurement](#get-body-measurement)
  - [Get Cycle By ID](#get-cycle-by-id)
  - [Get Cycle Collection](#get-cycle-collection)
  - [Get Recovery For Cycle](#get-recovery-for-cycle)
  - [Get Recovery Collection](#get-recovery-collection)
  - [Get Sleep By ID](#get-sleep-by-id)
  - [Get Sleep Collection](#get-sleep-collection)
  - [Get Workout By ID](#get-workout-by-id)
  - [Get Workout Collection](#get-workout-collection)

## Installation

The `whoop` module can be installed via pip:

`pip install whoop`

## Getting Started

In order to use the WHOOP client, you must have your WHOOP email and password.

It is best practice to store these values in a `.env` file:

```bash
# WHOOP credentials
USERNAME="<USERNAME>"
PASSWORD="<PASSWORD>"
```

You can use [`python-dotenv`](https://github.com/theskumar/python-dotenv) to load the enviroment variables for use in code:

```python
import os
from dotenv import load_dotenv

load_dotenv()

un = os.getenv("USERNAME") or ""
pw = os.getenv("PASSWORD") or ""
```

Once the environment variables are loaded, a `WhoopClient` object can be created:

```python
from whoop import WhoopClient

# Using a traditional constructor
client = WhoopClient(username, password)
...

# Using a context manager
with WhoopClient(username, password) as client:
    ...
```

The WHOOP client will authenticate the client upon construction by default. This involves fetching an access token from the API. If you don't want this request to happen automatically, pass `authenticate=False` into the object constructor. In order to make other requests, you will need to manually call the `authenticate()` method so that the other requests have the proper authorization headers:

```python
client = WhoopClient(
    client_id, client_secret, refresh_token, authenticate=False
)

client.authenticate()
...
```

## API Requests

There are ten different API requests that `WhoopClient` can make. Full WHOOP API documentation can be found on [WHOOP's website](https://developer.whoop.com/api).

### Get Profile

Get the user's basic profile.

**Method**: `get_profile()`

**Payload**: None

**Example Response**:

```python
{
    "user_id": 10129,
    "email": "jsmith123@whoop.com",
    "first_name": "John",
    "last_name": "Smith"
}
```

### Get Body Measurement

Get the user's body measurements.

**Method**: `get_body_measurement()`

**Payload**: None

**Example Response**:

```python
{
    "height_meter": 1.8288,
    "weight_kilogram": 90.7185,
    "max_heart_rate": 200
}
```

### Get Cycle By ID

Get the cycle for the specified ID.

**Method**: `get_cycle_by_id(cycle_id: str)`

**Payload**:

- `cycle_id`: ID of the cycle to retrieve. Passed into the request path.

**Example Response**:

```python
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
```

### Get Cycle Collection

Get all physiological cycles for a user. Results are sorted by start time in descending order.

**Method**: `get_cycle_collection(start_date: str = None, end_date: str = <today's date>)`

**Payload**:

- `startDate`: The earliest date for which to get data, pulled from the `start_date` parameter. Returns cycles that occurred after or during (inclusive) this time. Expected in ISO 8601 format (YYYY-MM-DD HH:MM:SS). Defaults to no start date.
- `endDate`: The latest date for which to get data, pulled from the `end_date` parameter. Returns cycles that intersect this time or ended before (exclusive) this time. Expected in ISO 8601 format (YYYY-MM-DD HH:MM:SS). Defaults to today's date.

**Example Response**:

```python
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
```

### Get Recovery For Cycle

Get the recovery for a cycle

**Method**: `get_recovery_for_cycle(cycle_id: str)`

**Payload**:

- `cycle_id`: ID of the cycle to retrieve. Passed into the request path.

**Example Response**:

```python
 {
    "cycle_id": 93845,
    "sleep_id": 10235,
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
```

### Get Recovery Collection

Get all recoveries for a user. Results are sorted by start time of the related sleep in descending order.

**Method**: `get_recovery_collection(start_date: str = None, end_date: str = <today's date>)`

**Payload**:

- `startDate`: The earliest date for which to get data, pulled from the `start_date` parameter. Returns cycles that occurred after or during (inclusive) this time. Expected in ISO 8601 format (YYYY-MM-DD HH:MM:SS). Defaults to no start date.
- `endDate`: The latest date for which to get data, pulled from the `end_date` parameter. Returns cycles that intersect this time or ended before (exclusive) this time. Expected in ISO 8601 format (YYYY-MM-DD HH:MM:SS). Defaults to today's date.

**Example Response**:

```python
[
    {
        "cycle_id": 93845,
        "sleep_id": 10235,
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
```

### Get Sleep By ID

Get the sleep for the specified ID.

**Method**: `get_sleep_by_id(sleep_id: str)`

**Payload**:

- `sleep`: ID of the sleep to retrieve. Passed into the request path.

**Example Response**:

```python
{
    "id": 93845,
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
```

### Get Sleep Collection

Get all sleeps for a user. Results are sorted by start time in descending order.

**Method**: `get_sleep_collection(start_date: str = None, end_date: str = <today's date>)`

**Payload**:

- `startDate`: The earliest date for which to get data, pulled from the `start_date` parameter. Returns sleeps that occurred after or during (inclusive) this time. Expected in ISO 8601 format (YYYY-MM-DD HH:MM:SS). Defaults to no start date.
- `endDate`: The latest date for which to get data, pulled from the `end_date` parameter. Returns sleeps that intersect this time or ended before (exclusive) this time. Expected in ISO 8601 format (YYYY-MM-DD HH:MM:SS). Defaults to today's date.

**Example Response**:

```python
[
    {
        "id": 93845,
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
```

### Get Workout By ID

Get the workout for the specified ID.

**Method**: `get_workout_by_id(workout_id: str)`

**Payload**:

- `workout_id`: ID of the workout to retrieve. Passed into the request path.

**Example Response**:

```python
{
    "id": 1043,
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
```

### Get Workout Collection

Get all workouts for a user. Results are sorted by start time in descending order.

**Method**: `get_workout_collection(start_date: str = None, end_date: str = <today's date>)`

**Payload**:

- `startDate`: The earliest date for which to get data, pulled from the `start_date` parameter. Returns workouts that occurred after or during (inclusive) this time. Expected in ISO 8601 format (YYYY-MM-DD HH:MM:SS). Defaults to no start date.
- `endDate`: The latest date for which to get data, pulled from the `end_date` parameter. Returns workouts that intersect this time or ended before (exclusive) this time. Expected in ISO 8601 format (YYYY-MM-DD HH:MM:SS). Defaults to today's date.

**Example Response**:

```python
[
    {
        "id": 1043,
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
```
