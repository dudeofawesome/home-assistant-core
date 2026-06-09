"""TOTO Washlet infrared commands."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from typing import override

from infrared_protocols import Command as InfraredCommand

PREAMBLE_HIGH = 6200
PREAMBLE_LOW = 2800
BIT_HIGH = 550
BIT_ONE_LOW = 1700
BIT_ZERO_LOW = 550
FRAME_GAP = 36000
MODULATION = 38000
TOTO_HEADER = 0x2008


@dataclass(frozen=True)
class TotoData:
    """TOTO infrared command data."""

    command: int
    rc_code_1: int = 0
    rc_code_2: int = 0

    @property
    def payload(self) -> int:
        """Return the 24-bit TOTO payload."""
        payload = self.rc_code_1 << 20
        payload |= self.rc_code_2 << 16
        payload |= self.command << 8
        payload |= ((payload & 0xFF0000) >> 16) ^ ((payload & 0x00FF00) >> 8)
        return payload


class TotoWashletCode(Enum):
    """TOTO Washlet IR command codes."""

    STOP = (TotoData(0x00),)
    REAR = (TotoData(0xA8, 0x6, 0x2),)
    USER_1 = (TotoData(0x95, 0x6, 0x1),)
    USER_2 = (TotoData(0x95, 0x6, 0x2),)
    OSCILLATE = (TotoData(0x60),)
    PULSATE = (TotoData(0xE0),)
    LID_OPEN_CLOSE = (TotoData(0x0E),)
    SEAT_OPEN_CLOSE = (TotoData(0xF6),)
    FULL_FLUSH = (TotoData(0xB0),)
    LIGHT_FLUSH = (TotoData(0x88),)
    ECO_FLUSH = (TotoData(0xB6),)
    DRYER = (TotoData(0xC0),)
    POWER_DEODORIZER = (TotoData(0x7C),)
    FRONT = (TotoData(0x10), TotoData(0x40, 0xA, 0xC))
    SOFT_REAR = (TotoData(0x60), TotoData(0xA8, 0xA, 0xC))

    def to_command(self) -> TotoCommand:
        """Build a TOTO command for this Washlet code."""
        return TotoCommand(self.value)


class TotoCommand(InfraredCommand):
    """TOTO infrared command."""

    def __init__(
        self,
        frames: Iterable[TotoData],
        *,
        modulation: int = MODULATION,
        repeat_count: int = 2,
    ) -> None:
        """Initialize the TOTO IR command."""
        super().__init__(modulation=modulation, repeat_count=repeat_count)
        self.frames = tuple(frames)

    @override
    def get_raw_timings(self) -> list[int]:
        """Get raw timings for the TOTO command."""
        timings: list[int] = []
        for frame_index, frame in enumerate(self.frames):
            if frame_index:
                timings.append(-FRAME_GAP)
            for repeat_index in range(self.repeat_count + 1):
                if repeat_index:
                    timings.append(-FRAME_GAP)
                timings.extend(_encode_frame(frame))
        return timings


def _encode_frame(frame: TotoData) -> list[int]:
    """Encode one TOTO frame."""
    timings = [PREAMBLE_HIGH, -PREAMBLE_LOW]
    _append_bits(timings, TOTO_HEADER, 15)
    _append_bits(timings, frame.payload, 24)
    timings.append(BIT_HIGH)
    return timings


def _append_bits(timings: list[int], value: int, bit_count: int) -> None:
    """Append MSB-first TOTO bits to timings."""
    for bit in range(bit_count - 1, -1, -1):
        timings.append(BIT_HIGH)
        timings.append(-BIT_ONE_LOW if value & (1 << bit) else -BIT_ZERO_LOW)
