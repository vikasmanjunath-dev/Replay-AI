"""Optional outbound Switch room progress notifications.

Uses Switch's documented agent message endpoint. It does not register agents,
read room messages, or expose task source, model output, credentials, or errors.
"""

from __future__ import annotations

import os
import re
from collections import OrderedDict
from dataclasses import dataclass, field
from urllib.parse import urlsplit

import httpx


_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_FINAL_STATES = {"AWAITING_HUMAN_APPROVAL", "FAILED", "CANCELLED"}
_REVIEW_STATES = {"APPROVE", "REJECT", "PENDING", "NOT_REVIEWED"}
_SECURITY_STATES = {"PASS", "WARN", "FAIL", "NOT_REVIEWED"}
_MAX_CACHED_STATES = 10_000
_TASK_STAGES = {
    "RECEIVED",
    "STAGE_A_TRIAGE",
    "STAGE_B_INVESTIGATION_AND_DEV",
    "SANDBOX_TEST_EXECUTION",
    "STAGE_C_REVIEW",
    "AWAITING_HUMAN_APPROVAL",
    "FAILED",
    "CANCELLED",
}
_TASK_STATES = {
    "RECEIVED", "QUEUED", "RUNNING", "TRIAGING", "INVESTIGATING", "SANDBOX_RUNNING",
    "REVIEWING", "TRIAGED", "INVESTIGATED", "PATCHED", "SANDBOX_TESTED", "REVIEWED",
    "AWAITING_HUMAN_APPROVAL", "APPROVED", "APPLIED", "COMMITTED", "REJECTED",
    "CANCELLED", "FAILED",
}


@dataclass(frozen=True)
class SwitchRoomConfig:
    base_url: str
    agent_id: str
    room_id: str
    api_key: str = field(repr=False)

    @classmethod
    def from_env(cls) -> "SwitchRoomConfig | None":
        values = {
            "RELAY_SWITCH_BASE_URL": os.environ.get("RELAY_SWITCH_BASE_URL", "").strip(),
            "RELAY_SWITCH_AGENT_ID": os.environ.get("RELAY_SWITCH_AGENT_ID", "").strip(),
            "RELAY_SWITCH_ROOM_ID": os.environ.get("RELAY_SWITCH_ROOM_ID", "").strip(),
            "RELAY_SWITCH_API_KEY": os.environ.get("RELAY_SWITCH_API_KEY", "").strip(),
        }
        if not any(values.values()):
            return None
        if not all(values.values()):
            raise ValueError("Switch room notifications require all four RELAY_SWITCH settings.")
        raw_base_url = values["RELAY_SWITCH_BASE_URL"]
        api_key = values["RELAY_SWITCH_API_KEY"]
        if len(raw_base_url) > 2048:
            raise ValueError("Switch bridge URL exceeds the 2,048-character limit.")
        if any(char.isspace() or ord(char) < 32 or ord(char) == 127 for char in raw_base_url):
            raise ValueError("Switch bridge URL must not contain whitespace or control characters.")
        if len(api_key) > 512 or any(not 33 <= ord(char) <= 126 for char in api_key):
            raise ValueError("Switch agent API key must be visible ASCII and no longer than 512 characters.")
        try:
            parsed = urlsplit(raw_base_url)
            port = parsed.port
        except ValueError as error:
            raise ValueError("Switch bridge URL has an invalid port or authority.") from error
        loopback = parsed.hostname in {"127.0.0.1", "::1", "localhost"}
        if (
            parsed.scheme not in ({"https", "http"} if loopback else {"https"})
            or not parsed.hostname
            or (port is not None and not 1 <= port <= 65535)
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("Switch bridge URL must be HTTPS, or loopback HTTP for local development.")
        if not _SAFE_ID.fullmatch(values["RELAY_SWITCH_AGENT_ID"]):
            raise ValueError("Switch agent ID has an invalid format.")
        if not _SAFE_ID.fullmatch(values["RELAY_SWITCH_ROOM_ID"]):
            raise ValueError("Switch room ID has an invalid format.")
        return cls(**{
            "base_url": values["RELAY_SWITCH_BASE_URL"].rstrip("/"),
            "agent_id": values["RELAY_SWITCH_AGENT_ID"],
            "room_id": values["RELAY_SWITCH_ROOM_ID"],
            "api_key": api_key,
        })


class SwitchRoomNotifier:
    """Publish deduplicated, content-minimal task status changes to one room."""

    def __init__(self, config: SwitchRoomConfig, client: httpx.Client | None = None):
        self._config = config
        self._client = client or httpx.Client(timeout=httpx.Timeout(3.0, connect=1.0))
        self._owns_client = client is None
        self._last_state: OrderedDict[str, tuple[str, str]] = OrderedDict()

    @classmethod
    def from_env(cls) -> "SwitchRoomNotifier | None":
        config = SwitchRoomConfig.from_env()
        return cls(config) if config else None

    def notify(
        self,
        task_id: str,
        stage: str,
        status: str,
        *,
        tests_passed: bool | None = None,
        security_assessment: str | None = None,
        recommendation: str | None = None,
    ) -> bool:
        if not _SAFE_ID.fullmatch(task_id) or stage not in _TASK_STAGES or status not in _TASK_STATES:
            return False
        state = (stage, status)
        if self._last_state.get(task_id) == state:
            self._last_state.move_to_end(task_id)
            return True
        final = status in _FINAL_STATES
        if final:
            test_result = "PASS" if tests_passed is True else "FAIL" if tests_passed is False else "NOT_RUN"
            security = security_assessment if security_assessment in _SECURITY_STATES else "NOT_REVIEWED"
            review = recommendation if recommendation in _REVIEW_STATES else "PENDING"
            gate = "Human approval is required before any repository action." if status == "AWAITING_HUMAN_APPROVAL" else ""
            content = (
                f"RELAY AI final report: task {task_id} is {status} at {stage}; "
                f"tests={test_result}, security={security}, review={review}. {gate}"
            ).strip()
        else:
            content = f"RELAY AI task {task_id}: {stage} — {status}."
        endpoint = (
            f"{self._config.base_url}/agents/{self._config.agent_id}/message"
        )
        try:
            with self._client.stream(
                "POST",
                endpoint,
                headers={"Authorization": f"Bearer {self._config.api_key}"},
                json={"room_id": self._config.room_id, "content": content},
            ) as response:
                if not 200 <= response.status_code < 300:
                    return False
        except httpx.HTTPError:
            # Never echo response bodies or request details; they may contain secrets.
            return False
        self._last_state[task_id] = state
        self._last_state.move_to_end(task_id)
        if len(self._last_state) > _MAX_CACHED_STATES:
            self._last_state.popitem(last=False)
        return True

    def close(self) -> None:
        if self._owns_client:
            self._client.close()
