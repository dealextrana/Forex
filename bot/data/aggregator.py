"""Timeframe-Aggregation (SPEC §4.1).

Aus einem Basis-Feed (1m-Bars vom Broker; 30s optional aus Ticks) werden
alle höheren Timeframes gebildet. Die Bucket-Grenzen sind am Epoch
ausgerichtet (UTC-Floor auf die Timeframe-Dauer) — das entspricht dem
Verhalten von MT5/TradingView für Intraday-Timeframes.

Hinweis D1/H4: Für die Bias-Timeframes wird in M5 die Ausrichtung an der
Broker-Serverzeit ergänzt (MT5-Tageskerzen folgen der Serverzeit, nicht
UTC). Die Detektor-Logik ist davon unabhängig.
"""

from __future__ import annotations

from datetime import datetime, timezone

from bot.core.models import Candle, Timeframe


def bucket_start(ts: datetime, timeframe: Timeframe) -> datetime:
    """Startzeitpunkt des Timeframe-Buckets, in den ``ts`` fällt."""
    epoch = int(ts.timestamp())
    floored = epoch - (epoch % timeframe.seconds)
    return datetime.fromtimestamp(floored, tz=timezone.utc)


def aggregate(candles: list[Candle], timeframe: Timeframe) -> list[Candle]:
    """Aggregiert Basis-Kerzen zu einem höheren Timeframe.

    Erwartet chronologisch sortierte Eingangskerzen, deren Dauer die
    Ziel-Timeframe-Dauer teilt (z. B. 1m → 5m). Unvollständige letzte
    Buckets werden mit ausgegeben (letzte Kerze = "laufende" Kerze) —
    Entscheidungen trifft die Engine grundsätzlich nur auf
    **geschlossenen** Kerzen (SPEC §2), das filtert der Aufrufer über
    ``drop_last_incomplete`` oder eigene Logik.
    """
    if not candles:
        return []

    result: list[Candle] = []
    cur_start: datetime | None = None
    o = h = l = c = v = 0.0

    for candle in candles:
        start = bucket_start(candle.ts, timeframe)
        if cur_start is None or start != cur_start:
            if cur_start is not None:
                result.append(Candle(cur_start, o, h, l, c, v))
            cur_start = start
            o, h, l, c, v = candle.open, candle.high, candle.low, candle.close, candle.volume
        else:
            h = max(h, candle.high)
            l = min(l, candle.low)
            c = candle.close
            v += candle.volume

    assert cur_start is not None
    result.append(Candle(cur_start, o, h, l, c, v))
    return result


def drop_last_incomplete(
    aggregated: list[Candle], timeframe: Timeframe, now: datetime
) -> list[Candle]:
    """Entfernt die noch laufende (nicht geschlossene) letzte Kerze.

    Eine Kerze gilt als geschlossen, wenn ihr Bucket-Ende <= ``now`` ist.
    Body-Close-Regeln (R2/R6) dürfen nur auf geschlossenen Kerzen
    ausgewertet werden.
    """
    if not aggregated:
        return aggregated
    last = aggregated[-1]
    bucket_end_epoch = int(last.ts.timestamp()) + timeframe.seconds
    if int(now.timestamp()) >= bucket_end_epoch:
        return aggregated
    return aggregated[:-1]
