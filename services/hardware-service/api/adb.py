"""
ADB management API routes.
"""
import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from drivers.adb_manager import adb_manager

router = APIRouter(prefix="/api/v1/adb", tags=["ADB"])


class ADBCommandRequest(BaseModel):
    command: str


class PushKeyRequest(BaseModel):
    public_key_path: str = "/root/.ssh/id_rsa.pub"


@router.get("/status")
def adb_status():
    """Return ADB availability and connected devices."""
    return adb_manager.get_status()


@router.get("/devices")
def list_devices():
    """List connected ADB devices."""
    if not adb_manager.is_available():
        raise HTTPException(status_code=503, detail="adb CLI not available on this host")
    return {"devices": adb_manager.list_devices()}


@router.post("/push-key")
def push_ssh_key(req: PushKeyRequest):
    """Push SSH public key to the board via ADB."""
    if not adb_manager.is_available():
        raise HTTPException(status_code=503, detail="adb CLI not available on this host")
    result = adb_manager.push_ssh_key(req.public_key_path)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("reason", "Unknown error"))
    return result


@router.post("/command")
def run_adb_command(req: ADBCommandRequest):
    """Execute an arbitrary adb shell command on the connected device."""
    if not adb_manager.is_available():
        raise HTTPException(status_code=503, detail="adb CLI not available on this host")
    return adb_manager.run_command(req.command)
