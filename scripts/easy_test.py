import argparse
import json
import sys
import urllib.error
import urllib.request
import uuid


class SmokeTestError(Exception):
    pass


def api_call(base_url: str, method: str, path: str, data: dict | None = None, token: str | None = None):
    url = f"{base_url}{path}"
    headers = {"Accept": "application/json"}
    body = None

    if data is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url=url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            payload = json.loads(raw) if raw else None
            return response.status, payload
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = raw
        raise SmokeTestError(f"{method} {path} failed ({exc.code}): {payload}") from exc
    except urllib.error.URLError as exc:
        raise SmokeTestError(f"{method} {path} failed (network): {exc.reason}") from exc


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeTestError(message)


def print_step(title: str) -> None:
    print(f"\n[STEP] {title}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run end-to-end smoke tests for AI Lead Qualification System")
    parser.add_argument("--base-url", default="http://localhost:8001/api/v1", help="Base API URL")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    health_base = base_url[:-7] if base_url.endswith("/api/v1") else base_url

    unique = uuid.uuid4().hex[:8]
    email = f"owner.{unique}@example.com"
    password = "StrongPass123"

    try:
        print_step("Health check")
        status, payload = api_call(health_base, "GET", "/health")
        require(status == 200, "Health endpoint did not return 200")
        print(f"PASS - /health => {payload}")

        print_step("Register tenant/admin")
        register_payload = {
            "business_name": f"Demo Business {unique}",
            "full_name": "Smoke Test Owner",
            "email": email,
            "password": password,
            "notification_email": email,
        }
        status, register_data = api_call(base_url, "POST", "/auth/register", data=register_payload)
        require(status in (200, 201), "Register endpoint did not return success")
        access_token = register_data.get("access_token")
        tenant_token = register_data.get("tenant", {}).get("widget_token")
        require(bool(access_token), "No access_token found in register response")
        require(bool(tenant_token), "No tenant widget token found in register response")
        print("PASS - register returned token and tenant widget token")

        print_step("Login")
        login_payload = {"email": email, "password": password}
        status, login_data = api_call(base_url, "POST", "/auth/login", data=login_payload)
        require(status == 200, "Login endpoint did not return 200")
        auth_token = login_data.get("access_token")
        require(bool(auth_token), "No access_token found in login response")
        print("PASS - login successful")

        print_step("Start chatbot session")
        status, session_data = api_call(
            base_url,
            "POST",
            "/chatbot/session/start",
            data={"tenant_token": tenant_token},
        )
        require(status == 200, "Session start did not return 200")
        session_id = session_data.get("session_id")
        require(bool(session_id), "No session_id returned")
        print(f"PASS - session started: {session_id}")

        print_step("Send chatbot message")
        chat_payload = {
            "tenant_token": tenant_token,
            "message": (
                "Hi, I am Alex Smoke. My email is alex.smoke@example.com and phone is +1 555 888 9999. "
                "Our budget is around 20k, timeline is this month, and we need help with lead automation setup."
            ),
        }
        status, reply_data = api_call(
            base_url,
            "POST",
            f"/chatbot/session/{session_id}/message",
            data=chat_payload,
        )
        require(status == 200, "Chat message endpoint did not return 200")
        score = reply_data.get("lead_score", 0)
        qualified = reply_data.get("is_qualified", False)
        print(f"PASS - chat response received (score={score}, qualified={qualified})")

        print_step("Admin endpoints")
        status, leads_data = api_call(base_url, "GET", "/leads", token=auth_token)
        require(status == 200, "GET /leads failed")

        status, conv_data = api_call(base_url, "GET", "/conversations", token=auth_token)
        require(status == 200, "GET /conversations failed")

        status, analytics_data = api_call(base_url, "GET", "/analytics", token=auth_token)
        require(status == 200, "GET /analytics failed")

        status, notifications_data = api_call(base_url, "GET", "/notifications", token=auth_token)
        require(status == 200, "GET /notifications failed")

        print(
            "PASS - admin endpoints: "
            f"leads={len(leads_data)}, conversations={len(conv_data)}, "
            f"qualified_leads={analytics_data.get('qualified_leads')}, notifications={len(notifications_data)}"
        )

        print("\nALL TESTS PASSED")
        return 0
    except SmokeTestError as exc:
        print(f"\nTEST FAILED: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
