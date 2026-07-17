"""Tests für die SMT-Divergenz (STRATEGY §2.10).

Golden-Test aus Video-Beispiel 1: „ES took it out, NASDAQ didn't" —
bullische SMT am Intermediate Low.
"""

from bot.core.models import Direction
from bot.detectors.swing import SwingKind
from bot.detectors.smt import detect_smt


def test_bullish_smt_reference_sweeps_primary_holds(mk):
    primary = mk([          # NQ/US100: hält das Tief (Low bleibt über 100)
        (101, 102, 100.2, 101.5),
        (101.5, 102, 100.4, 101),
    ])
    reference = mk([        # ES/US500: sweept sein Tief (Low 199.5 < 200)
        (201, 202, 199.5, 201.5),
        (201.5, 202, 200.5, 201),
    ])
    signal = detect_smt(primary, reference,
                        primary_level=100, reference_level=200,
                        kind=SwingKind.LOW)
    assert signal is not None
    assert signal.direction is Direction.BULLISH
    assert signal.primary_held  # der gehandelte Index hat gehalten


def test_no_smt_when_both_sweep(mk):
    primary = mk([(101, 102, 99.5, 101)])
    reference = mk([(201, 202, 199.5, 201)])
    assert detect_smt(primary, reference, 100, 200, SwingKind.LOW) is None


def test_no_smt_when_neither_sweeps(mk):
    primary = mk([(101, 102, 100.5, 101)])
    reference = mk([(201, 202, 200.5, 201)])
    assert detect_smt(primary, reference, 100, 200, SwingKind.LOW) is None


def test_bearish_smt_at_highs(mk):
    """Beispiel 3: ES nimmt das Hoch, NQ nicht → bärische SMT am Swing High."""
    primary = mk([(101, 101.8, 100, 101)])       # hält unter 102
    reference = mk([(201, 202.5, 200, 201)])     # sweept 202
    signal = detect_smt(primary, reference, 102, 202, SwingKind.HIGH)
    assert signal is not None
    assert signal.direction is Direction.BEARISH
    assert signal.primary_held
