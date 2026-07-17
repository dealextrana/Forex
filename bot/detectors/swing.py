"""Swing-Erkennung (STRATEGY §2.1, R1).

Ein Swing High ist eine Kerze, deren Hoch strikt höher ist als die Hochs
der ``n`` Kerzen links und rechts (Standard-Fraktal). Vom Inhaber
bestätigt: ``n = 1`` („jede lokale Struktur", R1). Swing Low
spiegelbildlich.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass

from bot.core.models import Candle


class SwingKind(enum.Enum):
    HIGH = "high"
    LOW = "low"


@dataclass(frozen=True, slots=True)
class SwingPoint:
    """Ein erkannter Swing-Punkt.

    ``index`` referenziert die Kerze in der übergebenen Liste,
    ``price`` das Extrem (High bzw. Low) dieser Kerze.
    """

    index: int
    price: float
    kind: SwingKind


def detect_swings(candles: list[Candle], n: int = 1) -> list[SwingPoint]:
    """Findet alle bestätigten Swing-Punkte.

    Ein Swing ist erst bestätigt, wenn rechts ``n`` Kerzen existieren —
    die letzten ``n`` Kerzen können daher nie ein Swing sein (kein
    Vorgriff auf die Zukunft, wichtig für Live-Betrieb und Backtest).
    """
    if n < 1:
        raise ValueError("n muss >= 1 sein (R1: Default 1)")

    swings: list[SwingPoint] = []
    for i in range(n, len(candles) - n):
        candle = candles[i]
        neighbors = candles[i - n : i] + candles[i + 1 : i + 1 + n]
        if all(candle.high > other.high for other in neighbors):
            swings.append(SwingPoint(i, candle.high, SwingKind.HIGH))
        # Ein- und dieselbe Kerze kann gleichzeitig Swing High und Low sein
        # (Outside-Bar) — deshalb kein elif.
        if all(candle.low < other.low for other in neighbors):
            swings.append(SwingPoint(i, candle.low, SwingKind.LOW))
    return swings


def last_swing(
    swings: list[SwingPoint], kind: SwingKind, before_index: int | None = None
) -> SwingPoint | None:
    """Letzter Swing der gewünschten Art, optional vor einem Kerzen-Index."""
    for swing in reversed(swings):
        if swing.kind is not kind:
            continue
        if before_index is not None and swing.index >= before_index:
            continue
        return swing
    return None
