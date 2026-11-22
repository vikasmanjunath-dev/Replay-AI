import json
import importlib.util
import os
from pathlib import Path
import subprocess

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[2]
SMOKE_SPEC = importlib.util.spec_from_file_location("target_host_smoke", ROOT / "deploy/target_host_smoke.py")
SMOKE = importlib.util.module_from_spec(SMOKE_SPEC)
assert SMOKE_SPEC and SMOKE_SPEC.loader
SMOKE_SPEC.loader.exec_module(SMOKE)
REQUIRED_HEADERS = SMOKE.REQUIRED_HEADERS
validate_origin = SMOKE.validate_origin
verify_target = SMOKE.verify_target


def test_release_blocker_matrix_marks_each_owner_step_blocked_with_an_exact_ask():
    data = json.loads((ROOT / "deploy/RELEASE_BLOCKERS.json").read_text())
    blockers = data["blockers"]
    assert len(blockers) >= 8
    assert len({item["id"] for item in blockers}) == len(blockers)
    assert all(item["status"] == "BLOCKED" and len(item["exact_ask"]) > 40 for item in blockers)
    assert "no deployment target" in data["note"].lower()


def test_every_release_blocker_has_a_signoff_evidence_field():
    blocker_data = json.loads((ROOT / "deploy/RELEASE_BLOCKERS.json").read_text())
    template = json.loads((ROOT / "deploy/RELEASE_SIGNOFF_TEMPLATE.json").read_text())
    signoff_fields = set(template)
    evidence_by_blocker = {
        "H6-TARGET-ISOLATION": {"sandbox_isolation"},
        "H10-PROXY-AUTH-CORS": {"nginx_config_test", "auth_cors_proxy_test"},
        "H10-BACKUP-ALERT": {"backup_alert_delivery"},
        "H10-RESTORE-DRILL": {"restore_drill"},
        "H10-ACCESSIBILITY-REVIEW": {"accessibility_review"},
        "H10-LOAD-REVIEW": {"load_review"},
        "H10-OWNERS": {"primary_owner", "backup_owner", "security_contact"},
        "H10-GEMINI-DATA-APPROVAL": {"gemini_data_approval"},
        "H10-SLO-ACCEPTANCE": {"slo_owner"},
    }

    assert {item["id"] for item in blocker_data["blockers"]} == set(evidence_by_blocker)
    assert all(fields <= signoff_fields for fields in evidence_by_blocker.values())


@pytest.mark.parametrize("raw", [
    "http://prod.example", "https://user:pass@prod.example", "https://prod.example/path",
    "https://prod.example?token=secret", "https://prod.example#fragment", "https://prod.example:bad",
])
def test_target_smoke_accepts_only_bare_https_or_loopback_origins(raw):
    with pytest.raises(ValueError):
        validate_origin(raw)
    assert validate_origin("https://prod.example") == "https://prod.example"
    assert validate_origin("http://127.0.0.1:8000") == "http://127.0.0.1:8000"


def test_target_smoke_checks_auth_readiness_headers_and_allowed_and_denied_cors():
    requests = []

    def respond(request):
        requests.append(request)
        if request.method == "GET" and request.url.path == "/health" and "authorization" not in request.headers:
            return httpx.Response(401)
        if request.method == "OPTIONS" and request.headers.get("origin") == "https://relay.example":
            return httpx.Response(200, headers={"access-control-allow-origin": "https://relay.example"})
        if request.method == "OPTIONS":
            return httpx.Response(400)
        if request.url.path == "/":
            return httpx.Response(200, headers={header: "present" for header in REQUIRED_HEADERS})
        return httpx.Response(200)

    with httpx.Client(transport=httpx.MockTransport(respond), follow_redirects=False) as client:
        checks = verify_target(client, "https://relay.example", "private-token")
    assert len(checks) == 7 and all(passed for _, passed in checks)
    assert all(request.headers.get("authorization") != "private-token" for request in requests)
    assert any(request.headers.get("authorization") == "Bearer private-token" for request in requests)


def test_host_release_script_requires_secret_configuration_without_printing_values():
    script = (ROOT / "deploy/run_target_host_drills.sh").read_text()
    for required in ("RELAY_NGINX_CONFIG", "RELAY_SMOKE_URL", "RELAY_SMOKE_TOKEN", "RELAY_SANDBOX_IMAGE"):
        assert required in script
    assert "nginx -t" in script
    assert "RELAY_RUN_ISOLATION_DRILL=true" in script
    assert "systemctl restart" not in script
    assert "nginx -s reload" not in script


def test_target_host_drill_rejects_mutable_sandbox_tag_before_host_access():
    env = os.environ.copy()
    env.update({
        "RELAY_NGINX_CONFIG": "/tmp/not-used.conf",
        "RELAY_SMOKE_URL": "https://relay.example.test",
        "RELAY_SMOKE_TOKEN": "release-test-token-do-not-print",
        "RELAY_SANDBOX_IMAGE": "relay-ai-sandbox:latest",
    })
    result = subprocess.run(
        ["bash", str(ROOT / "deploy/run_target_host_drills.sh")],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=5,
    )

    assert result.returncode == 2
    assert "must be pinned by a SHA-256" in result.stderr
    assert "release-test-token-do-not-print" not in result.stdout + result.stderr


@pytest.mark.parametrize("image", [
    "sha256:" + "a" * 64,
    "ghcr.io/acme/relay@sha256:" + "b" * 64,
])
def test_target_host_drill_accepts_immutable_digest_forms_before_host_access(image):
    env = os.environ.copy()
    env.update({
        "RELAY_NGINX_CONFIG": "/tmp/not-used.conf",
        "RELAY_SMOKE_URL": "https://relay.example.test",
        "RELAY_SMOKE_TOKEN": "release-test-token-do-not-print",
        "RELAY_SANDBOX_IMAGE": image,
        "RELAY_RELEASE_PYTHON": "/tmp/not-a-python-runtime",
    })
    result = subprocess.run(
        ["bash", str(ROOT / "deploy/run_target_host_drills.sh")],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=5,
    )

    assert result.returncode == 2
    assert "configured release Python is missing" in result.stderr
    assert "must be pinned by a SHA-256" not in result.stderr
    assert "release-test-token-do-not-print" not in result.stdout + result.stderr


def test_host_free_release_script_runs_checks_and_marks_preflight_as_non_certifying():
    script = (ROOT / "deploy/run_host_free_release_checks.sh").read_text()
    for command in (
        "pytest -q relay-ai/tests", "compileall -q relay-ai", "npm test",
        "npm run lint", "npm run build", "git diff --check", "git diff --cached --check",
    ):
        assert command in script
    assert "not a host certification" in script
