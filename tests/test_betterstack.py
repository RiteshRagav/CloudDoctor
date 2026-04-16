"""Quick test: BetterStack Logtail ingestion + source validation"""
import asyncio
import httpx
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / "backend" / ".env")

SOURCE_TOKEN = os.environ.get("BETTERSTACK_SOURCE_TOKEN")
QUERY_TOKEN = os.environ.get("BETTERSTACK_QUERY_TOKEN")

INGEST_URL = "https://in.logs.betterstack.com"
SOURCES_API = "https://telemetry.betterstack.com/api/v1/sources"


async def test_ingestion():
    """Test sending a log to BetterStack Logtail."""
    print("=" * 60)
    print("TEST 1: BetterStack Log Ingestion")
    print("=" * 60)
    print(f"  Source Token: {SOURCE_TOKEN[:8]}...")

    log_event = {
        "dt": datetime.now(timezone.utc).isoformat(),
        "level": "INFO",
        "message": "CloudDoctor test log - BetterStack integration verified",
        "service": "clouddoctor-test",
        "source": "poc-test",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            INGEST_URL,
            json=log_event,
            headers={
                "Authorization": f"Bearer {SOURCE_TOKEN}",
                "Content-Type": "application/json",
            },
        )
        print(f"  Status: {resp.status_code}")
        print(f"  Response: {resp.text[:200]}")
        if resp.status_code in (200, 202):
            print("  ✅ Log ingested successfully!")
            return True
        else:
            print(f"  ❌ Ingestion failed: {resp.status_code}")
            return False


async def test_sources_api():
    """Test listing sources via BetterStack API."""
    print("\n" + "=" * 60)
    print("TEST 2: BetterStack Sources API (Query Token)")
    print("=" * 60)
    print(f"  Query Token: {QUERY_TOKEN[:8]}...")

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            SOURCES_API,
            headers={"Authorization": f"Bearer {QUERY_TOKEN}"},
        )
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            sources = data.get("data", [])
            print(f"  Found {len(sources)} source(s)")
            for src in sources[:3]:
                attrs = src.get("attributes", {})
                print(f"    - {attrs.get('name', 'unnamed')} (ID: {src.get('id')}, platform: {attrs.get('platform')})")
            print("  ✅ Sources API accessible!")
            return True
        else:
            print(f"  ❌ Sources API failed: {resp.text[:200]}")
            return False


async def test_batch_ingestion():
    """Test sending multiple logs at once."""
    print("\n" + "=" * 60)
    print("TEST 3: BetterStack Batch Ingestion")
    print("=" * 60)

    logs = [
        {
            "dt": datetime.now(timezone.utc).isoformat(),
            "level": "ERROR",
            "message": "CloudDoctor batch test - Database connection pool exhausted",
            "service": "database-service",
            "scenario": "db-crash",
        },
        {
            "dt": datetime.now(timezone.utc).isoformat(),
            "level": "WARN",
            "message": "CloudDoctor batch test - Request queue depth: 250",
            "service": "api-gateway",
            "scenario": "db-crash",
        },
        {
            "dt": datetime.now(timezone.utc).isoformat(),
            "level": "FATAL",
            "message": "CloudDoctor batch test - Service health check failed",
            "service": "database-service",
            "scenario": "db-crash",
        },
    ]

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            INGEST_URL,
            json=logs,
            headers={
                "Authorization": f"Bearer {SOURCE_TOKEN}",
                "Content-Type": "application/json",
            },
        )
        print(f"  Status: {resp.status_code}")
        print(f"  Sent {len(logs)} logs")
        if resp.status_code in (200, 202):
            print("  ✅ Batch ingestion successful!")
            return True
        else:
            print(f"  ❌ Batch ingestion failed: {resp.text[:200]}")
            return False


async def main():
    print("🏥 CloudDoctor — BetterStack Integration Test")
    print("=" * 60)

    results = {}
    results["Ingestion"] = await test_ingestion()
    results["Sources API"] = await test_sources_api()
    results["Batch Ingestion"] = await test_batch_ingestion()

    print("\n" + "=" * 60)
    print("📊 RESULTS")
    print("=" * 60)
    all_ok = True
    for name, ok in results.items():
        print(f"  {'✅' if ok else '❌'} {name}")
        if not ok:
            all_ok = False

    if all_ok:
        print("\n🎉 All BetterStack tests passed!")
    else:
        print("\n⚠️ Some tests failed")
    return all_ok


if __name__ == "__main__":
    asyncio.run(main())
