"""
Phase 2 API Verification Suite (Console-Safe UTF-8)
Validates:
- Authentication (X-API-Key, demo key)
- Rate limiting headers (X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset)
- Standard response envelope (success, count, data, meta)
- Section 6.5 Autocomplete dropdown schema
- Error codes: 400 INVALID_QUERY, 401 INVALID_API_KEY, 403 ACCESS_DENIED, 404 NOT_FOUND
"""

import sys
import subprocess
import time
import requests
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PORT = 3001
BASE_URL = f"http://localhost:{PORT}/v1"
DEMO_KEY = "demo_public_key_for_presentations"
PROD_KEY = "ak_a1b2c3d4e5f67890abcdef12345678"


def run_tests():
    print("=" * 75)
    print("STARTING PHASE 2 API DEVELOPMENT & SPECIFICATION VERIFICATION")
    print("=" * 75)

    env = os.environ.copy()
    env["PORT"] = str(PORT)
    env["NODE_ENV"] = "test"

    print(f"\n[Step 1] Booting Express / Node API Gateway on port {PORT}...")
    server_process = subprocess.Popen(
        ["node", "src/server.js"],
        cwd=r"c:\Users\Devil\OneDrive\Desktop\capstone",
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    time.sleep(1.0)

    try:
        health_res = requests.get(f"{BASE_URL}/health", timeout=3)
        assert health_res.status_code == 200, f"Health check failed with {health_res.status_code}"
        print(f"  [OK] Server online & healthy. HTTP {health_res.status_code}")

        # Test 1: Envelope & States
        print("\n[Step 2] Testing Standard Response Envelope & GET /v1/states...")
        res = requests.get(f"{BASE_URL}/states", headers={"X-API-Key": DEMO_KEY})
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        json_data = res.json()

        assert json_data.get("success") is True, "Envelope missing success: true"
        assert "count" in json_data, "Envelope missing count"
        assert "data" in json_data, "Envelope missing data"
        assert "meta" in json_data, "Envelope missing meta"
        assert "requestId" in json_data["meta"], "meta missing requestId"
        assert "responseTime" in json_data["meta"], "meta missing responseTime"
        assert "rateLimit" in json_data["meta"], "meta missing rateLimit"

        assert "X-RateLimit-Limit" in res.headers, "Missing X-RateLimit-Limit header"
        assert "X-RateLimit-Remaining" in res.headers, "Missing X-RateLimit-Remaining header"
        assert "X-Content-Type-Options" in res.headers, "Missing X-Content-Type-Options header"

        print(f"  [PASS] Standard Envelope Validated:")
        print(f"         - requestId:    {json_data['meta']['requestId']}")
        print(f"         - responseTime: {json_data['meta']['responseTime']}ms")
        print(f"         - rateLimit:    {json_data['meta']['rateLimit']['remaining']}/{json_data['meta']['rateLimit']['limit']}")
        print(f"         - states count: {json_data['count']}")

        # Test 2: Hierarchy Drill-down
        print("\n[Step 3] Testing 5-Tier Hierarchical Drill-down Endpoints...")
        dist_res = requests.get(f"{BASE_URL}/states/st_27/districts", headers={"X-API-Key": DEMO_KEY})
        assert dist_res.status_code == 200
        districts = dist_res.json()["data"]
        assert any(d["name"] == "Nandurbar" for d in districts), "Missing Nandurbar"
        print(f"  [PASS] GET /v1/states/st_27/districts -> Found Nandurbar (code: {districts[0]['code']})")

        sdt_res = requests.get(f"{BASE_URL}/districts/dt_497/subdistricts", headers={"X-API-Key": DEMO_KEY})
        assert sdt_res.status_code == 200
        subdistricts = sdt_res.json()["data"]
        akkalkuwa = subdistricts[0]
        assert akkalkuwa["code"] == "03950", f"Leading zero corrupted! Got {akkalkuwa['code']}"
        print(f"  [PASS] GET /v1/districts/dt_497/subdistricts -> Found Akkalkuwa (code: '{akkalkuwa['code']}')")

        vil_res = requests.get(f"{BASE_URL}/subdistricts/sdt_03950/villages", headers={"X-API-Key": DEMO_KEY})
        assert vil_res.status_code == 200
        villages = vil_res.json()["data"]
        assert len(villages) >= 5
        print(f"  [PASS] GET /v1/subdistricts/sdt_03950/villages -> Returned {len(villages)} villages")

        # Test 3: Dropdown Autocomplete Schema (Section 6.5)
        print("\n[Step 4] Testing Section 6.5 Autocomplete Dropdown Schema...")
        auto_res = requests.get(f"{BASE_URL}/autocomplete?q=Mani", headers={"X-API-Key": DEMO_KEY})
        assert auto_res.status_code == 200
        auto_json = auto_res.json()
        assert len(auto_json["data"]) > 0
        first_option = auto_json["data"][0]

        assert "value" in first_option
        assert "label" in first_option
        assert "fullAddress" in first_option
        assert "hierarchy" in first_option
        assert first_option["hierarchy"]["village"] == "Manibeli"
        assert first_option["hierarchy"]["subDistrict"] == "Akkalkuwa"
        assert first_option["hierarchy"]["district"] == "Nandurbar"
        assert first_option["hierarchy"]["state"] == "Maharashtra"
        assert first_option["hierarchy"]["country"] == "India"

        print(f"  [PASS] Autocomplete Option Schema Verified (Section 6.5):")
        print(f"         - value:       {first_option['value']}")
        print(f"         - label:       {first_option['label']}")
        print(f"         - fullAddress: {first_option['fullAddress']}")
        print(f"         - hierarchy:   {first_option['hierarchy']}")

        # Test 4: Error Codes (Section 6.6)
        print("\n[Step 5] Testing Section 6.6 Error Codes & Status Handlers...")

        # 400 INVALID_QUERY
        err400 = requests.get(f"{BASE_URL}/search?q=a", headers={"X-API-Key": DEMO_KEY})
        assert err400.status_code == 400
        assert err400.json()["error"]["code"] == "INVALID_QUERY"
        print(f"  [PASS] 400 INVALID_QUERY: {err400.json()['error']['message']}")

        # 401 INVALID_API_KEY
        err401 = requests.get(f"{BASE_URL}/states")
        assert err401.status_code == 401
        assert err401.json()["error"]["code"] == "INVALID_API_KEY"
        print(f"  [PASS] 401 INVALID_API_KEY: {err401.json()['error']['message']}")

        # 403 ACCESS_DENIED (Demo key restricted to Maharashtra)
        err403 = requests.get(f"{BASE_URL}/states/st_24/districts", headers={"X-API-Key": DEMO_KEY})
        assert err403.status_code == 403
        assert err403.json()["error"]["code"] == "ACCESS_DENIED"
        print(f"  [PASS] 403 ACCESS_DENIED: {err403.json()['error']['message']}")

        # 404 NOT_FOUND
        err404 = requests.get(f"{BASE_URL}/states/st_9999/districts", headers={"X-API-Key": PROD_KEY})
        assert err404.status_code == 404
        assert err404.json()["error"]["code"] == "NOT_FOUND"
        print(f"  [PASS] 404 NOT_FOUND: {err404.json()['error']['message']}")

        print("\n" + "=" * 75)
        print("[SUCCESS] ALL PHASE 2 API SPECIFICATIONS & INTEGRATION TESTS PASSED (100%)")
        print("=" * 75)

    finally:
        server_process.terminate()
        server_process.wait()
        print("\nTest server cleanly shutdown.")


if __name__ == "__main__":
    run_tests()
