#!/usr/bin/env python3
"""Check and package the static homepage for the server-side Caddy image.

The input is deliberately treated as an already materialized source snapshot.
No Git command, build tool, or network access is needed here.  The package
contains only the public site under ``out/site``; Caddy configuration and the
manifest stay beside that webroot.
"""

from __future__ import annotations

import argparse
import hashlib
import html.parser
import json
import os
import posixpath
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple
from urllib.parse import unquote, urlsplit


MANIFEST_FORMAT = 1
HEALTH_PATH = "__deploy_health"
HEALTH_BODY = "HOME_OK"
HEALTH_CONTENT_TYPE = "text/plain; charset=utf-8"
HEADER_NAME_RE = re.compile(r"^[!#$%&'*+\-.^_`|~0-9A-Za-z]+$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

# These are repository/deployment metadata rather than public site content.
# _headers and _redirects are parsed into the generated Caddyfile instead of
# being copied into the webroot.  README.md, skill docs and lesson exercises
# are intentionally retained as public files.  Dot files/directories are
# treated as repository or deployment metadata and are never public.
SITE_METADATA_FILES = frozenset({".gitignore", "_headers", "_redirects"})
EXCLUDED_ROOT_DIRS = frozenset({".git", ".github", "artifacts", "deploy"})
EXCLUDED_DIR_NAMES = frozenset({".git", ".github", ".ssh", ".venv", "__pycache__", "node_modules", "secrets", "vendor"})
SECRET_FILE_NAMES = frozenset({"authorized_keys", "id_rsa", "id_ed25519", "known_hosts"})
SECRET_SUFFIXES = (".pem", ".key", ".p12", ".pfx", ".der", ".crt")
KNOWN_MISSING_DOCUMENT_LINKS = frozenset(
    {
        (
            "courses/浪漫主义古典音乐/01-classical-to-romantic/lesson.html",
            "courses/浪漫主义古典音乐/02-beethoven/lesson.html",
        ),
    }
)


class PackageError(ValueError):
    """A deterministic source or package validation failure."""


def _as_path(value: str) -> Path:
    path = Path(value)
    if not path.exists() or not path.is_dir() or path.is_symlink():
        raise PackageError(f"source must be a real directory: {value}")
    return path.resolve()


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _relative(path: Path) -> str:
    return path.as_posix()


def _parts(path: str) -> Tuple[str, ...]:
    return tuple(part for part in path.replace("\\", "/").split("/") if part)


def _is_secret_path(rel: str) -> bool:
    parts = _parts(rel)
    if not parts:
        return False
    if any(part in {".ssh", "secrets", "secret"} for part in parts[:-1]):
        return True
    name = parts[-1]
    if name == ".env" or (name.startswith(".env.") and name != ".env.example"):
        return True
    if name in SECRET_FILE_NAMES:
        return True
    lowered = name.lower()
    return lowered.endswith(SECRET_SUFFIXES)


def _is_excluded(rel: str) -> bool:
    parts = _parts(rel)
    if not parts:
        return False
    if any(part.startswith(".") for part in parts):
        return True
    if parts[0] in EXCLUDED_ROOT_DIRS:
        return True
    if any(part in EXCLUDED_DIR_NAMES for part in parts[:-1]):
        return True
    if parts[-1] in SITE_METADATA_FILES:
        return True
    if parts[-1].endswith(".pyc"):
        return True
    return _is_secret_path(rel)


def _read_utf8(path: Path) -> str:
    try:
        return path.read_bytes().decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise PackageError(f"{path} is not valid UTF-8: {exc}") from exc


def _validate_header_entries(entries: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    result: List[Dict[str, str]] = []
    names: Set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"name", "value"}:
            raise PackageError("header entries must contain only name and value")
        name = entry["name"]
        value = entry["value"]
        if not isinstance(name, str) or not HEADER_NAME_RE.fullmatch(name):
            raise PackageError(f"invalid response header name: {name!r}")
        if not isinstance(value, str) or any(ord(char) < 0x20 or ord(char) == 0x7F for char in value):
            raise PackageError(f"invalid response header value for {name}")
        folded = name.lower()
        if folded in names:
            raise PackageError(f"duplicate response header: {name}")
        names.add(folded)
        result.append({"name": name, "value": value})
    return result


def parse_headers(path: Path) -> List[Dict[str, str]]:
    """Parse only the repository's single global ``/*`` header block."""

    text = _read_utf8(path)
    lines = text.splitlines()
    if not lines or lines[0].strip() != "/*":
        raise PackageError("_headers must start with a single global /* block")

    entries: List[Dict[str, str]] = []
    for number, raw in enumerate(lines[1:], start=2):
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped == "}":
            raise PackageError(f"Caddy-style _headers closing brace is not supported at line {number}")
        match = re.fullmatch(r"[ \t]*([^:]+):[ \t]*(.*?)[ \t]*", raw)
        if not match:
            raise PackageError(f"unsupported _headers syntax at line {number}")
        name, value = match.groups()
        name = name.strip()
        value = value.strip()
        if not HEADER_NAME_RE.fullmatch(name):
            raise PackageError(f"invalid _headers name at line {number}: {name!r}")
        if any(ord(char) < 0x20 or ord(char) == 0x7F for char in value):
            raise PackageError(f"control character in _headers at line {number}")
        entries.append({"name": name, "value": value})

    if not entries:
        raise PackageError("_headers global block contains no headers")
    return _validate_header_entries(entries)


def parse_redirects(path: Path) -> Dict[str, object]:
    """Parse the one root 302 rule used by the existing static site."""

    text = _read_utf8(path)
    rules: List[Tuple[str, str, int]] = []
    for number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        fields = stripped.split()
        if len(fields) != 3 or fields[0] != "/" or fields[2] != "302":
            raise PackageError(f"unsupported _redirects syntax at line {number}")
        location = fields[1]
        parsed = urlsplit(location)
        if not location.startswith("/") or location.startswith("//") or parsed.scheme or parsed.netloc:
            raise PackageError(f"_redirects target must be a local path at line {number}")
        if any(char.isspace() for char in location):
            raise PackageError(f"whitespace in _redirects target at line {number}")
        rules.append((fields[0], location, 302))
    if len(rules) != 1:
        raise PackageError("_redirects must contain exactly one root 302 rule")
    path_value, location, status = rules[0]
    return {"path": path_value, "location": location, "status": status}


class _HTMLReferenceParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: List[Tuple[str, str, str]] = []

    def _collect(self, tag: str, attrs: Sequence[Tuple[str, Optional[str]]]) -> None:
        for name, value in attrs:
            if name.lower() in {"href", "src"} and value is not None:
                self.references.append((tag.lower(), name.lower(), value))

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        self._collect(tag, attrs)

    def handle_startendtag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        self._collect(tag, attrs)


def _normalize_reference(raw: str, current: str) -> Optional[str]:
    """Normalize a local URL without requiring its target to exist."""

    if not raw or raw.startswith("#"):
        return None
    parsed = urlsplit(raw)
    if parsed.scheme or parsed.netloc:
        return None
    try:
        decoded = unquote(parsed.path, encoding="utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise PackageError(f"invalid UTF-8 URL reference {raw!r} in {current}") from exc
    if not decoded:
        return current
    trailing_slash = decoded.endswith("/")
    if decoded.startswith("/"):
        joined = decoded.lstrip("/")
    else:
        joined = posixpath.join(posixpath.dirname(current), decoded)
    normalized = posixpath.normpath(joined)
    if normalized in {"", "."}:
        normalized = "index.html"
    if normalized == ".." or normalized.startswith("../") or normalized.startswith("/"):
        raise PackageError(f"local URL escapes the site root: {raw!r} in {current}")
    if trailing_slash:
        normalized = normalized.rstrip("/") + "/index.html"
    return normalized


def _resolve_reference(raw: str, current: str, available: Set[str]) -> Optional[str]:
    """Return a normalized local site path, or None for an external URL."""

    normalized = _normalize_reference(raw, current)
    if normalized is None:
        return None
    if normalized in available:
        return normalized
    if normalized + "/index.html" in available:
        return normalized + "/index.html"
    raise PackageError(f"missing local resource {raw!r} referenced by {current}")


def _collect_files(source: Path) -> Dict[str, Path]:
    files: Dict[str, Path] = {}
    for root, directories, names in os.walk(source, topdown=True, followlinks=False):
        root_path = Path(root)
        directories.sort()
        names.sort()
        kept_directories: List[str] = []
        for name in directories:
            path = root_path / name
            rel = _relative(path.relative_to(source))
            if _is_excluded(rel):
                continue
            if path.is_symlink():
                raise PackageError(f"symlink directory is not allowed in the site source: {rel}")
            kept_directories.append(name)
        directories[:] = kept_directories
        for name in names:
            path = root_path / name
            rel = _relative(path.relative_to(source))
            if _is_excluded(rel):
                continue
            if path.is_symlink():
                raise PackageError(f"symlink file is not allowed in the site source: {rel}")
            if not path.is_file():
                raise PackageError(f"unsupported non-regular site entry: {rel}")
            files[rel] = path
    return dict(sorted(files.items()))


def _parse_html_references(files: Dict[str, Path]) -> Tuple[int, List[Dict[str, str]]]:
    available = set(files)
    count = 0
    missing: Dict[Tuple[str, str], Dict[str, str]] = {}
    for rel, path in files.items():
        if path.suffix.lower() not in {".html", ".htm"}:
            continue
        try:
            text = path.read_bytes().decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise PackageError(f"HTML file is not UTF-8: {rel}") from exc
        parser = _HTMLReferenceParser()
        try:
            parser.feed(text)
            parser.close()
        except Exception as exc:  # HTMLParser errors are source validation errors.
            raise PackageError(f"could not parse HTML file {rel}: {exc}") from exc
        for tag, attribute, reference in parser.references:
            normalized = _normalize_reference(reference, rel)
            try:
                _resolve_reference(reference, rel, available)
            except PackageError:
                if (
                    tag == "a"
                    and attribute == "href"
                    and normalized is not None
                    and normalized.lower().endswith((".html", ".htm"))
                    and (rel, normalized) in KNOWN_MISSING_DOCUMENT_LINKS
                ):
                    missing[(rel, normalized)] = {
                        "source": rel,
                        "target": normalized,
                        "tag": "a",
                        "attribute": "href",
                    }
                else:
                    raise
            if reference and not reference.startswith("#"):
                parsed = urlsplit(reference)
                if not parsed.scheme and not parsed.netloc:
                    count += 1
    return count, [missing[key] for key in sorted(missing)]


def inspect_source(source_value: str) -> Dict[str, object]:
    source = _as_path(source_value)
    headers_path = source / "_headers"
    redirects_path = source / "_redirects"
    if not headers_path.is_file() or headers_path.is_symlink():
        raise PackageError("source must contain a regular _headers file")
    if not redirects_path.is_file() or redirects_path.is_symlink():
        raise PackageError("source must contain a regular _redirects file")
    files = _collect_files(source)
    if "index.html" not in files:
        raise PackageError("source must contain index.html")
    health_collision = source / HEALTH_PATH
    if health_collision.exists() or health_collision.is_symlink():
        raise PackageError(f"reserved health endpoint collides with source path: /{HEALTH_PATH}")
    headers = parse_headers(headers_path)
    redirect = parse_redirects(redirects_path)
    target = _resolve_reference(str(redirect["location"]), "index.html", set(files))
    if target is None:
        raise PackageError("redirect target must resolve to a local site file")
    references, missing_document_links = _parse_html_references(files)
    return {
        "source": source,
        "files": files,
        "headers": headers,
        "redirect": redirect,
        "local_references": references,
        "missing_document_links": missing_document_links,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _manifest_from_inspection(inspection: Dict[str, object]) -> Dict[str, object]:
    files = inspection["files"]
    assert isinstance(files, dict)
    entries = []
    for rel, path in files.items():
        assert isinstance(rel, str) and isinstance(path, Path)
        entries.append({"path": rel, "sha256": _sha256(path), "size": path.stat().st_size})
    return {
        "format": MANIFEST_FORMAT,
        "files": entries,
        "redirect": inspection["redirect"],
        "headers": inspection["headers"],
        "missing_document_links": inspection["missing_document_links"],
        "health": {
            "path": "/" + HEALTH_PATH,
            "status": 200,
            "content_type": HEALTH_CONTENT_TYPE,
            "body": HEALTH_BODY,
        },
    }


def validate_manifest(manifest: object) -> Dict[str, object]:
    if not isinstance(manifest, dict) or manifest.get("format") != MANIFEST_FORMAT:
        raise PackageError("unsupported site manifest format")
    raw_files = manifest.get("files")
    if not isinstance(raw_files, list) or not raw_files:
        raise PackageError("site manifest must contain files")
    files: List[Dict[str, object]] = []
    seen: Set[str] = set()
    for entry in raw_files:
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256", "size"}:
            raise PackageError("invalid site manifest file entry")
        rel = entry["path"]
        checksum = entry["sha256"]
        size = entry["size"]
        if not isinstance(rel, str) or not rel or rel.startswith("/") or "\\" in rel:
            raise PackageError(f"invalid manifest path: {rel!r}")
        parts = _parts(rel)
        if any(part in {"", ".", ".."} for part in rel.split("/")) or _is_excluded(rel):
            raise PackageError(f"unsafe or excluded manifest path: {rel!r}")
        if "/".join(parts) != rel:
            raise PackageError(f"non-normalized manifest path: {rel!r}")
        if rel == HEALTH_PATH:
            raise PackageError(f"manifest path is reserved for the health endpoint: {rel!r}")
        if rel in seen:
            raise PackageError(f"duplicate manifest path: {rel}")
        if not isinstance(checksum, str) or not SHA256_RE.fullmatch(checksum):
            raise PackageError(f"invalid checksum for {rel}")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise PackageError(f"invalid size for {rel}")
        seen.add(rel)
        files.append({"path": rel, "sha256": checksum, "size": size})
    if "index.html" not in seen:
        raise PackageError("site manifest is missing index.html")

    redirect = manifest.get("redirect")
    if not isinstance(redirect, dict) or set(redirect) != {"path", "location", "status"}:
        raise PackageError("invalid manifest redirect")
    if redirect.get("path") != "/" or redirect.get("status") != 302:
        raise PackageError("manifest must describe the root 302 redirect")
    location = redirect.get("location")
    if not isinstance(location, str) or not location.startswith("/") or location.startswith("//"):
        raise PackageError("manifest redirect target must be a local path")
    parsed = urlsplit(location)
    if parsed.scheme or parsed.netloc or any(char.isspace() for char in location):
        raise PackageError("manifest redirect target is not a local URL")
    _resolve_reference(location, "index.html", seen)
    headers = _validate_header_entries(manifest.get("headers", []))

    raw_missing = manifest.get("missing_document_links", [])
    if not isinstance(raw_missing, list):
        raise PackageError("missing_document_links must be a list")
    missing_document_links: List[Dict[str, str]] = []
    seen_missing: Set[Tuple[str, str]] = set()
    for entry in raw_missing:
        if not isinstance(entry, dict) or set(entry) != {"source", "target", "tag", "attribute"}:
            raise PackageError("invalid known missing document link entry")
        source = entry["source"]
        target = entry["target"]
        if (
            not isinstance(source, str)
            or not isinstance(target, str)
            or entry["tag"] != "a"
            or entry["attribute"] != "href"
            or (source, target) not in KNOWN_MISSING_DOCUMENT_LINKS
            or not target.lower().endswith((".html", ".htm"))
        ):
            raise PackageError("manifest contains an unapproved missing document link")
        if (source, target) in seen_missing:
            raise PackageError("duplicate known missing document link")
        seen_missing.add((source, target))
        missing_document_links.append({"source": source, "target": target, "tag": "a", "attribute": "href"})
    missing_document_links.sort(key=lambda entry: (entry["source"], entry["target"]))

    health = manifest.get("health")
    if not isinstance(health, dict) or set(health) != {"path", "status", "content_type", "body"}:
        raise PackageError("invalid manifest health endpoint")
    if health != {
        "path": "/" + HEALTH_PATH,
        "status": 200,
        "content_type": HEALTH_CONTENT_TYPE,
        "body": HEALTH_BODY,
    }:
        raise PackageError("unexpected health endpoint definition")
    return {
        "format": MANIFEST_FORMAT,
        "files": files,
        "redirect": redirect,
        "headers": headers,
        "missing_document_links": missing_document_links,
        "health": health,
    }


def _caddy_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_caddy(inspection: Dict[str, object]) -> str:
    redirect = inspection["redirect"]
    headers = inspection["headers"]
    assert isinstance(redirect, dict) and isinstance(headers, list)
    location = str(redirect["location"])
    lines = [
        "{",
        "    admin off",
        "    auto_https off",
        "    persist_config off",
        "}",
        "",
        ":8080 {",
        "    root * /srv/site",
        "",
        "    @home path /",
        "    @deployHealth path /__deploy_health",
        "    @forbiddenDot path_regexp dotfile `(?:^|/)\\.[^/]*(?:/|$)`",
        "    @forbiddenDir path /.git /.git/* /node_modules /node_modules/* /vendor /vendor/* /.venv /.venv/*",
        "    @forbiddenMetadata path /_headers /_redirects /Caddyfile /site-manifest.json",
        "    @asset {",
        "        path_regexp assetExtension `\\.[A-Za-z0-9]+$`",
        "        not path *.html *.htm",
        "    }",
        "    @documentFile file {",
        "        try_files {path} {path}.html {path}/index.html",
        "    }",
        "",
        "    route {",
        "        header {",
    ]
    for entry in headers:
        assert isinstance(entry, dict)
        lines.append(f"            {entry['name']} {_caddy_quote(str(entry['value']))}")
    lines.extend(
        [
            "        }",
            "        header @deployHealth Content-Type \"text/plain; charset=utf-8\"",
            "        encode gzip zstd",
            "        respond @forbiddenDot \"Not Found\" 404",
            "        respond @forbiddenDir \"Not Found\" 404",
            "        respond @forbiddenMetadata \"Not Found\" 404",
            f"        redir @home {_caddy_quote(location)} 302",
            "        respond @deployHealth \"HOME_OK\" 200",
            "        handle @asset {",
            "            file_server",
            "        }",
            "        handle @documentFile {",
            "            rewrite * {http.matchers.file.relative}",
            "            file_server",
            "        }",
            "        rewrite * /index.html",
            "        file_server",
            "    }",
            "",
            "    handle_errors {",
            "        handle @asset {",
            "            respond \"Not Found\" 404",
            "        }",
            "        @hasMpa404 file /404.html",
            "        handle @hasMpa404 {",
            "            request_header -Range",
            "            request_header -If-Range",
            "            rewrite * {http.matchers.file.relative}",
            "            file_server",
            "        }",
            "        respond \"Not Found\" 404",
            "    }",
            "",
            "    log {",
            "        output stderr",
            "    }",
            "}",
            "",
        ]
    )
    return "\n".join(lines)


def build(source_value: str, out_value: str) -> Dict[str, object]:
    inspection = inspect_source(source_value)
    source = inspection["source"]
    assert isinstance(source, Path)
    out = Path(out_value).resolve()
    if out.exists() or out.is_symlink():
        raise PackageError(f"output directory already exists: {out}")
    if _is_within(out, source):
        raise PackageError("output directory must be outside the source snapshot")
    out.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=out.name + ".tmp-", dir=str(out.parent)))
    try:
        temporary.chmod(0o755)
        site = temporary / "site"
        site.mkdir()
        site.chmod(0o755)
        files = inspection["files"]
        assert isinstance(files, dict)
        for rel, original in files.items():
            assert isinstance(rel, str) and isinstance(original, Path)
            destination = site.joinpath(*rel.split("/"))
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.parent.chmod(0o755)
            shutil.copyfile(original, destination)
            destination.chmod(original.stat().st_mode & 0o777 or 0o644)
        manifest = _manifest_from_inspection(inspection)
        (temporary / "site-manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (temporary / "Caddyfile").write_text(render_caddy(inspection), encoding="utf-8")
        os.replace(temporary, out)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return {"ok": True, "out": str(out), "files": len(manifest["files"]), "headers": len(manifest["headers"])}


def _run_check(source_value: str) -> Dict[str, object]:
    inspection = inspect_source(source_value)
    files = inspection["files"]
    assert isinstance(files, dict)
    return {
        "ok": True,
        "source": str(inspection["source"]),
        "files": len(files),
        "html": sum(path.suffix.lower() in {".html", ".htm"} for path in files.values()),
        "local_references": inspection["local_references"],
        "missing_document_links": inspection["missing_document_links"],
        "headers": len(inspection["headers"]),
        "redirect": inspection["redirect"],
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    check_parser = subparsers.add_parser("check", help="validate source links and deployment metadata")
    check_parser.add_argument("source")
    build_parser = subparsers.add_parser("build", help="build an immutable site package")
    build_parser.add_argument("source")
    build_parser.add_argument("out")
    args = parser.parse_args(argv)
    try:
        if args.command == "check":
            result = _run_check(args.source)
        else:
            result = build(args.source, args.out)
    except (OSError, PackageError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
