"""Tests für die Timeframe-Aggregation (SPEC §4.1)."""

from datetime import timedelta

from bot.core.models import Timeframe
from bot.data.aggregator import aggregate, bucket_start, drop_last_incomplete
from tests.conftest import START


def test_aggregate_1m_to_5m(mk):
    # 10 Ein-Minuten-Kerzen → zwei 5m-Kerzen (START liegt auf :30, also
    # exakt an einer 5m-Grenze).
    ohlc = [
        (100, 102, 99, 101),
        (101, 103, 100, 102),
        (102, 104, 101, 103),
        (103, 105, 102, 104),
        (104, 106, 103, 105),  # Ende Bucket 1
        (105, 107, 104, 106),
        (106, 108, 105, 107),
        (107, 109, 106, 108),
        (108, 110, 107, 109),
        (109, 111, 108, 110),  # Ende Bucket 2
    ]
    candles = mk(ohlc)
    result = aggregate(candles, Timeframe.M5)
    assert len(result) == 2
    b1, b2 = result
    assert (b1.open, b1.high, b1.low, b1.close) == (100, 106, 99, 105)
    assert (b2.open, b2.high, b2.low, b2.close) == (105, 111, 104, 110)
    assert b1.ts == START and b2.ts == START + timedelta(minutes=5)


def test_bucket_start_floors_to_timeframe():
    ts = START + timedelta(minutes=7, seconds=42)
    assert bucket_start(ts, Timeframe.M5) == START + timedelta(minutes=5)
    assert bucket_start(ts, Timeframe.M1) == START + timedelta(minutes=7)


def test_partial_last_bucket_is_emitted_and_droppable(mk):
    candles = mk([
        (100, 101, 99, 100),
        (100, 102, 100, 101),
        (101, 103, 100, 102),
        (102, 104, 101, 103),
        (103, 105, 102, 104),
        (104, 106, 103, 105),  # 6. Kerze → zweiter 5m-Bucket, unvollständig
    ])
    result = aggregate(candles, Timeframe.M5)
    assert len(result) == 2

    # Zum Zeitpunkt „Ende der 6. Minute" ist der zweite Bucket noch offen →
    # für Body-Close-Entscheidungen (R2/R6) muss er verworfen werden.
    now = START + timedelta(minutes=6)
    closed = drop_last_incomplete(result, Timeframe.M5, now)
    assert len(closed) == 1

    # Nach Bucket-Ende zählt er als geschlossen.
    now = START + timedelta(minutes=10)
    assert len(drop_last_incomplete(result, Timeframe.M5, now)) == 2


def test_aggregate_empty():
    assert aggregate([], Timeframe.M5) == []
