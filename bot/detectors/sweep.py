"""Liquidity-Sweep-Erkennung (STRATEGY §2.4, R3).

Vom Inhaber bestätigt (R3): Der reine **Wick-Durchstich** genügt — die
Kerze muss nicht hinter das Level zurückschließen. Ein Sweep eines Tiefs
liegt also vor, sobald ein späteres Low unter dem Referenz-Tief handelt
(spiegelbildlich für Hochs).

Verwendung in der Strategie:
* K2: mitigiertes FVG wird erst nach Sweep des Intermediate-Levels wieder
  ein valides Key Level.
* §10 Rang 9: Sweep unmittelbar vor der Umkehr als Konfluenz-Punkt.
"""

from __future__ import annotations

from dataclasses import dataclass

from bot.core.models import Candle
from bot.detectors.swing import SwingKind


@dataclass(frozen=True, slots=True)
class Sweep:
    """Ein erkannter Sweep eines Referenz-Levels."""

    level_price: float
    level_kind: SwingKind  # HIGH = Buy-Side-, LOW = Sell-Side-Liquidität
    candle_index: int  # Kerze, deren Wick das Level durchstochen hat
    extreme: float  # das erreichte Extrem (High bzw. Low der Sweep-Kerze)


def find_sweep(
    candles: list[Candle],
    level_price: float,
    level_kind: SwingKind,
    start_index: int = 0,
) -> Sweep | None:
    """Erste Kerze ab ``start_index``, die das Level per Wick durchsticht.

    HIGH-Level: ``high > level`` (Buy-Side genommen).
    LOW-Level:  ``low < level`` (Sell-Side genommen).
    Strikte Ungleichheit — exaktes Berühren ist kein Sweep.
    """
    for i in range(start_index, len(candles)):
        candle = candles[i]
        if level_kind is SwingKind.HIGH and candle.high > level_price:
            return Sweep(level_price, level_kind, i, candle.high)
        if level_kind is SwingKind.LOW and candle.low < level_price:
            return Sweep(level_price, level_kind, i, candle.low)
    return None


def is_swept(
    candles: list[Candle],
    level_price: float,
    level_kind: SwingKind,
    start_index: int = 0,
) -> bool:
    """Bequemlichkeitsvariante von ``find_sweep`` als Ja/Nein-Frage."""
    return find_sweep(candles, level_price, level_kind, start_index) is not None
