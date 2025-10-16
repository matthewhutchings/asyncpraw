# Reddit API Wrapper

A comprehensive FastAPI-based REST API wrapper around [Async PRAW](https://github.com/praw-dev/asyncpraw) for Reddit API access. This service provides OAuth2-based authentication and exposes core Reddit functionality through HTTP endpoints with automatic Swagger documentation.

## 🚀 Features

- **Full Reddit API Access**: Submit posts, comment, vote, search, and manage user content
- **OAuth2 Authentication**: Secure credential handling via HTTP headers
- **Swagger Documentation**: Comprehensive API documentation at `/docs`
- **Async Performance**: Built on FastAPI and Async PRAW for high performance
- **Docker Support**: Easy containerization and deployment
- **Input Validation**: Comprehensive request validation and error handling
- **Rate Limiting**: Built-in protection against API abuse
- **Health Monitoring**: Health check endpoints for monitoring

## 📋 Prerequisites

- Python 3.9+
- Reddit OAuth2 Application (created at https://www.reddit.com/prefs/apps/)
- Docker (optional, for containerized deployment)

## 🛠️ Installation

### Local Development

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd asyncpraw/api_wrapper
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python run.py
   ```

### Docker Deployment

1. **Build and run with Docker Compose**:
   ```bash
   ./deploy.sh
   ```

   Or manually:
   ```bash
   docker-compose up -d
   ```

## 🔐 Authentication

All endpoints require Reddit OAuth2 credentials passed as HTTP headers:

| Header | Description | Example |
|--------|-------------|---------|
| `X-Reddit-Client-ID` | Your Reddit app client ID | `abc123def456` |
| `X-Reddit-Client-Secret` | Your Reddit app client secret | `xyz789uvw012` |
| `X-Reddit-Username` | Your Reddit username | `your_username` |
| `X-Reddit-Password` | Your Reddit password | `your_password` |
| `X-Reddit-User-Agent` | Your app's user agent | `MyApp/1.0 by your_username` |

### Creating a Reddit App

1. Go to https://www.reddit.com/prefs/apps/
2. Click "Create App" or "Create Another App"
3. Choose "script" type
4. Note your `client_id` (under the app name) and `client_secret`

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🔗 Available Endpoints

### Subreddits
- `GET /subreddit/{name}` - Get subreddit information
- `GET /subreddit/{name}/hot` - Get hot posts
- `GET /subreddit/{name}/new` - Get new posts
- `GET /subreddit/{name}/top` - Get top posts
- `GET /subreddit/{name}/moderators` - Get moderators
- `POST /subreddit/{name}/submit` - Submit a post

### Submissions
- `GET /submission/{id}` - Get submission details
- `GET /submission/{id}/comments` - Get submission comments
- `POST /submission/{id}/comment` - Comment on submission
- `POST /submission/{id}/upvote` - Upvote submission
- `POST /submission/{id}/downvote` - Downvote submission

### Comments
- `POST /comment/{id}/reply` - Reply to comment
- `POST /comment/{id}/upvote` - Upvote comment
- `POST /comment/{id}/downvote` - Downvote comment

### Users
- `GET /user/{username}` - Get user information
- `GET /user/{username}/submissions` - Get user's submissions
- `GET /user/me` - Get current user info
- `GET /user/me/submissions` - Get current user's submissions
- `GET /user/me/comments` - Get current user's comments

### Search & Browse
- `GET /search` - Search Reddit
- `GET /front/hot` - Get front page hot posts

### Utility
- `GET /health` - Health check

## 📝 Usage Examples

### Submit a Post

```bash
curl -X POST "http://localhost:8000/subreddit/test/submit" \
  -H "X-Reddit-Client-ID: your_client_id" \
  -H "X-Reddit-Client-Secret: your_client_secret" \
  -H "X-Reddit-Username: your_username" \
  -H "X-Reddit-Password: your_password" \
  -H "X-Reddit-User-Agent: MyApp/1.0 by your_username" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Post from API",
    "selftext": "This is a test post submitted via the Reddit API wrapper"
  }'
```

### Get Subreddit Hot Posts

```bash
curl "http://localhost:8000/subreddit/python/hot?limit=10" \
  -H "X-Reddit-Client-ID: your_client_id" \
  -H "X-Reddit-Client-Secret: your_client_secret" \
  -H "X-Reddit-Username: your_username" \
  -H "X-Reddit-Password: your_password" \
  -H "X-Reddit-User-Agent: MyApp/1.0 by your_username"
```

### Search Reddit

```bash
curl "http://localhost:8000/search?query=python&subreddit=programming&limit=5" \
  -H "X-Reddit-Client-ID: your_client_id" \
  -H "X-Reddit-Client-Secret: your_client_secret" \
  -H "X-Reddit-Username: your_username" \
  -H "X-Reddit-Password: your_password" \
  -H "X-Reddit-User-Agent: MyApp/1.0 by your_username"
```

## 🏗️ Project Structure

```
api_wrapper/
├── main.py                 # Main FastAPI application
├── models.py              # Pydantic models for request/response
├── auth.py                # Authentication handling
├── exceptions.py          # Custom exception classes
├── validation.py          # Input validation utilities
├── additional_endpoints.py # Extended API endpoints
├── run.py                 # Application startup script
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── nginx.conf            # Nginx reverse proxy config
├── deploy.sh             # Deployment script
├── .env.example          # Environment variables template
└── README.md             # This file
```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
HOST=0.0.0.0
PORT=8000
DEBUG=True
LOG_LEVEL=INFO
```

### Production Deployment

For production deployment:

1. **Set environment variables**:
   ```bash
   export DEBUG=False
   export LOG_LEVEL=WARNING
   ```

2. **Configure CORS** (in `main.py`):
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

3. **Enable HTTPS** (update `nginx.conf`):
   - Uncomment HTTPS server block
   - Add SSL certificates

4. **Use production WSGI server**:
   ```bash
   pip install gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

## 🔧 Error Handling

The API provides comprehensive error handling with detailed error messages:

- **400 Bad Request**: Invalid input data or malformed requests
- **401 Unauthorized**: Invalid Reddit credentials
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation errors
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server-side errors

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "Reddit API Wrapper"
}
```

### Logs

View application logs:
```bash
docker-compose logs -f reddit-api-wrapper
```

## 🛡️ Security Considerations

- **Never log Reddit credentials**
- **Use HTTPS in production**
- **Implement rate limiting**
- **Validate all input data**
- **Keep dependencies updated**
- **Use environment variables for secrets**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📜 License

This project is licensed under the BSD License - see the LICENSE file for details.

## 🔗 Related Projects

- [Async PRAW](https://github.com/praw-dev/asyncpraw) - The underlying Reddit API wrapper
- [PRAW](https://github.com/praw-dev/praw) - The synchronous version
- [FastAPI](https://fastapi.tiangolo.com/) - The web framework used

## 🆘 Support

- **Documentation**: https://asyncpraw.readthedocs.io/
- **Reddit**: r/redditdev
- **Issues**: GitHub Issues

---

Made with ❤️ using [FastAPI](https://fastapi.tiangolo.com/) and [Async PRAW](https://github.com/praw-dev/asyncpraw)