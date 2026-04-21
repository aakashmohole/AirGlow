Perfect! Let me give you a **complete, simple auth system** with Redis integration.

---

## What Info to Collect from User

### Registration (Keep it simple for MVP)

```json
{
  "email": "john@example.com",
  "password": "SecurePass123",
  "tenant_name": "Acme Corp"
}
```

**That's it for MVP.** No name, no phone, no company size.

### Login (Even simpler)

```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

### Response After Login

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600,
  "tenant_id": "tenant_abc123"
}
```

---

## Database Schema (PostgreSQL)

```sql
-- Tenants table (isolates data between companies)
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- Store hashed, never plain text
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    UNIQUE(tenant_id, email)  -- Same email can exist in different tenants
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_tenant ON users(tenant_id);
```

---

## Complete Auth Flow with Redis

### How Redis is Used in Auth System

| Redis Key                    | Purpose                          | TTL                 |
| ---------------------------- | -------------------------------- | ------------------- |
| `token:{user_id}:{jwt_id}` | Blacklist revoked tokens         | Until token expires |
| `rate_limit:login:{email}` | Prevent brute force attacks      | 15 minutes          |
| `rate_limit:register:{ip}` | Prevent spam registrations       | 1 hour              |
| `session:{user_id}`        | Track active sessions (optional) | 24 hours            |
| `tenant:{tenant_id}:users` | Cache user list for tenant       | 5 minutes           |

---

## Complete Code Implementation

### 1. Project Structure

```
auth-service/
├── app/
│   ├── main.py
│   ├── auth.py
│   ├── database.py
│   ├── redis_client.py
│   ├── models.py
│   ├── schemas.py
│   └── routes/
│       ├── auth.py
│       └── users.py
├── requirements.txt
└── Dockerfile
```

### 2. Requirements

```txt
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
psycopg2-binary==2.9.9
redis==5.0.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic==2.5.0
email-validator==2.1.0
```

### 3. Redis Client Setup

```python
# app/redis_client.py
import redis
import json
from datetime import timedelta

class RedisClient:
    def __init__(self):
        self.redis = redis.Redis(
            host="localhost",  # or use environment variable
            port=6379,
            decode_responses=True,
            db=0
        )
  
    # === Rate Limiting Functions ===
    def check_rate_limit(self, key: str, max_attempts: int, window_seconds: int) -> bool:
        """
        Check if action is allowed within rate limit
        Returns True if allowed, False if rate limited
        """
        current = self.redis.get(key)
      
        if current is None:
            # First attempt
            self.redis.setex(key, window_seconds, 1)
            return True
      
        attempts = int(current)
        if attempts >= max_attempts:
            return False
      
        # Increment attempts
        self.redis.incr(key)
        return True
  
    def get_remaining_attempts(self, key: str, max_attempts: int) -> int:
        """Get how many attempts remaining"""
        current = self.redis.get(key)
        if current is None:
            return max_attempts
        return max_attempts - int(current)
  
    def reset_rate_limit(self, key: str):
        """Reset rate limit (on successful login)"""
        self.redis.delete(key)
  
    # === Token Blacklist Functions ===
    def blacklist_token(self, jti: str, user_id: str, expires_in: int):
        """
        Add token to blacklist
        jti = JWT ID (unique token identifier)
        """
        key = f"blacklist:{jti}"
        self.redis.setex(key, expires_in, user_id)
  
    def is_token_blacklisted(self, jti: str) -> bool:
        """Check if token is revoked"""
        return self.redis.exists(f"blacklist:{jti}") == 1
  
    # === Session Management ===
    def create_session(self, user_id: str, session_data: dict, ttl_seconds: int = 86400):
        """Store user session"""
        key = f"session:{user_id}"
        self.redis.setex(key, ttl_seconds, json.dumps(session_data))
  
    def get_session(self, user_id: str):
        """Get user session"""
        data = self.redis.get(f"session:{user_id}")
        return json.loads(data) if data else None
  
    def delete_session(self, user_id: str):
        """End user session (logout)"""
        self.redis.delete(f"session:{user_id}")
  
    # === Cache Functions ===
    def cache_tenant_users(self, tenant_id: str, users_data: list, ttl_seconds: int = 300):
        """Cache user list for a tenant"""
        key = f"tenant:{tenant_id}:users"
        self.redis.setex(key, ttl_seconds, json.dumps(users_data))
  
    def get_cached_tenant_users(self, tenant_id: str):
        """Get cached user list"""
        data = self.redis.get(f"tenant:{tenant_id}:users")
        return json.loads(data) if data else None

# Singleton instance
redis_client = RedisClient()
```

### 4. Database Setup

```python
# app/database.py
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime

DATABASE_URL = "postgresql://admin:secret@localhost/pipeline"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Tenant(Base):
    __tablename__ = "tenants"
  
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
  
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 5. Pydantic Schemas

```python
# app/schemas.py
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

# Request schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=50)
    tenant_name: str = Field(..., min_length=2, max_length=100)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    tenant_id: UUID

# Response schemas
class UserResponse(BaseModel):
    id: UUID
    email: str
    tenant_id: UUID
    created_at: datetime
    last_login: Optional[datetime]

class TenantResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime
```

### 6. Auth Core Logic

```python
# app/auth.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from uuid import uuid4
import os

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour

def hash_password(password: str) -> str:
    """Hash password before storing"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password during login"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> tuple:
    """
    Create JWT token
    Returns: (token, jti, expires_at)
    """
    to_encode = data.copy()
  
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  
    # Add unique JWT ID for token blacklisting
    jti = str(uuid4())
  
    to_encode.update({
        "exp": expire,
        "jti": jti,
        "iat": datetime.utcnow()
    })
  
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, jti, expire
```

### 7. Auth Routes (Complete API)

```python
# app/routes/auth.py
from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from uuid import uuid4

from ..database import get_db, User, Tenant
from ..schemas import UserRegister, UserLogin, TokenResponse, UserResponse
from ..auth import hash_password, verify_password, create_access_token
from ..redis_client import redis_client

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, request: Request, db: Session = Depends(get_db)):
    """
    Register a new user with their tenant
    """
    # 1. Rate limiting by IP (prevent spam)
    ip_key = f"rate_limit:register:{request.client.host}"
    if not redis_client.check_rate_limit(ip_key, max_attempts=5, window_seconds=3600):
        remaining = redis_client.get_remaining_attempts(ip_key, 5)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many registration attempts. Try again in 1 hour. {remaining} attempts remaining"
        )
  
    # 2. Check if tenant already exists
    tenant = db.query(Tenant).filter(Tenant.name == user_data.tenant_name).first()
  
    if tenant:
        # Tenant exists, check if user email already in this tenant
        existing_user = db.query(User).filter(
            and_(
                User.tenant_id == tenant.id,
                User.email == user_data.email
            )
        ).first()
      
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists in this tenant"
            )
    else:
        # Create new tenant
        tenant = Tenant(
            id=uuid4(),
            name=user_data.tenant_name
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
  
    # 3. Create user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        id=uuid4(),
        tenant_id=tenant.id,
        email=user_data.email,
        password_hash=hashed_password,
        is_active=True
    )
  
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
  
    # 4. Clear rate limit on success
    redis_client.reset_rate_limit(ip_key)
  
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        tenant_id=new_user.tenant_id,
        created_at=new_user.created_at,
        last_login=new_user.last_login
    )


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    """
    Login user and return JWT token
    """
    # 1. Rate limiting by email (prevent brute force)
    email_key = f"rate_limit:login:{user_data.email}"
    if not redis_client.check_rate_limit(email_key, max_attempts=5, window_seconds=900):  # 5 attempts in 15 min
        remaining = redis_client.get_remaining_attempts(email_key, 5)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many login attempts. Try again in 15 minutes. {remaining} attempts remaining"
        )
  
    # 2. Find user
    user = db.query(User).filter(User.email == user_data.email).first()
  
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
  
    # 3. Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled"
        )
  
    # 4. Verify password
    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
  
    # 5. Update last login
    user.last_login = datetime.utcnow()
    db.commit()
  
    # 6. Create JWT token
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "tenant_id": str(user.tenant_id)
    }
  
    access_token, jti, expires = create_access_token(
        token_data,
        expires_delta=timedelta(minutes=60)
    )
  
    # 7. Store session in Redis
    session_data = {
        "user_id": str(user.id),
        "email": user.email,
        "tenant_id": str(user.tenant_id),
        "jti": jti
    }
    redis_client.create_session(str(user.id), session_data, ttl_seconds=3600)
  
    # 8. Clear rate limit on successful login
    redis_client.reset_rate_limit(email_key)
  
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=3600,
        tenant_id=user.tenant_id
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
    """
    Logout user (blacklist current token)
    """
    # Decode token to get JTI
    from jose import jwt
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    jti = payload.get("jti")
    exp = payload.get("exp")
  
    # Calculate remaining TTL
    expires_in = exp - datetime.utcnow().timestamp()
  
    if expires_in > 0 and jti:
        # Blacklist the token
        redis_client.blacklist_token(jti, str(current_user.id), int(expires_in))
  
    # Delete session
    redis_client.delete_session(str(current_user.id))
  
    return {"message": "Successfully logged out"}


# Dependency to get current user (protected routes)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

oauth2_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get current user from JWT token
    Use this dependency for protected routes
    """
    token = credentials.credentials
  
    try:
        # Decode token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        jti = payload.get("jti")
      
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
      
        # Check if token is blacklisted
        if redis_client.is_token_blacklisted(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )
      
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
      
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
      
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is disabled"
            )
      
        return user
      
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
```

### 8. Main FastAPI App

```python
# app/main.py
from fastapi import FastAPI, Depends
from app.routes import auth
from app.auth import get_current_user

app = FastAPI(title="Data Pipeline Auth Service")

# Include auth routes
app.include_router(auth.router)

# Example protected route
@app.get("/protected")
async def protected_route(current_user = Depends(get_current_user)):
    """
    Example of a protected endpoint
    Only accessible with valid JWT token
    """
    return {
        "message": "You have access!",
        "user_id": str(current_user.id),
        "email": current_user.email,
        "tenant_id": str(current_user.tenant_id)
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
```

### 9. Docker Compose (Auth Service Only)

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: pipeline
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  auth-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://admin:secret@postgres/pipeline
      REDIS_URL: redis://redis:6379
      SECRET_KEY: your-super-secret-key-change-this
    depends_on:
      - postgres
      - redis
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
  redis_data:
```

---

## Testing Your Auth API

### 1. Register a User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@acme.com",
    "password": "SecurePass123",
    "tenant_name": "Acme Corp"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@acme.com",
    "password": "SecurePass123"
  }'
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600,
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 3. Access Protected Route

```bash
curl -X GET http://localhost:8000/protected \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### 4. Logout

```bash
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

## Redis Commands to Verify Everything

```bash
# Connect to Redis
docker exec -it <redis_container_id> redis-cli

# Check rate limit keys
KEYS rate_limit:*

# Check blacklisted tokens
KEYS blacklist:*

# Check sessions
KEYS session:*

# Check cached tenant users
KEYS tenant:*:users

# Get value of specific key
GET rate_limit:login:john@acme.com

# Check TTL of a key
TTL session:user_123_id

# Monitor real-time Redis activity
MONITOR
```

---

## Summary: What Redis Does for Auth

| Feature           | Without Redis                 | With Redis                 |
| ----------------- | ----------------------------- | -------------------------- |
| Rate limiting     | Need complex DB queries       | Simple increment/decrement |
| Token blacklist   | Need database table + cleanup | Auto-expiring keys         |
| Session storage   | Need DB table with cleanup    | TTL handles expiration     |
| Cache users       | Query DB every time           | 5ms vs 50ms response       |
| Distributed locks | Need external system          | Built-in                   |

---

## Next Steps

Now you have:

1. ✅ What user info to collect (email + password + tenant_name)
2. ✅ Complete PostgreSQL schema
3. ✅ Redis integration for rate limiting + blacklist + sessions
4. ✅ Working FastAPI auth service

**Want me to next:**

- Add refresh tokens?
- Integrate this auth into the API Service?
- Add role-based access (admin vs user)?
- Show how other services validate JWT tokens?
