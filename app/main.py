import time
import uuid
import hmac
import hashlib
import json
import re
from fastapi import FastAPI, Request, HTTPException , Query
from fastapi.responses import PlainTextResponse
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError
from app.config import WEBHOOK_SECRET
from app.models import init_db
from app.storage import insert_message, fetch_messages, fetch_stats  
from app.models import get_connection
from app.logging_utils import log_json


HTTP_REQUESTS_TOTAL = 0
WEBHOOK_REQUESTS_TOTAL = 0
WEBHOOK_REJECTED_TOTAL = 0

app = FastAPI()


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    global HTTP_REQUESTS_TOTAL

    HTTP_REQUESTS_TOTAL += 1
    request_id = str(uuid.uuid4())
    start_time = time.time()

    response = await call_next(request)

    latency_ms = int((time.time() - start_time) * 1000)

    log_json(
        level="INFO",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        latency_ms=latency_ms
    )

    return response



# Health
@app.get("/health/live")
def live():
    return {"status": "alive"}

@app.get("/health/ready")
def ready():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        conn.close()
        return {"status": "ready"}
    except Exception:
        return {"status": "not_ready"}
    
# Startup
@app.on_event("startup")
def startup():
    if not WEBHOOK_SECRET:
        raise RuntimeError("WEBHOOK_SECRET is not set")
    init_db()
    print("WEBHOOK_SECRET IN APP =", WEBHOOK_SECRET)


# HMAC Verification
def verify_hmac_signature(secret: str, raw_body: bytes, signature: str) -> bool:
    computed = hmac.new(
        secret.encode(),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(computed, signature)

E164_REGEX = re.compile(r"^\+\d+$")

class WebhookMessage(BaseModel):
    message_id: str = Field(..., min_length=1)
    from_msisdn: str = Field(..., alias="from")
    to_msisdn: str = Field(..., alias="to")
    ts: datetime
    text: str | None = Field(default=None, max_length=4096)

    @staticmethod
    def _validate_msisdn(v: str) -> str:
        if not E164_REGEX.match(v):
            raise ValueError("invalid msisdn")
        return v

    @classmethod
    def validate(cls, value):
        return value

    def __init__(self, **data):
        super().__init__(**data)
        self.from_msisdn = self._validate_msisdn(self.from_msisdn)
        self.to_msisdn = self._validate_msisdn(self.to_msisdn)

# Webhook Endpoint
@app.post("/webhook")
async def webhook(request: Request):
    global WEBHOOK_REQUESTS_TOTAL, WEBHOOK_REJECTED_TOTAL
    WEBHOOK_REQUESTS_TOTAL += 1
    raw_body = await request.body()

    signature = request.headers.get("X-Signature")
    if not signature:
        log_json(
            event="webhook",
            result="rejected",
            reason="missing_signature",
            message_id=None,
            dup=None
        )
        raise HTTPException(status_code=401, detail="invalid signature")

    if not verify_hmac_signature(WEBHOOK_SECRET, raw_body, signature):
        log_json(
            event="webhook",
            result="rejected",
            reason="invalid_signature",
            message_id=None,
            dup=None
        )
        raise HTTPException(status_code=401, detail="invalid signature")

    # Validation
    try:
        payload = json.loads(raw_body)
        msg = WebhookMessage(**payload)
    except (json.JSONDecodeError, ValidationError, ValueError):
        log_json(
            event="webhook",
            result="rejected",
            reason="invalid_payload",
            message_id=None,
            dup=None
        )
        raise HTTPException(status_code=422, detail="invalid payload")

    result = insert_message(msg)  # "created" or "duplicate"

    log_json(
        event="webhook",
        result=result,
        message_id=msg.message_id,
        dup=(result == "duplicate")
    )

    return {"status": "ok"}


@app.get("/messages")
def get_messages(

    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    from_msisdn: str | None = Query(None, alias="from"),
    to_msisdn: str | None = Query(None, alias="to"),
    start_ts: str | None = None,
    end_ts: str | None = None
):
    
    messages,total = fetch_messages(
        limit=limit,
        offset=offset,
        from_msisdn=from_msisdn,
        to_msisdn=to_msisdn,
        start_ts=start_ts,
        end_ts=end_ts
    )

    return {
        "data": messages,
        "total": total,
        "limit": limit,
        "offset": offset
            
    }


@app.get("/stats")
def stats():
    return fetch_stats()


@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return (
        f"http_requests_total {HTTP_REQUESTS_TOTAL}\n"
        f"webhook_requests_total {WEBHOOK_REQUESTS_TOTAL}\n"
        f"webhook_rejected_total {WEBHOOK_REJECTED_TOTAL}\n"
    )
