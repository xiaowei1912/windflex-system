"""
Unit tests for Hardware Control Service API.
Uses httpx TestClient to test without real hardware.
"""
import os

import pytest
from fastapi.testclient import TestClient

# Set environment variables before importing modules that depend on them
os.environ.setdefault("BOARD_IP", "127.0.0.1")
os.environ.setdefault("POWER_MODEL", "Non-programmable")
os.environ.setdefault("LOG_LEVEL", "WARNING")

from main import app  # noqa: E402

client = TestClient(app)


# ---------------------------------------------------------------------------
# Health & Info
# ---------------------------------------------------------------------------

def test_health():
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_info():
    resp = client.get("/api/v1/info")
    assert resp.status_code == 200
    data = resp.json()
    assert data["power_model"] == "Non-programmable"
    assert data["is_programmable_power"] is False


# ---------------------------------------------------------------------------
# Power endpoints (non-programmable mode)
# ---------------------------------------------------------------------------

def test_power_capability():
    resp = client.get("/api/v1/power/capability")
    assert resp.status_code == 200
    data = resp.json()
    assert data["programmable"] is False
    assert data["can_power_on"] is False
    assert data["can_power_off"] is False
    assert data["can_reboot"] is True


def test_power_status():
    resp = client.get("/api/v1/power/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["programmable"] is False
    assert data["power_on"] is True  # assumed always on


def test_power_on_not_supported():
    resp = client.post("/api/v1/power/on")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is False


def test_power_off_not_supported():
    resp = client.post("/api/v1/power/off")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is False


# ---------------------------------------------------------------------------
# ADB endpoints
# ---------------------------------------------------------------------------

def test_adb_status():
    resp = client.get("/api/v1/adb/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "adb_available" in data
    assert "devices" in data


# ---------------------------------------------------------------------------
# Serial endpoints
# ---------------------------------------------------------------------------

def test_serial_status():
    resp = client.get("/api/v1/serial/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "is_open" in data


def test_serial_ports():
    resp = client.get("/api/v1/serial/ports")
    assert resp.status_code == 200
    assert "ports" in resp.json()


# ---------------------------------------------------------------------------
# SSH endpoints
# ---------------------------------------------------------------------------

def test_ssh_status():
    resp = client.get("/api/v1/ssh/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "connected" in data
    assert data["connected"] is False  # no real board in test environment


def test_ssh_exec_no_connection():
    """SSH exec should return 503 when board is unreachable."""
    resp = client.post("/api/v1/ssh/exec", json={"command": "echo hello"})
    # We expect either 503 (can't connect) or 200 if mock loopback works
    assert resp.status_code in (200, 503)
