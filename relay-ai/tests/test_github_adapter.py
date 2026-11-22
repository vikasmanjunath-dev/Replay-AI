import base64
import json

import httpx
import pytest

from github_adapter import GitHubAdapter, GitHubAdapterError, GitHubConfig


BASE = "1" * 40
HEAD = "2" * 40


def _config():
    return GitHubConfig(token="ghp_test_secret_do_not_log", repositories={"relay": "acme/relay"})


def test_configuration_fails_closed_for_partial_and_invalid_allow_lists(monkeypatch):
    monkeypatch.setenv("RELAY_GITHUB_TOKEN", "secret")
    monkeypatch.delenv("RELAY_GITHUB_REPOSITORIES_JSON", raising=False)
    with pytest.raises(RuntimeError, match="requires a token"):
        GitHubConfig.from_env()

    monkeypatch.setenv("RELAY_GITHUB_REPOSITORIES_JSON", json.dumps({"../oops": "acme/relay"}))
    with pytest.raises(RuntimeError, match="repository IDs"):
        GitHubConfig.from_env()

    config = _config()
    assert "ghp_test_secret" not in repr(config)
    with pytest.raises(GitHubAdapterError, match="not allow-listed"):
        config.repository("elsewhere")


def test_configuration_rejects_duplicate_repository_ids(monkeypatch):
    monkeypatch.setenv("RELAY_GITHUB_TOKEN", "secret")
    monkeypatch.setenv(
        "RELAY_GITHUB_REPOSITORIES_JSON",
        '{"relay":"acme/relay","relay":"attacker/other"}',
    )

    with pytest.raises(RuntimeError, match="without duplicate keys"):
        GitHubConfig.from_env()


def test_contents_reads_only_allow_listed_bounded_utf8_files():
    content = "safe file\n"

    def respond(request):
        assert request.url.path == "/repos/acme/relay/contents/src/main.py"
        assert request.url.params["ref"] == "a" * 40
        return httpx.Response(200, json={
            "type": "file", "encoding": "base64", "path": "src/main.py",
            "sha": "b" * 40, "content": base64.b64encode(content.encode()).decode(),
        })

    adapter = GitHubAdapter(_config(), transport=httpx.MockTransport(respond))
    try:
        result = adapter.get_contents("relay", "src/main.py", ref="a" * 40)
        assert result["content"] == content
        with pytest.raises(GitHubAdapterError, match="path is invalid"):
            adapter.get_contents("relay", "../secret")
        with pytest.raises(GitHubAdapterError, match="reference is invalid"):
            adapter.get_contents("relay", "src/main.py", ref="a" * 241)
        with pytest.raises(GitHubAdapterError, match="reference is invalid"):
            adapter.get_contents("relay", "src/main.py", ref="../private")
    finally:
        adapter.close()


def test_pull_request_creation_requires_approval_before_network_access():
    adapter = GitHubAdapter(_config(), transport=httpx.MockTransport(lambda _request: pytest.fail("network must not run")))
    try:
        with pytest.raises(GitHubAdapterError, match="Human approval is required"):
            adapter.create_pull_request(
                "relay", approved=False, head_branch="codex/fix", base_branch="main",
                expected_base_sha=BASE, expected_head_sha=HEAD, title="Fix", body="",
            )
    finally:
        adapter.close()


def test_pull_request_rejects_a_ref_component_with_trailing_dot_before_network_access():
    adapter = GitHubAdapter(_config(), transport=httpx.MockTransport(lambda _request: pytest.fail("network must not run")))
    try:
        with pytest.raises(GitHubAdapterError, match="Git branch name is invalid"):
            adapter.create_pull_request(
                "relay", approved=True, head_branch="codex./fix", base_branch="main",
                expected_base_sha=BASE, expected_head_sha=HEAD, title="Fix", body="",
            )
    finally:
        adapter.close()


def test_pull_request_verifies_exact_base_and_commit_before_opening():
    requests = []

    def respond(request):
        requests.append(request)
        if "/compare/" in request.url.path:
            return httpx.Response(200, json={
                "base_commit": {"sha": BASE}, "head_commit": {"sha": "3" * 40},
            })
        pytest.fail("must not list or create a pull request for a mismatched head")

    adapter = GitHubAdapter(_config(), transport=httpx.MockTransport(respond))
    try:
        with pytest.raises(GitHubAdapterError, match="revisions do not match"):
            adapter.create_pull_request(
                "relay", approved=True, head_branch="codex/fix", base_branch="main",
                expected_base_sha=BASE, expected_head_sha=HEAD, title="Fix", body="",
            )
        assert len(requests) == 1
        assert requests[0].method == "GET"
        assert "Authorization" in requests[0].headers
    finally:
        adapter.close()


def test_pull_request_is_idempotent_and_never_calls_merge_or_deploy():
    methods = []

    def respond(request):
        methods.append((request.method, request.url.path))
        if "/compare/" in request.url.path:
            return httpx.Response(200, json={
                "base_commit": {"sha": BASE}, "head_commit": {"sha": HEAD},
            })
        if request.url.path.endswith("/pulls") and request.method == "GET":
            return httpx.Response(200, json=[])
        if request.url.path.endswith("/pulls") and request.method == "POST":
            return httpx.Response(201, json={
                "number": 42, "html_url": "https://github.com/acme/relay/pull/42", "state": "open",
            })
        pytest.fail(f"unexpected GitHub API request: {request.method} {request.url.path}")

    adapter = GitHubAdapter(_config(), transport=httpx.MockTransport(respond))
    try:
        result = adapter.create_pull_request(
            "relay", approved=True, head_branch="codex/fix", base_branch="main",
            expected_base_sha=BASE, expected_head_sha=HEAD, title=" Fix ", body="reviewed change", draft=True,
        )
        assert result == {"number": 42, "url": "https://github.com/acme/relay/pull/42", "state": "open", "already_open": False}
        assert [method for method, _ in methods] == ["GET", "GET", "POST"]
        assert all("/merge" not in path and "/deploy" not in path for _, path in methods)
        post = methods[-1]
        assert post == ("POST", "/repos/acme/relay/pulls")
    finally:
        adapter.close()


def test_existing_open_pull_request_is_returned_without_duplicate_creation():
    def respond(request):
        if "/compare/" in request.url.path:
            return httpx.Response(200, json={"base_commit": {"sha": BASE}, "head_commit": {"sha": HEAD}})
        return httpx.Response(200, json=[{
            "number": 8, "html_url": "https://github.com/acme/relay/pull/8", "state": "open",
        }])

    adapter = GitHubAdapter(_config(), transport=httpx.MockTransport(respond))
    try:
        result = adapter.create_pull_request(
            "relay", approved=True, head_branch="codex/fix", base_branch="main",
            expected_base_sha=BASE, expected_head_sha=HEAD, title="Fix", body="",
        )
        assert result["number"] == 8
        assert result["already_open"] is True
    finally:
        adapter.close()


def test_oversized_github_responses_are_stopped_at_the_configured_bound():
    adapter = GitHubAdapter(
        _config(),
        transport=httpx.MockTransport(
            lambda _request: httpx.Response(200, content=b"x" * 1_000_001)
        ),
    )
    try:
        with pytest.raises(GitHubAdapterError, match="exceeded the configured size limit"):
            adapter.get_repository("relay")
    finally:
        adapter.close()


def test_upstream_errors_do_not_leak_response_bodies_or_follow_redirects():
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(
            403,
            content=b"ghp_test_secret_do_not_log",
            headers={"Location": "https://attacker.example/collect"},
        )

    adapter = GitHubAdapter(_config(), transport=httpx.MockTransport(respond))
    try:
        with pytest.raises(GitHubAdapterError) as error:
            adapter.get_repository("relay")
        assert str(error.value) == "GitHub request failed with HTTP 403."
        assert "ghp_test_secret" not in str(error.value)
        assert len(requests) == 1
        assert requests[0].url.host == "api.github.com"
    finally:
        adapter.close()


@pytest.mark.parametrize("result", [
    {"number": True, "html_url": "https://github.com/acme/relay/pull/1", "state": "open"},
    {"number": 0, "html_url": "https://github.com/acme/relay/pull/0", "state": "open"},
    {"number": 1, "html_url": "https://github.com/acme/relay/pull/1", "state": {"unexpected": "object"}},
    {"number": 1, "html_url": "https://github.com/acme/relay/pull/1", "state": "merged"},
])
def test_pull_request_response_rejects_invalid_numbers_and_states(result):
    with pytest.raises(GitHubAdapterError, match="invalid pull request result"):
        GitHubAdapter._pull_request_result(result, already_open=False)
