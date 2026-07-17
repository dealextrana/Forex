"""Tests für die Sweep-Erkennung (STRATEGY §2.4, R3)."""

from bot.detectors.swing import SwingKind
from bot.detectors.sweep import find_sweep, is_swept


def test_wick_pierce_is_sweep_without_close_back(mk):
    """R3-Golden-Test: Wick unter das Tief genügt — die Kerze schließt hier
    sogar UNTER dem Level und es ist trotzdem ein gültiger Sweep."""
    candles = mk([
        (100, 101, 98, 99),
        (99, 100, 97.5, 97.8),  # Low 97.5 < 98 → Sweep (Close egal)
    ])
    sweep = find_sweep(candles, level_price=98, level_kind=SwingKind.LOW)
    assert sweep is not None
    assert sweep.candle_index == 1
    assert sweep.extreme == 97.5


def test_exact_touch_is_no_sweep(mk):
    candles = mk([
        (100, 101, 98, 99),
        (99, 100, 98, 98.5),  # exakt 98 berührt → kein Sweep
    ])
    assert not is_swept(candles, 98, SwingKind.LOW)


def test_high_sweep(mk):
    candles = mk([
        (100, 102, 99, 101),
        (101, 102.5, 100, 100.2),  # High 102.5 > 102 → Buy-Side genommen
    ])
    assert is_swept(candles, 102, SwingKind.HIGH)


def test_start_index_respected(mk):
    candles = mk([
        (100, 101, 97, 99),  # sweept bereits
        (99, 100, 98.5, 99),
    ])
    assert is_swept(candles, 98, SwingKind.LOW, start_index=0)
    assert not is_swept(candles, 98, SwingKind.LOW, start_index=1)
