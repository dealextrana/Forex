"""IFVG — Inversion Fair Value Gap (STRATEGY §2.8/§5, R6/R8).

Die Inversion ist der **Entry-Trigger** der Strategie (Schritt 3):

* Bullische Inversion: eine Kerze schließt per Body **über** einem
  bärischen FVG (Close > obere Kante) → Gap wechselt die Rolle zu Support.
* Bärische Inversion: Body-Close **unter** einem bullischen FVG.

„Valid close" (R6, bestätigt): Body-Close vollständig **jenseits der
fernen Gap-Kante**; kein zusätzlicher Mindestabstand.

Auswahlregel (C2–C6): Es zählen nur Gaps **innerhalb des Manipulation
Legs**, und getriggert wird auf dem **höchsten** Timeframe, auf dem dort
ein Gap existiert (R8: Default; Option ``allow_lower_tf_inversion``).
Die Leg-Bestimmung selbst ist Aufgabe der State-Machine (M3) — hier leben
die reinen Prüf-/Auswahlfunktionen.
"""

from __future__ import annotations

from dataclasses import dataclass

from bot.core.models import Candle, Direction, Timeframe
from bot.detectors.fvg import FVG


@dataclass(frozen=True, slots=True)
class Inversion:
    """Eine bestätigte FVG-Inversion (Entry-Trigger)."""

    gap: FVG
    direction: Direction  # Richtung des daraus folgenden Trades
    confirmed_index: int  # Kerze mit dem „valid close" (R6)
    close_price: float


def check_inversion(
    gap: FVG, candles: list[Candle], direction: Direction, start_index: int = 0
) -> Inversion | None:
    """Sucht den ersten „valid close" durch das Gap in Trade-Richtung.

    Bullischer Trade invertiert ein **bärisches** Gap (und umgekehrt) —
    ein Gap in Trade-Richtung kann nicht invertiert werden und ergibt
    ``None``.
    """
    if gap.direction is direction:
        return None  # nur Gegen-Gaps sind invertierbar

    begin = max(start_index, gap.created_index + 1)
    for i in range(begin, len(candles)):
        close = candles[i].close
        if direction is Direction.BULLISH and close > gap.top:
            # R6: Body-Close vollständig über der oberen (fernen) Kante.
            return Inversion(gap, direction, i, close)
        if direction is Direction.BEARISH and close < gap.bottom:
            return Inversion(gap, direction, i, close)
    return None


def gaps_in_leg(
    gaps: list[FVG], leg_low: float, leg_high: float, direction: Direction
) -> list[FVG]:
    """Filtert Gaps, die vollständig **innerhalb des Manipulation Legs** liegen.

    C2: Gaps oberhalb/unterhalb des Legs zählen NICHT („you just have to
    be paying attention to the manipulation leg"). Ein Gap liegt im Leg,
    wenn seine gesamte Zone im Preisbereich [leg_low, leg_high] liegt.
    Es kommen nur Gegen-Gaps infrage (siehe ``check_inversion``).
    """
    return [
        gap
        for gap in gaps
        if gap.direction is not direction
        and gap.bottom >= leg_low
        and gap.top <= leg_high
    ]


def highest_timeframe_gap(gaps: list[FVG]) -> FVG | None:
    """C3/R8: das Gap des höchsten vorhandenen Timeframes im Leg.

    Existieren auf dem höchsten Timeframe mehrere Gaps, zählt das zuletzt
    entstandene (das „frischeste" im Leg).
    """
    if not gaps:
        return None
    top_tf: Timeframe = max(gap.timeframe for gap in gaps)
    candidates = [gap for gap in gaps if gap.timeframe is top_tf]
    return max(candidates, key=lambda gap: gap.created_index)
