"""Tests for TOTO Washlet infrared commands."""

from __future__ import annotations

from homeassistant.components.toto_washlet.commands import TotoData, TotoWashletCode


def test_toto_data_payload_checksum() -> None:
    """Test TOTO payload checksum generation."""
    assert TotoData(0xA8, 0x6, 0x2).payload == 0x62A8CA
    assert TotoData(0xB0).payload == 0x00B0B0
    assert TotoData(0x40, 0xA, 0xC).payload == 0xAC40EC


def test_toto_command_timings() -> None:
    """Test TOTO command timing generation."""
    command = TotoWashletCode.REAR.to_command()
    timings = command.get_raw_timings()

    assert command.modulation == 38000
    assert len(timings) == 245
    assert timings[:2] == [6200, -2800]
    assert timings[81:84] == [-36000, 6200, -2800]
    assert timings[-1] == 550
