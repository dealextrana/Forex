"""Tests für die Swing-Erkennung (STRATEGY §2.1, R1: Fraktal n=1)."""

from bot.detectors.swing import SwingKind, detect_swings, last_swing


def test_simple_swing_high_and_low(mk):
    candles = mk([
        (100, 101, 99, 100),
        (100, 103, 100, 102),  # Swing High bei 103
        (102, 102, 98, 99),    # Swing Low bei 98
        (99, 101, 99, 100),
    ])
    swings = detect_swings(candles, n=1)
    highs = [s for s in swings if s.kind is SwingKind.HIGH]
    lows = [s for s in swings if s.kind is SwingKind.LOW]
    assert [(s.index, s.price) for s in highs] == [(1, 103)]
    assert [(s.index, s.price) for s in lows] == [(2, 98)]


def test_last_candles_cannot_be_swing(mk):
    """Ohne rechte Nachbarkerze keine Bestätigung — kein Blick in die Zukunft."""
    candles = mk([
        (100, 101, 99, 100),
        (100, 105, 100, 104),  # höchstes Hoch, aber letzte Kerze
    ])
    assert detect_swings(candles, n=1) == []


def test_outside_bar_is_both_swings(mk):
    candles = mk([
        (100, 101, 99, 100),
        (100, 104, 96, 101),  # Outside-Bar: Swing High UND Swing Low
        (101, 102, 100, 101),
    ])
    swings = detect_swings(candles, n=1)
    kinds = {s.kind for s in swings if s.index == 1}
    assert kinds == {SwingKind.HIGH, SwingKind.LOW}


def test_equal_highs_are_no_swing(mk):
    """Strikte Ungleichheit: equal highs bilden keinen bestätigten Swing —
    sie sind Liquidität (STRATEGY §2.4), keine Struktur."""
    candles = mk([
        (100, 102, 99, 101),
        (101, 102, 100, 101),  # gleiches Hoch wie links
        (101, 101, 99, 100),
    ])
    assert all(s.kind is not SwingKind.HIGH for s in detect_swings(candles))


def test_last_swing_helper(mk):
    candles = mk([
        (100, 101, 99, 100),
        (100, 103, 100, 102),
        (102, 102, 98, 99),
        (99, 104, 99, 103),
        (103, 103, 101, 102),
        (102, 102, 100, 101),
    ])
    swings = detect_swings(candles)
    latest_high = last_swing(swings, SwingKind.HIGH)
    assert latest_high is not None and latest_high.index == 3
    earlier_high = last_swing(swings, SwingKind.HIGH, before_index=3)
    assert earlier_high is not None and earlier_high.index == 1
