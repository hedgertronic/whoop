"""OAuth2 authentication for the WHOOP API.

Implements WHOOP's official OAuth2 authorization-code flow on top of Authlib's
`OAuth2Session`. `WhoopAuth` owns the session lifecycle, builds authorization
URLs, exchanges codes for tokens, and refreshes tokens automatically. The data
endpoints live on `WhoopClient`, which extends this class.

Attributes:
    AUTHORIZE_URL (str): OAuth2 authorization endpoint (user consent).
    TOKEN_URL (str): OAuth2 token endpoint (code exchange and refresh).
    REVOKE_URL (str): OAuth2 access revocation endpoint.
    DEFAULT_SCOPES (list[str]): Read scopes for all endpoints plus ``offline``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from authlib.integrations.requests_client import OAuth2Session

AUTHORIZE_URL = "https://api.prod.whoop.com/oauth/oauth2/auth"
TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"  # noqa: S105 (URL, not a secret)
REVOKE_URL = "https://api.prod.whoop.com/developer/v2/user/access"

DEFAULT_SCOPES = [
    "read:profile",
    "read:body_measurement",
    "read:cycles",
    "read:recovery",
    "read:sleep",
    "read:workout",
    "offline",
]


class WhoopAuth:
    """Manage OAuth2 authentication for the WHOOP API.

    Authenticates with WHOOP's official OAuth2 authorization-code flow: create a
    client with your app credentials, send the user through `authorization_url()`
    to grant access, then exchange the returned code via `fetch_token()`. Tokens
    refresh automatically using the refresh token (request the ``offline`` scope,
    which is included by default).

    Attributes:
        session (authlib.OAuth2Session): Session used to access the WHOOP API.
        user_id (str): User ID of the session owner. Empty unless explicitly set.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str | None = None,
        *,
        scopes: list[str] | None = None,
        token: dict[str, Any] | None = None,
        on_token_refresh: Callable[[dict[str, Any]], None] | None = None,
    ):
        """Initialize an OAuth2 session for making API requests.

        Args:
            client_id (str): OAuth2 client ID from the WHOOP Developer Dashboard.
            client_secret (str): OAuth2 client secret from the dashboard.
            redirect_uri (str | None): Redirect URI registered for the app. Required
                to authorize a new token; optional when reusing a saved `token`.
            scopes (list[str] | None): Scopes to request. Defaults to `DEFAULT_SCOPES`.
            token (dict[str, Any] | None): A previously fetched token to reuse so the
                authorization flow can be skipped. Defaults to None.
            on_token_refresh (Callable[[dict[str, Any]], None] | None): Called with the
                new token whenever it is refreshed, so callers can persist it. Defaults
                to None.
        """
        self._on_token_refresh = on_token_refresh

        self.session = OAuth2Session(
            client_id=client_id,
            client_secret=client_secret,
            # WHOOP expects credentials in the request body, not a Basic auth header.
            token_endpoint_auth_method="client_secret_post",  # noqa: S106 (auth method name)
            scope=" ".join(scopes if scopes is not None else DEFAULT_SCOPES),
            redirect_uri=redirect_uri,
            token=token,
            token_endpoint=TOKEN_URL,
            update_token=self._update_token,
        )

        self.user_id = ""

    def __str__(self) -> str:
        """Generate string representation of the client.

        Returns:
            str: Representation featuring the user ID or authentication status.
        """
        status = self.user_id or (
            "authenticated" if self.is_authenticated() else "unauthenticated"
        )
        return f"{type(self).__name__}({status})"

    def close(self) -> None:
        """Close the OAuth2 Session."""
        self.session.close()

    def revoke_access(self) -> None:
        """Revoke this user's OAuth access grant.

        After a successful request, the current access token can no longer access
        WHOOP data and webhook delivery stops for the associated OAuth client.
        """
        response = self.session.delete(REVOKE_URL)
        response.raise_for_status()

    def authorization_url(self, **kwargs: Any) -> tuple[str, str]:
        """Build the URL a user visits to authorize the app.

        Send the user to the returned URL. After they consent, WHOOP redirects them
        to the registered `redirect_uri` with an authorization code in the query
        string. Pass that redirect URL (or the bare code) to `fetch_token()`.

        Args:
            kwargs (dict[str, Any], optional): Extra parameters for the authorization
                request (e.g. a custom `state`).

        Returns:
            tuple[str, str]: The authorization URL and the `state` used to build it.
        """
        url, state = self.session.create_authorization_url(AUTHORIZE_URL, **kwargs)
        return url, state

    def fetch_token(
        self,
        authorization_response: str | None = None,
        code: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Exchange an authorization code for an access token.

        Provide either the full `authorization_response` URL the user was redirected
        to, or the bare `code` extracted from it.

        Args:
            authorization_response (str | None): The full redirect URL containing the
                code and state. Defaults to None.
            code (str | None): The authorization code on its own. Defaults to None.
            kwargs (dict[str, Any], optional): Additional arguments for `fetch_token()`.

        Returns:
            dict[str, Any]: The fetched token (access token, refresh token, expiry).

        Raises:
            ValueError: If neither `authorization_response` nor `code` is provided.
        """
        if not authorization_response and not code:
            raise ValueError("Provide either authorization_response or code.")

        # Forward only the argument that was set; passing code=None makes Authlib
        # build an authorization-code request with a null code instead of failing.
        if authorization_response:
            kwargs["authorization_response"] = authorization_response
        if code:
            kwargs["code"] = code

        token: dict[str, Any] = self.session.fetch_token(url=TOKEN_URL, **kwargs)
        return token

    def is_authenticated(self) -> bool:
        """Check whether the session holds a token.

        Reports token *presence*, not validity: a stored token may be expired. An
        expired token is refreshed automatically on the next request when a refresh
        token is available.

        Returns:
            bool: Whether the session holds a token.
        """
        return self.session.token is not None

    @property
    def token(self) -> dict[str, Any] | None:
        """Current OAuth2 token, suitable for persisting and later reuse.

        Returns:
            dict[str, Any] | None: The active token, or None if not yet authorized.
        """
        token: dict[str, Any] | None = self.session.token
        return token

    def _update_token(
        self,
        token: dict[str, Any],
        refresh_token: str | None = None,
        access_token: str | None = None,
    ) -> None:
        """Handle a refreshed token by forwarding it to the caller's callback.

        Args:
            token (dict[str, Any]): The newly issued token.
            refresh_token (str | None): The refresh token used, if any.
            access_token (str | None): The prior access token, if any.
        """
        if self._on_token_refresh:
            self._on_token_refresh(token)
