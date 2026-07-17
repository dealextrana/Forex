"""CISD — Change In State of Delivery (STRATEGY §2.6, R4).

Bullischer CISD (bärisch spiegelbildlich):

1. Eine Kerze oder **Serie zusammenhängender Down-Close-Kerzen** handelt
   in ein Key Level (FVG oder Intermediate Low im FVG).
2. Anker = **Open der ersten Kerze dieser Serie** (R4).
3. Bestätigt, sobald eine spätere Kerze per **Body-Close über** dem Anker
   schließt.

Der bestätigte Anker dient danach selbst als Key Level (Retest-Zone,
K4). Multi-Timeframe-CISDs erhöhen die Setup-Qualität („super high
probability", §10 Rang 3).
"""

from __future__ import annotations

from dataclasses import dataclass

from bot.core.models import Candle, Direction


@dataclass(frozen=True, slots=True)
class CISD:
    """Ein erkannter (ggf. bereits bestätigter) CISD.

    ``anchor_price``: Open der ersten Kerze der Serie (R4).
    ``series_start``/``series_end``: Index-Bereich der Kerzenserie.
    ``confirmed_index``: Kerze, deren Body-Close den CISD bestätigte
    (``None`` = noch unbestätigt, Level existiert noch nicht, K4).
    """

    direction: Direction
    anchor_price: float
    series_start: int
    series_end: int
    confirmed_index: int | None

    @property
    def is_confirmed(self) -> bool:
        return self.confirmed_index is not None


def _series_bounds(
    candles: list[Candle], touch_index: int, direction: Direction
) -> tuple[int, int] | None:
    """Findet die zusammenhängende Down-/Up-Close-Serie am Level-Kontakt.

    Bullischer CISD → Down-Close-Serie (``is_bearish``); bärischer CISD →
    Up-Close-Serie. Beginnt die Suche an der Kerze, die das Level berührt
    hat; ist diese neutral/gegenfarbig (Berührung nur per Wick), wird die
    unmittelbar vorausgehende Serie verwendet.
    """
    matches = (
        (lambda c: c.is_bearish)
        if direction is Direction.BULLISH
        else (lambda c: c.is_bullish)
    )

    end = touch_index
    if not matches(candles[end]):
        end -= 1
        if end < 0 or not matches(candles[end]):
            return None  # keine Serie vorhanden → kein CISD möglich

    start = end
    while start - 1 >= 0 and matches(candles[start - 1]):
        start -= 1
    return start, end


def detect_cisd(
    candles: list[Candle], touch_index: int, direction: Direction
) -> CISD | None:
    """Erkennt den CISD zur Level-Berührung bei ``touch_index``.

    :param direction: Richtung des erwarteten Orderflow-Wechsels —
        ``BULLISH`` = Body-Close **über** dem Anker bestätigt,
        ``BEARISH`` = Body-Close **unter** dem Anker.
    :return: CISD (bestätigt oder wartend) oder ``None``, wenn an der
        Berührung keine passende Kerzenserie existiert.
    """
    bounds = _series_bounds(candles, touch_index, direction)
    if bounds is None:
        return None
    start, end = bounds
    anchor = candles[start].open  # R4: Open der ERSTEN Kerze der Serie

    confirmed: int | None = None
    for i in range(end + 1, len(candles)):
        close = candles[i].close
        if direction is Direction.BULLISH and close > anchor:
            confirmed = i
            break
        if direction is Direction.BEARISH and close < anchor:
            confirmed = i
            break

    return CISD(direction, anchor, start, end, confirmed)
