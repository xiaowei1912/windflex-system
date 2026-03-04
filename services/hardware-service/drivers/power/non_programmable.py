"""
Non-programmable power supply driver.
The board is always powered on. Only SSH soft-reboot is supported.
"""
import logging
from typing import Optional

from drivers.power.base import BasePowerDriver, PowerCapability, PowerStatus

logger = logging.getLogger(__name__)


class NonProgrammablePowerDriver(BasePowerDriver):
    """
    Driver for boards with non-programmable (always-on) power supplies.
    Hardware power control is not available; soft reboot via SSH is provided
    as a best-effort mechanism by delegating to the SSH client.
    """

    MODEL = "Non-programmable"

    def __init__(self, ssh_reboot_fn=None):
        """
        :param ssh_reboot_fn: Optional callable that performs an SSH soft-reboot.
                              If None the reboot call will return a warning.
        """
        self._ssh_reboot_fn = ssh_reboot_fn

    def get_capability(self) -> PowerCapability:
        return PowerCapability(
            model=self.MODEL,
            programmable=False,
            can_power_on=False,
            can_power_off=False,
            can_read_voltage=False,
            can_read_current=False,
            can_reboot=True,
            notes=(
                "Non-programmable power supply: board is always powered on. "
                "Reboot is performed via SSH (shutdown -r now)."
            ),
        )

    def get_status(self) -> PowerStatus:
        return PowerStatus(
            model=self.MODEL,
            programmable=False,
            voltage=None,
            current=None,
            power_on=True,  # assumed always on
            status_message="Non-programmable supply: always on, no telemetry available.",
        )

    def power_on(self) -> dict:
        return {
            "success": False,
            "reason": "Power ON not supported with non-programmable supply.",
            "model": self.MODEL,
        }

    def power_off(self) -> dict:
        return {
            "success": False,
            "reason": "Power OFF not supported with non-programmable supply.",
            "model": self.MODEL,
        }

    def reboot(self) -> dict:
        if self._ssh_reboot_fn is None:
            return {
                "success": False,
                "reason": "SSH reboot function not configured.",
                "model": self.MODEL,
            }
        try:
            result = self._ssh_reboot_fn()
            return {"success": True, "method": "ssh_soft_reboot", "detail": result}
        except Exception as exc:
            logger.exception("SSH reboot failed")
            return {"success": False, "reason": str(exc), "model": self.MODEL}

    def get_voltage(self) -> Optional[float]:
        return None

    def get_current(self) -> Optional[float]:
        return None
