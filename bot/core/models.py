"""Zentrale Basistypen: Kerzen, Timeframes, Richtungen.

Diese Typen sind bewusst minimal und unveränderlich (frozen dataclasses),
damit die Detektoren (bot/detectors/) reine Funktionen ohne Seiteneffekte
bleiben und einfach getestet werden können.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from datetime import datetime, timezone


class Direction(enum.Enum):
    """Handels- bzw. Strukturrichtung."""

    BULLISH = "bullish"
    BEARISH = "bearish"

    @property
    def opposite(self) -> "Direction":
        return Direction.BEARISH if self is Direction.BULLISH else Direction.BULLISH


class Timeframe(enum.Enum):
    """Alle von der Strategie genutzten Timeframes (STRATEGY §1).

    Der Wert ist die Dauer in Sekunden. S30 ist nur aktiv, wenn die
    Option ``use_30s`` gesetzt ist (STRATEGY §5, D7).
    """

    S30 = 30
    M1 = 60
    M2 = 120
    M3 = 180
    M4 = 240
    M5 = 300
    M15 = 900
    M30 = 1800
    H1 = 3600
    H4 = 14400
    D1 = 86400

    @property
    def seconds(self) -> int:
        return self.value

    def __lt__(self, other: "Timeframe") -> bool:  # ermöglicht max()/Sortierung
        return self.value < other.value

    def __le__(self, other: "Timeframe") -> bool:
        return self.value <= other.value


#: Entry-Timeframes für die IFVG-Suche (STRATEGY §5, C2) in aufsteigender
#: Reihenfolge. S30 wird nur mit Option ``use_30s`` vorangestellt.
ENTRY_TIMEFRAMES: tuple[Timeframe, ...] = (
    Timeframe.M1,
    Timeframe.M2,
    Timeframe.M3,
    Timeframe.M4,
    Timeframe.M5,
)


@dataclass(frozen=True, slots=True)
class Candle:
    """Eine OHLCV-Kerze.

    ``ts`` ist der **Startzeitpunkt** der Kerze in UTC. Alle
    Body-/Wick-Berechnungen, die die Strategie braucht (Body-Close-Regeln
    R2/R6, Wick-Definitionen §2.7), sind hier als Properties gekapselt.
    """

    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

    def __post_init__(self) -> None:
        if self.ts.tzinfo is None:
            # Naive Zeitstempel führen zu subtilen Sessionfehlern → verbieten.
            raise ValueError("Candle.ts muss zeitzonenbewusst (UTC) sein")
        if self.high < self.low:
            raise ValueError(f"Ungültige Kerze: high {self.high} < low {self.low}")

    # --- Kerzenfarbe -----------------------------------------------------
    @property
    def is_bullish(self) -> bool:
        """Up-Close-Kerze (close > open) — relevant für CISD-Serien (§2.6)."""
        return self.close > self.open

    @property
    def is_bearish(self) -> bool:
        """Down-Close-Kerze (close < open) — relevant für CISD-Serien (§2.6)."""
        return self.close < self.open

    # --- Body & Wicks ----------------------------------------------------
    @property
    def body_top(self) -> float:
        return max(self.open, self.close)

    @property
    def body_bottom(self) -> float:
        return min(self.open, self.close)

    @property
    def upper_wick_size(self) -> float:
        return self.high - self.body_top

    @property
    def lower_wick_size(self) -> float:
        return self.body_bottom - self.low


def utc(ts: datetime) -> datetime:
    """Hilfsfunktion: Zeitstempel nach UTC normalisieren."""
    return ts.astimezone(timezone.utc)
