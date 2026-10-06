"""Local preview of the website, served like GitHub Pages: /dir/ -> dir/index.html, unknown paths -> 404.html with
status 404. Links into the application (https://app.logicalknight.com) point at a local IPPC Ledger, and staff links
(https://staff.logicalknight.com) at a local Growth Desk, so login and pilot request work in the preview. Nothing here is published (dot directory).

    python .github/scripts/preview.py [--port 8766] [--app http://127.0.0.1:8765]
"""

from __future__ import annotations

import argparse
import http.server
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_APP = "https://app.logicalknight.com"
PUBLIC_STAFF = "https://staff.logicalknight.com"


class Handler(http.server.SimpleHTTPRequestHandler):
    app_origin = "http://127.0.0.1:8765"
    staff_origin = "http://127.0.0.1:8080"

    def _target(self) -> Path | None:
        path = Path(self.translate_path(self.path))
        if path.is_dir():
            path = path / "index.html"
        if not path.is_file() or ROOT not in path.resolve().parents or any(p.startswith(".") for p in path.relative_to(ROOT).parts):
            return None
        return path

    def do_GET(self):
        if self.path.split("?")[0].endswith("/") is False and Path(self.translate_path(self.path)).is_dir():
            self.send_response(301)
            self.send_header("Location", self.path.split("?")[0] + "/")
            self.end_headers()
            return
        target, status = self._target(), 200
        if target is None:
            target, status = ROOT / "404.html", 404
        body = target.read_bytes()
        if target.suffix == ".html":
            body = body.replace(PUBLIC_APP.encode(), self.app_origin.encode()).replace(PUBLIC_STAFF.encode(), self.staff_origin.encode())
        self.send_response(status)
        self.send_header("Content-Type", self.guess_type(str(target)))
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # quiet
        pass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--app", default="http://127.0.0.1:8765")
    parser.add_argument("--staff", default="http://127.0.0.1:8080")
    args = parser.parse_args()
    Handler.app_origin = args.app.rstrip("/")
    Handler.staff_origin = args.staff.rstrip("/")
    server = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), partial(Handler, directory=str(ROOT)))
    print(f"website preview: http://127.0.0.1:{args.port}/  (application links -> {Handler.app_origin})")
    server.serve_forever()


if __name__ == "__main__":
    main()
