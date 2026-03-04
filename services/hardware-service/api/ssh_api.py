"""
SSH management API routes.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from drivers.ssh_client import ssh_client

router = APIRouter(prefix="/api/v1/ssh", tags=["SSH"])


class SSHExecRequest(BaseModel):
    command: str
    timeout: int = 60


@router.get("/status")
def ssh_status():
    """Return SSH connection status."""
    return ssh_client.get_status()


@router.post("/connect")
def ssh_connect():
    """Establish SSH connection to the board."""
    success = ssh_client.connect()
    if not success:
        raise HTTPException(status_code=503, detail="Failed to connect via SSH")
    return {"success": True, "message": "SSH connected"}


@router.delete("/disconnect")
def ssh_disconnect():
    """Disconnect SSH session."""
    ssh_client.disconnect()
    return {"success": True, "message": "SSH disconnected"}


@router.post("/exec")
def ssh_exec(req: SSHExecRequest):
    """
    Execute a command on the board via SSH.
    Returns exit_code, stdout, stderr.
    """
    try:
        exit_code, stdout, stderr = ssh_client.exec_command(
            command=req.command,
            timeout=req.timeout,
        )
        return {
            "success": exit_code == 0,
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "command": req.command,
        }
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
