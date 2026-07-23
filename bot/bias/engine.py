"""Bias-Engine (STRATEGY §3, SPEC §4.3).

Bestimmt den Higher-Timeframe-Bias aus dem Respektieren/Missachten von
FVGs je Timeframe (B1) und kombiniert die konfigurierten Bias-Timeframes
zu einem Gesamtbias: nur wenn alle Timeframes übereinstimmen, gilt ein
Bias — sonst NEUTRAL (``None``). Der 15m-Check (R7) kann einen
bestehenden Bias bei Widerspruch oder starker Gegen-Rejection verwerfen.

Design-Entscheidung (Implementierungsdetail, kein Video-Inhalt): Für die
Einzel-Timeframe-Bewertung wird das jeweils **zuletzt entstandene** FVG
pro Richtung herangezogen — das bildet nach, wie im Video der Chart
überflogen wird ("this bullish 4-hour gap … these bearish gaps … getting
ran through"), ohne eine Lookback-Fensterlänge zu erfinden, die das
Video nicht nennt.
"""

from __future__ import annotations

from dataclasses import dataclass

from bot.core.models import Direction, Timeframe
from bot.detectors.fvg import FVG, FVGState
from bot.detectors.swing import SwingKind, SwingPoint


def _latest(gaps: list[FVG], direction: Direction) -> FVG | None:
    candidates = [g for g in gaps if g.direction is direction]
    if not candidates:
        return None
    return max(candidates, key=lambda g: g.created_index)


def single_timeframe_bias(gaps: list[FVG]) -> Direction | None:
    """B1: Bias eines einzelnen Timeframes aus dem jüngsten FVG je Richtung.

    Bullisch, wenn das jüngste bullische FVG hält UND das jüngste
    bärische FVG missachtet ist. Bärisch spiegelbildlich. Fehlt eines der
    beiden Signale oder widerspricht sich die Evidenz, ist der Bias auf
    diesem Timeframe unklar (``None``).
    """
    latest_bullish = _latest(gaps, Direction.BULLISH)
    latest_bearish = _latest(gaps, Direction.BEARISH)

    bullish_holds = latest_bullish is not None and latest_bullish.state is not FVGState.DISRESPECTED
    bullish_broken = latest_bullish is not None and latest_bullish.state is FVGState.DISRESPECTED
    bearish_holds = latest_bearish is not None and latest_bearish.state is not FVGState.DISRESPECTED
    bearish_broken = latest_bearish is not None and latest_bearish.state is FVGState.DISRESPECTED

    if bullish_holds and bearish_broken:
        return Direction.BULLISH
    if bearish_holds and bullish_broken:
        return Direction.BEARISH
    return None


def combined_bias(per_timeframe: dict[Timeframe, Direction | None]) -> Direction | None:
    """SPEC §4.3: Gesamtbias nur, wenn ALLE konfigurierten Timeframes übereinstimmen."""
    values = list(per_timeframe.values())
    if not values or any(v is None for v in values):
        return None
    first = values[0]
    return first if all(v is first for v in values) else None


def apply_intraday_check(
    bias: Direction | None,
    m15_bias: Direction | None,
    *,
    strong_rejection_against: bool = False,
) -> Direction | None:
    """R7: 15m-Gegencheck + Beachtung starker Rejections gegen den Bias.

    Widerspricht die 15m-Bewertung dem übergeordneten Bias eindeutig,
    oder liegt eine starke Rejection gegen die Bias-Richtung vor, wird
    der Bias auf NEUTRAL gesetzt (B6). Offene Positionen bleiben davon
    unberührt (R14) — neue Entries werden dadurch nur blockiert, das
    regelt die aufrufende State-Machine.
    """
    if bias is None:
        return None
    if m15_bias is not None and m15_bias is not bias:
        return None
    if strong_rejection_against:
        return None
    return bias


@dataclass(frozen=True, slots=True)
class DrawOnLiquidity:
    """Das Tagesziel bzw. Low-Hanging-Fruit-Ziel (§2.11)."""

    price: float
    source: str  # "swing" | "unfilled_gap"


def find_dol(
    swings: list[SwingPoint],
    direction: Direction,
    current_price: float,
    unfilled_gaps: list[FVG] | None = None,
) -> DrawOnLiquidity | None:
    """B2: nächstes ungesweeptes externes Swing High/Low bzw. unfilled Gap.

    Bullisch: nächstes Swing High ÜBER dem aktuellen Preis; bärisch:
    nächstes Swing Low DARUNTER. Ein unfilled Gap in Bias-Richtung, das
    näher liegt, wird bevorzugt ("unfilled gaps are great draws", §2.11).
    Diese Funktion dient sowohl für das HTF-DOL (Schritt 1) als auch für
    das LTF-„Low-Hanging-Fruit"-Ziel (Schritt 4, T2) — je nachdem, welche
    Swings/Gaps übergeben werden.
    """
    wanted = SwingKind.HIGH if direction is Direction.BULLISH else SwingKind.LOW
    prices = [s.price for s in swings if s.kind is wanted]

    if direction is Direction.BULLISH:
        above = [p for p in prices if p > current_price]
        swing_target = min(above) if above else None
    else:
        below = [p for p in prices if p < current_price]
        swing_target = max(below) if below else None

    gap_target: float | None = None
    if unfilled_gaps:
        relevant = [
            g for g in unfilled_gaps if g.direction is direction and g.state is FVGState.FRESH
        ]
        if direction is Direction.BULLISH:
            above_gaps = [g.top for g in relevant if g.top > current_price]
            gap_target = min(above_gaps) if above_gaps else None
        else:
            below_gaps = [g.bottom for g in relevant if g.bottom < current_price]
            gap_target = max(below_gaps) if below_gaps else None

    if swing_target is None and gap_target is None:
        return None

    if gap_target is not None and (
        swing_target is None
        or (direction is Direction.BULLISH and gap_target < swing_target)
        or (direction is Direction.BEARISH and gap_target > swing_target)
    ):
        return DrawOnLiquidity(gap_target, "unfilled_gap")
    assert swing_target is not None
    return DrawOnLiquidity(swing_target, "swing")
