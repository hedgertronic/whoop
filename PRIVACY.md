# Privacy Policy

_Last updated: 2026-06-22_

This privacy policy describes how the **`whoop`** software ("the Software") — an
open-source Python client for the WHOOP API, available at
<https://github.com/hedgertronic/whoop> — handles data.

## What the Software is

The Software is a client library that runs **locally on the machine of the person
using it**. It authenticates to the WHOOP API using OAuth 2.0 and retrieves the
authenticating user's own WHOOP data on their behalf. It is a tool the user runs;
it is not a hosted service.

## Data the Software accesses

With the scopes you grant during WHOOP authorization, the Software can read the
authenticating user's:

- Basic profile (`read:profile`)
- Body measurements (`read:body_measurement`)
- Physiological cycles (`read:cycles`)
- Recovery scores (`read:recovery`)
- Sleep activities (`read:sleep`)
- Workouts (`read:workout`)

It only accesses the data of the user who authorizes it, and only the categories
the user consents to. The Software makes **read-only** requests; it does not
modify or delete any WHOOP data.

## How data is handled

- Data flows directly between the user's own machine and WHOOP's servers. It is
  **not** sent to, collected by, or stored on any server operated by the author of
  the Software.
- OAuth tokens (access and refresh tokens) exist only in the running process and
  anywhere the user themselves chooses to store them. The author of the Software
  has no access to them.
- The author does **not** collect, retain, sell, or share any user data. The
  Software has no analytics, telemetry, or third-party data sharing.

Any data the user chooses to save, export, or transmit is under the user's own
control and subject to the user's own handling.

## Third-party services

The Software communicates with the WHOOP API. Use of WHOOP and your WHOOP data is
governed by WHOOP's own privacy policy and terms: <https://www.whoop.com/legal/>.

## Contact

Questions about this policy can be raised via the project's issue tracker at
<https://github.com/hedgertronic/whoop/issues>.
