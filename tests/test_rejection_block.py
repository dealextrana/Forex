"""Tests für Rejection Blocks (STRATEGY §2.7, R5)."""

from bot.core.models import Direction, Timeframe
from bot.detectors.fvg import FVG
from bot.detectors.rejection_block import detect_rejection_block


def _bullish_gap() -> FVG:
    return FVG(Direction.BULLISH, top=103, bottom=101,
               created_index=0, timeframe=Timeframe.H1)


def _bearish_gap() -> FVG:
    return FVG(Direction.BEARISH, top=110, bottom=108,
               created_index=0, timeframe=Timeframe.H1)


def test_bullish_rejection_block_box_and_midpoint(mk):
    candles = mk([
        (105, 106, 102, 105.5),  # Wick bis 102 in die Zone, Close 105.5 > 103
    ])
    block = detect_rejection_block(candles, _bullish_gap(), 0)
    assert block is not None
    # Box: Körper-Tief (105) bis Wick-Tief (102)
    assert (block.box_top, block.box_bottom) == (105, 102)
    # R5: 50 %-Linie des Wicks („C of the range")
    assert block.midpoint == 103.5


def test_bullish_no_block_if_close_inside_zone(mk):
    """Ohne Rückschluss über die Zone keine sichtbare Ablehnung → kein Block."""
    candles = mk([
        (105, 105.5, 101.5, 102.5),  # schließt IN der Zone
    ])
    assert detect_rejection_block(candles, _bullish_gap(), 0) is None


def test_bullish_no_block_if_zone_not_reached(mk):
    candles = mk([
        (105, 106, 103.5, 105.5),  # Low 103.5 > Zonen-Top 103
    ])
    assert detect_rejection_block(candles, _bullish_gap(), 0) is None


def test_bearish_rejection_block_mirror(mk):
    candles = mk([
        (106, 109, 105.5, 106.5),  # Wick bis 109 in [108, 110], Close < 108
    ])
    block = detect_rejection_block(candles, _bearish_gap(), 0)
    assert block is not None
    # Box: Wick-Hoch (109) bis Körper-Hoch (106.5)
    assert (block.box_top, block.box_bottom) == (109, 106.5)
    assert block.midpoint == 107.75
