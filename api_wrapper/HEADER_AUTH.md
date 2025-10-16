# Header-Based Authentication

The Reddit API Wrapper now supports flexible header-based authentication, allowing you to pass Reddit client credentials directly via HTTP headers instead of embedding them in tokens.

## 🔐 Authentication Methods

### Method 1: Access Token Only
Use just the Reddit access token obtained from OAuth2 flow:

```bash
curl -H "Authorization: Bearer <reddit_access_token>" \
     http://localhost:8000/user/me
```

### Method 2: Access Token + Client Credentials
Include Reddit app credentials for enhanced authentication context:

```bash
curl -H "Authorization: Bearer <reddit_access_token>" \
     -H "X-Reddit-Client-Id: your_client_id" \
     -H "X-Reddit-Client-Secret: your_client_secret" \
     -H "X-Reddit-User-Agent: YourApp/1.0 by your_username" \
     http://localhost:8000/user/me
```

## 📋 Available Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | ✅ | Bearer token with Reddit access token |
| `X-Reddit-Client-Id` | ❌ | Your Reddit app's client ID |
| `X-Reddit-Client-Secret` | ❌ | Your Reddit app's client secret |
| `X-Reddit-User-Agent` | ❌ | User agent string for Reddit API |

## 🚀 Benefits

### Flexibility
- **Simple**: Use just access token for basic operations
- **Enhanced**: Add credentials for operations requiring app context
- **Dynamic**: Different credentials per request if needed

### Security
- **No Credential Storage**: Client credentials not stored server-side
- **Request-Scoped**: Credentials only used for that specific request
- **Granular Control**: Full control over what credentials are sent

### Use Cases
- **Multi-App Support**: Different Reddit apps in same wrapper instance
- **Development/Testing**: Easy switching between app configurations
- **Microservices**: Pass credentials from upstream services

## 🔄 OAuth2 Flow with Headers

1. **Get Authorization URL**
   ```bash
   POST /auth/authorize-url
   ```

2. **User Authorization**
   User visits Reddit authorization URL

3. **Exchange Code for Token**
   ```bash
   POST /auth/callback
   ```

4. **Use Access Token**
   ```bash
   # Method 1: Token only
   GET /user/me
   Authorization: Bearer <access_token>

   # Method 2: Token + credentials
   GET /user/me
   Authorization: Bearer <access_token>
   X-Reddit-Client-Id: <client_id>
   X-Reddit-Client-Secret: <client_secret>
   X-Reddit-User-Agent: <user_agent>
   ```

## 📝 Implementation Details

The authentication system:
1. Extracts access token from `Authorization` header
2. Checks for optional client credential headers
3. Creates Reddit client with appropriate configuration
4. Caches clients for performance
5. Validates authentication with Reddit API

## 🔧 Code Example

```python
import requests

# Your Reddit OAuth2 credentials
headers = {
    "Authorization": "Bearer your_reddit_access_token",
    "X-Reddit-Client-Id": "your_client_id",
    "X-Reddit-Client-Secret": "your_client_secret",
    "X-Reddit-User-Agent": "YourApp/1.0 by username"
}

# Get current user info
response = requests.get("http://localhost:8000/user/me", headers=headers)
user_data = response.json()

# Get saved content
response = requests.get("http://localhost:8000/user/me/saved", headers=headers)
saved_items = response.json()

# Edit a comment
edit_data = {"body": "Updated comment text"}
response = requests.post(
    "http://localhost:8000/comment/abc123/edit",
    headers=headers,
    json=edit_data
)
```

## 🧪 Testing

Run the test script to verify header authentication:

```bash
python test_header_auth.py
```

This will guide you through:
1. OAuth2 authorization flow
2. Testing both authentication methods
3. Verifying endpoint functionality
4. Demonstrating header flexibility

## 📊 Endpoints Supporting Header Auth

All endpoints now support header-based authentication:

- ✅ **User Endpoints**: `/user/me`, `/user/{username}`
- ✅ **Content Endpoints**: Edit, delete, save/unsave content
- ✅ **Inbox Endpoints**: Messages, notifications, blocking
- ✅ **Draft Endpoints**: Draft management
- ✅ **Submission Endpoints**: Advanced submissions (polls, galleries)
- ✅ **Settings Endpoints**: User preferences and configuration
- ✅ **Live Thread Endpoints**: Live thread management
- ✅ **Subreddit Endpoints**: Subreddit operations

## 🔍 Migration Guide

### From JWT-Only Authentication
**Before:**
```bash
# Only JWT token with embedded credentials
curl -H "Authorization: Bearer <jwt_token>" /user/me
```

**After:**
```bash
# Option 1: Reddit access token only
curl -H "Authorization: Bearer <reddit_access_token>" /user/me

# Option 2: Reddit access token + client credentials
curl -H "Authorization: Bearer <reddit_access_token>" \
     -H "X-Reddit-Client-Id: <client_id>" \
     -H "X-Reddit-Client-Secret: <client_secret>" \
     /user/me
```

### Benefits of Migration
- 🚀 **Direct Reddit Integration**: No custom token wrapper
- 🔒 **Enhanced Security**: Reddit's native token validation
- 🔧 **More Flexibility**: Mix and match credentials per request
- 📈 **Better Performance**: Reduced token processing overhead