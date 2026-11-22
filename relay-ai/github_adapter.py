"""Least-privilege GitHub REST adapter for verified, already-published commits.

The adapter never pushes, merges, or deploys. Opening a pull request requires an
explicit approval flag and an exact match for the task's base and commit SHAs.
"""

from __future__ import annotations

import json
import os
import re
import base64
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote

import httpx


_REPOSITORY_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")
_OWNER_REPO = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?/[A-Za-z0-9](?:[A-Za-z0-9_.-]{0,98}[A-Za-z0-9])?$")
_BRANCH_INVALID = re.compile(r"[\x00-\x20~^:?*\[\\]")
_SHA = re.compile(r"^[0-9a-f]{40}$")
_MAX_RESPONSE_BYTES = 1_000_000


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def _valid_git_ref(value: str) -> bool:
    components = value.split("/") if isinstance(value, str) else []
    return bool(
        isinstance(value, str) and 1 <= len(value) <= 240
        and not value.startswith("-") and not value.startswith("/") and not value.endswith("/")
        and "//" not in value and ".." not in value and "@{" not in value and value != "@"
        and not value.endswith(".") and not _BRANCH_INVALID.search(value)
        and not any(
            component.startswith(".") or component.endswith(".") or component.lower().endswith(".lock")
            for component in components
        )
    )


class GitHubAdapterError(RuntimeError):
    """Safe-to-display adapter failure without upstream body or credential details."""


@dataclass(frozen=True)
class GitHubConfig:
    token: str = field(repr=False)
    repositories: dict[str, str]
    api_url: str = "https://api.github.com"

    @classmethod
    def from_env(cls) -> "GitHubConfig | None":
        token = os.environ.get("RELAY_GITHUB_TOKEN", "")
        raw_repositories = os.environ.get("RELAY_GITHUB_REPOSITORIES_JSON", "")
        if not token and not raw_repositories:
            return None
        if not token or not raw_repositories or len(token) > 512 or any(c.isspace() for c in token):
            raise RuntimeError("GitHub configuration requires a token and repository allow-list.")
        if len(raw_repositories) > 16_000:
            raise RuntimeError("GitHub repository allow-list exceeds the configuration size limit.")
        try:
            repositories = json.loads(raw_repositories, object_pairs_hook=_unique_json_object)
        except (json.JSONDecodeError, ValueError) as error:
            raise RuntimeError("RELAY_GITHUB_REPOSITORIES_JSON must be a valid JSON object without duplicate keys.") from error
        if not isinstance(repositories, dict) or not 1 <= len(repositories) <= 50:
            raise RuntimeError("GitHub repository allow-list must contain 1..50 repositories.")
        checked: dict[str, str] = {}
        for repository_id, full_name in repositories.items():
            if not isinstance(repository_id, str) or not _REPOSITORY_ID.fullmatch(repository_id):
                raise RuntimeError("GitHub repository IDs must be 1..64 safe identifier characters.")
            if not isinstance(full_name, str) or not _OWNER_REPO.fullmatch(full_name):
                raise RuntimeError("GitHub repositories must use the owner/repository form.")
            checked[repository_id] = full_name
        return cls(token=token, repositories=checked)

    def repository(self, repository_id: str) -> str:
        try:
            return self.repositories[repository_id]
        except KeyError as error:
            raise GitHubAdapterError("GitHub repository is not allow-listed.") from error


class GitHubAdapter:
    def __init__(self, config: GitHubConfig, *, transport: httpx.BaseTransport | None = None):
        self._config = config
        self._client = httpx.Client(
            base_url=config.api_url,
            timeout=httpx.Timeout(5.0, connect=2.0),
            follow_redirects=False,
            trust_env=False,
            transport=transport,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {config.token}",
                "X-GitHub-Api-Version": "2026-03-10",
                "User-Agent": "RELAY-AI",
            },
        )

    def close(self) -> None:
        self._client.close()

    def _request(self, method: str, path: str, *, json_body: dict[str, Any] | None = None, params: dict[str, str] | None = None) -> Any:
        try:
            with self._client.stream(method, path, json=json_body, params=params) as response:
                content = bytearray()
                for chunk in response.iter_bytes():
                    if len(content) + len(chunk) > _MAX_RESPONSE_BYTES:
                        raise GitHubAdapterError("GitHub response exceeded the configured size limit.")
                    content.extend(chunk)
                status_code = response.status_code
            if not 200 <= status_code < 300:
                raise GitHubAdapterError(f"GitHub request failed with HTTP {status_code}.")
            try:
                return json.loads(content)
            except (ValueError, TypeError) as error:
                raise GitHubAdapterError("GitHub returned an invalid response.") from error
        except httpx.TimeoutException as error:
            raise GitHubAdapterError("GitHub request timed out.") from error
        except httpx.RequestError as error:
            raise GitHubAdapterError("GitHub request could not be completed.") from error

    def get_repository(self, repository_id: str) -> dict[str, Any]:
        full_name = self._config.repository(repository_id)
        owner, name = full_name.split("/", 1)
        data = self._request("GET", f"/repos/{quote(owner, safe='')}/{quote(name, safe='')}")
        if not isinstance(data, dict):
            raise GitHubAdapterError("GitHub returned invalid repository metadata.")
        return {key: data.get(key) for key in ("id", "full_name", "private", "default_branch", "html_url")}

    def get_contents(self, repository_id: str, file_path: str, *, ref: str | None = None) -> dict[str, Any]:
        if not isinstance(file_path, str) or not file_path or len(file_path) > 500 or file_path.startswith("/"):
            raise GitHubAdapterError("Repository path is invalid.")
        if ref is not None and not _valid_git_ref(ref):
            raise GitHubAdapterError("Git reference is invalid.")
        pieces = file_path.split("/")
        if any(piece in {"", ".", ".."} or "\\" in piece for piece in pieces):
            raise GitHubAdapterError("Repository path is invalid.")
        full_name = self._config.repository(repository_id)
        owner, name = full_name.split("/", 1)
        path = "/".join(quote(piece, safe="") for piece in pieces)
        params = {"ref": ref} if ref else None
        data = self._request("GET", f"/repos/{quote(owner, safe='')}/{quote(name, safe='')}/contents/{path}", params=params)
        if (
            not isinstance(data, dict) or data.get("type") != "file"
            or data.get("encoding") != "base64" or not isinstance(data.get("content"), str)
        ):
            raise GitHubAdapterError("Requested GitHub content is not a supported file.")
        try:
            encoded = re.sub(r"\s+", "", data.get("content", ""))
            raw = base64.b64decode(encoded, validate=True)
            content = raw.decode("utf-8")
        except (ValueError, UnicodeDecodeError) as error:
            raise GitHubAdapterError("GitHub file is not valid UTF-8 text.") from error
        if len(raw) > 256_000:
            raise GitHubAdapterError("GitHub file exceeds the 256 KiB read limit.")
        return {"path": data.get("path"), "sha": data.get("sha"), "size": len(raw), "content": content}

    def create_pull_request(
        self,
        repository_id: str,
        *,
        approved: bool,
        head_branch: str,
        base_branch: str,
        expected_base_sha: str,
        expected_head_sha: str,
        title: str,
        body: str,
        draft: bool = False,
    ) -> dict[str, Any]:
        if approved is not True:
            raise GitHubAdapterError("Human approval is required before opening a pull request.")
        for branch in (head_branch, base_branch):
            if not _valid_git_ref(branch):
                raise GitHubAdapterError("Git branch name is invalid.")
        if not _SHA.fullmatch(expected_base_sha) or not _SHA.fullmatch(expected_head_sha):
            raise GitHubAdapterError("Expected Git revisions must be full 40-character SHA-1 IDs.")
        if expected_base_sha == expected_head_sha:
            raise GitHubAdapterError("Pull request head and base revisions must differ.")
        if not isinstance(title, str) or not title.strip() or len(title) > 200 or any(ord(c) < 32 for c in title):
            raise GitHubAdapterError("Pull request title is invalid.")
        if not isinstance(body, str) or len(body) > 20_000:
            raise GitHubAdapterError("Pull request body exceeds the 20,000-character limit.")

        full_name = self._config.repository(repository_id)
        owner, name = full_name.split("/", 1)
        repo_path = f"/repos/{quote(owner, safe='')}/{quote(name, safe='')}"
        compare = self._request(
            "GET", f"{repo_path}/compare/{quote(base_branch, safe='')}...{quote(head_branch, safe='')}"
        )
        base = compare.get("base_commit", {}).get("sha") if isinstance(compare, dict) else None
        head = compare.get("head_commit", {}).get("sha") if isinstance(compare, dict) else None
        if base != expected_base_sha or head != expected_head_sha:
            raise GitHubAdapterError("GitHub branch revisions do not match the approved task revisions.")

        params = {"state": "open", "head": f"{owner}:{head_branch}", "base": base_branch, "per_page": "100"}
        existing = self._request("GET", f"{repo_path}/pulls", params=params)
        if not isinstance(existing, list):
            raise GitHubAdapterError("GitHub returned an invalid pull request list.")
        if len(existing) > 1:
            raise GitHubAdapterError("Multiple open pull requests already exist for this head and base.")
        if existing:
            pr = existing[0]
            return self._pull_request_result(pr, already_open=True)

        created = self._request("POST", f"{repo_path}/pulls", json_body={
            "title": title.strip(), "head": head_branch, "base": base_branch,
            "body": body, "draft": bool(draft),
        })
        return self._pull_request_result(created, already_open=False)

    @staticmethod
    def _pull_request_result(data: Any, *, already_open: bool) -> dict[str, Any]:
        number = data.get("number") if isinstance(data, dict) else None
        state = data.get("state", "open") if isinstance(data, dict) else None
        if (
            not isinstance(data, dict)
            or isinstance(number, bool)
            or not isinstance(number, int)
            or number < 1
            or not isinstance(data.get("html_url"), str)
            or not data["html_url"].startswith("https://github.com/")
            or not isinstance(state, str)
            or state not in {"open", "closed"}
        ):
            raise GitHubAdapterError("GitHub returned an invalid pull request result.")
        return {
            "number": number,
            "url": data["html_url"],
            "state": state,
            "already_open": already_open,
        }
