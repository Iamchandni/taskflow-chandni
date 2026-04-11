"""
app/main.py
───────────
FastAPI application entry point. Responsible for:
1. Application lifespan (startup/shutdown)
2. Structured logging setup
3. Router registration
4. Exception handlers that map domain exceptions → HTTP responses
5. Pydantic validation error override (422 → 400 with structured body)

This file is the outermost layer. It imports from api/ and core/ only.
"""

import signal
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.core.logging import get_logger, setup_logging

# Import routers
from app.api.v1.auth_router import router as auth_router
from app.api.v1.project_router import router as project_router
from app.api.v1.task_router import router as task_router

logger = get_logger(__name__)


# ── Lifespan (startup + shutdown) ──────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    - Startup: configure logging, log ready message
    - Shutdown: graceful cleanup
    """
    setup_logging(json_logs=True, log_level="INFO")
    logger.info("taskflow_starting", version="1.0.0")

    yield  # Application runs here

    logger.info("taskflow_shutting_down")


# ── Create app ─────────────────────────────────────────────────

app = FastAPI(
    title="TaskFlow API",
    description="A minimal but real task management system with DDD architecture.",
    version="1.0.0",
    lifespan=lifespan,
)


# ── Register routers ──────────────────────────────────────────

app.include_router(auth_router)
app.include_router(project_router)
app.include_router(task_router)


# ── Exception handlers ─────────────────────────────────────────


@app.exception_handler(RequestValidationError)
async def pydantic_validation_handler(request: Request, exc: RequestValidationError):
    """
    Override FastAPI's default 422 → 400 with structured field errors.
    Produces: { "error": "validation failed", "fields": { "email": "is required" } }
    """
    fields = {}
    for error in exc.errors():
        # Get the field name from the location tuple
        loc = error.get("loc", ())
        field_name = str(loc[-1]) if loc else "unknown"
        # Skip 'body' prefix
        if field_name == "body" and len(loc) > 1:
            field_name = str(loc[-1])

        msg = error.get("msg", "invalid")
        # Simplify common Pydantic messages
        if "missing" in msg.lower() or "required" in msg.lower():
            msg = "is required"
        elif "string" in msg.lower() and "short" in msg.lower():
            msg = "is too short"

        fields[field_name] = msg

    return JSONResponse(
        status_code=400,
        content={"error": "validation failed", "fields": fields},
    )


@app.exception_handler(ValidationError)
async def domain_validation_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": "validation failed", "fields": exc.fields},
    )


@app.exception_handler(AuthenticationError)
async def authentication_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(
        status_code=401,
        content={"error": exc.message},
    )


@app.exception_handler(AuthorizationError)
async def authorization_handler(request: Request, exc: AuthorizationError):
    return JSONResponse(
        status_code=403,
        content={"error": exc.message},
    )


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={"error": exc.message},
    )


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(
        status_code=409,
        content={"error": exc.message},
    )


# ── Graceful shutdown on SIGTERM ──────────────────────────────

def handle_sigterm(*args):
    logger.info("received_sigterm")
    sys.exit(0)


signal.signal(signal.SIGTERM, handle_sigterm)


# ── Health check ──────────────────────────────────────────────


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
