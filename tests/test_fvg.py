"""Tests für FVG-Erkennung und -Zustände (STRATEGY §2.3/§2.5, R2)."""

from bot.core.models import Direction, Timeframe
from bot.detectors.fvg import (
    FVGState,
    detect_fvgs,
    intermediate_levels,
    update_fvg_states,
)
from bot.detectors.swing import detect_swings


def test_bullish_fvg_detection(mk):
    candles = mk([
        (100, 101, 99, 100),   # K1: High 101
        (100, 105, 100, 104),  # K2: Impulskerze
        (104, 107, 103, 106),  # K3: Low 103 > 101 → bullisches FVG [101, 103]
    ])
    gaps = detect_fvgs(candles, Timeframe.M1)
    assert len(gaps) == 1
    gap = gaps[0]
    assert gap.direction is Direction.BULLISH
    assert (gap.bottom, gap.top) == (101, 103)
    assert gap.state is FVGState.FRESH


def test_bearish_fvg_detection(mk):
    candles = mk([
        (100, 101, 99, 100),   # K1: Low 99
        (99, 99.5, 95, 96),    # K2
        (96, 97, 94, 95),      # K3: High 97 < 99 → bärisches FVG [97, 99]
    ])
    gaps = detect_fvgs(candles, Timeframe.M1)
    assert len(gaps) == 1
    gap = gaps[0]
    assert gap.direction is Direction.BEARISH
    assert (gap.bottom, gap.top) == (97, 99)


def test_wick_into_gap_mitigates_but_does_not_disrespect(mk):
    """R2-Golden-Test: Wick durch die gesamte Zone, Close aber darüber →
    das Gap ist mitigiert, NICHT missachtet (Wick allein reicht nicht)."""
    candles = mk([
        (100, 101, 99, 100),
        (100, 105, 100, 104),
        (104, 107, 103, 106),   # bullisches FVG [101, 103]
        (106, 106, 100.5, 104), # Wick bis unter die Zone, Close 104 darüber
    ])
    gaps = detect_fvgs(candles, Timeframe.M1)
    update_fvg_states(gaps, candles)
    assert gaps[0].state is FVGState.MITIGATED


def test_body_close_through_gap_disrespects(mk):
    """R2: Body-Close komplett unter der Zone → missachtet („ran through")."""
    candles = mk([
        (100, 101, 99, 100),
        (100, 105, 100, 104),
        (104, 107, 103, 106),  # bullisches FVG [101, 103]
        (106, 106, 100, 100.5),  # Close 100.5 < 101 → durchschlagen
    ])
    gaps = detect_fvgs(candles, Timeframe.M1)
    update_fvg_states(gaps, candles)
    assert gaps[0].state is FVGState.DISRESPECTED


def test_untouched_gap_stays_fresh(mk):
    candles = mk([
        (100, 101, 99, 100),
        (100, 105, 100, 104),
        (104, 107, 103, 106),  # bullisches FVG [101, 103]
        (106, 108, 105, 107),  # bleibt über der Zone
    ])
    gaps = detect_fvgs(candles, Timeframe.M1)
    update_fvg_states(gaps, candles)
    assert gaps[0].state is FVGState.FRESH


def test_intermediate_low_inside_gap(mk):
    """§2.5: Swing Low, dessen Preis in der Gap-Zone ruht (nach Entstehung)."""
    candles = mk([
        (100, 101, 99, 100),
        (100, 105, 100, 104),
        (104, 107, 103, 106),   # bullisches FVG [101, 103]
        (106, 106.5, 104, 105),
        (105, 105.5, 102, 104),  # Swing Low 102 → liegt in [101, 103]
        (104, 108, 103.5, 107),
        (107, 109, 106, 108),
    ])
    gaps = detect_fvgs(candles, Timeframe.M1)
    swings = detect_swings(candles)
    levels = intermediate_levels(gaps[0], swings)
    assert [(s.index, s.price) for s in levels] == [(4, 102)]
