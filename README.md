# WHOOP for Python <!-- omit in toc -->

Tools for acquiring and analyzing Whoop API data.

WHOOP is a wearable strap for monitoring sleep, activity, and workouts. Learn more about WHOOP at https://www.whoop.com.

WHOOP API documentation can be found at https://developer.whoop.com/api.

## Contents <!-- omit in toc -->

- [Installation](#installation)
- [Getting Started](#getting-started)
- [Migration From Pre-1.0](#migration-from-pre-10)
- [API Requests](#api-requests)
  - [Get Activity Mapping](#get-activity-mapping)
  - [Get Profile](#get-profile)
  - [Get Body Measurement](#get-body-measurement)
  - [Get Cycle By ID](#get-cycle-by-id)
  - [Get Cycle Collection](#get-cycle-collection)
  - [Get Recovery For Cycle](#get-recovery-for-cycle)
  - [Get Sleep For Cycle](#get-sleep-for-cycle)
  - [Get Recovery Collection](#get-recovery-collection)
  - [Get Sleep By ID](#get-sleep-by-id)
  - [Get Sleep Collection](#get-sleep-collection)
  - [Get Sleep Stream](#get-sleep-stream)
  - [Get Workout By ID](#get-workout-by-id)
  - [Get Workout Collection](#get-workout-collection)
- [Usage With DataFrame](#usage-with-dataframe)

## Installation

The `whoop` module can be installed via pip:

`pip install whoop`

## Getting Started

This client uses WHOOP's official OAuth2 authorization-code flow against the WHOOP v2 API.

### Register an app

Before you can authenticate, you must register an application in the [WHOOP Developer Dashboard](https://developer.whoop.com). Registration gives you a `client_id` and `client_secret`, and lets you register one or more redirect URIs.

The redirect URI must use an `https://` or `whoop://` scheme — plain `http://localhost` is **not** accepted. A value like `https://localhost:8080/whoop/callback` works for local development.

It is best practice to store these values in a `.env` file:

```bash
# WHOOP app credentials
CLIENT_ID="<CLIENT_ID>"
CLIENT_SECRET="<CLIENT_SECRET>"
REDIRECT_URI="<REDIRECT_URI>"
```

You can use [`python-dotenv`](https://github.com/theskumar/python-dotenv) to load the environment variables for use in code:

```python
import os
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("CLIENT_ID") or ""
client_secret = os.getenv("CLIENT_SECRET") or ""
redirect_uri = os.getenv("REDIRECT_URI") or ""
```

### Authorize a new client

Constructing a `WhoopClient` does not make any network requests. To authorize a brand-new client, build the authorization URL, send the user there to grant access, then exchange the authorization code returned on the redirect:

```python
from whoop import WhoopClient

client = WhoopClient(client_id, client_secret, redirect_uri)

# Send the user to this URL to grant access. After they consent, WHOOP redirects
# them to your redirect_uri with an authorization code in the query string.
url, state = client.authorization_url()
print(url)

# Exchange the code for a token. Pass either the full redirect URL the user
# landed on, or the bare code extracted from it.
client.fetch_token(authorization_response=input("Redirect URL: "))
# client.fetch_token(code="<authorization code>")
```

### Reuse a saved token (headless)

The constructor also accepts a previously fetched `token`, which skips the interactive consent flow entirely. The current token is available via the `.token` property:

```python
saved_token = client.token  # persist this somewhere

# Later, in a headless process:
client = WhoopClient(client_id, client_secret, token=saved_token)
```

Tokens auto-refresh as long as you request the `offline` scope (included by default — see [Scopes](#scopes)). To persist rotated tokens, pass an `on_token_refresh` callback that is invoked with the new token whenever a refresh occurs:

```python
def save_token(token):
    ...  # write token to disk, a database, etc.

client = WhoopClient(
    client_id,
    client_secret,
    token=saved_token,
    on_token_refresh=save_token,
)
```

You can check whether a client holds a token with `client.is_authenticated()`. The client also works as a context manager, which closes the underlying session on exit:

```python
with WhoopClient(client_id, client_secret, token=saved_token) as client:
    ...
```

### Scopes

By default the client requests every read scope plus `offline` (required for token refresh). Pass a custom `scopes` list to narrow the request:

```python
client = WhoopClient(
    client_id, client_secret, redirect_uri, scopes=["read:sleep", "offline"]
)
```

The default scopes are:

- `read:profile`
- `read:body_measurement`
- `read:cycles`
- `read:recovery`
- `read:sleep`
- `read:workout`
- `offline`

Note WHOOP's mixed pluralization: `read:cycles` is plural while `read:workout` is singular.

## Migration From Pre-1.0

Version 1.0 removes the legacy username/password flow and uses WHOOP's official OAuth2 authorization-code flow instead.

- Replace `WhoopClient(username, password)` with `WhoopClient(client_id, client_secret, redirect_uri)`.
- Replace eager constructor authentication and `authenticate()` calls with `authorization_url()` plus `fetch_token(...)`.
- Persist `client.token` after authorization and pass it back with `WhoopClient(client_id, client_secret, token=saved_token)` for headless use.
- Use `get_activity_mapping(...)` to look up a v2 UUID for a stored v1 activity ID.
- Request the default `offline` scope, or include it in custom scopes, if you need refresh-token based auto-refresh.

## API Requests

There are thirteen different API requests that `WhoopClient` can make. Full WHOOP API documentation can be found on [WHOOP's website](https://developer.whoop.com/api).

### Get Activity Mapping

Look up the V2 UUID for a legacy V1 activity ID.

**Method**: `get_activity_mapping(activity_v1_id: int)`

**Payload**:

- `activityV1Id`: Legacy V1 activity ID. Passed into the request path.

**Example Response**:

```python
{
    "v2_activity_id": "ecfc6a15-4661-442f-a9a4-f160dd7afae8"
}
```

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

**Method**: `get_cycle_by_id(cycle_id: int)`

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

**Method**: `get_cycle_collection(start_date: str | None = None, end_date: str | None = None)`

**Payload**:

- `start`: The earliest time for which to get data, derived from the `start_date` parameter. Returns cycles that occurred after or during (inclusive) this time. Accepts `YYYY-MM-DD` date strings or ISO datetimes. Date-only values cover whole UTC days. Defaults to six days before today (a trailing seven-day window).
- `end`: The latest time for which to get data, derived from the `end_date` parameter. Returns cycles that intersect this time or ended before (exclusive) this time. Accepts `YYYY-MM-DD` date strings or ISO datetimes. Date-only values cover whole UTC days. Defaults to today's date.

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

**Method**: `get_recovery_for_cycle(cycle_id: int)`

**Payload**:

- `cycle_id`: ID of the cycle to retrieve. Passed into the request path.

**Example Response**:

```python
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
```

### Get Sleep For Cycle

Get the sleep associated with the specified cycle ID.

**Method**: `get_sleep_for_cycle(cycle_id: int)`

**Payload**:

- `cycle_id`: ID of the cycle to retrieve sleep for. Passed into the request path.

**Example Response**:

```python
{
    "id": "5c060dd1-975d-4544-880c-3def81bdfb0d",
    "cycle_id": 93845,
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

### Get Recovery Collection

Get all recoveries for a user. Results are sorted by start time of the related sleep in descending order.

**Method**: `get_recovery_collection(start_date: str | None = None, end_date: str | None = None)`

**Payload**:

- `start`: The earliest time for which to get data, derived from the `start_date` parameter. Returns recoveries that occurred after or during (inclusive) this time. Accepts `YYYY-MM-DD` date strings or ISO datetimes. Date-only values cover whole UTC days. Defaults to six days before today (a trailing seven-day window).
- `end`: The latest time for which to get data, derived from the `end_date` parameter. Returns recoveries that intersect this time or ended before (exclusive) this time. Accepts `YYYY-MM-DD` date strings or ISO datetimes. Date-only values cover whole UTC days. Defaults to today's date.

**Example Response**:

```python
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
```

### Get Sleep By ID

Get the sleep for the specified ID.

**Method**: `get_sleep_by_id(sleep_id: str)`

**Payload**:

- `sleep`: ID of the sleep to retrieve. Passed into the request path.

**Example Response**:

```python
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
```

### Get Sleep Collection

Get all sleeps for a user. Results are sorted by start time in descending order.

**Method**: `get_sleep_collection(start_date: str | None = None, end_date: str | None = None)`

**Payload**:

- `start`: The earliest time for which to get data, derived from the `start_date` parameter. Returns sleeps that occurred after or during (inclusive) this time. Accepts `YYYY-MM-DD` date strings or ISO datetimes. Date-only values cover whole UTC days. Defaults to six days before today (a trailing seven-day window).
- `end`: The latest time for which to get data, derived from the `end_date` parameter. Returns sleeps that intersect this time or ended before (exclusive) this time. Accepts `YYYY-MM-DD` date strings or ISO datetimes. Date-only values cover whole UTC days. Defaults to today's date.

**Example Response**:

```python
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
```

### Get Sleep Stream

Get raw stream data for the specified sleep ID. Request `types=["sleep_classification"]` to include sleep-stage classification samples when WHOOP returns them.

**Method**: `get_sleep_stream(sleep_id: str, types: list[str] | tuple[str, ...] | None = None)`

**Payload**:

- `sleep`: ID of the sleep to retrieve stream data for. Passed into the request path.
- `types`: Optional stream types to request. WHOOP documents `hr`, `skin_temp`, `board_temp`, `battery_temp`, `sleep_classification`, and `charging_status`.

**Example Response**:

```python
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
```

### Get Workout By ID

Get the workout for the specified ID.

**Method**: `get_workout_by_id(workout_id: str)`

**Payload**:

- `workout_id`: ID of the workout to retrieve. Passed into the request path.

**Example Response**:

```python
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
```

### Get Workout Collection

Get all workouts for a user. Results are sorted by start time in descending order.

**Method**: `get_workout_collection(start_date: str | None = None, end_date: str | None = None)`

**Payload**:

- `start`: The earliest time for which to get data, derived from the `start_date` parameter. Returns workouts that occurred after or during (inclusive) this time. Accepts `YYYY-MM-DD` date strings or ISO datetimes. Date-only values cover whole UTC days. Defaults to six days before today (a trailing seven-day window).
- `end`: The latest time for which to get data, derived from the `end_date` parameter. Returns workouts that intersect this time or ended before (exclusive) this time. Accepts `YYYY-MM-DD` date strings or ISO datetimes. Date-only values cover whole UTC days. Defaults to today's date.

**Example Response**:

```python
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
```

## Usage With DataFrame

Using WHOOP API data with a Pandas DataFrame is very straightforward:

```python
>>> import pandas as pd

>>> sleep = client.get_sleep_collection("2022-05-01", "2022-05-07")
>>> pd.json_normalize(sleep)

                                     id  user_id                created_at                updated_at  \
0  0e8c8c6e-1a2b-4c3d-8e4f-1a2b3c4d5e6f   995945  2022-05-07T14:56:28.389Z  2022-05-07T15:12:22.933Z
1  1f9d9d7f-2b3c-4d4e-9f5a-2b3c4d5e6f70   995945  2022-05-06T18:11:27.029Z  2022-05-06T18:11:29.172Z
2  2a0e0e80-3c4d-4e5f-a06b-3c4d5e6f7081   995945  2022-05-05T14:31:14.954Z  2022-05-05T14:43:15.744Z
3  3b1f1f91-4d5e-4f60-b17c-4d5e6f708192   995945  2022-05-04T13:35:13.911Z  2022-05-04T13:35:15.758Z
4  4c2a20a2-5e6f-4071-c28d-5e6f708192a3   995945  2022-05-03T12:26:02.170Z  2022-05-03T12:26:04.151Z
5  5d3b31b3-6f70-4182-d39e-6f708192a3b4   995945  2022-05-02T15:55:10.734Z  2022-05-02T15:55:13.140Z
6  6e4c42c4-7081-4293-e4af-708192a3b4c5   995945  2022-05-01T17:06:54.808Z  2022-05-01T17:06:57.067Z
7  7f5d53d5-8192-43a4-f5b0-8192a3b4c5d6   995945  2022-05-01T11:26:47.991Z  2022-05-01T11:26:49.684Z

                      start                       end timezone_offset    nap  \
0  2022-05-07T04:46:52.867Z  2022-05-07T14:40:57.427Z          -04:00  False
1  2022-05-06T05:09:00.681Z  2022-05-06T15:09:12.415Z          -04:00  False
2  2022-05-05T04:59:16.774Z  2022-05-05T14:29:44.886Z          -04:00  False
3  2022-05-04T05:04:02.916Z  2022-05-04T13:28:57.733Z          -04:00  False
4  2022-05-03T05:29:46.133Z  2022-05-03T12:14:54.861Z          -04:00  False
5  2022-05-02T05:12:48.073Z  2022-05-02T15:49:36.453Z          -04:00  False
6  2022-05-01T11:53:13.942Z  2022-05-01T14:51:19.894Z          -04:00   True
7  2022-05-01T06:14:52.087Z  2022-05-01T09:19:14.856Z          -04:00  False

  score_state  score.stage_summary.total_in_bed_time_milli  \
0      SCORED                                     35643599
1      SCORED                                     35460907
2      SCORED                                     34240959
3      SCORED                                     30293855
4      SCORED                                     24307767
5      SCORED                                     38003623
6      SCORED                                     10396599
7      SCORED                                     11004129

   score.stage_summary.total_awake_time_milli  \
0                                     3744035
1                                     2064515
2                                     2937299
3                                     2769352
4                                     3384733
5                                     2235345
6                                      681103
7                                     1608235

   score.stage_summary.total_no_data_time_milli  \
0                                             0
1                                             0
2                                             0
3                                             0
4                                             0
5                                             0
6                                             0
7                                             0

   score.stage_summary.total_light_sleep_time_milli  \
0                                          15384266
1                                          13169346
2                                          12210534
3                                          12689932
4                                           6655383
5                                          11195003
6                                           5900698
7                                           4971785

   score.stage_summary.total_slow_wave_sleep_time_milli  \
0                                            7633425
1                                            7874053
2                                            7814364
3                                            5554196
4                                            5526290
5                                           10101551
6                                            1762533
7                                            3008130

   score.stage_summary.total_rem_sleep_time_milli  \
0                                         8881873
1                                        12352993
2                                        11278762
3                                         9280375
4                                         8741361
5                                        14471724
6                                         2052265
7                                         1415979

   score.stage_summary.sleep_cycle_count  \
0                                      8
1                                      9
2                                      5
3                                      4
4                                      4
5                                      9
6                                      3
7                                      1

   score.stage_summary.disturbance_count  score.sleep_needed.baseline_milli  \
0                                     17                           27975800
1                                     12                           27976121
2                                     21                           27976442
3                                     15                           27976764
4                                     12                           27977085
5                                      8                           27977406
6                                      1                           27977728
7                                      4                           27977728

   score.sleep_needed.need_from_sleep_debt_milli  \
0                                              0
1                                         359692
2                                        3237274
3                                        3636979
4                                              0
5                                        9792092
6                                        9792204
7                                        2098329

   score.sleep_needed.need_from_recent_strain_milli  \
0                                            367539
1                                            304726
2                                            655901
3                                           1812597
4                                            270597
5                                            426795
6                                                 0
7                                           1463907

   score.sleep_needed.need_from_recent_nap_milli  score.respiratory_rate  \
0                                              0               13.398438
1                                              0               13.066406
2                                              0               12.568359
3                                              0               13.164062
4                                              0               13.535156
5                                       -9715496               13.535156
6                                              0               14.121094
7                                              0               14.941406

   score.sleep_performance_percentage  score.sleep_consistency_percentage  \
0                               100.0                                83.0
1                               100.0                                81.0
2                                98.0                                75.0
3                                82.0                                68.0
4                                74.0                                65.0
5                               100.0                                62.0
6                                26.0                                51.0
7                                30.0                                78.0

   score.sleep_efficiency_percentage
0                          89.857010
1                          94.178050
2                          91.421684
3                          91.993940
4                          89.586520
5                          94.118080
6                          93.448790
7                          87.927660

[8 rows x 25 columns]
```
