#!/usr/bin/env python3
"""
Simple test to check header passing with curl.
"""

import subprocess
import sys

def test_headers():
    """Test header passing with curl."""

    print("🧪 Testing Header Passing")
    print("=" * 40)

    # Test command with headers
    cmd = [
        "curl",
        "-X", "GET",
        "http://localhost:8000/user/me",
        "-H", "Authorization: Bearer test_token_12345",
        "-H", "X-Reddit-Client-Id: test_client_id",
        "-H", "X-Reddit-Client-Secret: test_client_secret",
        "-H", "X-Reddit-User-Agent: TestApp/1.0 by testuser",
        "-v"
    ]

    print("Running command:")
    print(" ".join(cmd))
    print("\n" + "="*40)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print("STDOUT:")
        print(result.stdout)
        print("\nSTDERR:")
        print(result.stderr)
        print(f"\nReturn code: {result.returncode}")
    except Exception as e:
        print(f"Error running curl: {e}")

if __name__ == "__main__":
    test_headers()