"""Tools for acquiring and analyzing WHOOP API data.

WHOOP is a wearable strap for monitoring sleep, activity, and workouts. Learn more
about WHOOP at https://www.whoop.com. API docs: https://developer.whoop.com/api.

Examples:
    Loading credentials from environment variables:
        import os

        from dotenv import load_dotenv

        load_dotenv()

        client_id = os.getenv("CLIENT_ID") or ""
        client_secret = os.getenv("CLIENT_SECRET") or ""
        redirect_uri = os.getenv("REDIRECT_URI") or ""

    Authorizing a new client (one-time, interactive):
        import whoop as wh

        client = wh.WhoopClient(client_id, client_secret, redirect_uri)

        # Send the user to this URL to grant access, then capture the redirect
        # they land on (its query string contains the authorization code).
        url, _state = client.authorization_url()
        print(url)

        client.fetch_token(authorization_response=input("Redirect URL: "))

    Reusing a saved token (headless, no consent prompt):
        client = wh.WhoopClient(client_id, client_secret, token=saved_token)

    Making requests:
        sleep = client.get_sleep_collection()
        recovery = client.get_recovery_collection()

        print(sleep)
        print(recovery)
"""

from importlib.metadata import PackageNotFoundError, version

from whoop.auth import AUTHORIZE_URL, DEFAULT_SCOPES, REVOKE_URL, TOKEN_URL, WhoopAuth
from whoop.client import REQUEST_URL, WhoopClient

try:
    __version__ = version("whoop")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

__all__ = [
    "AUTHORIZE_URL",
    "DEFAULT_SCOPES",
    "REQUEST_URL",
    "REVOKE_URL",
    "TOKEN_URL",
    "__version__",
    "WhoopAuth",
    "WhoopClient",
]
