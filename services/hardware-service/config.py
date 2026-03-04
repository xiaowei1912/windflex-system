"""
Configuration management for the Hardware Control Service.
All settings are loaded from environment variables.
"""
import os
from enum import Enum


class PowerModel(str, Enum):
    PROGRAMMABLE = "DLX-30V10AMP"
    NON_PROGRAMMABLE = "Non-programmable"


class Settings:
    # Board
    BOARD_IP: str = os.environ.get("BOARD_IP", "192.168.1.100")
    BOARD_SSH_PORT: int = int(os.environ.get("BOARD_SSH_PORT", "22"))
    BOARD_SSH_USER: str = os.environ.get("BOARD_SSH_USER", "root")
    BOARD_SSH_KEY_PATH: str = os.environ.get(
        "BOARD_SSH_KEY_PATH", "/root/.ssh/id_rsa"
    )
    BOARD_SSH_TIMEOUT: int = int(os.environ.get("BOARD_SSH_TIMEOUT", "30"))

    # Power
    POWER_MODEL: PowerModel = PowerModel(
        os.environ.get("POWER_MODEL", PowerModel.NON_PROGRAMMABLE.value)
    )
    SERIAL_DEVICE: str = os.environ.get("SERIAL_DEVICE", "/dev/ttyUSB0")
    BAUD_RATE: int = int(os.environ.get("BAUD_RATE", "9600"))

    # Application
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    SERVICE_HOST: str = os.environ.get("SERVICE_HOST", "0.0.0.0")
    SERVICE_PORT: int = int(os.environ.get("SERVICE_PORT", "8000"))

    @property
    def is_programmable_power(self) -> bool:
        return self.POWER_MODEL == PowerModel.PROGRAMMABLE


settings = Settings()
