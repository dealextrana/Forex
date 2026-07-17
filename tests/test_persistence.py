"""Tests für die Persistenzschicht (SPEC §11) — SQLite in-memory."""

from datetime import datetime, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from bot.persistence.db import init_db, make_engine, make_session_factory, session_scope
from bot.persistence.models import BotInstance, OrderRecord, Trade


@pytest.fixture
def factory():
    engine = make_engine("sqlite:///:memory:")
    init_db(engine)
    return make_session_factory(engine)


def test_instance_and_trade_roundtrip(factory):
    with session_scope(factory) as session:
        instance = BotInstance(name="ftmo-demo", broker="mt5", symbol="US100")
        session.add(instance)
        session.flush()
        session.add(
            Trade(
                instance_id=instance.id,
                symbol="US100",
                direction="bullish",
                entry_time=datetime(2026, 5, 13, 14, 0, tzinfo=timezone.utc),
                entry_price=18500.0,
                stop_loss=18450.0,
                take_profit=18600.0,
                size=0.5,
                risk_usd=250.0,
                score=57,
                score_breakdown={"smt_divergence": 12},
            )
        )

    with session_scope(factory) as session:
        trade = session.query(Trade).one()
        assert trade.score_breakdown == {"smt_divergence": 12}
        assert trade.outcome is None  # noch offen


def test_client_key_uniqueness_blocks_double_entry(factory):
    """I5/SPEC §11: derselbe client_key kann nie zweimal gespeichert werden —
    das ist die letzte Verteidigungslinie gegen Doppel-Einstiege."""
    with session_scope(factory) as session:
        instance = BotInstance(name="x", broker="paper", symbol="US100")
        session.add(instance)
        session.flush()
        session.add(OrderRecord(instance_id=instance.id, client_key="setup-1-entry",
                                kind="entry", status="pending"))

    with pytest.raises(IntegrityError):
        with session_scope(factory) as session:
            session.add(OrderRecord(instance_id=1, client_key="setup-1-entry",
                                    kind="entry", status="pending"))
