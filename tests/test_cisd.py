"""Tests für den CISD-Detektor (STRATEGY §2.6, R4).

Der bullische Fall stellt die Video-Sequenz nach: Down-Close-Serie
handelt in ein Key Level, Anker = Open der ersten Serienkerze, Body-Close
darüber bestätigt den CISD.
"""

from bot.core.models import Direction
from bot.detectors.cisd import detect_cisd


def test_bullish_cisd_video_sequence(mk):
    candles = mk([
        (105, 106, 104, 105.5),  # 0: Up-Kerze (vor der Serie)
        (105.5, 105.5, 103, 104),  # 1: erste Down-Close-Kerze → Anker = 105.5
        (104, 104, 101, 102),      # 2: Down-Serie
        (102, 102.5, 99, 100),     # 3: Down-Serie, trifft das Level (touch)
        (100, 103, 99.5, 102.5),   # 4: dreht, aber Close 102.5 < 105.5
        (102.5, 107, 102, 106),    # 5: Body-Close 106 > 105.5 → CISD bestätigt
    ])
    cisd = detect_cisd(candles, touch_index=3, direction=Direction.BULLISH)
    assert cisd is not None
    assert cisd.anchor_price == 105.5  # R4: Open der ERSTEN Kerze der Serie
    assert (cisd.series_start, cisd.series_end) == (1, 3)
    assert cisd.confirmed_index == 5
    assert cisd.is_confirmed


def test_unconfirmed_cisd_has_no_level_yet(mk):
    candles = mk([
        (105, 106, 104, 105.5),
        (105.5, 105.5, 103, 104),
        (104, 104, 101, 102),
        (102, 103, 101, 102.5),  # dreht, bleibt aber unter dem Anker
    ])
    cisd = detect_cisd(candles, touch_index=2, direction=Direction.BULLISH)
    assert cisd is not None
    assert not cisd.is_confirmed  # K4: Level existiert erst nach Body-Close


def test_touch_by_wick_of_bullish_candle_uses_preceding_series(mk):
    """Berührt eine Up-Kerze das Level nur per Wick, zählt die
    unmittelbar vorausgehende Down-Close-Serie."""
    candles = mk([
        (106, 106.5, 105, 106.2),
        (106.2, 106.2, 103, 104),  # Serie beginnt → Anker = 106.2
        (104, 104.5, 101, 102),    # Serie
        (102, 105, 99, 104.5),     # Up-Kerze, Wick trifft das Level
        (104.5, 108, 104, 107),    # Close 107 > 106.2 → bestätigt
    ])
    cisd = detect_cisd(candles, touch_index=3, direction=Direction.BULLISH)
    assert cisd is not None
    assert cisd.anchor_price == 106.2
    assert (cisd.series_start, cisd.series_end) == (1, 2)
    assert cisd.confirmed_index == 4


def test_bearish_cisd_mirror(mk):
    candles = mk([
        (95, 96, 94, 94.5),
        (94.5, 97, 94, 96),     # erste Up-Close-Kerze → Anker = 94.5
        (96, 99, 95.5, 98),     # Up-Serie trifft bärisches Level
        (98, 98.5, 93, 94),     # Body-Close 94 < 94.5 → bestätigt
    ])
    cisd = detect_cisd(candles, touch_index=2, direction=Direction.BEARISH)
    assert cisd is not None
    assert cisd.anchor_price == 94.5
    assert cisd.confirmed_index == 3


def test_no_series_returns_none(mk):
    """Nur Up-Kerzen vor der Berührung → kein bullischer CISD möglich."""
    candles = mk([
        (100, 102, 99.5, 101.5),
        (101.5, 103, 101, 102.5),
    ])
    assert detect_cisd(candles, touch_index=1, direction=Direction.BULLISH) is None
