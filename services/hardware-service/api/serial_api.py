"""
Serial communication API routes.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from drivers.serial_communicator import serial_communicator

router = APIRouter(prefix="/api/v1/serial", tags=["Serial"])


class SerialOpenRequest(BaseModel):
    device: Optional[str] = None
    baud_rate: Optional[int] = None


class SerialSendRequest(BaseModel):
    data: str
    newline: bool = True
    wait_response: bool = True


@router.get("/status")
def serial_status():
    """Return serial port status and available ports."""
    return serial_communicator.get_status()


@router.get("/ports")
def list_ports():
    """List all available serial ports on the host."""
    return {"ports": serial_communicator.list_ports()}


@router.post("/open")
def open_serial(req: SerialOpenRequest = SerialOpenRequest()):
    """Open the serial port."""
    result = serial_communicator.open(device=req.device, baud_rate=req.baud_rate)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("reason", "Failed to open port"))
    return result


@router.post("/close")
def close_serial():
    """Close the serial port."""
    return serial_communicator.close()


@router.post("/send")
def send_serial(req: SerialSendRequest):
    """Send data over the serial port."""
    result = serial_communicator.send(
        data=req.data,
        newline=req.newline,
        wait_response=req.wait_response,
    )
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("reason", "Send failed"))
    return result
