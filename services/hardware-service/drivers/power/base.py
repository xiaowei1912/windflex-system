"""
Abstract base class for all power supply drivers.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class PowerCapability:
    model: str
    programmable: bool
    can_power_on: bool
    can_power_off: bool
    can_read_voltage: bool
    can_read_current: bool
    can_reboot: bool  # True for both modes (programmable = hard, non-prog = SSH)
    notes: str = ""


@dataclass
class PowerStatus:
    model: str
    programmable: bool
    voltage: Optional[float] = None
    current: Optional[float] = None
    power_on: Optional[bool] = None
    status_message: str = ""


class BasePowerDriver(ABC):
    @abstractmethod
    def get_capability(self) -> PowerCapability:
        ...

    @abstractmethod
    def get_status(self) -> PowerStatus:
        ...

    @abstractmethod
    def power_on(self) -> dict:
        ...

    @abstractmethod
    def power_off(self) -> dict:
        ...

    @abstractmethod
    def reboot(self) -> dict:
        ...

    @abstractmethod
    def get_voltage(self) -> Optional[float]:
        ...

    @abstractmethod
    def get_current(self) -> Optional[float]:
        ...
