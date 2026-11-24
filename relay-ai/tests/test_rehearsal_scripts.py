from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_rehearsal_shell_scripts_parse_and_show_help():
    scripts = (
        ROOT / "scripts/rehearse_checkout_fixture.sh",
        ROOT / "scripts/rehearse_checkout_fake.sh",
        ROOT / "scripts/rehearse_checkout_gemini.sh",
        ROOT / "scripts/record_demo_backup.sh",
    )
    for script in scripts:
        parsed = subprocess.run(
            ["bash", "-n", str(script)], capture_output=True, text=True, check=False
        )
        assert parsed.returncode == 0, parsed.stderr
        help_result = subprocess.run(
            ["bash", str(script), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert help_result.returncode == 0, help_result.stderr
        assert help_result.stdout.strip()
        if script.name == "rehearse_checkout_fake.sh":
            assert "--docker" in help_result.stdout


def test_gemini_rehearsal_fails_closed_without_key():
    env = os.environ.copy()
    env.pop("GEMINI_API_KEY", None)
    result = subprocess.run(
        [sys.executable, str(ROOT / "relay-ai/scripts/rehearse_checkout_gemini.py")],
        cwd=ROOT / "relay-ai",
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 2
    assert "GEMINI_API_KEY is required" in result.stderr
    assert "Bearer " not in result.stdout + result.stderr


def test_live_gemini_rehearsal_checks_isolation_before_submit_and_never_approves():
    source = (ROOT / "relay-ai/scripts/rehearse_checkout_gemini.py").read_text(encoding="utf-8")

    assert 'os.environ["RELAY_ALLOW_UNSAFE_SUBPROCESS"] = "false"' in source
    assert source.index('if not os.environ.get("GEMINI_API_KEY"') < source.index("import main as relay_api")
    assert source.index("if not sandbox.docker_available or not sandbox.sandbox_image_available") < source.index(
        'client.post(\n                "/api/v1/tasks"'
    )
    assert 'client.post(\n                "/api/v1/tasks/' not in source
    assert '"/actions"' not in source
