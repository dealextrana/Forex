"""Gemeinsame Test-Helfer: kompakte Erzeugung synthetischer Kerzenserien."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from bot.core.models import Candle

START = datetime(2026, 5, 13, 13, 30, tzinfo=timezone.utc)  # 9:30 ET


def make_candles(
    ohlc: list[tuple[float, float, float, float]],
    *,
    start: datetime = START,
    seconds: int = 60,
) -> list[Candle]:
    """Baut eine chronologische Kerzenliste aus (open, high, low, close)-Tupeln."""
    return [
        Candle(start + timedelta(seconds=i * seconds), o, h, l, c)
        for i, (o, h, l, c) in enumerate(ohlc)
    ]


@pytest.fixture
def mk():
    return make_candles
