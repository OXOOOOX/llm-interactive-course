#!/usr/bin/env python3
"""Verify a running packaged homepage without following external links."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Dict, Optional, Sequence, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

# Verification runs directly from an immutable source snapshot on the server.
# Loading its sibling must not add __pycache__ files to that snapshot.
sys.dont_write_bytecode = True

TIMEOUT_SECONDS = 12
MAX_RESPONSE_BYTES = 64 * 1024 * 1024


def _load_package_module():
    path = Path(__file__).with_name("site-package.py")
    spec = importlib.util.spec_from_file_location("site_package", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load deploy/site-package.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):  # type: ignore[override]
        return None


def _base_url(value: str) -> str:
    parsed = urlsplit(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("base_url must be an http(s) origin")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("base_url must not contain credentials")
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise ValueError("base_url must be the site origin, without a path/query/fragment")
    try:
        _ = parsed.port
    except ValueError as exc:
        raise ValueError("base_url contains an invalid port") from exc
    return f"{parsed.scheme}://{parsed.netloc}"


def _url_for(base: str, path: str) -> str:
    encoded = quote(path.lstrip("/"), safe="/-._~")
    return base + "/" + encoded


def _read_response(response) -> bytes:
    data = bytearray()
    while True:
        chunk = response.read(1024 * 1024)
        if not chunk:
            break
        data.extend(chunk)
        if len(data) > MAX_RESPONSE_BYTES:
            raise ValueError("HTTP response exceeds verification size limit")
    return bytes(data)


def _fetch(opener, base: str, path: str) -> Tuple[int, object, bytes]:
    request = Request(
        _url_for(base, path),
        headers={"Accept-Encoding": "identity", "User-Agent": "homepage-site-verify/1"},
    )
    try:
        response = opener.open(request, timeout=TIMEOUT_SECONDS)
    except HTTPError as error:
        response = error
    except (OSError, URLError) as exc:
        raise ValueError(f"request failed for {path}: {exc}") from exc
    try:
        body = _read_response(response)
        status = int(getattr(response, "status", getattr(response, "code", 0)))
        return status, response.headers, body
    finally:
        response.close()


def _check_headers(headers, expected) -> None:
    for entry in expected:
        name = entry["name"]
        actual = headers.get(name)
        if actual != entry["value"]:
            raise ValueError(f"response header {name!r} expected {entry['value']!r}, got {actual!r}")


def verify(base_value: str, manifest_path_value: str) -> Dict[str, object]:
    package = _load_package_module()
    base = _base_url(base_value)
    manifest_path = Path(manifest_path_value)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not read site manifest: {exc}") from exc
    manifest = package.validate_manifest(manifest)

    opener = build_opener(ProxyHandler({}), _NoRedirect())
    headers = manifest["headers"]
    status, response_headers, _body = _fetch(opener, base, "/")
    if status != 302:
        raise ValueError(f"root request expected 302, got {status}")
    expected_location = manifest["redirect"]["location"]
    location = response_headers.get("Location")
    if location != expected_location:
        raise ValueError(f"root Location expected {expected_location!r}, got {location!r}")
    _check_headers(response_headers, headers)

    health = manifest["health"]
    health_status, health_headers, health_body = _fetch(opener, base, health["path"])
    if health_status != health["status"]:
        raise ValueError(f"health endpoint expected {health['status']}, got {health_status}")
    if health_body != health["body"].encode("utf-8"):
        raise ValueError("health endpoint body does not equal HOME_OK")
    content_type = health_headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
    if content_type != "text/plain":
        raise ValueError(f"health endpoint content type is not text/plain: {content_type!r}")
    _check_headers(health_headers, headers)

    checked = 0
    html_checked = 0
    byte_count = 0
    for entry in manifest["files"]:
        path = entry["path"]
        file_status, file_headers, body = _fetch(opener, base, "/" + path)
        if file_status != 200:
            raise ValueError(f"{path} expected 200, got {file_status}")
        digest = hashlib.sha256(body).hexdigest()
        if digest != entry["sha256"]:
            raise ValueError(f"SHA-256 mismatch for {path}")
        if len(body) != entry["size"]:
            raise ValueError(f"byte-size mismatch for {path}")
        _check_headers(file_headers, headers)
        checked += 1
        byte_count += len(body)
        if path.lower().endswith((".html", ".htm")):
            html_checked += 1

    return {
        "ok": True,
        "base_url": base,
        "root_status": status,
        "health_status": health_status,
        "files_checked": checked,
        "html_checked": html_checked,
        "bytes_checked": byte_count,
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url")
    parser.add_argument("manifest")
    args = parser.parse_args(argv)
    try:
        result = verify(args.base_url, args.manifest)
    except (OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
