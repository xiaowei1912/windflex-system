"""
ADB manager: wraps the system `adb` CLI tool.
Assumes a single board is connected (no device ID required).
"""
import logging
import os
import shutil
import subprocess
from typing import List, Optional

logger = logging.getLogger(__name__)

_ADB_TIMEOUT = 30


def _run(args: List[str], timeout: int = _ADB_TIMEOUT) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


class ADBManager:
    def __init__(self):
        self._adb_available: Optional[bool] = None

    # ------------------------------------------------------------------
    # Availability
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        if self._adb_available is None:
            self._adb_available = shutil.which("adb") is not None
        return self._adb_available

    def _check_available(self):
        if not self.is_available():
            raise RuntimeError(
                "adb CLI not found. Install Android SDK platform-tools and ensure "
                "adb is on PATH."
            )

    # ------------------------------------------------------------------
    # Device management
    # ------------------------------------------------------------------

    def list_devices(self) -> List[dict]:
        """Return list of connected ADB devices."""
        self._check_available()
        result = _run(["adb", "devices", "-l"])
        devices = []
        for line in result.stdout.splitlines()[1:]:
            line = line.strip()
            if not line or "offline" in line:
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[1] in ("device", "recovery", "sideload"):
                entry: dict = {"serial": parts[0], "state": parts[1]}
                for kv in parts[2:]:
                    if ":" in kv:
                        k, v = kv.split(":", 1)
                        entry[k] = v
                devices.append(entry)
        return devices

    def get_connected_device(self) -> Optional[str]:
        """Return serial of the single connected device, or None."""
        devices = self.list_devices()
        if len(devices) == 1:
            return devices[0]["serial"]
        if len(devices) > 1:
            logger.warning("Multiple ADB devices connected; returning first.")
            return devices[0]["serial"]
        return None

    # ------------------------------------------------------------------
    # SSH key push
    # ------------------------------------------------------------------

    def push_ssh_key(self, public_key_path: str) -> dict:
        """
        Push the SSH public key to the board via ADB.
        Sets up /root/.ssh/authorized_keys on the device.
        """
        self._check_available()
        if not os.path.exists(public_key_path):
            return {"success": False, "reason": f"Key file not found: {public_key_path}"}

        device = self.get_connected_device()
        if not device:
            return {"success": False, "reason": "No ADB device connected"}

        # Make sure .ssh dir exists with correct permissions
        _run(["adb", "-s", device, "shell", "mkdir -p /root/.ssh && chmod 700 /root/.ssh"])

        # Push the key
        remote_tmp = "/tmp/id_rsa_tmp.pub"
        push = _run(["adb", "-s", device, "push", public_key_path, remote_tmp])
        if push.returncode != 0:
            return {"success": False, "reason": push.stderr}

        # Append (avoiding duplicates)
        append = _run([
            "adb", "-s", device, "shell",
            f"grep -qxF \"$(cat {remote_tmp})\" /root/.ssh/authorized_keys 2>/dev/null "
            f"|| cat {remote_tmp} >> /root/.ssh/authorized_keys && "
            f"chmod 600 /root/.ssh/authorized_keys && rm {remote_tmp}"
        ])
        if append.returncode != 0:
            return {"success": False, "reason": append.stderr}

        logger.info("SSH public key pushed via ADB to device %s", device)
        return {"success": True, "device": device, "key": public_key_path}

    # ------------------------------------------------------------------
    # Generic ADB command
    # ------------------------------------------------------------------

    def run_command(self, command: str) -> dict:
        """Run an arbitrary `adb shell <command>` on the single connected device."""
        self._check_available()
        device = self.get_connected_device()
        if not device:
            return {"success": False, "reason": "No ADB device connected"}
        result = _run(["adb", "-s", device, "shell", command])
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        }

    def get_status(self) -> dict:
        available = self.is_available()
        devices = self.list_devices() if available else []
        return {
            "adb_available": available,
            "device_count": len(devices),
            "devices": devices,
        }


# Singleton instance
adb_manager = ADBManager()
