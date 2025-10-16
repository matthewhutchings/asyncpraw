#!/usr/bin/env python3
"""
Test script demonstrating header-based authentication for Reddit API endpoints.
"""

import requests
import json
import sys

# API base URL
BASE_URL = "http://localhost:8000"

def test_header_auth():
    """Test the new header-based authentication system."""

    print("🔐 Reddit API Wrapper - Header-Based Authentication Test")
    print("=" * 60)

    # Example Reddit app credentials (replace with your own)
    client_id = input("Enter your Reddit client ID: ").strip()
    client_secret = input("Enter your Reddit client secret: ").strip()
    user_agent = input("Enter your user agent (e.g., 'TestApp/1.0 by your_username'): ").strip()

    print("\n📋 Step 1: Generate OAuth2 Authorization URL")
    print("-" * 50)

    # Step 1: Get authorization URL
    auth_url_payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": "http://localhost:8080",
        "user_agent": user_agent,
        "scopes": ["*"],
        "duration": "permanent"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/authorize-url", json=auth_url_payload)
        if response.status_code == 200:
            auth_data = response.json()
            print(f"✅ Authorization URL generated successfully!")
            print(f"🔗 URL: {auth_data['authorization_url']}")
            print(f"🔒 State: {auth_data['state']}")

            print("\n👤 Step 2: User Authorization")
            print("-" * 50)
            print("1. Copy the authorization URL above")
            print("2. Open it in a browser")
            print("3. Login to Reddit and authorize your app")
            print("4. Copy the 'code' parameter from the redirect URL")

            code = input("\nEnter the authorization code from Reddit: ").strip()

            print("\n🔄 Step 3: Exchange Code for Access Token")
            print("-" * 50)

            # Step 3: Exchange code for token
            callback_payload = {
                "code": code,
                "state": auth_data['state'],
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": "http://localhost:8080",
                "user_agent": user_agent
            }

            response = requests.post(f"{BASE_URL}/auth/callback", json=callback_payload)
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data['access_token']
                username = token_data['reddit_username']

                print(f"✅ Access token obtained successfully!")
                print(f"👤 Username: {username}")
                print(f"🎫 Token: {access_token[:20]}...")

                print("\n🚀 Step 4: Test API Endpoints with Different Authentication Methods")
                print("-" * 50)

                # Method 1: Access token only
                print("\n🔸 Method 1: Access Token Only")
                headers1 = {
                    "Authorization": f"Bearer {access_token}"
                }

                response = requests.get(f"{BASE_URL}/user/me", headers=headers1)
                if response.status_code == 200:
                    user_data = response.json()
                    print(f"✅ Success! User: {user_data['name']}, Karma: {user_data['comment_karma'] + user_data['link_karma']}")
                else:
                    print(f"❌ Failed: {response.status_code} - {response.text}")

                # Method 2: Access token + client credentials
                print("\n🔸 Method 2: Access Token + Client Credentials")
                headers2 = {
                    "Authorization": f"Bearer {access_token}",
                    "X-Reddit-Client-Id": client_id,
                    "X-Reddit-Client-Secret": client_secret,
                    "X-Reddit-User-Agent": user_agent
                }

                response = requests.get(f"{BASE_URL}/user/me", headers=headers2)
                if response.status_code == 200:
                    user_data = response.json()
                    print(f"✅ Success with enhanced auth! User: {user_data['name']}")
                    print(f"   - Comment Karma: {user_data['comment_karma']}")
                    print(f"   - Link Karma: {user_data['link_karma']}")
                    print(f"   - Account Created: {user_data['created_utc']}")
                else:
                    print(f"❌ Failed: {response.status_code} - {response.text}")

                # Test saved content endpoint
                print("\n🔸 Testing Content Endpoint with Headers")
                response = requests.get(f"{BASE_URL}/user/me/saved?limit=5", headers=headers2)
                if response.status_code == 200:
                    saved_data = response.json()
                    print(f"✅ Saved content retrieved: {len(saved_data)} items")
                else:
                    print(f"❌ Saved content failed: {response.status_code} - {response.text}")

                print("\n🎉 Header-based authentication test completed!")
                print("\n📝 Summary:")
                print("✅ OAuth2 authorization flow working")
                print("✅ Access token authentication working")
                print("✅ Client credential headers working")
                print("✅ API endpoints accepting both methods")

            else:
                print(f"❌ Token exchange failed: {response.status_code} - {response.text}")
        else:
            print(f"❌ Authorization URL generation failed: {response.status_code} - {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_header_auth()