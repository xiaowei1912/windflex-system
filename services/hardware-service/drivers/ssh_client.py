"""
SSH client wrapper using paramiko.
Provides connection pooling (single cached connection) with automatic reconnect.
"""
import logging
import time
from typing import Optional, Tuple

import paramiko

from config import settings

logger = logging.getLogger(__name__)


class SSHClient:
    def __init__(self):
        self._client: Optional[paramiko.SSHClient] = None
        self._connected: bool = False

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def connect(self) -> bool:
        """Establish SSH connection to the board. Returns True on success."""
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            connect_kwargs = dict(
                hostname=settings.BOARD_IP,
                port=settings.BOARD_SSH_PORT,
                username=settings.BOARD_SSH_USER,
                timeout=settings.BOARD_SSH_TIMEOUT,
            )
            # Prefer key-based auth; fall back to password if env var set
            import os
            ssh_password = os.environ.get("BOARD_SSH_PASSWORD")
            if ssh_password:
                connect_kwargs["password"] = ssh_password
            else:
                key_path = settings.BOARD_SSH_KEY_PATH
                if key_path and os.path.exists(key_path):
                    connect_kwargs["key_filename"] = key_path
                else:
                    connect_kwargs["look_for_keys"] = True
                    connect_kwargs["allow_agent"] = True

            client.connect(**connect_kwargs)
            self._client = client
            self._connected = True
            logger.info(
                "SSH connected to %s:%s", settings.BOARD_IP, settings.BOARD_SSH_PORT
            )
            return True
        except Exception as exc:
            logger.error("SSH connect failed: %s", exc)
            self._connected = False
            return False

    def disconnect(self) -> None:
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None
        self._connected = False
        logger.info("SSH disconnected")

    def is_connected(self) -> bool:
        if not self._connected or self._client is None:
            return False
        transport = self._client.get_transport()
        return transport is not None and transport.is_active()

    def ensure_connected(self) -> bool:
        if not self.is_connected():
            return self.connect()
        return True

    # ------------------------------------------------------------------
    # Command execution
    # ------------------------------------------------------------------

    def exec_command(
        self,
        command: str,
        timeout: int = 60,
        get_pty: bool = False,
    ) -> Tuple[int, str, str]:
        """
        Execute a command on the remote board.

        Returns:
            (exit_code, stdout, stderr)
        Raises:
            RuntimeError if not connected and reconnect fails.
        """
        if not self.ensure_connected():
            raise RuntimeError(
                f"Cannot connect to board at {settings.BOARD_IP}:{settings.BOARD_SSH_PORT}"
            )

        try:
            stdin, stdout, stderr = self._client.exec_command(
                command, timeout=timeout, get_pty=get_pty
            )
            exit_code = stdout.channel.recv_exit_status()
            out = stdout.read().decode("utf-8", errors="replace").strip()
            err = stderr.read().decode("utf-8", errors="replace").strip()
            logger.debug("exec[%d] %r -> %r", exit_code, command, out[:200])
            return exit_code, out, err
        except Exception as exc:
            logger.error("exec_command failed: %s", exc)
            self._connected = False
            raise

    def reboot(self, wait_seconds: int = 5) -> dict:
        """Issue a soft reboot via SSH."""
        try:
            # Fire-and-forget; the connection will drop after reboot
            if not self.ensure_connected():
                raise RuntimeError("SSH not available")
            stdin, stdout, stderr = self._client.exec_command(
                "shutdown -r now", timeout=10
            )
            time.sleep(wait_seconds)
            self.disconnect()
            return {"success": True, "command": "shutdown -r now"}
        except Exception as exc:
            logger.exception("SSH reboot failed")
            return {"success": False, "reason": str(exc)}

    def get_status(self) -> dict:
        return {
            "host": settings.BOARD_IP,
            "port": settings.BOARD_SSH_PORT,
            "user": settings.BOARD_SSH_USER,
            "connected": self.is_connected(),
        }


# Singleton instance
ssh_client = SSHClient()
