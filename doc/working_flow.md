
## Microservice Architecture (5 Services - Manageable)

Here's a **realistic** microservice split that makes sense for this project:

```mermaid
flowchart TD
    subgraph Client["Client"]
        U[User / Frontend]
    end

    subgraph Gateway["Gateway Layer"]
        AG[API Gateway<br/>Nginx / Traefik]
    end

    subgraph Services["Your Microservices"]
        API[Service 1: API Service<br/>FastAPI<br/>Pipeline CRUD, Auth, Triggers]
      
        SCH[Service 2: Scheduler Service<br/>Python + Celery Beat<br/>Cron & Webhook Triggers]
      
        WKR[Service 3: Worker Service<br/>Celery Workers<br/>Executes Pipeline Steps]
      
        MD[Service 4: Metadata Service<br/>FastAPI<br/>Reads/Writes Pipeline State]
      
        ART[Service 5: Artifact Service<br/>FastAPI<br/>File Upload/Download]
    end

    subgraph Storage["Storage Layer"]
        PG[(PostgreSQL)]
        RD[(Redis)]
        OB[(MinIO/S3)]
    end

    U --> AG
    AG --> API
    AG --> ART
  
    API -->|Queue tasks| RD
    SCH -->|Create runs| API
    SCH -->|Queue| RD
  
    RD --> WKR
  
    WKR -->|Read pipeline| MD
    WKR -->|Write status| MD
    WKR -->|Store files| ART
  
    MD --> PG
    ART --> OB
  
    API --> MD
```

---

## The 5 Microservices (With Responsibilities)

### **Service 1: API Service** (Entry Point)

```yaml
Port: 8000
Tech: FastAPI
Responsibilities:
  - User authentication (JWT)
  - Tenant isolation
  - Pipeline CRUD operations
  - Manual run triggers (POST /pipelines/{id}/run)
  - Run status queries (GET /runs/{id})
  - Schedule management (CRON)
  - Webhook receiver endpoint
```

### **Service 2: Scheduler Service** (Trigger Engine)

```yaml
Port: 8001 (internal only)
Tech: Python + Celery Beat + Redis locks
Responsibilities:
  - Scan cron schedules every minute
  - Create run records via API Service
  - Prevent duplicate triggers (distributed lock)
  - Handle webhook-triggered runs
```

### **Service 3: Worker Service** (Execution Engine)

```yaml
Port: None (background)
Tech: Celery workers + Redis broker
Responsibilities:
  - Execute pipeline steps (extract, validate, dedup, transform, load)
  - Handle retries and dead letters
  - Update task status in Metadata Service
  - Idempotent execution (check before run)
```

### **Service 4: Metadata Service** (State Manager)

```yaml
Port: 8002 (internal only)
Tech: FastAPI + SQLAlchemy
Responsibilities:
  - All database read/write operations
  - Run history queries
  - Task status persistence
  - Audit log writes
  - Exposes internal APIs only
```

### **Service 5: Artifact Service** (File Manager)

```yaml
Port: 8003 (internal + authenticated external)
Tech: FastAPI + boto3/minio-py
Responsibilities:
  - Upload raw CSV files
  - Download transformed outputs
  - Store execution logs
  - Generate presigned URLs for sharing
```

---

## Communication Between Services

| Caller            | Callee           | Method       | Why                                    |
| ----------------- | ---------------- | ------------ | -------------------------------------- |
| API Service       | Metadata Service | gRPC or HTTP | Create pipeline, get run status        |
| Scheduler Service | API Service      | HTTP         | Trigger runs (reuse existing endpoint) |
| Worker Service    | Metadata Service | gRPC (fast)  | Update task status frequently          |
| Worker Service    | Artifact Service | HTTP         | Store/retrieve files                   |
| API Service       | Artifact Service | HTTP         | File upload/download                   |

**Recommendation:** Use **HTTP/REST** for everything initially. Switch to gRPC only if latency becomes an issue.

---

## Docker Compose for Microservices

```yaml
version: '3.8'

services:
  # Infrastructure
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: pipeline
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - internal

  redis:
    image: redis:7-alpine
    networks:
      - internal

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio_data:/data
    networks:
      - internal

  # Your Microservices
  api-service:
    build: ./api-service
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://admin:secret@postgres/pipeline
      REDIS_URL: redis://redis:6379
      METADATA_SERVICE_URL: http://metadata-service:8002
      ARTIFACT_SERVICE_URL: http://artifact-service:8003
    depends_on:
      - postgres
      - redis
      - metadata-service
    networks:
      - internal
      - public

  scheduler-service:
    build: ./scheduler-service
    environment:
      API_SERVICE_URL: http://api-service:8000
      REDIS_URL: redis://redis:6379
    depends_on:
      - api-service
      - redis
    networks:
      - internal

  worker-service:
    build: ./worker-service
    environment:
      REDIS_URL: redis://redis:6379
      METADATA_SERVICE_URL: http://metadata-service:8002
      ARTIFACT_SERVICE_URL: http://artifact-service:8003
    depends_on:
      - redis
      - metadata-service
      - artifact-service
    networks:
      - internal
    deploy:
      replicas: 3  # Scale workers horizontally

  metadata-service:
    build: ./metadata-service
    ports:
      - "8002:8002"  # Internal only, not exposed publicly
    environment:
      DATABASE_URL: postgresql://admin:secret@postgres/pipeline
    depends_on:
      - postgres
    networks:
      - internal

  artifact-service:
    build: ./artifact-service
    ports:
      - "8003:8003"
    environment:
      MINIO_ENDPOINT: minio:9000
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
    depends_on:
      - minio
    networks:
      - internal

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api-service
      - artifact-service
    networks:
      - public

networks:
  public:
    driver: bridge
  internal:
    driver: bridge
    internal: true  # No external access

volumes:
  postgres_data:
  minio_data:
```

---

## Service Folder Structure

```

data-pipeline-saas/
├── api-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── routers/
│       │   ├── pipelines.py
│       │   ├── runs.py
│       │   └── schedules.py
│       ├── auth.py
│       └── clients/
│           ├── metadata_client.py
│           └── artifact_client.py
│
├── scheduler-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── cron_scanner.py
│       └── lock_manager.py
│
├── worker-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── worker.py
│       ├── steps/
│       │   ├── extract.py
│       │   ├── validate.py
│       │   ├── deduplicate.py
│       │   ├── transform.py
│       │   └── load.py
│       └── clients/
│           ├── metadata_client.py
│           └── artifact_client.py
│
├── metadata-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── models.py
│       ├── crud.py
│       └── routers/
│           ├── pipelines.py
│           ├── runs.py
│           ├── tasks.py
│           └── audit.py
│
├── artifact-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── storage.py
│       └── routers/
│           ├── upload.py
│           ├── download.py
│           └── presigned.py
│
├── docker-compose.yml
└── nginx.conf
```

---

## API Endpoints Per Service

### API Service (Public - Port 8000)

```
POST   /v1/pipelines
GET    /v1/pipelines/{id}
PUT    /v1/pipelines/{id}
DELETE /v1/pipelines/{id}
POST   /v1/pipelines/{id}/run
GET    /v1/runs/{run_id}
GET    /v1/runs/{run_id}/tasks
POST   /v1/schedules
POST   /v1/webhooks/{pipeline_id}  (external trigger)
POST   /v1/auth/login
```

### Metadata Service (Internal - Port 8002)

```
GET    /internal/pipelines/{id}
POST   /internal/runs
PATCH  /internal/runs/{id}/status
POST   /internal/tasks
PATCH  /internal/tasks/{id}
GET    /internal/runs/{id}/tasks
POST   /internal/audit
```

### Artifact Service (Internal + Authenticated - Port 8003)

```
POST   /artifacts/upload
GET    /artifacts/{artifact_id}
GET    /artifacts/{artifact_id}/url  (presigned)
DELETE /artifacts/{artifact_id}
```

---

## Communication Flow Example

**User triggers a pipeline run:**

```
1. POST /v1/pipelines/123/run → API Service
  
2. API Service calls Metadata Service:
   POST /internal/runs → creates run record (status: pending)

3. API Service pushes to Redis:
   queue: "pipeline.123.run.456"

4. Worker Service picks up from Redis

5. For each step, Worker calls Metadata Service:
   PATCH /internal/tasks/{id} (status: running)

6. Worker calls Artifact Service for file storage:
   POST /artifacts/upload (stores raw CSV)

7. After completion, Worker updates Metadata Service:
   PATCH /internal/runs/456 (status: success)

8. API Service shows status when user queries:
   GET /v1/runs/456
```

---

## Build Order (Start Simple)

| Phase       | What to build                          | Why                      |
| ----------- | -------------------------------------- | ------------------------ |
| **1** | Metadata Service + PostgreSQL          | Foundation for all state |
| **2** | API Service (no triggers yet)          | CRUD operations          |
| **3** | Worker Service + 1 step type (extract) | Prove execution works    |
| **4** | Artifact Service                       | File handling            |
| **5** | All other step types                   | Complete pipeline        |
| **6** | Scheduler Service                      | Cron triggers            |
| **7** | Webhook triggers                       | External events          |

---

## MVP Microservice Scope (Achievable)

For your **first working version**, build these 3 services:

```yaml
services:
  api-service:      # Combines API + Scheduler for MVP
  worker-service:   # All step types
  metadata-service: # Database access
  # Artifact service can be a folder in API service initially
```

Then add:

- **Artifact Service** when you need S3/MinIO
- **Scheduler Service** when cron gets complex
- **Separate workers** when one type is overloaded

---

Would you like me to provide:

1. **Complete code** for the Metadata Service (models + CRUD)?
2. **Worker implementation** for one complete pipeline step?
3. **API service code** for pipeline CRUD and run triggers?
4. **Kubernetes deployment** files for these 5 services?
