"""Fair Value Gaps: Erkennung, Zustand, Intermediate Levels.

Regeln aus STRATEGY §2.3/§2.5 (vom Inhaber bestätigt):

* 3-Kerzen-Definition: bullisches FVG, wenn ``Low(K3) > High(K1)``;
  bärisches FVG, wenn ``High(K3) < Low(K1)``.
* **Mitigiert**: Preis hat die Zone seit Entstehung berührt (Wick genügt).
* **Missachtet/disrespected (R2)**: eine Kerze schließt per Body-Close
  **komplett durch** die Zone (Close jenseits der fernen Kante). Ein
  reiner Wick-Durchstich reicht nicht.
* **Intermediate High/Low (§2.5)**: Swing-Punkt, dessen Preis innerhalb
  der FVG-Zone liegt.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field

from bot.core.models import Candle, Direction, Timeframe
from bot.detectors.swing import SwingKind, SwingPoint


class FVGState(enum.Enum):
    FRESH = "fresh"  # unmitigiert ("unfilled") — bevorzugtes Ziel/Level (K1)
    MITIGATED = "mitigated"  # berührt — als Key Level erst nach Sweep (K2)
    DISRESPECTED = "disrespected"  # Body-Close durch die Zone (R2)


@dataclass(slots=True)
class FVG:
    """Eine Fair-Value-Gap-Zone auf einem Timeframe.

    ``created_index`` ist der Index der dritten Kerze des Musters (erst
    mit ihrem Schluss existiert das Gap).
    """

    direction: Direction
    top: float
    bottom: float
    created_index: int
    timeframe: Timeframe
    state: FVGState = FVGState.FRESH

    @property
    def size(self) -> float:
        return self.top - self.bottom

    def contains(self, price: float) -> bool:
        return self.bottom <= price <= self.top

    @property
    def far_edge(self) -> float:
        """Die „ferne" Kante in Durchbruchsrichtung (R2/R6).

        Bullisches FVG (Support, Preis kommt von oben): fern = ``bottom``.
        Bärisches FVG (Resistance, Preis kommt von unten): fern = ``top``.
        """
        return self.bottom if self.direction is Direction.BULLISH else self.top


def detect_fvgs(candles: list[Candle], timeframe: Timeframe) -> list[FVG]:
    """Findet alle FVGs in einer Kerzenserie (Zustand: FRESH).

    Die Zustandsfortschreibung übernimmt ``update_fvg_states`` — getrennt,
    damit im Live-Betrieb pro neuer Kerze inkrementell aktualisiert werden
    kann.
    """
    gaps: list[FVG] = []
    for i in range(2, len(candles)):
        k1, k3 = candles[i - 2], candles[i]
        if k3.low > k1.high:  # Aufwärts-Impuls, Kerze 2 überspringt den Bereich
            gaps.append(
                FVG(Direction.BULLISH, top=k3.low, bottom=k1.high,
                    created_index=i, timeframe=timeframe)
            )
        if k3.high < k1.low:  # Abwärts-Impuls
            gaps.append(
                FVG(Direction.BEARISH, top=k1.low, bottom=k3.high,
                    created_index=i, timeframe=timeframe)
            )
    return gaps


def update_fvg_states(gaps: list[FVG], candles: list[Candle]) -> None:
    """Schreibt die Zustände aller Gaps anhand der Kerzen nach Entstehung fort.

    Reihenfolge der Prüfung pro Kerze: erst Missachtung (R2, Body-Close
    durch die ferne Kante), dann Mitigation (Wick-Berührung). Ein einmal
    missachtetes Gap bleibt missachtet.
    """
    for gap in gaps:
        if gap.state is FVGState.DISRESPECTED:
            continue
        for candle in candles[gap.created_index + 1 :]:
            if gap.direction is Direction.BULLISH:
                # R2: Close (Body) komplett unter der Zone → missachtet.
                if candle.close < gap.bottom:
                    gap.state = FVGState.DISRESPECTED
                    break
                # Wick-Berührung der Zone → mitigiert.
                if candle.low <= gap.top:
                    gap.state = FVGState.MITIGATED
            else:
                if candle.close > gap.top:
                    gap.state = FVGState.DISRESPECTED
                    break
                if candle.high >= gap.bottom:
                    gap.state = FVGState.MITIGATED


def intermediate_levels(gap: FVG, swings: list[SwingPoint]) -> list[SwingPoint]:
    """Intermediate Highs/Lows innerhalb der Gap-Zone (§2.5).

    Bullisches Gap → relevante Levels sind Swing **Lows** in der Zone
    (Key-Level-Kandidat Typ A, §4.1); bärisches Gap → Swing **Highs**.
    Nur Swings nach Entstehung des Gaps zählen — ein Swing, der vor dem
    Gap entstand, kann nicht „im Gap ruhen".
    """
    wanted = SwingKind.LOW if gap.direction is Direction.BULLISH else SwingKind.HIGH
    return [
        swing
        for swing in swings
        if swing.kind is wanted
        and swing.index > gap.created_index
        and gap.contains(swing.price)
    ]
