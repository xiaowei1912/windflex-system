"""
Serial port communicator using pyserial.
Used for logging/AT-command communication with the board or power supply.
"""
import logging
import threading
import time
from typing import Optional

import serial
import serial.tools.list_ports

from config import settings

logger = logging.getLogger(__name__)


class SerialCommunicator:
    def __init__(self):
        self._port: Optional[serial.Serial] = None
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def open(
        self,
        device: Optional[str] = None,
        baud_rate: Optional[int] = None,
    ) -> dict:
        """Open the serial port."""
        device = device or settings.SERIAL_DEVICE
        baud_rate = baud_rate or settings.BAUD_RATE
        with self._lock:
            if self._port and self._port.is_open:
                return {"success": True, "message": "Already open", "device": device}
            try:
                self._port = serial.Serial(
                    port=device,
                    baudrate=baud_rate,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=2,
                    write_timeout=2,
                )
                logger.info("Serial port %s opened at %d baud", device, baud_rate)
                return {"success": True, "device": device, "baud_rate": baud_rate}
            except serial.SerialException as exc:
                logger.error("Failed to open serial port %s: %s", device, exc)
                return {"success": False, "reason": str(exc), "device": device}

    def close(self) -> dict:
        """Close the serial port."""
        with self._lock:
            if self._port and self._port.is_open:
                self._port.close()
                logger.info("Serial port closed")
                return {"success": True}
            return {"success": True, "message": "Port was not open"}

    def is_open(self) -> bool:
        return self._port is not None and self._port.is_open

    # ------------------------------------------------------------------
    # Read / Write
    # ------------------------------------------------------------------

    def send(self, data: str, newline: bool = True, wait_response: bool = True) -> dict:
        """
        Send data over the serial port.
        :param data: String to send.
        :param newline: Append CR+LF.
        :param wait_response: If True, read back a response line.
        """
        if not self.is_open():
            auto = self.open()
            if not auto["success"]:
                return {"success": False, "reason": "Serial port not open and could not be opened"}

        payload = (data + "\r\n" if newline else data).encode()
        with self._lock:
            try:
                self._port.reset_input_buffer()
                self._port.write(payload)
                self._port.flush()
                response = ""
                if wait_response:
                    time.sleep(0.1)
                    raw = self._port.read(self._port.in_waiting or 256)
                    response = raw.decode("utf-8", errors="replace").strip()
                return {"success": True, "sent": data, "response": response}
            except serial.SerialException as exc:
                logger.error("Serial send error: %s", exc)
                return {"success": False, "reason": str(exc)}

    def read_line(self, timeout_s: float = 2.0) -> Optional[str]:
        """Read a single line from the serial port."""
        if not self.is_open():
            return None
        try:
            self._port.timeout = timeout_s
            line = self._port.readline()
            return line.decode("utf-8", errors="replace").strip() if line else None
        except serial.SerialException as exc:
            logger.error("Serial read error: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def list_ports() -> list:
        return [
            {"device": p.device, "description": p.description, "hwid": p.hwid}
            for p in serial.tools.list_ports.comports()
        ]

    def get_status(self) -> dict:
        return {
            "device": self._port.port if self._port else settings.SERIAL_DEVICE,
            "baud_rate": self._port.baudrate if self._port else settings.BAUD_RATE,
            "is_open": self.is_open(),
            "available_ports": self.list_ports(),
        }


# Singleton instance
serial_communicator = SerialCommunicator()
