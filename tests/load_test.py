"""Simple load test script to measure API performance and cache effectiveness.

Not part of the automated pytest suite.

Assumes the API is already running locally at http://localhost:8000

Run in separate session with:
> uv run python tests/load_test.py
"""

import time
import sys
from statistics import mean, stdev
from typing import List

import httpx

# Simulated realistic traffic pattern with location repeats
# Hot locations (frequently requested), warm locations (moderately), cold (infrequent)
LOCATIONS = [
    # Hot locations (10 requests each)
    "Denver",
    "Denver",
    "Denver",
    "Denver",
    "Denver",
    "Denver",
    "Denver",
    "Denver",
    "Denver",
    "Denver",
    "London",
    "London",
    "London",
    "London",
    "London",
    "London",
    "London",
    "London",
    "London",
    "London",
    # Warm locations (5 requests each)
    "Paris",
    "Paris",
    "Paris",
    "Paris",
    "Paris",
    "Tokyo",
    "Tokyo",
    "Tokyo",
    "Tokyo",
    "Tokyo",
    "New York",
    "New York",
    "New York",
    "New York",
    "New York",
    # Medium locations (3 requests each)
    "Sydney",
    "Sydney",
    "Sydney",
    "Dubai",
    "Dubai",
    "Dubai",
    "Singapore",
    "Singapore",
    "Singapore",
    "Toronto",
    "Toronto",
    "Toronto",
    "Berlin",
    "Berlin",
    "Berlin",
    # Cold locations (1-2 requests each)
    "Mexico City",
    "Mumbai",
    "Bangkok",
    "Istanbul",
    "Barcelona",
    "Amsterdam",
    "Vienna",
    "Prague",
    "Stockholm",
    "Madrid",
    "Rome",
    "Athens",
]

BASE_URL = "http://localhost:8000"


def run_load_test(locations: List[str]) -> None:
    """Run load test against weather API."""
    print(f"\n{'=' * 60}")
    print("Weather API Load Test")
    print(f"{'=' * 60}")
    print(f"Total requests: {len(locations)}")
    print(f"Unique locations: {len(set(locations))}")
    print()

    times = []
    errors = 0

    print(f"{'Location':<16} {'Time (s)':<10} {'Status':<10}")
    print("-" * 36)

    with httpx.Client(timeout=30.0) as client:
        for i, location in enumerate(locations, 1):
            try:
                start = time.time()
                response = client.get(
                    f"{BASE_URL}/weather",
                    params={"location": location},
                )
                elapsed = time.time() - start
                times.append(elapsed)

                status = (
                    "✓" if response.status_code == 200 else f"✗ {response.status_code}"
                )
                print(f"{location:<16} {elapsed:<10.3f} {status:<10}")

            except Exception as e:
                print(f"{location:<16} {'ERROR':<10} {str(e):<10}")
                errors += 1

    print()
    print(f"{'=' * 60}")
    print("Results Summary")
    print(f"{'=' * 60}")
    print(f"Total requests: {len(locations)}")
    print(f"Successful: {len(times)}")
    print(f"Errors: {errors}")
    print()

    if times:
        print("Response Times:")
        print(f"  Minimum:  {min(times):.3f}s")
        print(f"  Maximum:  {max(times):.3f}s")
        print(f"  Mean:     {mean(times):.3f}s")
        if len(times) > 1:
            print(f"  Stdev:    {stdev(times):.3f}s")
        print(f"  Total:    {sum(times):.3f}s")
        print()
        print("Throughput:")
        print(f"  Requests/sec: {len(times) / sum(times):.2f}")
        print()

        # Estimate cache effectiveness
        location_counts = {}
        for loc in locations:
            location_counts[loc] = location_counts.get(loc, 0) + 1

        unique_count = len(location_counts)
        repeat_count = len(locations) - unique_count
        if repeat_count > 0:
            potential_cache_savings = (repeat_count / len(locations)) * 100
            print("Cache Potential:")
            print(f"  Unique locations: {unique_count}")
            print(f"  Repeated requests: {repeat_count}")
            print(f"  Potential cache reduction: {potential_cache_savings:.1f}%")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print(__doc__)
        sys.exit(0)

    try:
        run_load_test(LOCATIONS)
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the API is running: uv run fastapi dev")
        sys.exit(1)
