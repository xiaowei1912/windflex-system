"""
Hardware Control Service - FastAPI application entry point.
"""
import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from config import settings
from api.power import router as power_router
from api.adb import router as adb_router
from api.serial_api import router as serial_router
from api.ssh_api import router as ssh_router

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan (replaces deprecated on_event)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(application: FastAPI):
    # Startup
    logger.info("Hardware Control Service starting up")
    logger.info("Power model: %s", settings.POWER_MODEL.value)
    logger.info("Board IP:    %s:%s", settings.BOARD_IP, settings.BOARD_SSH_PORT)
    if not settings.is_programmable_power:
        logger.warning(
            "Non-programmable power supply configured. "
            "Power ON/OFF will not be available. Only SSH soft-reboot is supported."
        )
    yield
    # Shutdown
    logger.info("Hardware Control Service shutting down")
    from drivers.ssh_client import ssh_client
    from drivers.serial_communicator import serial_communicator
    ssh_client.disconnect()
    serial_communicator.close()


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Windflex Hardware Control Service",
    description=(
        "REST API for controlling test board hardware: "
        "SSH, ADB, Serial port, and Power supply."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(power_router)
app.include_router(adb_router)
app.include_router(serial_router)
app.include_router(ssh_router)


# ---------------------------------------------------------------------------
# Health & Info
# ---------------------------------------------------------------------------
@app.get("/api/v1/health", tags=["System"])
def health_check():
    return {"status": "ok"}


@app.get("/api/v1/info", tags=["System"])
def system_info():
    """Return current system configuration (no secrets)."""
    return {
        "board_ip": settings.BOARD_IP,
        "board_ssh_port": settings.BOARD_SSH_PORT,
        "power_model": settings.POWER_MODEL.value,
        "is_programmable_power": settings.is_programmable_power,
        "serial_device": settings.SERIAL_DEVICE,
        "baud_rate": settings.BAUD_RATE,
        "log_level": settings.LOG_LEVEL,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.SERVICE_HOST,
        port=settings.SERVICE_PORT,
        reload=False,
        log_level=settings.LOG_LEVEL.lower(),
    )
