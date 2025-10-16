"""
Test script for the Reddit API Wrapper with OAuth2 code flow authentication.
Run this script to verify the API is working correctly.
"""

import asyncio
import aiohttp
import json
import sys
import webbrowser
from urllib.parse import urlparse, parse_qs


class RedditOAuth2Tester:
    """Test client for the Reddit API Wrapper using OAuth2 flow."""

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.access_token = None

    async def get_authorization_url(self, app_config):
        """Get Reddit OAuth2 authorization URL."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/auth/authorize-url",
                json=app_config,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    error = await response.text()
                    raise Exception(f"Failed to get authorization URL: {response.status} - {error}")

    async def exchange_code_for_token(self, callback_data):
        """Exchange authorization code for JWT token."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/auth/callback",
                json=callback_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.access_token = data["access_token"]
                    return data
                else:
                    error = await response.text()
                    raise Exception(f"Failed to exchange code for token: {response.status} - {error}")

    async def login_with_refresh_token(self, refresh_token_data):
        """Login using a refresh token."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/auth/login-refresh-token",
                json=refresh_token_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.access_token = data["access_token"]
                    return data
                else:
                    error = await response.text()
                    raise Exception(f"Failed to login with refresh token: {response.status} - {error}")

    def get_auth_headers(self):
        """Get authorization headers with JWT token."""
        if not self.access_token:
            raise Exception("Not logged in. Call login method first.")
        return {"Authorization": f"Bearer {self.access_token}"}


async def test_oauth2_flow():
    """Test the OAuth2 code flow."""

    # Configuration - UPDATE THESE WITH YOUR REDDIT APP CREDENTIALS
    app_config = {
        "client_id": "your_client_id_here",
        "client_secret": "your_client_secret_here",
        "redirect_uri": "http://localhost:8080",
        "user_agent": "TestApp/1.0 by your_username_here",
        "scopes": ["*"],
        "duration": "permanent"
    }

    tester = RedditOAuth2Tester()

    print("🔐 Testing Reddit API Wrapper OAuth2 Code Flow...")
    print("=" * 70)

    try:
        # Step 1: Get authorization URL
        print("\n1. Getting Reddit authorization URL...")
        auth_data = await tester.get_authorization_url(app_config)
        auth_url = auth_data["authorization_url"]
        state = auth_data["state"]

        print(f"✅ Authorization URL generated!")
        print(f"   State: {state}")
        print(f"   URL: {auth_url[:80]}...")

        # Step 2: Simulate user authorization (in real app, user visits URL)
        print("\n2. User Authorization Step...")
        print("📖 In a real application, you would:")
        print("   1. Direct the user to visit the authorization URL")
        print("   2. User authorizes your application on Reddit")
        print("   3. Reddit redirects to your redirect_uri with a code")
        print("   4. Extract the code and exchange it for a token")

        print("\n🌐 Opening authorization URL in browser...")
        print("💡 After authorization, copy the 'code' parameter from the callback URL")

        # Open browser (optional - comment out if running headless)
        try:
            webbrowser.open(auth_url)
        except:
            print("❌ Could not open browser automatically")

        print(f"\n🔗 Authorization URL: {auth_url}")
        print("\nAfter visiting the URL and authorizing:")
        print("1. You'll be redirected to your redirect_uri")
        print("2. Copy the 'code' parameter from the URL")
        print("3. Use it in the callback endpoint")

        # For demo purposes, show what the callback would look like
        print("\n3. Callback Example (for testing with real code)...")
        print("Once you have the authorization code, you would call:")
        print('curl -X POST "http://localhost:8000/auth/callback" \\')
        print('  -H "Content-Type: application/json" \\')
        print('  -d \'{\n' +
              '    "client_id": "your_client_id",\n' +
              '    "client_secret": "your_client_secret",\n' +
              '    "redirect_uri": "http://localhost:8080",\n' +
              '    "user_agent": "TestApp/1.0 by your_username",\n' +
              '    "code": "AUTHORIZATION_CODE_FROM_REDDIT"\n' +
              '  }\'')

        return True

    except Exception as e:
        print(f"❌ OAuth2 flow test failed: {e}")
        return False


async def test_refresh_token_flow():
    """Test the refresh token flow."""

    print("\n" + "=" * 70)
    print("🔄 Testing Refresh Token Flow...")
    print("=" * 70)

    # If you have a refresh token, you can test this flow
    refresh_token_config = {
        "client_id": "your_client_id_here",
        "client_secret": "your_client_secret_here",
        "user_agent": "TestApp/1.0 by your_username_here",
        "refresh_token": "your_refresh_token_here"  # Replace with actual refresh token
    }

    tester = RedditOAuth2Tester()

    print("💡 If you have a Reddit refresh token, update the config above and uncomment the test below")
    print("📖 Refresh tokens are obtained from the OAuth2 flow or Reddit's API directly")

    # Uncomment to test with real refresh token:
    # try:
    #     login_data = await tester.login_with_refresh_token(refresh_token_config)
    #     print(f"✅ Refresh token login successful!")
    #     print(f"   Username: {login_data['reddit_username']}")
    #     print(f"   Token expires in: {login_data['expires_in']} seconds")
    #     return True
    # except Exception as e:
    #     print(f"❌ Refresh token login failed: {e}")
    #     return False


async def test_api_with_token(access_token):
    """Test API endpoints with a valid JWT token."""

    print("\n" + "=" * 70)
    print("🧪 Testing API Endpoints with JWT Token...")
    print("=" * 70)

    headers = {"Authorization": f"Bearer {access_token}"}
    base_url = "http://localhost:8000"

    async with aiohttp.ClientSession() as session:

        # Test current user
        print("\n1. Testing Current User Info...")
        try:
            async with session.get(f"{base_url}/user/me", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Current user: {data['name']}")
                    print(f"   Comment karma: {data['comment_karma']}")
                    print(f"   Link karma: {data['link_karma']}")
                else:
                    error = await response.text()
                    print(f"❌ User info failed: {response.status} - {error}")
        except Exception as e:
            print(f"❌ User info error: {e}")

        # Test subreddit info
        print("\n2. Testing Subreddit Info...")
        try:
            async with session.get(f"{base_url}/subreddit/test", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ r/{data['name']} - {data['subscribers']} subscribers")
                else:
                    error = await response.text()
                    print(f"❌ Subreddit request failed: {response.status} - {error}")
        except Exception as e:
            print(f"❌ Subreddit request error: {e}")


def print_oauth2_setup_instructions():
    """Print OAuth2 setup instructions."""
    print("⚠️  OAuth2 Setup Required!")
    print("=" * 70)
    print("Before testing OAuth2 flow, you need to:")
    print("\n1. Create a Reddit App:")
    print("   - Go to: https://www.reddit.com/prefs/apps/")
    print("   - Click 'Create App' or 'Create Another App'")
    print("   - Choose 'web app' type (NOT 'script')")
    print("   - Set redirect URI to: http://localhost:8080")
    print("   - Note your client_id and client_secret")
    print("\n2. Update this test script:")
    print("   - Replace 'your_client_id_here' with your actual client ID")
    print("   - Replace 'your_client_secret_here' with your actual client secret")
    print("   - Update the user_agent with your app name and username")
    print("\n3. Make sure the API server is running:")
    print("   - Run: python run.py")
    print("   - Server should be available at: http://localhost:8000")
    print("\n🔐 OAuth2 Flow Benefits:")
    print("   ✅ No username/password storage required")
    print("   ✅ Users can revoke access from Reddit settings")
    print("   ✅ More secure than password-based authentication")
    print("   ✅ Supports long-lived refresh tokens")


def print_refresh_token_info():
    """Print refresh token information."""
    print("\n� Refresh Token Information:")
    print("=" * 70)
    print("A refresh token is a long-lived credential that allows your app")
    print("to access Reddit on behalf of a user without requiring them to")
    print("re-authorize every time.")
    print("\nHow to get a refresh token:")
    print("1. Complete the OAuth2 code flow (this test)")
    print("2. The callback response includes the refresh token")
    print("3. Store the refresh token securely")
    print("4. Use it with /auth/login-refresh-token endpoint")
    print("\nRefresh tokens:")
    print("  - Don't expire (unless revoked by user)")
    print("  - Can be revoked by user from Reddit settings")
    print("  - Should be stored securely (encrypted if possible)")
    print("  - Are specific to your app and the authorizing user")


async def main():
    """Main test function."""
    print("🚀 Reddit API Wrapper OAuth2 Test Suite")
    print("🔐 Testing modern, secure Reddit API authentication")

    # Test health endpoint first
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as response:
                if response.status == 200:
                    print("✅ API server is healthy")
                else:
                    print("❌ API server health check failed")
                    return
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        print("💡 Make sure to run: python run.py")
        return

    # Test OAuth2 flow
    await test_oauth2_flow()

    # Test refresh token flow
    await test_refresh_token_flow()

    print("\n" + "=" * 70)
    print("🎉 OAuth2 Test Suite Completed!")
    print("\n📖 Visit http://localhost:8000/docs for full API documentation")
    print("🔐 OAuth2 flow provides the most secure authentication method")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--setup":
            print_oauth2_setup_instructions()
        elif sys.argv[1] == "--refresh-info":
            print_refresh_token_info()
        elif sys.argv[1] == "--test-token" and len(sys.argv) > 2:
            # Test API with provided token
            token = sys.argv[2]
            asyncio.run(test_api_with_token(token))
        else:
            print("Usage: python test_api.py [--setup|--refresh-info|--test-token <token>]")
    else:
        print("💡 Run with --setup for detailed setup instructions")
        print("💡 Run with --refresh-info for refresh token information")
        asyncio.run(main())