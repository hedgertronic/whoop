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
- [Usage With DataFrame](#usage-with-dataframe)

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

## Usage With DataFrame

Using WHOOP API data with a Pandas DataFrame is very straightforward:

```python
>>> import pandas as pd

>>> sleep = client.get_sleep_collection("2022-05-01", "2022-05-07")
>>> pd.json_normalize(sleep)

          id  user_id                created_at                updated_at  \
0  430878903   995945  2022-05-07T14:56:28.389Z  2022-05-07T15:12:22.933Z
1  430378149   995945  2022-05-06T18:11:27.029Z  2022-05-06T18:11:29.172Z
2  429704502   995945  2022-05-05T14:31:14.954Z  2022-05-05T14:43:15.744Z
3  429055399   995945  2022-05-04T13:35:13.911Z  2022-05-04T13:35:15.758Z
4  428375477   995945  2022-05-03T12:26:02.170Z  2022-05-03T12:26:04.151Z
5  427873268   995945  2022-05-02T15:55:10.734Z  2022-05-02T15:55:13.140Z
6  427300091   995945  2022-05-01T17:06:54.808Z  2022-05-01T17:06:57.067Z
7  427069852   995945  2022-05-01T11:26:47.991Z  2022-05-01T11:26:49.684Z

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
