"""
Power supply API routes (non-programmable mode).
"""
from fastapi import APIRouter
from pydantic import BaseModel

from config import settings, PowerModel
from drivers.power.non_programmable import NonProgrammablePowerDriver
from drivers.ssh_client import ssh_client

router = APIRouter(prefix="/api/v1/power", tags=["Power"])

# Instantiate driver once; inject SSH reboot function
_driver = NonProgrammablePowerDriver(ssh_reboot_fn=ssh_client.reboot)


class RebootRequest(BaseModel):
    reason: str = "manual"


@router.get("/capability")
def get_power_capability():
    """Return the capabilities of the currently configured power supply."""
    cap = _driver.get_capability()
    return {
        "model": cap.model,
        "programmable": cap.programmable,
        "can_power_on": cap.can_power_on,
        "can_power_off": cap.can_power_off,
        "can_read_voltage": cap.can_read_voltage,
        "can_read_current": cap.can_read_current,
        "can_reboot": cap.can_reboot,
        "notes": cap.notes,
    }


@router.get("/status")
def get_power_status():
    """Return current power status."""
    s = _driver.get_status()
    return {
        "model": s.model,
        "programmable": s.programmable,
        "voltage": s.voltage,
        "current": s.current,
        "power_on": s.power_on,
        "status_message": s.status_message,
    }


@router.post("/on")
def power_on():
    """Power ON the board (not supported in non-programmable mode)."""
    return _driver.power_on()


@router.post("/off")
def power_off():
    """Power OFF the board (not supported in non-programmable mode)."""
    return _driver.power_off()


@router.post("/reboot")
def reboot(req: RebootRequest = RebootRequest()):
    """
    Soft-reboot the board via SSH.
    Non-programmable mode: issues `shutdown -r now`.
    """
    return _driver.reboot()
