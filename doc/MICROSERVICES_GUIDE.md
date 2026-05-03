# AirGlow Microservices Architecture Guide

This document provides a template and example of how to scale your current application into a fully-fledged microservices architecture. 

As you add new features (e.g., managing user profiles, bookings, or products), you should isolate them into separate services just like we did with the `auth_service`.

## 📂 Ideal Folder Structure Example

Here is an example of what your project structure will look like when you add a new `user_service` and a central `api_gateway`.

```text
AirGlow/
├── .env                          # Shared environment variables (or separate ones for each service)
├── docker-compose.yml            # Central orchestration file for all services
├── README.md
│
├── api_gateway/                  # (Optional but recommended) Routes incoming traffic to the right microservice
│   ├── nginx.conf                # NGINX configuration for reverse proxy routing
│   └── Dockerfile                # Dockerfile for the gateway
│
├── auth_service/                 # Your existing Authentication Microservice
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── api/
│       ├── core/
│       ├── db/
│       ├── models/
│       └── schemas/
│
└── user_service/                 # 🆕 Example of a New Microservice
    ├── Dockerfile
    ├── requirements.txt
    └── app/
        ├── main.py               # Runs on port 8001
        ├── api/
        │   └── routes.py         # e.g., GET /users/me, PUT /users/{id}
        ├── core/                 # Dependencies (like validating the JWT token from auth_service)
        ├── db/                   # Database connection (Can share Supabase or use its own DB)
        ├── models/               # User profile models
        └── schemas/              # Pydantic validation schemas
```

---

## 🛠️ Step-by-Step Implementation for a New Service

### 1. Create the Service Directory
Duplicate the structure of `auth_service` for your new service (e.g., `user_service`). Ensure it has its own `requirements.txt` and `Dockerfile`.

### 2. Update the `Dockerfile` for the new service
The `Dockerfile` will look almost identical, but make sure the `CMD` port doesn't conflict if you're running them locally outside of Docker. Inside Docker, they can all run on `8000` internally, but mapped differently externally.

```dockerfile
# user_service/Dockerfile
FROM python:3.12.3-slim
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
# Run internally on 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 
```

### 3. Add to `docker-compose.yml`
You need to register your new microservice in the central `docker-compose.yml` file so they run together.

```yaml
version: '3.8'

services:
  # 1. Existing Auth Service
  auth_service:
    build:
      context: ./auth_service
    container_name: airglow_auth_service
    env_file:
      - .env
    ports:
      - "8000:8000"     # Accessible externally on http://localhost:8000
    restart: unless-stopped
    volumes:
      - ./auth_service:/app

  # 2. New User Service
  user_service:
    build:
      context: ./user_service
    container_name: airglow_user_service
    env_file:
      - .env
    ports:
      - "8001:8000"     # Accessible externally on http://localhost:8001
    restart: unless-stopped
    volumes:
      - ./user_service:/app
```

---

## 🔗 How Microservices Communicate

When you have multiple services, they often need to talk to each other:

1. **Client to Service**: The frontend app calls `http://localhost:8000/login` to get a JWT token.
2. **Service to Service**: The frontend calls `http://localhost:8001/users/me` and passes the JWT token. The `user_service` decodes the token (using the shared `SECRET_KEY` from the `.env` file) to verify the user without needing to talk to the `auth_service` directly.

If they *do* need to talk directly, Docker Compose automatically links them. The `user_service` can literally make an HTTP request to `http://auth_service:8000` because Docker resolves the container name to its internal IP address!
