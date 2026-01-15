# 🚀 Lyftr AI - Containerized Webhook API

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)

A production-ready, containerized FastAPI service for ingesting and managing WhatsApp-like webhook messages with HMAC signature verification, idempotency guarantees, and comprehensive observability.

---

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [API Endpoints](#-api-endpoints)
- [Testing the API](#-testing-the-api)
- [Architecture & Design Decisions](#-architecture--design-decisions)
- [Configuration](#-configuration)
- [Observability](#-observability)
- [Development](#-development)
- [Setup Used](#-setup-used)

---

## ✨ Features

- **🔐 HMAC Signature Verification** - Secure webhook ingestion with SHA-256 HMAC validation
- **🔄 Idempotent Message Processing** - Guaranteed exactly-once message storage
- **📊 Analytics & Statistics** - Real-time message statistics and sender analytics
- **📈 Prometheus Metrics** - Production-ready metrics for monitoring
- **📝 Structured JSON Logging** - Request tracking with correlation IDs
- **🔍 Advanced Filtering & Pagination** - Flexible message querying
- **💊 Health Probes** - Kubernetes-ready liveness and readiness checks
- **🐳 Fully Containerized** - Docker Compose for easy deployment
- **⚡ High Performance** - Async FastAPI with efficient SQLite storage

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Make (optional, for convenience commands)

### Running the Application

```bash
# 1. Clone the repository
git clone https://github.com/Bhavishya-Chaturvedi/Lyfter-backend.git
cd Lyfter-backend

# 2. Set environment variables (optional - defaults provided)
export WEBHOOK_SECRET="testsecret"
export DATABASE_URL="sqlite:////data/app.db"
export LOG_LEVEL="INFO"

# 3. Start the application
make up
# OR
docker compose up -d --build

# 4. Wait for the service to be ready (~10 seconds)
# The API will be available at http://localhost:8000
```

### Verify Installation

```bash
# Check health endpoints
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready

# View API documentation
open http://localhost:8000/docs
```

### Stopping the Application

```bash
make down
# OR
docker compose down -v
```

---

## 📡 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook` | POST | Ingest WhatsApp-like messages |
| `/messages` | GET | List messages with pagination & filters |
| `/stats` | GET | Message analytics and statistics |
| `/health/live` | GET | Liveness probe |
| `/health/ready` | GET | Readiness probe |
| `/metrics` | GET | Prometheus metrics |

### Detailed Endpoint Documentation

#### 1. **POST /webhook** - Ingest Messages

Receives and stores WhatsApp-like messages with HMAC signature verification.

**Request:**
```bash
# Compute HMAC signature (example using Python)
python3 -c "
import hmac, hashlib, sys
secret = 'testsecret'
body = '{\"message_id\":\"m1\",\"from\":\"+919876543210\",\"to\":\"+14155550100\",\"ts\":\"2025-01-15T10:00:00Z\",\"text\":\"Hello\"}'
sig = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
print(sig)
"

# Send request with signature
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -H "X-Signature: <computed_signature>" \
  -d '{
    "message_id": "m1",
    "from": "+919876543210",
    "to": "+14155550100",
    "ts": "2025-01-15T10:00:00Z",
    "text": "Hello"
  }'
```

**Response:**
```json
{
  "status": "ok"
}
```

**Status Codes:**
- `200` - Message processed successfully (created or duplicate)
- `401` - Invalid or missing signature
- `422` - Validation error (invalid payload)

#### 2. **GET /messages** - List Messages

Query stored messages with pagination and filtering.

**Query Parameters:**
- `limit` (optional, default: 50, max: 100) - Number of messages per page
- `offset` (optional, default: 0) - Pagination offset
- `from` (optional) - Filter by sender phone number
- `since` (optional) - Filter messages after ISO-8601 timestamp
- `q` (optional) - Free-text search in message content

**Examples:**
```bash
# Get all messages
curl http://localhost:8000/messages

# Pagination
curl "http://localhost:8000/messages?limit=10&offset=20"

# Filter by sender
curl "http://localhost:8000/messages?from=%2B919876543210"

# Filter by timestamp
curl "http://localhost:8000/messages?since=2025-01-15T09:00:00Z"

# Text search
curl "http://localhost:8000/messages?q=hello"

# Combined filters
curl "http://localhost:8000/messages?from=%2B919876543210&since=2025-01-15T00:00:00Z&limit=20"
```

**Response:**
```json
{
  "data": [
    {
      "message_id": "m1",
      "from": "+919876543210",
      "to": "+14155550100",
      "ts": "2025-01-15T10:00:00Z",
      "text": "Hello"
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

#### 3. **GET /stats** - Analytics

Get aggregated message statistics.

**Example:**
```bash
curl http://localhost:8000/stats | jq
```

**Response:**
```json
{
  "total_messages": 123,
  "senders_count": 10,
  "messages_per_sender": [
    { "from": "+919876543210", "count": 50 },
    { "from": "+911234567890", "count": 30 }
  ],
  "first_message_ts": "2025-01-10T09:00:00Z",
  "last_message_ts": "2025-01-15T10:00:00Z"
}
```

#### 4. **GET /metrics** - Prometheus Metrics

Exposes application metrics in Prometheus format.

**Key Metrics:**
- `http_requests_total` - Total HTTP requests by path and status
- `webhook_requests_total` - Webhook processing outcomes
- `request_latency_ms_bucket` - Request latency histograms

**Example:**
```bash
curl http://localhost:8000/metrics
```

---

## 🧪 Testing the API

### Using Make Commands

```bash
# Check health
make health

# View messages
make messages

# View statistics
make stats

# View metrics
make metrics

# Run quick validation test
make quick-test
```

### Manual Testing Workflow

```bash
# 1. Generate HMAC signature helper
cat > sign.py << 'EOF'
import hmac
import hashlib
import sys

secret = sys.argv[1] if len(sys.argv) > 1 else "testsecret"
body = sys.stdin.read()
signature = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
print(signature)
EOF

# 2. Send a test message
BODY='{"message_id":"test1","from":"+919876543210","to":"+14155550100","ts":"2025-01-15T10:00:00Z","text":"Test message"}'
SIG=$(echo -n "$BODY" | python3 sign.py "testsecret")

curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -H "X-Signature: $SIG" \
  -d "$BODY"

# 3. Verify message was stored
curl http://localhost:8000/messages | jq '.data[] | select(.message_id=="test1")'

# 4. Test idempotency (send same message again)
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -H "X-Signature: $SIG" \
  -d "$BODY"

# Should still return 200, but no duplicate in database
curl "http://localhost:8000/messages?from=%2B919876543210" | jq '.total'
```

---

## 🏗️ Architecture & Design Decisions

### 1. HMAC Signature Verification

**Implementation:**
- Uses HMAC-SHA256 for webhook authentication
- Signature computed over raw request body bytes
- Constant-time comparison to prevent timing attacks
- Validation occurs before any processing or database interaction

**Security Considerations:**
- `WEBHOOK_SECRET` must be set or application won't start
- Invalid signatures return 401 immediately
- No data leakage on signature failures

```python
# Signature validation logic
signature = hmac.new(
    WEBHOOK_SECRET.encode(),
    request_body_bytes,
    hashlib.sha256
).hexdigest()

if not hmac.compare_digest(signature, provided_signature):
    # Reject request - return 401
```

### 2. Idempotency & Message Storage

**Design:**
- SQLite with `PRIMARY KEY` constraint on `message_id`
- Application-level handling of duplicate key conflicts
- Idempotent responses: duplicate messages return 200 with same response

**Benefits:**
- Guarantees exactly-once storage at database level
- Safe for retries and network issues
- No duplicate processing even under concurrent requests

**Database Schema:**
```sql
CREATE TABLE messages (
    message_id TEXT PRIMARY KEY,
    from_msisdn TEXT NOT NULL,
    to_msisdn TEXT NOT NULL,
    ts TEXT NOT NULL,
    text TEXT,
    created_at TEXT NOT NULL
);
```

### 3. Pagination & Filtering

**Contract:**
- **Ordering:** Deterministic `ORDER BY ts ASC, message_id ASC`
- **Pagination:** Offset-based with `limit` and `offset`
- **Total Count:** Accurate total matching filters (not just page size)
- **Filters:** Composable - can combine `from`, `since`, and `q`

**Performance:**
- Indexed queries for efficient filtering
- Separate count query for accurate totals
- Bounded result sets (max limit: 100)

### 4. Statistics Endpoint

**Aggregation Strategy:**
- Uses SQL aggregation for efficiency
- Top 10 senders by message count
- Min/max timestamps computed in single query
- O(N log N) complexity for sender ranking

**SQL Approach:**
```sql
-- Efficient single-query aggregation
SELECT 
    COUNT(*) as total,
    COUNT(DISTINCT from_msisdn) as senders,
    MIN(ts) as first_ts,
    MAX(ts) as last_ts
FROM messages;
```

### 5. Metrics & Observability

**Prometheus Metrics:**
- **Counters:** Request totals, webhook outcomes
- **Histograms:** Request latency buckets
- **Labels:** Path, status, result type

**Structured Logging:**
- JSON format for log aggregation
- Request ID for correlation
- Webhook-specific fields: `message_id`, `dup`, `result`

**Request Tracking:**
```json
{
  "ts": "2025-01-15T10:00:00Z",
  "level": "INFO",
  "request_id": "abc123",
  "method": "POST",
  "path": "/webhook",
  "status": 200,
  "latency_ms": 45.2,
  "message_id": "m1",
  "dup": false,
  "result": "created"
}
```

---

## ⚙️ Configuration

All configuration via environment variables (12-factor app):

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `WEBHOOK_SECRET` | HMAC secret for signature verification | - | ✅ Yes |
| `DATABASE_URL` | SQLite database path | `sqlite:////data/app.db` | No |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | `INFO` | No |

### Setting Environment Variables

**Option 1: Export in shell**
```bash
export WEBHOOK_SECRET="your-secret-key"
export LOG_LEVEL="DEBUG"
make up
```

**Option 2: Create .env file**
```bash
cat > .env << EOF
WEBHOOK_SECRET=your-secret-key
DATABASE_URL=sqlite:////data/app.db
LOG_LEVEL=INFO
EOF

docker compose up -d --build
```

---

## 📊 Observability

### Logs

View structured JSON logs:
```bash
# Follow logs
make logs

# Parse with jq
docker compose logs api | jq -r 'select(.message_id != null)'

# Filter by level
docker compose logs api | jq -r 'select(.level == "ERROR")'
```

### Metrics

```bash
# View all metrics
curl http://localhost:8000/metrics

# Specific metrics
curl -s http://localhost:8000/metrics | grep http_requests_total
curl -s http://localhost:8000/metrics | grep webhook_requests_total
```

### Health Monitoring

```bash
# Liveness (is container alive?)
curl http://localhost:8000/health/live

# Readiness (is app ready to serve traffic?)
curl http://localhost:8000/health/ready
```

---

## 🛠️ Development

### Available Make Commands

```bash
make help          # Show all available commands
make up            # Start services
make down          # Stop services
make restart       # Restart services
make logs          # View logs
make test          # Run tests
make health        # Check health endpoints
make messages      # Query messages
make stats         # View statistics
make metrics       # View metrics
make shell         # Open container shell
make db-shell      # Open SQLite shell
make clean         # Full cleanup
make quick-test    # Run validation tests
```

### Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI app, routes, middleware
│   ├── models.py            # Database models & initialization
│   ├── storage.py           # Database operations
│   ├── logging_utils.py     # JSON logger setup
│   ├── metrics.py           # Prometheus metrics
│   └── config.py            # Environment configuration
├── tests/
│   ├── test_webhook.py      # Webhook endpoint tests
│   ├── test_messages.py     # Messages endpoint tests
│   └── test_stats.py        # Statistics tests
├── Dockerfile               # Multi-stage container build
├── docker-compose.yml       # Service orchestration
├── Makefile                 # Development commands
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
docker compose exec api pytest tests/test_webhook.py -v

# Run with coverage
docker compose exec api pytest --cov=app tests/
```

### Inspecting the Database

```bash
# Open SQLite shell
make db-shell

# Run queries
sqlite> SELECT COUNT(*) FROM messages;
sqlite> SELECT * FROM messages LIMIT 5;
sqlite> .schema messages
```

---

## 🧰 Setup Used

**Development Environment:**
- VSCode with Python extension
- Claude AI (Anthropic) for architecture discussions and documentation
- ChatGPT for specific implementation patterns

**Tools & Technologies:**
- Python 3.11+
- FastAPI (async web framework)
- SQLite (embedded database)
- Docker & Docker Compose
- Pydantic (data validation)

---

## 📝 Notes

- **Database:** SQLite file persists in Docker volume at `/data/app.db`
- **Port:** Application runs on `http://localhost:8000`
- **Signature:** All webhook requests require valid HMAC-SHA256 signature
- **Idempotency:** Duplicate `message_id` values are handled gracefully
- **Ordering:** Messages always returned in `ts ASC, message_id ASC` order

---

## 🤝 Contributing

This is a backend assignment submission. For questions or issues, contact:
- Email: careers@lyftr.ai
- Repository: https://github.com/Bhavishya-Chaturvedi/Lyfter-backend

---

## 📄 License

This project is part of the Lyftr AI backend assignment.

---

<div align="center">
  <strong>Built with ❤️ for Lyftr AI</strong>
</div>
