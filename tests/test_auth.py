"""Tests for whoop.auth: authorization URL, token exchange, session lifecycle.

Network is never hit. `authorization_url` works offline for real; `fetch_token`
is exercised by patching the session's `fetch_token`.
"""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from whoop import (
    AUTHORIZE_URL,
    DEFAULT_SCOPES,
    REVOKE_URL,
    TOKEN_URL,
    WhoopAuth,
    WhoopClient,
)

from .conftest import CLIENT_ID, REDIRECT_URI, SYNTHETIC_TOKEN


def test_exports_are_wired():
    assert WhoopClient is not None
    assert WhoopAuth is not None
    assert AUTHORIZE_URL == "https://api.prod.whoop.com/oauth/oauth2/auth"
    assert TOKEN_URL == "https://api.prod.whoop.com/oauth/oauth2/token"  # noqa: S105
    assert REVOKE_URL == "https://api.prod.whoop.com/developer/v2/user/access"
    assert "offline" in DEFAULT_SCOPES


def test_authorization_url_offline(unauth_client: WhoopClient):
    url, state = unauth_client.authorization_url()

    assert url.startswith(AUTHORIZE_URL)
    assert state

    query = parse_qs(urlparse(url).query)
    assert query["client_id"] == [CLIENT_ID]
    assert query["response_type"] == ["code"]
    assert query["redirect_uri"] == [REDIRECT_URI]
    assert query["state"] == [state]
    # Default scopes, space-joined.
    assert query["scope"] == [" ".join(DEFAULT_SCOPES)]


def test_authorization_url_passes_kwargs(unauth_client: WhoopClient):
    url, state = unauth_client.authorization_url(state="fixed-state")

    assert state == "fixed-state"
    assert "state=fixed-state" in url


def test_custom_scopes_used():
    scopes = ["read:profile", "read:sleep"]
    client = WhoopClient(CLIENT_ID, "secret", REDIRECT_URI, scopes=scopes)  # noqa: S106
    url, _ = client.authorization_url()

    query = parse_qs(urlparse(url).query)
    assert query["scope"] == [" ".join(scopes)]


def test_fetch_token_delegates_with_authorization_response(unauth_client: WhoopClient):
    from unittest.mock import MagicMock

    mock = MagicMock(return_value=dict(SYNTHETIC_TOKEN))
    unauth_client.session.fetch_token = mock

    result = unauth_client.fetch_token(
        authorization_response="https://example.test/callback?code=abc&state=xyz"
    )

    assert result == SYNTHETIC_TOKEN
    # Only the provided argument is forwarded — code=None is not passed through.
    mock.assert_called_once_with(
        url=TOKEN_URL,
        authorization_response="https://example.test/callback?code=abc&state=xyz",
    )


def test_fetch_token_delegates_with_code(unauth_client: WhoopClient):
    from unittest.mock import MagicMock

    mock = MagicMock(return_value=dict(SYNTHETIC_TOKEN))
    unauth_client.session.fetch_token = mock

    unauth_client.fetch_token(code="bare-code")

    mock.assert_called_once_with(url=TOKEN_URL, code="bare-code")


def test_fetch_token_requires_response_or_code(unauth_client: WhoopClient):
    import pytest

    with pytest.raises(ValueError, match="authorization_response or code"):
        unauth_client.fetch_token()


def test_is_authenticated_false_then_true(unauth_client, client):
    assert unauth_client.is_authenticated() is False
    assert client.is_authenticated() is True


def test_token_property(unauth_client, client):
    assert unauth_client.token is None
    assert client.token["access_token"] == SYNTHETIC_TOKEN["access_token"]


def test_str_unauthenticated(unauth_client: WhoopClient):
    assert str(unauth_client) == "WhoopClient(unauthenticated)"


def test_str_authenticated(client: WhoopClient):
    # No user_id set, but a token is present.
    assert str(client) == "WhoopClient(authenticated)"


def test_str_with_user_id(client: WhoopClient):
    client.user_id = "user-42"
    assert str(client) == "WhoopClient(user-42)"


def test_on_token_refresh_callback_fires():
    captured: list[dict] = []
    client = WhoopClient(
        CLIENT_ID,
        "secret",  # noqa: S106
        REDIRECT_URI,
        on_token_refresh=captured.append,
    )

    new_token = {"access_token": "refreshed"}
    client._update_token(new_token)

    assert captured == [new_token]


def test_update_token_without_callback_is_noop():
    client = WhoopClient(CLIENT_ID, "secret", REDIRECT_URI)  # noqa: S106
    # No callback registered; must not raise.
    client._update_token({"access_token": "refreshed"})


def test_close_closes_session(unauth_client: WhoopClient):
    from unittest.mock import MagicMock

    unauth_client.session.close = MagicMock()
    unauth_client.close()
    unauth_client.session.close.assert_called_once_with()


def test_revoke_access_deletes_user_access(client: WhoopClient):
    from unittest.mock import MagicMock

    response = MagicMock()
    client.session.delete = MagicMock(return_value=response)

    client.revoke_access()

    client.session.delete.assert_called_once_with(REVOKE_URL)
    response.raise_for_status.assert_called_once_with()


def test_context_manager_calls_close():
    from unittest.mock import MagicMock

    client = WhoopClient(CLIENT_ID, "secret", REDIRECT_URI)  # noqa: S106
    client.session.close = MagicMock()

    with client as entered:
        assert entered is client

    client.session.close.assert_called_once_with()


def test_expired_token_triggers_authlib_refresh():
    """An expired token + refresh token drives Authlib's real refresh on request.

    Patches the transport (`session.send`) so no network is used, proving the
    end-to-end wiring: token_endpoint metadata -> refresh POST -> update_token ->
    on_token_refresh callback, after which the original data request proceeds.
    """
    import json
    from unittest.mock import MagicMock

    import requests

    captured: list[dict] = []
    expired_token = {
        "access_token": "old-access",
        "refresh_token": "old-refresh",  # noqa: S106
        "token_type": "bearer",  # noqa: S106
        "expires_at": 1000000000,  # year 2001 -> already expired
    }
    client = WhoopClient(
        CLIENT_ID,
        "secret",  # noqa: S106
        REDIRECT_URI,
        token=expired_token,
        on_token_refresh=captured.append,
    )

    new_token = {
        "access_token": "new-access",
        "refresh_token": "new-refresh",  # noqa: S106
        "token_type": "bearer",  # noqa: S106
        "expires_in": 3600,
    }
    profile = {"user_id": 12345}

    def fake_send(request, **_kwargs):
        resp = requests.Response()
        resp.status_code = 200
        resp.headers["Content-Type"] = "application/json"
        payload = new_token if request.url.startswith(TOKEN_URL) else profile
        resp._content = json.dumps(payload).encode()
        resp.request = request
        return resp

    client.session.send = MagicMock(side_effect=fake_send)

    result = client.get_profile()

    # The data request returned, with a refresh POST occurring in between.
    assert result == profile
    sent_urls = [call.args[0].url for call in client.session.send.call_args_list]
    assert any(u.startswith(TOKEN_URL) for u in sent_urls), "expected a refresh POST"
    # The rotated token reached the persistence callback and the live session.
    assert captured and captured[-1]["access_token"] == "new-access"  # noqa: S105
    assert client.token["access_token"] == "new-access"  # noqa: S105
