# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0]

### Added
- OAuth2 support for WHOOP's authorization-code flow via `WhoopClient`.
- Token reuse and refresh persistence through `client.token` and `on_token_refresh`.
- OAuth access revocation via `revoke_access()`.
- V1-to-V2 activity ID lookup via `get_activity_mapping(...)`.
- Cycle-to-sleep lookup via `get_sleep_for_cycle(...)`.
- Sleep stream access via `get_sleep_stream(...)`, including `sleep_classification` requests.
- `whoop.__version__`.
- `py.typed` marker -- the package now ships its inline type annotations (PEP 561).
- GitHub Actions CI across Python 3.12-3.14 (ruff, mypy, pytest with coverage, package build).

### Changed
- Replaced the legacy username/password flow with WHOOP's official OAuth2 app flow.
- Packaged as the `whoop/` package (`client.py`, `auth.py`) with Hatchling and uv.
- Minimum supported Python is now 3.12.
- Collection date filters accept date-only whole-day windows or ISO datetimes for narrower windows.

### Notes
- This release intentionally returns raw WHOOP API JSON and raises HTTP errors from the underlying session.
- Request the `offline` scope, included by default, when you need automatic token refresh.
