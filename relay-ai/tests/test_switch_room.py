from __future__ import annotations

import logging
from types import SimpleNamespace

import httpx
import pytest
import json

import switch_room
from schemas import PipelineStatus
from switch_room import SwitchRoomConfig, SwitchRoomNotifier
from worker import PipelineWorker


def config(**overrides):
    values = {
        "base_url": "https://switch.example.test",
        "agent_id": "relay-agent",
        "room_id": "room-123",
        "api_key": "test-secret-never-log",
    }
    values.update(overrides)
    return SwitchRoomConfig(**values)


def test_posts_only_minimal_progress_to_documented_agent_message_route():
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(200, json={"message_id": "message-1"})

    client = httpx.Client(transport=httpx.MockTransport(handle))
    notifier = SwitchRoomNotifier(config(), client=client)

    assert notifier.notify("task-1", "STAGE_A_TRIAGE", "RUNNING") is True
    assert len(requests) == 1
    request = requests[0]
    assert request.method == "POST"
    assert request.url.path == "/agents/relay-agent/message"
    assert request.headers["Authorization"] == "Bearer test-secret-never-log"
    body = json.loads(request.read())
    assert body == {
        "room_id": "room-123",
        "content": "RELAY AI task task-1: STAGE_A_TRIAGE — RUNNING.",
    }
    assert b"test-secret-never-log" not in request.read()
    client.close()


def test_notifier_does_not_buffer_unused_switch_response_body():
    class TrackingStream(httpx.SyncByteStream):
        def __init__(self):
            self.consumed = False
            self.closed = False

        def __iter__(self):
            self.consumed = True
            yield b"unused response" * 100_000

        def close(self):
            self.closed = True

    stream = TrackingStream()
    client = httpx.Client(
        transport=httpx.MockTransport(lambda _request: httpx.Response(200, stream=stream))
    )
    notifier = SwitchRoomNotifier(config(), client=client)

    assert notifier.notify("task-stream", "STAGE_A_TRIAGE", "RUNNING") is True
    assert stream.consumed is False
    assert stream.closed is True
    client.close()


def test_deduplicates_progress_and_final_status_explains_approval_gate():
    bodies = []

    def handle(request):
        bodies.append(request.read())
        return httpx.Response(200)

    client = httpx.Client(transport=httpx.MockTransport(handle))
    notifier = SwitchRoomNotifier(config(), client=client)

    assert notifier.notify("task-2", "STAGE_A_TRIAGE", "RUNNING")
    assert notifier.notify("task-2", "STAGE_A_TRIAGE", "RUNNING")
    assert notifier.notify(
        "task-2",
        "AWAITING_HUMAN_APPROVAL",
        "AWAITING_HUMAN_APPROVAL",
        tests_passed=True,
        security_assessment="PASS",
        recommendation="APPROVE",
    )
    assert notifier.notify(
        "task-2",
        "AWAITING_HUMAN_APPROVAL",
        "AWAITING_HUMAN_APPROVAL",
        tests_passed=True,
        security_assessment="PASS",
        recommendation="APPROVE",
    )
    assert len(bodies) == 2
    final_report = json.loads(bodies[-1])["content"]
    assert "tests=PASS, security=PASS, review=APPROVE" in final_report
    assert "Human approval is required" in final_report
    client.close()


def test_delivery_error_is_safe_and_does_not_escape():
    def handle(_request):
        return httpx.Response(503, text="secret-bearing upstream diagnostic")

    client = httpx.Client(transport=httpx.MockTransport(handle))
    notifier = SwitchRoomNotifier(config(), client=client)

    assert notifier.notify("task-3", "STAGE_A_TRIAGE", "RUNNING") is False
    client.close()


def test_failed_delivery_is_not_marked_delivered_and_can_be_retried():
    attempts = 0

    def handle(_request):
        nonlocal attempts
        attempts += 1
        return httpx.Response(503 if attempts == 1 else 200)

    client = httpx.Client(transport=httpx.MockTransport(handle))
    notifier = SwitchRoomNotifier(config(), client=client)

    assert notifier.notify("task-retry", "STAGE_A_TRIAGE", "RUNNING") is False
    assert notifier.notify("task-retry", "STAGE_A_TRIAGE", "RUNNING") is True
    assert attempts == 2
    client.close()


def test_successful_state_deduplication_cache_is_bounded(monkeypatch):
    monkeypatch.setattr(switch_room, "_MAX_CACHED_STATES", 2)
    client = httpx.Client(transport=httpx.MockTransport(lambda _request: httpx.Response(200)))
    notifier = SwitchRoomNotifier(config(), client=client)

    for task_id in ("task-a", "task-b", "task-c"):
        assert notifier.notify(task_id, "STAGE_A_TRIAGE", "RUNNING") is True

    assert len(notifier._last_state) == 2
    assert list(notifier._last_state) == ["task-b", "task-c"]
    client.close()


@pytest.mark.parametrize("raise_error", [False, True])
def test_worker_logs_safe_warning_when_delivery_fails(caplog, raise_error):
    class FailedNotifier:
        def notify(self, *_args, **_kwargs):
            if raise_error:
                raise RuntimeError("credential=worker-secret-do-not-log")
            return False

    worker = PipelineWorker(None, None, FailedNotifier())
    task = SimpleNamespace(
        task_id="task-delivery-failed",
        current_stage="STAGE_A_TRIAGE",
        status=PipelineStatus.RUNNING,
        sandbox_result=None,
        reviewer=None,
    )

    with caplog.at_level(logging.WARNING, logger="relay.worker"):
        worker._notify_room_progress(task)

    assert len(caplog.records) == 1
    assert caplog.records[0].getMessage() == "Switch room progress delivery failed"
    assert caplog.records[0].task_id == "task-delivery-failed"
    assert "worker-secret-do-not-log" not in caplog.text


def test_unrecognized_stage_is_rejected_without_delivery():
    calls = []
    client = httpx.Client(transport=httpx.MockTransport(lambda request: calls.append(request)))
    notifier = SwitchRoomNotifier(config(), client=client)

    assert notifier.notify("task-4", "AI_GENERATED_CONTENT", "RUNNING") is False
    assert calls == []
    client.close()


@pytest.mark.parametrize(
    "values",
    [
        {"RELAY_SWITCH_BASE_URL": "https://switch.example.test"},
        {
            "RELAY_SWITCH_BASE_URL": "http://switch.example.test",
            "RELAY_SWITCH_AGENT_ID": "relay-agent",
            "RELAY_SWITCH_ROOM_ID": "room-1",
            "RELAY_SWITCH_API_KEY": "secret",
        },
        {
            "RELAY_SWITCH_BASE_URL": "https://user:pass@switch.example.test",
            "RELAY_SWITCH_AGENT_ID": "relay-agent",
            "RELAY_SWITCH_ROOM_ID": "room-1",
            "RELAY_SWITCH_API_KEY": "secret",
        },
        {
            "RELAY_SWITCH_BASE_URL": "https://switch.example.test:0",
            "RELAY_SWITCH_AGENT_ID": "relay-agent",
            "RELAY_SWITCH_ROOM_ID": "room-1",
            "RELAY_SWITCH_API_KEY": "secret",
        },
        {
            "RELAY_SWITCH_BASE_URL": "https://switch.example.test:65536",
            "RELAY_SWITCH_AGENT_ID": "relay-agent",
            "RELAY_SWITCH_ROOM_ID": "room-1",
            "RELAY_SWITCH_API_KEY": "secret",
        },
        {
            "RELAY_SWITCH_BASE_URL": "https://switch.example.test\n.attacker.invalid",
            "RELAY_SWITCH_AGENT_ID": "relay-agent",
            "RELAY_SWITCH_ROOM_ID": "room-1",
            "RELAY_SWITCH_API_KEY": "secret",
        },
        {
            "RELAY_SWITCH_BASE_URL": "x" * 2049,
            "RELAY_SWITCH_AGENT_ID": "relay-agent",
            "RELAY_SWITCH_ROOM_ID": "room-1",
            "RELAY_SWITCH_API_KEY": "secret",
        },
    ],
)
def test_invalid_or_partial_configuration_fails_closed(monkeypatch, values):
    for name in (
        "RELAY_SWITCH_BASE_URL",
        "RELAY_SWITCH_AGENT_ID",
        "RELAY_SWITCH_ROOM_ID",
        "RELAY_SWITCH_API_KEY",
    ):
        monkeypatch.delenv(name, raising=False)
    for name, value in values.items():
        monkeypatch.setenv(name, value)

    with pytest.raises(ValueError):
        SwitchRoomConfig.from_env()


@pytest.mark.parametrize("api_key", ["secret with space", "s" * 513, "sëcret"])
def test_invalid_or_oversized_agent_api_key_fails_closed(monkeypatch, api_key):
    monkeypatch.setenv("RELAY_SWITCH_BASE_URL", "https://switch.example.test")
    monkeypatch.setenv("RELAY_SWITCH_AGENT_ID", "relay-agent")
    monkeypatch.setenv("RELAY_SWITCH_ROOM_ID", "room-1")
    monkeypatch.setenv("RELAY_SWITCH_API_KEY", api_key)

    with pytest.raises(ValueError, match="visible ASCII and no longer than 512 characters"):
        SwitchRoomConfig.from_env()


def test_switch_agent_api_key_is_not_exposed_by_config_repr(monkeypatch):
    secret = "switch-sentinel-never-log"
    monkeypatch.setenv("RELAY_SWITCH_BASE_URL", "https://switch.example.test")
    monkeypatch.setenv("RELAY_SWITCH_AGENT_ID", "relay-agent")
    monkeypatch.setenv("RELAY_SWITCH_ROOM_ID", "room-1")
    monkeypatch.setenv("RELAY_SWITCH_API_KEY", secret)

    config = SwitchRoomConfig.from_env()

    assert config is not None
    assert secret not in repr(config)
