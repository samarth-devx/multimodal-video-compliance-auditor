import asyncio
import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.src.config import get_settings

settings = get_settings()  # loads .env before telemetry reads it

from backend.src.api.telemetry import setup_telemetry
setup_telemetry()

from backend.src.graph.workflow import build_graph
from backend.src.schemas import AuditRequest, AuditResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mvca-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.graph = build_graph(settings)   # built once, not at import time
    yield


app = FastAPI(
    title="Multimodal Video Compliance Auditor API",
    description="Audits YouTube ad content against FTC and brand compliance rules.",
    version="1.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _to_response(session_id: str, video_id: str, state: dict) -> AuditResponse:
    errors = state.get("errors")
    if errors:
        return AuditResponse(
            session_id=session_id, video_id=video_id, status="ERROR",
            final_report="Audit could not be completed: " + "; ".join(errors),
            compliance_results=[],
        )
    return AuditResponse(
        session_id=session_id, video_id=video_id, status=state["status"],
        final_report=state["report"], compliance_results=state["violations"],
    )


@app.post("/audit", response_model=AuditResponse)
async def audit_video(payload: AuditRequest, request: Request):
    session_id = str(uuid.uuid4())
    video_id = f"vid_{session_id[:8]}"
    logger.info("Audit request %s (session %s)", payload.video_url, session_id)

    state = await asyncio.to_thread(
        request.app.state.graph.invoke,
        {"video_url": payload.video_url, "video_id": video_id, "errors": []},
    )
    return _to_response(session_id, video_id, state)


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Multimodal Video Compliance Auditor"}