#!/usr/bin/env python3
"""Deep verification script for the backend API at localhost:51971."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# ── dependencies ──────────────────────────────────────────────────────────────
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx", "-q"])
except subprocess.CalledProcessError:
    pass

for _pkg in ("psycopg2-binary", "bcrypt", "PyJWT"):
    _import_name = _pkg.replace("-binary", "")
    try:
        __import__(_import_name)
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", _pkg, "-q"])
        except subprocess.CalledProcessError:
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    _pkg,
                    "-q",
                    "--break-system-packages",
                ]
            )

import bcrypt
import httpx
import jwt
import psycopg2
import psycopg2.extras

# ── configuration ─────────────────────────────────────────────────────────────
BASE_URL = "http://localhost:51971"
DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/project_ed52af27"
TEST_PASSWORD = "AlexTest1!"

PROJECT_ROOT = Path(__file__).resolve().parent
ENV_FILE = PROJECT_ROOT / ".env"
if ENV_FILE.exists():
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

JWT_SECRET = os.getenv("JWT_SECRET_KEY") or os.getenv("JWT_SECRET") or ""
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

SEED_USERS = [
    {"email": "admin@alextest.dev", "role": "admin", "is_active": True},
    {"email": "user@alextest.dev", "role": "user", "is_active": True},
    {"email": "viewer@alextest.dev", "role": "viewer", "is_active": True},
    {"email": "editor@alextest.dev", "role": "editor", "is_active": True},
    {"email": "inactive@alextest.dev", "role": "inactive", "is_active": False},
]

FRONTEND_EXPECTED_FIELDS = [
    "link",
    "id",
    "message",
    "description",
    "error",
    "email",
    "name",
    "bio",
    "profile",
]

# ── result tracking ───────────────────────────────────────────────────────────
failures: list[dict[str, Any]] = []
contract_violations: list[dict[str, Any]] = []
response_times: list[int] = []
slow_endpoints: list[dict[str, Any]] = []
passed = 0
failed = 0
endpoints_tested = 0
users_seeded = 0
db_verified = True
frontend_fields_present: set[str] = set()

# Schema definitions derived from src/models/schema.py
SCHEMAS: dict[str, dict[str, type | tuple]] = {
    "RegisterResponse": {"email": str, "message": str},
    "LoginResponse": {"session_token": str},
    "ConfirmEmailResponse": {"email": str, "message": str},
    "ErrorResponse": {"detail": (str, list, dict), "error": str},
    "ProfileDetail": {
        "id": int,
        "email": str,
        "first_name": (str, type(None)),
        "last_name": (str, type(None)),
        "name": (str, type(None)),
        "bio": (str, type(None)),
        "description": (str, type(None)),
        "mobile_number": (str, type(None)),
        "address": (str, type(None)),
        "profile_picture": (str, type(None)),
        "link": (str, type(None)),
    },
    "ProfileResponse": {
        "id": int,
        "email": str,
        "first_name": (str, type(None)),
        "last_name": (str, type(None)),
        "name": (str, type(None)),
        "bio": (str, type(None)),
        "description": (str, type(None)),
        "mobile_number": (str, type(None)),
        "address": (str, type(None)),
        "profile_picture": (str, type(None)),
        "link": (str, type(None)),
        "profile": dict,
    },
    "HealthResponse": {"status": str},
}


def _type_matches(value: Any, expected: type | tuple) -> bool:
    if isinstance(expected, tuple):
        return isinstance(value, expected)
    return isinstance(value, expected)


def validate_schema(
    data: Any,
    schema_name: str,
    endpoint: str,
    *,
    prefix: str = "",
) -> None:
    """Validate response data against expected Pydantic schema shapes."""
    if schema_name not in SCHEMAS:
        return
    if not isinstance(data, dict):
        contract_violations.append(
            {
                "endpoint": endpoint,
                "field": prefix or "root",
                "expected_type": "object",
                "actual_type": type(data).__name__,
                "issue": f"Expected object for {schema_name}",
            }
        )
        return

    schema = SCHEMAS[schema_name]
    for field, expected_type in schema.items():
        if field not in data:
            contract_violations.append(
                {
                    "endpoint": endpoint,
                    "field": f"{prefix}{field}" if prefix else field,
                    "expected_type": getattr(expected_type, "__name__", str(expected_type)),
                    "actual_type": "missing",
                    "issue": "Required field missing",
                }
            )
            continue
        value = data[field]
        if not _type_matches(value, expected_type):
            contract_violations.append(
                {
                    "endpoint": endpoint,
                    "field": f"{prefix}{field}" if prefix else field,
                    "expected_type": getattr(expected_type, "__name__", str(expected_type)),
                    "actual_type": type(value).__name__,
                    "issue": "Type mismatch",
                }
            )

    if schema_name == "ProfileResponse" and isinstance(data.get("profile"), dict):
        validate_schema(data["profile"], "ProfileDetail", endpoint, prefix="profile.")


def collect_frontend_fields(data: Any) -> None:
    if isinstance(data, dict):
        for key, value in data.items():
            if key in FRONTEND_EXPECTED_FIELDS:
                frontend_fields_present.add(key)
            collect_frontend_fields(value)
    elif isinstance(data, list):
        for item in data:
            collect_frontend_fields(item)


def record_result(
    *,
    method: str,
    path: str,
    role: str,
    status_code: int,
    expected: int,
    error: str | None,
    response_time_ms: int,
) -> None:
    global passed, failed, endpoints_tested
    endpoints_tested += 1
    response_times.append(response_time_ms)
    if response_time_ms > 500:
        slow_endpoints.append(
            {"method": method, "path": path, "response_time_ms": response_time_ms}
        )
    if status_code == expected and error is None:
        passed += 1
    else:
        failed += 1
        failures.append(
            {
                "method": method,
                "path": path,
                "role": role,
                "status_code": status_code,
                "expected": expected,
                "error": error or f"Expected HTTP {expected}, got {status_code}",
                "response_time_ms": response_time_ms,
            }
        )


def db_connect():
    return psycopg2.connect(DATABASE_URL)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def generate_session_token(user_id: int, email: str) -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "session",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def generate_confirmation_token(email: str) -> str:
    payload = {
        "sub": email,
        "type": "email_confirmation",
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def seed_users() -> dict[str, dict[str, Any]]:
    """Seed test users directly in PostgreSQL. Returns email -> user info."""
    global users_seeded, db_verified
    hashed = hash_password(TEST_PASSWORD)
    seeded: dict[str, dict[str, Any]] = {}

    try:
        with db_connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                emails = [u["email"] for u in SEED_USERS]
                cur.execute(
                    "DELETE FROM users WHERE email = ANY(%s)",
                    (emails,),
                )
                for spec in SEED_USERS:
                    cur.execute(
                        """
                        INSERT INTO users (
                            email, hashed_password, is_confirmed, is_active,
                            first_name, last_name, bio
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING id, email, is_active, first_name, last_name, bio
                        """,
                        (
                            spec["email"],
                            hashed,
                            True,
                            spec["is_active"],
                            spec["role"].capitalize(),
                            "TestUser",
                            f"Bio for {spec['role']}",
                        ),
                    )
                    row = cur.fetchone()
                    token = generate_session_token(row["id"], row["email"])
                    seeded[spec["email"]] = {
                        "id": row["id"],
                        "email": row["email"],
                        "role": spec["role"],
                        "is_active": row["is_active"],
                        "session_token": token,
                    }
                    users_seeded += 1
            conn.commit()
    except Exception as exc:
        db_verified = False
        failures.append(
            {
                "method": "SEED",
                "path": "/users",
                "role": "system",
                "status_code": 0,
                "expected": 200,
                "error": f"Database seeding failed: {exc}",
                "response_time_ms": 0,
            }
        )
    return seeded


def db_get_user(email: str) -> dict[str, Any] | None:
    try:
        with db_connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, email, is_confirmed, is_active, first_name, last_name, "
                    "mobile_number, bio, address, profile_picture FROM users WHERE email = %s",
                    (email,),
                )
                return cur.fetchone()
    except Exception:
        return None


def request(
    client: httpx.Client,
    method: str,
    path: str,
    *,
    role: str = "public",
    expected: int,
    json_body: dict | None = None,
    headers: dict | None = None,
    schema: str | None = None,
    endpoint_label: str | None = None,
    error_ok: bool = False,
) -> tuple[httpx.Response | None, int]:
    """Send HTTP request, validate, and record result."""
    url = f"{BASE_URL}{path}"
    hdrs = headers or {}
    start = time.time()
    resp: httpx.Response | None = None
    try:
        resp = client.request(method, url, json=json_body, headers=hdrs, timeout=30.0)
    except Exception as exc:
        elapsed = int((time.time() - start) * 1000)
        record_result(
            method=method,
            path=path,
            role=role,
            status_code=0,
            expected=expected,
            error=str(exc),
            response_time_ms=elapsed,
        )
        return None, elapsed
    elapsed = int((time.time() - start) * 1000)

    label = endpoint_label or f"{method} {path}"
    err_msg: str | None = None

    if resp is None:
        return None, elapsed

    if resp.status_code != expected:
        err_msg = f"Expected HTTP {expected}, got {resp.status_code}: {resp.text[:200]}"

    if resp.status_code < 500 or error_ok:
        try:
            body = resp.json()
            collect_frontend_fields(body)
            if schema and resp.status_code < 400:
                validate_schema(body, schema, label)
            if resp.status_code >= 400 and not error_ok:
                validate_schema(body, "ErrorResponse", label)
                if "error" not in body or "detail" not in body:
                    contract_violations.append(
                        {
                            "endpoint": label,
                            "field": "error/detail",
                            "expected_type": "str",
                            "actual_type": "missing",
                            "issue": "Error response missing detail and error fields",
                        }
                    )
        except json.JSONDecodeError:
            if resp.status_code < 400:
                err_msg = err_msg or "Response is not valid JSON"

    record_result(
        method=method,
        path=path,
        role=role,
        status_code=resp.status_code,
        expected=expected,
        error=err_msg,
        response_time_ms=elapsed,
    )
    return resp, elapsed


def login_token(client: httpx.Client, email: str, role: str) -> str | None:
    resp, _ = request(
        client,
        "POST",
        "/auth/login",
        role=role,
        expected=200,
        json_body={"email": email, "password": TEST_PASSWORD},
        schema="LoginResponse",
    )
    if resp is None or resp.status_code != 200:
        return None
    data = resp.json()
    if "session_token" not in data:
        contract_violations.append(
            {
                "endpoint": "POST /auth/login",
                "field": "session_token",
                "expected_type": "str",
                "actual_type": "missing",
                "issue": "LoginResponse missing session_token",
            }
        )
    for fe_field in ("access_token", "token_type", "expires_in"):
        if fe_field not in data:
            contract_violations.append(
                {
                    "endpoint": "POST /auth/login",
                    "field": fe_field,
                    "expected_type": "str/int",
                    "actual_type": "missing",
                    "issue": "Frontend expects OAuth-style token fields",
                }
            )
    return data.get("session_token")


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def run_tests(seeded: dict[str, dict[str, Any]]) -> None:
    global db_verified

    with httpx.Client() as client:
        # ── GET /health ───────────────────────────────────────────────────
        for spec in SEED_USERS:
            request(
                client,
                "GET",
                "/health",
                role=spec["role"],
                expected=200,
                schema="HealthResponse",
            )

        # ── GET /health/db ────────────────────────────────────────────────
        for spec in SEED_USERS:
            resp, _ = request(
                client,
                "GET",
                "/health/db",
                role=spec["role"],
                expected=200,
            )
            if resp is not None and resp.status_code == 200:
                body = resp.json()
                for field in ("status", "database"):
                    if field not in body:
                        contract_violations.append(
                            {
                                "endpoint": "GET /health/db",
                                "field": field,
                                "expected_type": "str",
                                "actual_type": "missing",
                                "issue": "Required health/db field missing",
                            }
                        )

        # ── POST /auth/register ───────────────────────────────────────────
        unique_email = f"register-{uuid.uuid4().hex[:8]}@alextest.dev"
        resp, _ = request(
            client,
            "POST",
            "/auth/register",
            role="admin",
            expected=201,
            json_body={"email": unique_email, "password": TEST_PASSWORD},
            schema="RegisterResponse",
        )
        if resp is not None and resp.status_code in (503, 201):
            user_row = db_get_user(unique_email)
            if not user_row or user_row["email"] != unique_email.lower():
                db_verified = False

        for spec in SEED_USERS:
            request(
                client,
                "POST",
                "/auth/register",
                role=spec["role"],
                expected=422,
                json_body={"email": "not-an-email"},
                error_ok=True,
            )
            break

        request(
            client,
            "POST",
            "/auth/register",
            role="public",
            expected=422,
            json_body={"password": "short"},
            error_ok=True,
        )

        request(
            client,
            "POST",
            "/auth/register",
            role="public",
            expected=409,
            json_body={"email": "user@alextest.dev", "password": TEST_PASSWORD},
            error_ok=True,
        )

        request(
            client,
            "POST",
            "/auth/register",
            role="public",
            expected=400,
            json_body={"email": f"weak-{uuid.uuid4().hex[:6]}@alextest.dev", "password": "weakpass1!"},
            error_ok=True,
        )

        time.sleep(13)

        # ── POST /auth/login ──────────────────────────────────────────────
        for email, info in seeded.items():
            role = info["role"]
            if info["is_active"]:
                login_token(client, email, role)
                time.sleep(6.5)
            else:
                request(
                    client,
                    "POST",
                    "/auth/login",
                    role=role,
                    expected=403,
                    json_body={"email": email, "password": TEST_PASSWORD},
                    error_ok=True,
                )
                time.sleep(6.5)

        request(
            client,
            "POST",
            "/auth/login",
            role="public",
            expected=401,
            json_body={"email": "user@alextest.dev", "password": "WrongPass1!"},
            error_ok=True,
        )

        request(
            client,
            "POST",
            "/auth/login",
            role="public",
            expected=422,
            json_body={"email": "user@alextest.dev"},
            error_ok=True,
        )

        # ── POST /auth/confirm ────────────────────────────────────────────
        confirm_email = f"confirm-{uuid.uuid4().hex[:8]}@alextest.dev"
        with db_connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (email, hashed_password, is_confirmed, is_active)
                    VALUES (%s, %s, false, true)
                    ON CONFLICT (email) DO NOTHING
                    """,
                    (confirm_email, hash_password(TEST_PASSWORD)),
                )
            conn.commit()

        token = generate_confirmation_token(confirm_email)
        request(
            client,
            "POST",
            "/auth/confirm",
            role="admin",
            expected=200,
            json_body={"token": token},
            schema="ConfirmEmailResponse",
        )

        user_after_confirm = db_get_user(confirm_email)
        if user_after_confirm and not user_after_confirm.get("is_confirmed"):
            db_verified = False

        request(
            client,
            "POST",
            "/auth/confirm",
            role="public",
            expected=400,
            json_body={"token": "invalid.token.value"},
            error_ok=True,
        )

        request(
            client,
            "POST",
            "/auth/confirm",
            role="public",
            expected=422,
            json_body={},
            error_ok=True,
        )

        # ── GET /api/profile ──────────────────────────────────────────────
        for email, info in seeded.items():
            role = info["role"]
            token = info["session_token"]

            if not info["is_active"]:
                request(
                    client,
                    "GET",
                    "/api/profile",
                    role=role,
                    expected=403,
                    headers=auth_headers(token),
                    error_ok=True,
                )
                continue

            resp, _ = request(
                client,
                "GET",
                "/api/profile",
                role=role,
                expected=200,
                headers=auth_headers(token),
                schema="ProfileResponse",
            )
            if resp is not None and resp.status_code == 200:
                body = resp.json()
                if body.get("email") != email:
                    db_verified = False
                    failures.append(
                        {
                            "method": "GET",
                            "path": "/api/profile",
                            "role": role,
                            "status_code": 200,
                            "expected": 200,
                            "error": f"Profile email mismatch: {body.get('email')}",
                            "response_time_ms": 0,
                        }
                    )

            request(
                client,
                "GET",
                "/api/profile",
                role=role,
                expected=403,
                error_ok=True,
            )

        # ── PUT /api/profile ──────────────────────────────────────────────
        for email, info in seeded.items():
            role = info["role"]
            token = info["session_token"]

            if not info["is_active"]:
                request(
                    client,
                    "PUT",
                    "/api/profile",
                    role=role,
                    expected=403,
                    json_body={"first_name": "Blocked"},
                    headers=auth_headers(token),
                    error_ok=True,
                )
                continue

            update_payload = {
                "first_name": f"{role.capitalize()}First",
                "last_name": "UpdatedLast",
                "mobile_number": "+12025550199",
                "bio": f"Updated bio for {role}",
                "address": "123 Test Street",
            }
            resp, _ = request(
                client,
                "PUT",
                "/api/profile",
                role=role,
                expected=200,
                json_body=update_payload,
                headers=auth_headers(token),
                schema="ProfileResponse",
            )
            if resp is not None and resp.status_code == 200:
                row = db_get_user(email)
                if not row:
                    db_verified = False
                else:
                    for field, value in update_payload.items():
                        if row.get(field) != value:
                            db_verified = False
                            failures.append(
                                {
                                    "method": "PUT",
                                    "path": "/api/profile",
                                    "role": role,
                                    "status_code": 200,
                                    "expected": 200,
                                    "error": f"DB field {field} mismatch: {row.get(field)!r} != {value!r}",
                                    "response_time_ms": 0,
                                }
                            )

            request(
                client,
                "PUT",
                "/api/profile",
                role=role,
                expected=403,
                json_body={"first_name": "NoAuth"},
                error_ok=True,
            )

            request(
                client,
                "PUT",
                "/api/profile",
                role=role,
                expected=400,
                json_body={"email": "bad-email"},
                headers=auth_headers(token),
                error_ok=True,
            )

            request(
                client,
                "PUT",
                "/api/profile",
                role=role,
                expected=400,
                json_body={"mobile_number": "abc"},
                headers=auth_headers(token),
                error_ok=True,
            )


def main() -> None:
    seeded = seed_users()
    try:
        run_tests(seeded)
    except Exception as exc:
        failures.append(
            {
                "method": "RUN",
                "path": "*",
                "role": "system",
                "status_code": 0,
                "expected": 200,
                "error": f"Unhandled test error: {exc}",
                "response_time_ms": 0,
            }
        )

    frontend_fields_missing = [
        f for f in FRONTEND_EXPECTED_FIELDS if f not in frontend_fields_present
    ]
    frontend_compatibility = {
        "frontend_fields_expected": FRONTEND_EXPECTED_FIELDS,
        "frontend_fields_present": sorted(frontend_fields_present),
        "frontend_fields_missing": frontend_fields_missing,
        "compatible": len(frontend_fields_missing) == 0,
    }

    avg_response_time_ms = (
        int(sum(response_times) / len(response_times)) if response_times else 0
    )

    seen_violations: set[tuple[str, str, str]] = set()
    unique_violations: list[dict[str, Any]] = []
    for v in contract_violations:
        key = (v["endpoint"], v["field"], v["issue"])
        if key not in seen_violations:
            seen_violations.add(key)
            unique_violations.append(v)

    result = {
        "endpoints_tested": endpoints_tested,
        "passed": passed,
        "failed": failed,
        "users_seeded": users_seeded,
        "db_verified": db_verified,
        "failures": failures,
        "slow_endpoints": slow_endpoints,
        "avg_response_time_ms": avg_response_time_ms,
        "contract_violations": unique_violations,
        "frontend_compatibility": frontend_compatibility,
    }

    print(json.dumps(result))


if __name__ == "__main__":
    main()
