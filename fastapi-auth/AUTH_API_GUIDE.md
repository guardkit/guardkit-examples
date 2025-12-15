# JWT Authentication API - User Guide

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -e .

# Or install from requirements
pip install -r requirements/base.txt
```

### 2. Run Development Server

```bash
uvicorn src.main:app --reload
```

Server will be available at `http://localhost:8000`

### 3. API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Authentication Flow

### Step 1: Register User (Manual Database Entry)

For development, add a user directly:

```python
from src.core.security import hash_password
from src.users.models import User
from src.db.session import async_session

async with async_session() as session:
    user = User(
        email="user@example.com",
        hashed_password=hash_password("SecurePassword"),
        is_active=True
    )
    session.add(user)
    await session.commit()
```

### Step 2: Login

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Step 3: Access Protected Endpoints

Use the `access_token` in Authorization header:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Step 4: Refresh Token

When access token expires, use refresh token:

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Step 5: Logout

```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer <access_token>"
```

Response: `204 No Content`

## API Endpoints

### POST /api/v1/auth/login
Authenticate user and receive tokens.

**Rate Limited**: 5 requests per 15 minutes per IP address

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword"
}
```

**Success Response (200 OK):**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid credentials or inactive user
- `422 Unprocessable Entity`: Invalid email format
- `429 Too Many Requests`: Rate limit exceeded

---

### POST /api/v1/auth/refresh
Get new access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

**Success Response (200 OK):**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired refresh token
- `422 Unprocessable Entity`: Missing refresh token

---

### POST /api/v1/auth/logout
Logout user (client should discard tokens).

**Required Header:**
```
Authorization: Bearer <access_token>
```

**Success Response (204 No Content):** (Empty body)

**Error Responses:**
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Missing authorization header

---

### GET /health
Health check endpoint (no authentication required).

**Success Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "FastAPI Auth API"
}
```

## Token Structure

### Access Token Payload
```json
{
  "sub": "1",                    // User ID (as string)
  "type": "access",              // Token type discriminator
  "iat": 1704067200,            // Issued at (Unix timestamp)
  "exp": 1704068100             // Expiration (Unix timestamp)
}
```

**Lifetime**: 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)

### Refresh Token Payload
```json
{
  "sub": "1",                    // User ID (as string)
  "type": "refresh",             // Token type discriminator
  "iat": 1704067200,            // Issued at (Unix timestamp)
  "exp": 1706745600             // Expiration (Unix timestamp)
}
```

**Lifetime**: 7 days (configurable via `REFRESH_TOKEN_EXPIRE_DAYS`)

## Error Handling

### Generic Errors (Security by Obscurity)

The API intentionally returns generic error messages to prevent user enumeration:

```json
{
  "detail": "Invalid email or password"
}
```

This message is returned for both:
- Non-existent email
- Incorrect password

### Validation Errors

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

### Authentication Errors

```json
{
  "detail": "Inactive user account"
}
```

or

```json
{
  "detail": "Invalid or expired token"
}
```

### Rate Limiting

```json
{
  "detail": "5 per 15 minute"
}
```

HTTP Status: `429 Too Many Requests`

## Security Best Practices

### For Clients

1. **Store Tokens Safely**
   - Never store in plain JavaScript variables
   - Use httpOnly cookies or secure storage
   - Clear tokens on logout

2. **Use Refresh Tokens**
   - Keep access tokens short-lived (30 min)
   - Refresh tokens as needed
   - Implement refresh token rotation

3. **HTTPS Only**
   - Always use HTTPS in production
   - Never send tokens over HTTP

4. **Token Transmission**
   ```
   Authorization: Bearer <access_token>
   ```

### For Developers

1. **Secret Key Management**
   ```bash
   # Generate strong secret key
   openssl rand -hex 32
   ```

2. **Environment Variables**
   ```env
   SECRET_KEY=<32+ character random string>
   DEBUG=False
   DATABASE_URL=postgresql://user:pass@localhost/db
   ```

3. **CORS Configuration**
   ```python
   # Only allow trusted origins
   BACKEND_CORS_ORIGINS = ["https://yourdomain.com"]
   ```

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Unit Tests

```bash
pytest tests/unit/ -v
```

### Run Integration Tests

```bash
pytest tests/integration/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=src --cov-report=html
```

### Manual Testing with cURL

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePassword"}'

# Save tokens
TOKEN=<access_token_from_response>
REFRESH=<refresh_token_from_response>

# Refresh token
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH\"}"

# Logout
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer $TOKEN"
```

## Common Issues

### Issue: "Secret key must be at least 32 characters"

**Solution**: Set `SECRET_KEY` environment variable
```bash
export SECRET_KEY="$(openssl rand -hex 32)"
```

### Issue: "Invalid email format"

**Solution**: Ensure email follows standard format
```
✅ user@example.com
❌ user@localhost
❌ not-an-email
```

### Issue: "Inactive user account"

**Solution**: Ensure user's `is_active` field is `True` in database
```python
user.is_active = True
session.commit()
```

### Issue: "Rate limit exceeded"

**Solution**: Wait 15 minutes or use different IP address (for testing)

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Migrations

Using Alembic for schema management:

```bash
# Create migration
alembic revision --autogenerate -m "Create users table"

# Apply migration
alembic upgrade head

# View migration status
alembic current
```

## Performance Considerations

### Caching
- Consider caching user lookups for frequently accessed users
- Redis integration recommended for production

### Database Indexing
- Email indexed for fast user lookups
- is_active indexed for user status checks

### Connection Pooling
- SQLAlchemy handles pooling automatically
- Configured for 10 connections, max 20 overflow

### Async Operations
- All database operations are async
- Non-blocking token validation
- Suitable for high-concurrency environments

## Deployment

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements/ .
RUN pip install -r base.txt

COPY src/ src/
ENV SECRET_KEY=<your-secret-key>
ENV DATABASE_URL=postgresql://user:pass@db/dbname

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

```bash
# Required
SECRET_KEY=<32+ character random string>
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Optional
DEBUG=False
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
RATE_LIMIT_LOGIN_REQUESTS=5
RATE_LIMIT_LOGIN_PERIOD_MINUTES=15
```

### Health Checks

```bash
# Docker health check
curl -f http://localhost:8000/health || exit 1
```

## Support & Documentation

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Code**: See `IMPLEMENTATION_SUMMARY.md` for architecture details
- **Tests**: `tests/` directory contains comprehensive test examples

---

**Version**: 1.0.0
**Last Updated**: 2025-12-14
