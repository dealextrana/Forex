"""Tests für IFVG-Inversion und Timeframe-Auswahl (STRATEGY §5, R6/R8/C2/C3).

Die Golden-Tests stellen die Auswahllogik aus Video-Beispiel 1 nach:
* „Das 4-Minuten-Gap war das höchste im Leg (1m/2m/3m vorhanden, kein 5m)."
* „Es gibt ein 30s-IFVG, aber auch ein 1m — kein 2m → das 1m ist das höchste."
* C2: Gaps außerhalb des Manipulation Legs zählen nicht.
"""

from bot.core.models import Direction, Timeframe
from bot.detectors.fvg import FVG
from bot.detectors.ifvg import check_inversion, gaps_in_leg, highest_timeframe_gap


def _gap(tf: Timeframe, bottom: float, top: float,
         direction: Direction = Direction.BEARISH, created: int = 0) -> FVG:
    return FVG(direction, top=top, bottom=bottom,
               created_index=created, timeframe=tf)


def test_valid_close_required_for_inversion(mk):
    """R6: Close IN der Zone reicht nicht; erst Body-Close über der fernen
    Kante (top) ist die bullische Inversion."""
    gap = _gap(Timeframe.M1, bottom=101, top=103, created=0)
    candles = mk([
        (104, 104.5, 100, 102),   # Close 102 in der Zone → keine Inversion
        (102, 103.5, 101.5, 102.9),  # Close 102.9 < 103 → immer noch nicht
        (102.9, 104.5, 102.5, 103.6),  # Close 103.6 > 103 → Inversion!
    ])
    inversion = check_inversion(gap, candles, Direction.BULLISH)
    assert inversion is not None
    assert inversion.confirmed_index == 2
    assert inversion.close_price == 103.6


def test_gap_in_trade_direction_cannot_invert(mk):
    bullish_gap = _gap(Timeframe.M1, bottom=101, top=103,
                       direction=Direction.BULLISH)
    candles = mk([(104, 106, 103.5, 105)])
    assert check_inversion(bullish_gap, candles, Direction.BULLISH) is None


def test_gaps_outside_manipulation_leg_are_ignored():
    """C2-Golden-Test: „They think they have to wait for these gaps up
    here … no" — nur Gaps im Leg [100, 110] zählen."""
    inside = _gap(Timeframe.M2, bottom=104, top=106)
    above_leg = _gap(Timeframe.M5, bottom=111, top=113)   # außerhalb (oben)
    partially = _gap(Timeframe.M3, bottom=108, top=111.5)  # ragt hinaus
    result = gaps_in_leg([inside, above_leg, partially],
                         leg_low=100, leg_high=110,
                         direction=Direction.BULLISH)
    assert result == [inside]


def test_highest_timeframe_selection_video_example_1():
    """Beispiel 1 (13. Mai): 1m/2m/3m/4m vorhanden, kein 5m → das 4m zählt."""
    gaps = [
        _gap(Timeframe.M1, 100, 101),
        _gap(Timeframe.M2, 100.5, 101.5),
        _gap(Timeframe.M3, 101, 102),
        _gap(Timeframe.M4, 101.5, 102.5),
    ]
    chosen = highest_timeframe_gap(gaps)
    assert chosen is not None and chosen.timeframe is Timeframe.M4


def test_highest_timeframe_selection_30s_and_1m():
    """Beispiel 1, Trade 2: 30s-IFVG vorhanden, aber auch 1m, kein 2m →
    das 1m ist das höchste und wird gehandelt."""
    gaps = [
        _gap(Timeframe.S30, 100, 100.5),
        _gap(Timeframe.M1, 100.2, 100.9),
    ]
    chosen = highest_timeframe_gap(gaps)
    assert chosen is not None and chosen.timeframe is Timeframe.M1


def test_highest_timeframe_latest_gap_wins_on_same_tf():
    older = _gap(Timeframe.M2, 100, 101, created=3)
    newer = _gap(Timeframe.M2, 100.5, 101.5, created=7)
    chosen = highest_timeframe_gap([older, newer])
    assert chosen is newer


def test_no_gaps_returns_none():
    assert highest_timeframe_gap([]) is None
