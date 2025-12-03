import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from models import DeviceConfig, Color, ColorMode
from ble_controller import BleDeviceController


@pytest.mark.asyncio
async def test_build_packet_and_color_command():
    cfg = DeviceConfig(target_mac="", write_char_uuid="uuid")
    ctrl = BleDeviceController(cfg, lambda s: None, lambda c: None, use_real_device=False)

    pkt = ctrl._build_packet(0x03, 10, 20, 30)
    assert isinstance(pkt, bytearray)
    assert pkt[0] == 0x7E and pkt[-1] == 0xEF
    assert pkt[3] == 0x03
    assert pkt[4] == 10 and pkt[5] == 20 and pkt[6] == 30


def test_set_speed_clamps_and_updates():
    cfg = DeviceConfig(target_mac="", write_char_uuid="uuid")
    ctrl = BleDeviceController(cfg, lambda s: None, lambda c: None, use_real_device=False)
    ctrl.speed = 10
    ctrl.set_speed(300)
    assert 0 <= ctrl.speed <= 255
    assert ctrl.speed == 255
    ctrl.set_speed(-5)
    assert ctrl.speed == 0


def test_is_gatt_timeout_exception_simple():
    cfg = DeviceConfig(target_mac="", write_char_uuid="uuid")
    ctrl = BleDeviceController(cfg, lambda s: None, lambda c: None, use_real_device=False)

    e = Exception("GATT CONN TIMEOUT: underlying error")
    assert ctrl._is_gatt_timeout_exception(e) is True

    e2 = Exception("random write error")
    assert ctrl._is_gatt_timeout_exception(e2) is False


@pytest.mark.asyncio
async def test_send_packet_handles_exception_and_increases_backoff():
    cfg = DeviceConfig(target_mac="", write_char_uuid="uuid")
    ctrl = BleDeviceController(cfg, lambda s: None, lambda c: None, auto_reconnect=True, reconnect_interval=1.0, use_real_device=False)

    # Prepare mock client that is connected but write raises
    mock_client = MagicMock()
    mock_client.is_connected = True
    async def raise_write(uuid, payload, response=False):
        raise Exception("GATT CONN TIMEOUT: write failed")
    mock_client.write_gatt_char = AsyncMock(side_effect=raise_write)
    ctrl.client = mock_client

    old_backoff = ctrl.current_backoff
    ok = await ctrl._send_packet(bytearray([0x7E,0x07,0x05,0x03,1,2,3,0x10,0xEF]), debug_label="test")
    assert ok is False
    assert ctrl.status.error_message == "GATT CONN TIMEOUT"
    assert ctrl.current_backoff >= old_backoff


@pytest.mark.asyncio
async def test_read_rssi_prefers_get_rssi_then_backend():
    cfg = DeviceConfig(target_mac="", write_char_uuid="uuid")
    ctrl = BleDeviceController(cfg, lambda s: None, lambda c: None, use_real_device=False)

    # Mock client.get_rssi
    mock_client = MagicMock()
    async def fake_get_rssi():
        return -42
    mock_client.get_rssi = AsyncMock(side_effect=fake_get_rssi)
    mock_client.is_connected = True
    ctrl.client = mock_client

    r = await ctrl._read_rssi()
    assert r == -42

    # Remove get_rssi, use backend._device.rssi
    delattr(mock_client, 'get_rssi')
    backend = MagicMock()
    dev = MagicMock()
    dev.rssi = -55
    backend._device = dev
    mock_client._backend = backend
    r2 = await ctrl._read_rssi()
    assert r2 == -55
