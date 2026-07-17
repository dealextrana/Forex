"""Rejection Block / Rejection Wick (STRATEGY §2.7, R5).

Bullischer Rejection Block: der **untere Wick** einer Kerze, die in ein
bullisches FVG (oder Intermediate Low im FVG) gehandelt und es respektiert
hat. Die Box reicht vom Kerzenkörper-Tief bis zum Wick-Tief; zusätzlich
wird die **50 %-Linie des Wicks** markiert („C of the range", R5) — dort
entstehen laut Video die „bottom tick entries".

Bärisch spiegelbildlich (oberer Wick, Box Körper-Hoch bis Wick-Hoch).

Ein Rejection Block ist ein **Key Level**, kein Entry-Signal (K7).
"""

from __future__ import annotations

from dataclasses import dataclass

from bot.core.models import Candle, Direction
from bot.detectors.fvg import FVG


@dataclass(frozen=True, slots=True)
class RejectionBlock:
    """Wick-Box einer Rejection-Kerze inkl. 50 %-Linie."""

    direction: Direction
    candle_index: int
    box_top: float
    box_bottom: float

    @property
    def midpoint(self) -> float:
        """R5: die 50 %-Linie des Wicks („C of the range")."""
        return (self.box_top + self.box_bottom) / 2.0


def detect_rejection_block(
    candles: list[Candle],
    gap: FVG,
    candle_index: int,
    *,
    require_close_outside: bool = True,
) -> RejectionBlock | None:
    """Prüft, ob die Kerze bei ``candle_index`` ein Rejection Block zur Gap ist.

    Bedingungen (bullisch; bärisch spiegelbildlich):

    1. Der untere Wick handelt in die Gap-Zone (``low <= gap.top``).
    2. Es existiert überhaupt ein Wick (Box hätte sonst Höhe 0).
    3. ``require_close_outside`` (Default): die Kerze schließt wieder
       **über** der Zone — der Markt hat das Level sichtbar respektiert
       (die Video-Beispiele zeigen stets eine klare Ablehnung; ohne diese
       Bedingung wäre jede mitigierende Kerze ein „Rejection" Block).
    """
    candle = candles[candle_index]

    if gap.direction is Direction.BULLISH:
        traded_in = candle.low <= gap.top
        has_wick = candle.lower_wick_size > 0
        closed_outside = candle.close > gap.top
        if traded_in and has_wick and (closed_outside or not require_close_outside):
            return RejectionBlock(
                Direction.BULLISH,
                candle_index,
                box_top=candle.body_bottom,
                box_bottom=candle.low,
            )
    else:
        traded_in = candle.high >= gap.bottom
        has_wick = candle.upper_wick_size > 0
        closed_outside = candle.close < gap.bottom
        if traded_in and has_wick and (closed_outside or not require_close_outside):
            return RejectionBlock(
                Direction.BEARISH,
                candle_index,
                box_top=candle.high,
                box_bottom=candle.body_top,
            )
    return None
