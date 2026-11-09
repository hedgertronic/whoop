"""Tests for whoop.auth: authorization URL, token exchange, session lifecycle.

Network is never hit. `authorization_url` works offline for real; `fetch_token`
is exercised by patching the session's `fetch_token`.
"""

from __future__ import annotations

from unittest.mock import MagicMock
from urllib.parse import parse_qs, urlparse

import pytest
from authlib.oauth2.rfc6749 import MismatchingStateException

from whoop import (
    AUTHORIZE_URL,
    DEFAULT_SCOPES,
    REVOKE_URL,
    TOKEN_URL,
    WhoopAuth,
    WhoopClient,
)

from .conftest import CLIENT_ID, REDIRECT_URI, SYNTHETIC_TOKEN


@pytest.fixture
def token_transport(unauth_client):
    response = MagicMock(status_code=200)
    response.json.return_value = dict(SYNTHETIC_TOKEN)
    unauth_client.session.send = MagicMock(return_value=response)
    return unauth_client.session.send


@pytest.mark.parametrize("state_kwargs", [{}, {"state": "custom-state"}])
def test_authorization_callback_matches_state(
    unauth_client, token_transport, state_kwargs
):
    _, state = unauth_client.authorization_url(**state_kwargs)
    result = unauth_client.fetch_token(
        authorization_response=f"{REDIRECT_URI}?code=abc&state={state}"
    )

    assert result == SYNTHETIC_TOKEN
    assert unauth_client.token == result
    assert unauth_client.is_authenticated()
    token_transport.assert_called_once()


@pytest.mark.parametrize("callback_query", ["code=abc", "code=abc&state=wrong"])
def test_authorization_callback_rejects_invalid_state_before_transport(
    unauth_client, token_transport, callback_query
):
    unauth_client.authorization_url()

    with pytest.raises(MismatchingStateException):
        unauth_client.fetch_token(
            authorization_response=f"{REDIRECT_URI}?{callback_query}"
        )

    token_transport.assert_not_called()
    assert unauth_client.token is None


def test_new_authorization_attempt_replaces_pending_state(
    unauth_client, token_transport
):
    _, old_state = unauth_client.authorization_url()
    _, new_state = unauth_client.authorization_url()

    with pytest.raises(MismatchingStateException):
        unauth_client.fetch_token(
            authorization_response=f"{REDIRECT_URI}?code=abc&state={old_state}"
        )

    token_transport.assert_not_called()
    unauth_client.fetch_token(
        authorization_response=f"{REDIRECT_URI}?code=abc&state={new_state}"
    )
    assert unauth_client.is_authenticated()


def test_callback_can_use_explicit_state_from_another_process(
    unauth_client, token_transport
):
    unauth_client.fetch_token(
        authorization_response=f"{REDIRECT_URI}?code=abc&state=saved-state",
        state="saved-state",
    )
    assert unauth_client.is_authenticated()


def test_bare_code_exchange_after_authorization_url(unauth_client, token_transport):
    unauth_client.authorization_url()
    unauth_client.fetch_token(code="bare-code")
    assert unauth_client.is_authenticated()


def test_revoke_access_clears_local_credentials_only_after_success(client):
    client.user_id = "user-42"
    client.session.delete = MagicMock(return_value=MagicMock())

    client.revoke_access()

    assert client.token is None
    assert client.is_authenticated() is False
    assert client.user_id == ""
    assert str(client) == "WhoopClient(unauthenticated)"


def test_failed_revocation_preserves_local_credentials(client):
    client.user_id = "user-42"
    response = MagicMock()
    response.raise_for_status.side_effect = RuntimeError("HTTP 503")
    client.session.delete = MagicMock(return_value=response)

    with pytest.raises(RuntimeError, match="HTTP 503"):
        client.revoke_access()

    assert client.token == SYNTHETIC_TOKEN
    assert client.is_authenticated()
    assert client.user_id == "user-42"


def test_unauthenticated_request_fails_before_transport(unauth_client, token_transport):
    from authlib.integrations.base_client import MissingTokenError

    with pytest.raises(MissingTokenError):
        unauth_client.get_profile()

    token_transport.assert_not_called()


@pytest.mark.parametrize("has_refresh_token", [False, True])
def test_expired_token_failure_prevents_data_request(
    unauth_client, token_transport, has_refresh_token
):
    from authlib.integrations.base_client import InvalidTokenError, OAuthError

    expired_token = {**SYNTHETIC_TOKEN, "expires_at": 1000000000}
    if not has_refresh_token:
        expired_token.pop("refresh_token")
    unauth_client.session.token = expired_token
    token_transport.return_value.json.return_value = {"error": "invalid_grant"}

    with pytest.raises(OAuthError if has_refresh_token else InvalidTokenError):
        unauth_client.get_profile()

    assert unauth_client.token == expired_token
    assert unauth_client.is_authenticated()
    assert token_transport.call_count == int(has_refresh_token)
    if has_refresh_token:
        assert token_transport.call_args.args[0].url == TOKEN_URL


def test_refresh_persistence_failure_keeps_rotated_token_in_memory(
    unauth_client, token_transport
):
    unauth_client.session.token = {**SYNTHETIC_TOKEN, "expires_at": 1000000000}
    unauth_client._on_token_refresh = MagicMock(
        side_effect=OSError("storage unavailable")
    )

    with pytest.raises(OSError, match="storage unavailable"):
        unauth_client.get_profile()

    assert unauth_client.token == SYNTHETIC_TOKEN
    unauth_client._on_token_refresh.assert_called_once_with(unauth_client.token)
    token_transport.assert_called_once()
    assert token_transport.call_args.args[0].url == TOKEN_URL


def test_context_manager_closes_session_on_exception(unauth_client):
    unauth_client.session.close = MagicMock()

    with pytest.raises(RuntimeError, match="request failed"), unauth_client:
        raise RuntimeError("request failed")

    unauth_client.session.close.assert_called_once_with()


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
