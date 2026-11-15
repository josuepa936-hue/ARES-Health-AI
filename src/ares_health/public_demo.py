"""Public HTTP boundary only; never changes the synthetic evaluation engine."""
from __future__ import annotations

import asyncio
import json
import math
import os
import time

from src.ares_health.version import APP_VERSION
from collections import deque
from urllib.parse import urlsplit

from starlette.responses import JSONResponse

GET_PATHS = {"/api/status", "/api/scenarios", "/api/evidence", "/api/demo",
             "/api/timeline", "/api/mission/risk-guide"}
POST_PATHS = {"/api/mission/fictional-check-in",
              "/api/mission/copilot", "/api/mission/wellness",
              "/api/mission/comprehensive-report"}
BODY_LIMIT = 64 * 1024
MAX_DAYS = 60


def enabled() -> bool:
    return os.getenv("ARES_PUBLIC_DEMO") == "1"


def public_origin() -> str:
    origin = (os.getenv("ARES_PUBLIC_ORIGIN") or os.getenv("RENDER_EXTERNAL_URL") or "").rstrip("/")
    parsed = urlsplit(origin)
    # Loopback HTTP is solely for local container validation. Public hosts need HTTPS.
    local = parsed.hostname in {"127.0.0.1", "localhost", "::1"}
    if (not parsed.hostname or parsed.username or parsed.password or parsed.path
            or parsed.query or parsed.fragment or (parsed.scheme != "https" and not
            (local and parsed.scheme == "http"))):
        raise RuntimeError("Public demo requires a single HTTPS ARES_PUBLIC_ORIGIN or RENDER_EXTERNAL_URL.")
    return origin


def finite(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Nonfinite JSON")
    return number


def reject_constant(_value):
    raise ValueError("Nonfinite JSON")


class PublicDemoBoundary:
    """Bound input before inner middleware buffers it; bound work before dispatch.

    Single-worker demo only. Peer limits never trust user-supplied forwarding
    headers. Global limits still apply when Render shares a proxy peer address.
    No payload, URL query, note, question or raw peer address is logged.
    """
    def __init__(self, app, origin: str, peer_limit: int = 240, global_limit: int = 1200,
                 concurrent_limit: int = 4):
        self.app = app
        self.origin = origin
        self.host = urlsplit(origin).netloc.lower()
        self.peer_limit = peer_limit
        self.global_limit = global_limit
        self.concurrent_limit = concurrent_limit
        self.peers = {}
        self.global_requests = deque()
        self.active = 0

    def rate_allowed(self, peer):
        now = time.monotonic()
        cutoff = now - 60
        for key in list(self.peers):
            if not self.peers[key] or self.peers[key][-1] <= cutoff:
                del self.peers[key]
        if peer not in self.peers:
            if len(self.peers) >= 2048:
                return False
            self.peers[peer] = deque()
        bucket = self.peers[peer]
        for queue in (bucket, self.global_requests):
            while queue and queue[0] <= cutoff:
                queue.popleft()
        if len(bucket) >= self.peer_limit or len(self.global_requests) >= self.global_limit:
            return False
        bucket.append(now)
        self.global_requests.append(now)
        return True

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            # No WebSocket or other public application protocol.
            if scope["type"] == "websocket":
                await send({"type": "websocket.close", "code": 1008})
                return
            return await self.app(scope, receive, send)
        headers = {k.decode("latin1").lower(): v.decode("latin1") for k, v in scope["headers"]}
        path, method = scope["path"], scope["method"]

        response_started = False
        async def secure_send(message):
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
                message["headers"] = list(message.get("headers", [])) + [
                    (b"content-security-policy", b"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'; object-src 'none'"),
                    (b"x-content-type-options", b"nosniff"),
                    (b"referrer-policy", b"no-referrer"),
                    (b"x-frame-options", b"DENY"),
                    (b"permissions-policy", b"camera=(), microphone=(), geolocation=()"),
                    (b"cache-control", b"no-store"),
                ]
                if self.origin.startswith("https://"):
                    message["headers"].append((b"strict-transport-security", b"max-age=31536000"))
            await send(message)

        async def error(code, detail, retry=False):
            response = JSONResponse({"detail": detail}, status_code=code,
                                    headers={"Retry-After": "60"} if retry else None)
            await response(scope, receive, secure_send)

        # Public health probe is constant, cheap and contains no user data.
        if path == "/api/status" and method == "GET":
            return await JSONResponse({"status": "ready", "mode": "public-demo",
                "data_provenance": "synthetic-only", "clinical_validation": False,
                "nasa_approved": False, "application_version": APP_VERSION})(scope, receive, secure_send)
        if headers.get("host", "").lower() != self.host:
            return await error(400, "Unrecognized demo host.")
        # Evaluators must be able to follow a link from the event website.
        # Permit a top-level document navigation, never cross-site API fetches
        # or frames. Origin remains pinned for requests that carry it.
        entry_navigation = (method in {"GET", "HEAD"} and path == "/"
                            and headers.get("sec-fetch-mode") == "navigate"
                            and headers.get("sec-fetch-dest") == "document")
        if (headers.get("origin") not in (None, self.origin)
                or (headers.get("sec-fetch-site") == "cross-site" and not entry_navigation)):
            return await error(403, "Use the demo's same-origin interface.")
        if method not in {"GET", "HEAD", "POST"}:
            return await error(405, "Method unavailable.")
        api_path = path.startswith("/api/")
        if api_path:
            if (method == "GET" and path not in GET_PATHS) or (method == "POST" and path not in POST_PATHS) or method == "HEAD":
                return await error(404, "Endpoint unavailable in the public demo.")
        elif method not in {"GET", "HEAD"} or (path != "/" and not path.startswith("/assets/")):
            return await error(404, "Resource unavailable in the public demo.")
        if len(scope.get("query_string", b"")) > 1024:
            return await error(414, "Query exceeds demo limit.")
        peer = (scope.get("client") or ("unknown",))[0]
        if not self.rate_allowed(peer):
            return await error(429, "Demo request limit reached. Try again in a minute.", True)
        if self.active >= self.concurrent_limit:
            return await error(503, "Demo busy. Please retry shortly.", True)
        self.active += 1
        try:
            # Validate query names/count/limits before any engine work.
            from urllib.parse import parse_qsl
            pairs = parse_qsl(scope.get("query_string", b"").decode("latin1"), keep_blank_values=True)
            allowed_query = {"scenario", "seed", "days"} if path in {"/api/demo", "/api/timeline"} else set()
            if len({k for k, _ in pairs}) != len(pairs) or any(k not in allowed_query for k, _ in pairs):
                return await error(422, "Unsupported demo query.")
            query = dict(pairs)
            if "days" in query and (not query["days"].isascii() or not query["days"].isdigit() or not 12 <= int(query["days"]) <= MAX_DAYS):
                return await error(422, "Public demo supports 12 to 60 fictional days.")
            if method == "POST":
                if headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
                    return await error(415, "Expected application/json.")
                if headers.get("content-encoding", "identity") != "identity":
                    return await error(415, "Compressed request bodies are unavailable.")
                length = headers.get("content-length")
                if length is not None:
                    if not length.isascii() or not length.isdigit():
                        return await error(400, "Invalid request length.")
                    if int(length) > BODY_LIMIT:
                        return await error(413, "Public demo JSON limit is 64 KiB.")
                data = bytearray()
                async with asyncio.timeout(10):
                    while True:
                        message = await receive()
                        if message["type"] == "http.disconnect":
                            return
                        data.extend(message.get("body", b""))
                        if len(data) > BODY_LIMIT:
                            return await error(413, "Public demo JSON limit is 64 KiB.")
                        if not message.get("more_body", False):
                            break
                try:
                    # Reject duplicate keys as well as deeply nested/nonfinite JSON.
                    def unique(pairs):
                        result = {}
                        for k, v in pairs:
                            if k in result:
                                raise ValueError("Duplicate field")
                            result[k] = v
                        return result
                    payload = json.loads(data, parse_float=finite, parse_constant=reject_constant,
                                         object_pairs_hook=unique)
                    if not isinstance(payload, dict):
                        raise ValueError("Expected object")
                    from src.ares_health.api import FictionalCheckInRequest
                    from src.ares_health.copilot_models import CopilotRequest, WellnessRequest, ComprehensiveRequest
                    models = {"/api/mission/fictional-check-in": FictionalCheckInRequest,
                              "/api/mission/copilot": CopilotRequest, "/api/mission/wellness": WellnessRequest,
                              "/api/mission/comprehensive-report": ComprehensiveRequest}
                    models[path].model_validate(payload, strict=True, extra="forbid")
                    if path == "/api/mission/fictional-check-in" and payload.get("fictional_attestation") is not True:
                        raise ValueError("Explicit fictional attestation required")
                    context = payload.get("context", payload)
                    if context.get("kind") == "synthetic_csv" or context.get("days", 21) > MAX_DAYS:
                        raise ValueError("Unsupported public context")
                except (ValueError, TypeError, RecursionError, UnicodeError):
                    return await error(422, "Invalid fictional demo input. Check fields and limits; do not enter real data.")
                delivered = False
                async def replay():
                    nonlocal delivered
                    if not delivered:
                        delivered = True
                        return {"type": "http.request", "body": bytes(data), "more_body": False}
                    return await receive()
                await self.app(scope, replay, secure_send)
            else:
                await self.app(scope, receive, secure_send)
        except TimeoutError:
            if not response_started:
                await error(408, "Request body timeout.")
        except Exception:
            if response_started:
                raise
            await error(500, "Demo temporarily unavailable.")
        finally:
            self.active -= 1
