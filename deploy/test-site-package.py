#!/usr/bin/env python3
"""Offline tests for the static site checker and package builder."""

from __future__ import annotations

import importlib.util
import http.server
import json
import tempfile
import threading
from urllib.parse import unquote, urlsplit
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("site-package.py")
SPEC = importlib.util.spec_from_file_location("site_package", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
PACKAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGE)
VERIFY_SPEC = importlib.util.spec_from_file_location("verify_site", Path(__file__).with_name("verify-site.py"))
assert VERIFY_SPEC is not None and VERIFY_SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(VERIFY_SPEC)
VERIFY_SPEC.loader.exec_module(VERIFY)


class SitePackageTests(unittest.TestCase):
    def make_source(self, name: str = "source") -> Path:
        root = Path(self.temp.name) / name
        root.mkdir()
        (root / "_headers").write_text(
            "/*\n"
            "  Cache-Control: no-cache\n"
            "  X-Content-Type-Options: nosniff\n",
            encoding="utf-8",
        )
        (root / "_redirects").write_text(
            "# homepage redirect\n"
            "/ /courses/%E8%AF%BE/index.html 302\n",
            encoding="utf-8",
        )
        (root / "index.html").write_text(
            "<!doctype html><html><head>"
            '<link rel="stylesheet" href="/assets/site.css?cache=1#top">'
            "</head><body>"
            '<a href="/courses/%E8%AF%BE/index.html#lesson">课</a>'
            '<a href="README.md">readme</a>'
            '<a href="https://example.invalid/external">external</a>'
            '<a href="mailto:test@example.invalid">mail</a>'
            '<a href="#local">anchor</a>'
            '<script src="assets/site.js"></script>'
            "</body></html>",
            encoding="utf-8",
        )
        (root / "assets").mkdir()
        (root / "assets" / "site.css").write_text("body { color: #123; }\n", encoding="utf-8")
        (root / "assets" / "site.js").write_text("console.log('ok');\n", encoding="utf-8")
        (root / "courses" / "课").mkdir(parents=True)
        (root / "courses" / "课" / "index.html").write_text(
            '<!doctype html><link rel="stylesheet" href="../../assets/site.css">', encoding="utf-8"
        )
        (root / "README.md").write_text("Public course documentation\n", encoding="utf-8")
        (root / "courses" / "课" / "exercise.py").write_text("print('exercise')\n", encoding="utf-8")
        (root / "skill").mkdir()
        (root / "skill" / "SKILL.md").write_text("public generation notes\n", encoding="utf-8")
        (root / ".gitattributes").write_text("*.py text eol=lf\n", encoding="utf-8")

        # These entries must never reach the webroot.
        (root / ".env").write_text("SECRET=do-not-copy\n", encoding="utf-8")
        (root / ".env.example").write_text("EXAMPLE=not-served\n", encoding="utf-8")
        (root / ".env.local").write_text("SECRET=do-not-copy\n", encoding="utf-8")
        (root / "id_rsa").write_text("private-key\n", encoding="utf-8")
        (root / "certificate.pem").write_text("private-key\n", encoding="utf-8")
        (root / "deploy").mkdir()
        (root / "deploy" / "secret.txt").write_text("deployment helper\n", encoding="utf-8")
        (root / ".github").mkdir()
        (root / ".github" / "workflow.yml").write_text("workflow\n", encoding="utf-8")
        (root / "artifacts").mkdir()
        (root / "artifacts" / "large.bin").write_bytes(b"artifact")
        (root / ".git").mkdir()
        (root / ".git" / "config").write_text("git metadata\n", encoding="utf-8")
        (root / ".gitignore").write_text(".env\n", encoding="utf-8")
        return root

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="site-package-test-")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_check_resolves_unicode_query_fragment_and_ignores_external(self) -> None:
        source = self.make_source()
        result = PACKAGE._run_check(str(source))
        self.assertTrue(result["ok"])
        self.assertEqual(result["html"], 2)
        self.assertGreaterEqual(result["local_references"], 4)

    def test_build_copies_public_files_and_excludes_operational_content(self) -> None:
        source = self.make_source()
        out = Path(self.temp.name) / "out"
        result = PACKAGE.build(str(source), str(out))
        self.assertTrue(result["ok"])
        self.assertTrue((out / "site" / "README.md").is_file())
        self.assertTrue((out / "site" / "courses" / "课" / "exercise.py").is_file())
        for excluded in [
            ".env",
            ".env.example",
            ".env.local",
            "id_rsa",
            "certificate.pem",
            "deploy",
            ".github",
            "artifacts",
            ".git",
            "_headers",
            "_redirects",
            ".gitignore",
            ".gitattributes",
        ]:
            self.assertFalse((out / "site" / excluded).exists(), excluded)
        manifest = json.loads((out / "site-manifest.json").read_text(encoding="utf-8"))
        paths = {entry["path"] for entry in manifest["files"]}
        self.assertIn("courses/课/index.html", paths)
        self.assertNotIn(".env", paths)
        caddy = (out / "Caddyfile").read_text(encoding="utf-8")
        self.assertIn("admin off", caddy)
        self.assertIn("auto_https off", caddy)
        self.assertIn("persist_config off", caddy)
        self.assertIn('/courses/%E8%AF%BE/index.html', caddy)
        self.assertIn("root * /srv/site", caddy)
        self.assertIn("@forbiddenMetadata path /_headers /_redirects /Caddyfile /site-manifest.json", caddy)
        self.assertIn('respond @deployHealth "HOME_OK" 200', caddy)
        with self.assertRaises(PACKAGE.PackageError):
            PACKAGE.build(str(source), str(out))

    def test_invalid_header_scope_is_rejected(self) -> None:
        source = self.make_source()
        (source / "_headers").write_text("/admin\n  X-Test: yes\n", encoding="utf-8")
        with self.assertRaises(PACKAGE.PackageError):
            PACKAGE.inspect_source(str(source))

    def test_caddy_style_header_brace_is_rejected(self) -> None:
        source = self.make_source()
        (source / "_headers").write_text("/*\n  X-Test: yes\n}\n", encoding="utf-8")
        with self.assertRaises(PACKAGE.PackageError):
            PACKAGE.inspect_source(str(source))

    def test_invalid_redirect_is_rejected(self) -> None:
        source = self.make_source()
        (source / "_redirects").write_text("/ /index.html 301\n", encoding="utf-8")
        with self.assertRaises(PACKAGE.PackageError):
            PACKAGE.inspect_source(str(source))

    def test_missing_local_resource_is_rejected(self) -> None:
        source = self.make_source()
        (source / "index.html").write_text('<script src="missing.js"></script>', encoding="utf-8")
        with self.assertRaises(PACKAGE.PackageError):
            PACKAGE.inspect_source(str(source))

    def test_only_the_historical_missing_document_link_is_allowed_and_recorded(self) -> None:
        source = self.make_source()
        known_source = source / "courses" / "浪漫主义古典音乐" / "01-classical-to-romantic" / "lesson.html"
        known_source.parent.mkdir(parents=True)
        known_source.write_text('<a href="../02-beethoven/lesson.html">下一课</a>', encoding="utf-8")
        result = PACKAGE._run_check(str(source))
        expected = {
            "source": "courses/浪漫主义古典音乐/01-classical-to-romantic/lesson.html",
            "target": "courses/浪漫主义古典音乐/02-beethoven/lesson.html",
            "tag": "a",
            "attribute": "href",
        }
        self.assertEqual(result["missing_document_links"], [expected])
        out = Path(self.temp.name) / "out"
        PACKAGE.build(str(source), str(out))
        manifest = json.loads((out / "site-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["missing_document_links"], [expected])

        for index, replacement in enumerate([
            '<a href="../03-beethoven/lesson.html">未列入的文档</a>',
            '<img src="../02-beethoven/lesson.html" alt="错误的资源引用">',
        ], start=1):
            other_source = self.make_source(f"source-replacement-{index}")
            other_page = other_source / "courses" / "浪漫主义古典音乐" / "01-classical-to-romantic" / "lesson.html"
            other_page.parent.mkdir(parents=True)
            other_page.write_text(replacement, encoding="utf-8")
            with self.assertRaises(PACKAGE.PackageError):
                PACKAGE.inspect_source(str(other_source))

    def test_health_path_collision_is_rejected(self) -> None:
        source = self.make_source()
        (source / "__deploy_health").write_text("not the health endpoint\n", encoding="utf-8")
        with self.assertRaises(PACKAGE.PackageError):
            PACKAGE.inspect_source(str(source))

    def test_verify_checks_root_health_headers_and_every_file(self) -> None:
        source = self.make_source()
        out = Path(self.temp.name) / "out"
        PACKAGE.build(str(source), str(out))
        manifest_path = out / "site-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        site = out / "site"
        expected_headers = {entry["name"]: entry["value"] for entry in manifest["headers"]}
        redirect = manifest["redirect"]["location"]

        class Handler(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def do_GET(self):  # noqa: N802 - stdlib handler API
                request_path = urlsplit(self.path).path
                if request_path == "/":
                    status, body = 302, b""
                elif request_path == "/__deploy_health":
                    status, body = 200, b"HOME_OK"
                else:
                    relative = unquote(request_path.lstrip("/"))
                    candidate = (site / Path(*relative.split("/"))).resolve()
                    try:
                        candidate.relative_to(site.resolve())
                    except ValueError:
                        candidate = site / "missing"
                    if not candidate.is_file():
                        status, body = 404, b"Not Found"
                    else:
                        status, body = 200, candidate.read_bytes()
                self.send_response(status)
                for name, value in expected_headers.items():
                    self.send_header(name, value)
                if request_path == "/":
                    self.send_header("Location", redirect)
                if request_path == "/__deploy_health":
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format, *args):  # noqa: A002 - stdlib handler API
                return

        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            result = VERIFY.verify(f"http://127.0.0.1:{server.server_port}", str(manifest_path))
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()
        self.assertEqual(result["files_checked"], len(manifest["files"]))
        self.assertEqual(result["root_status"], 302)
        self.assertEqual(result["health_status"], 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
