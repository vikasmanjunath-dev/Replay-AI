"""Read-only target-host HTTP smoke checks. Credentials are never printed."""

from __future__ import annotations

import os
import sys
from urllib.parse import urlsplit

import httpx

REQUIRED_HEADERS = (
    "content-security-policy", "permissions-policy", "referrer-policy",
    "strict-transport-security", "x-content-type-options", "x-frame-options",
)


def validate_origin(raw: str) -> str:
    parsed = urlsplit(raw)
    try:
        parsed.port
    except ValueError as error:
        raise ValueError("Smoke URL has an invalid port.") from error
    local = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if (
        parsed.scheme != ("http" if local else "https") or not parsed.hostname
        or parsed.username is not None or parsed.password is not None
        or parsed.path or parsed.query or parsed.fragment
    ):
        raise ValueError("Use a bare HTTPS origin (HTTP is allowed only for loopback development).")
    return raw.rstrip("/")


def verify_target(client: httpx.Client, origin: str, token: str) -> list[tuple[str, bool]]:
    auth = {"Authorization": f"Bearer {token}"}
    checks: list[tuple[str, bool]] = []
    unauthenticated = client.get(f"{origin}/health")
    checks.append(("unauthenticated request rejected", unauthenticated.status_code in {401, 403}))
    for endpoint in ("/health", "/ready", "/metrics"):
        response = client.get(f"{origin}{endpoint}", headers=auth)
        checks.append((f"authenticated {endpoint}", response.status_code == 200))
    root = client.get(origin, headers=auth)
    missing = [header for header in REQUIRED_HEADERS if header not in root.headers]
    checks.append(("security response headers", root.status_code == 200 and not missing))
    allowed = client.options(
        f"{origin}/health",
        headers={"Origin": origin, "Access-Control-Request-Method": "GET"},
    )
    checks.append(("configured CORS origin", allowed.headers.get("access-control-allow-origin") == origin))
    denied = client.options(
        f"{origin}/health",
        headers={"Origin": "https://invalid.example", "Access-Control-Request-Method": "GET"},
    )
    checks.append(("unconfigured CORS origin denied", "access-control-allow-origin" not in denied.headers))
    return checks


def main() -> int:
    try:
        origin = validate_origin(os.environ.get("RELAY_SMOKE_URL", ""))
    except ValueError as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 2
    token = os.environ.get("RELAY_SMOKE_TOKEN", "")
    if not token or len(token) > 4096 or any(char in token for char in "\r\n"):
        print("BLOCKED: RELAY_SMOKE_TOKEN must be configured in the protected environment.", file=sys.stderr)
        return 2
    try:
        with httpx.Client(timeout=httpx.Timeout(8.0, connect=3.0), follow_redirects=False, trust_env=False) as client:
            checks = verify_target(client, origin, token)
    except httpx.RequestError:
        print("FAIL: target request could not be completed; request details were suppressed.", file=sys.stderr)
        return 1
    for name, passed in checks:
        print(f"{'PASS' if passed else 'FAIL'}: {name}")
    failures = sum(not passed for _, passed in checks)
    print(f"{len(checks) - failures}/{len(checks)} target HTTP checks passed.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
