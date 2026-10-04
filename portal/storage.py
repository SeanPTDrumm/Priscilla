from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import base64
import json
import urllib.error
import urllib.parse
import urllib.request

import streamlit as st


@dataclass
class SaveResult:
    ok: bool
    persisted: bool
    message: str


def _github_config() -> tuple[str, str, str]:
    try:
        token = str(st.secrets.get("GITHUB_TOKEN", "")).strip()
        repo = str(st.secrets.get("GITHUB_REPO", "")).strip()
        branch = str(st.secrets.get("GITHUB_BRANCH", "main")).strip() or "main"
    except Exception:
        token, repo, branch = "", "", "main"
    return token, repo, branch


def github_enabled() -> bool:
    token, repo, _ = _github_config()
    return bool(token and repo)


def editor_password() -> str:
    try:
        return str(st.secrets.get("EDITOR_PASSWORD", ""))
    except Exception:
        return ""


def _api_request(url: str, token: str, method: str = "GET", payload: dict | None = None):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "Priscilla-Player-Portal",
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, headers=headers, data=data, method=method)
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _save_to_github(relative_path: str, payload_bytes: bytes, message: str) -> tuple[bool, str]:
    token, repo, branch = _github_config()
    if not token or not repo:
        return False, "GitHub persistence is not configured."

    quoted_path = "/".join(urllib.parse.quote(part) for part in relative_path.split("/"))
    base_url = f"https://api.github.com/repos/{repo}/contents/{quoted_path}"

    sha = None
    try:
        current = _api_request(f"{base_url}?ref={urllib.parse.quote(branch)}", token)
        sha = current.get("sha")
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            try:
                detail = exc.read().decode("utf-8")
            except Exception:
                detail = str(exc)
            return False, f"GitHub read failed: {detail}"
    except Exception as exc:
        return False, f"Could not reach GitHub: {exc}"

    body = {
        "message": message,
        "content": base64.b64encode(payload_bytes).decode("ascii"),
        "branch": branch,
    }
    if sha:
        body["sha"] = sha

    try:
        result = _api_request(base_url, token, method="PUT", payload=body)
        commit_sha = (result.get("commit") or {}).get("sha", "")
        suffix = f" ({commit_sha[:7]})" if commit_sha else ""
        return True, f"Saved permanently to GitHub{suffix}."
    except urllib.error.HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8")
        except Exception:
            detail = str(exc)
        return False, f"GitHub rejected the save: {detail}"
    except Exception as exc:
        return False, f"Could not save to GitHub: {exc}"


def save_bytes(root: Path, relative_path: str, data: bytes, message: str) -> SaveResult:
    local_path = root / relative_path
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_bytes(data)

    if not github_enabled():
        return SaveResult(
            ok=True,
            persisted=False,
            message="Saved in the running app. Add GitHub Secrets once to make edits survive redeploys.",
        )

    ok, msg = _save_to_github(relative_path, data, message)
    return SaveResult(ok=ok, persisted=ok, message=msg)


def save_text(root: Path, relative_path: str, text: str, message: str) -> SaveResult:
    return save_bytes(root, relative_path, text.encode("utf-8"), message)


def show_save_result(result: SaveResult) -> None:
    if result.ok and result.persisted:
        st.success(result.message)
    elif result.ok:
        st.warning(result.message)
    else:
        st.error(result.message)
