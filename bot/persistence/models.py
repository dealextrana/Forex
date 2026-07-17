"""Datenbank-Modelle (Kern-Teilmenge für M1–M4, SPEC §11).

Web-/Nutzer-Tabellen (users, invite_codes, broker_accounts, …) folgen in
M7. Hier liegt alles, was Bot-Betrieb, Recovery und Journal brauchen:
jeder Zustandsübergang wird sofort persistiert, damit der Bot nach einem
Neustart gegen den Broker rekonsilieren und nahtlos weiterarbeiten kann.

Flexible Nutzdaten (Score-Breakdown, Level-Metadaten) liegen als JSON —
das hält das Schema stabil, während die Strategie-Details evolvieren.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class BotInstance(Base):
    """Eine Bot-Instanz = ein verbundenes Broker-Konto mit eigener Config."""

    __tablename__ = "bot_instances"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    broker: Mapped[str] = mapped_column(String(30))  # "mt5" | "tradovate" | "paper"
    symbol: Mapped[str] = mapped_column(String(30))  # z. B. "US100", "MNQ"
    enabled: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    configs: Mapped[list["ConfigVersion"]] = relationship(back_populates="instance")
    trades: Mapped[list["Trade"]] = relationship(back_populates="instance")


class ConfigVersion(Base):
    """Versionierte Konfiguration (SPEC §13) — Änderungen greifen nur für
    neue Setups, nie in laufende Trades (SPEC §10.2)."""

    __tablename__ = "config_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    instance_id: Mapped[int] = mapped_column(ForeignKey("bot_instances.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    #: Vollständiger BotConfig-Dump (bot/core/config.py) als JSON.
    payload: Mapped[dict] = mapped_column(JSON)

    instance: Mapped[BotInstance] = relationship(back_populates="configs")


class SetupRecord(Base):
    """Zustand der Setup-State-Machine (SPEC §4.5) — Grundlage der Recovery."""

    __tablename__ = "setups"

    id: Mapped[int] = mapped_column(primary_key=True)
    instance_id: Mapped[int] = mapped_column(ForeignKey("bot_instances.id"))
    state: Mapped[str] = mapped_column(String(30))  # IDLE/ARMED/TAPPED/...
    direction: Mapped[str | None] = mapped_column(String(10), nullable=True)
    #: Serialisierter Kontext: Key Level, Manipulation Leg, IFVG-Kandidaten,
    #: Score-Breakdown — alles, was zum Wiederaufsetzen nötig ist.
    context: Mapped[dict] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class OrderRecord(Base):
    """Jede an den Broker gesendete Order (SPEC §11).

    ``client_key`` ist der idempotente Schlüssel gegen Doppel-Einstiege
    (I5): dieselbe Setup-Instanz kann nie zwei Entry-Orders erzeugen.
    """

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    instance_id: Mapped[int] = mapped_column(ForeignKey("bot_instances.id"))
    setup_id: Mapped[int | None] = mapped_column(ForeignKey("setups.id"), nullable=True)
    client_key: Mapped[str] = mapped_column(String(64), unique=True)
    kind: Mapped[str] = mapped_column(String(20))  # entry/sl/tp/modify/cancel
    status: Mapped[str] = mapped_column(String(20))  # pending/filled/rejected/...
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Trade(Base):
    """Trade-Journal (SPEC §12): ein abgeschlossener oder laufender Trade."""

    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(primary_key=True)
    instance_id: Mapped[int] = mapped_column(ForeignKey("bot_instances.id"))
    symbol: Mapped[str] = mapped_column(String(30))
    direction: Mapped[str] = mapped_column(String(10))
    entry_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    entry_price: Mapped[float] = mapped_column(Float)
    stop_loss: Mapped[float] = mapped_column(Float)
    take_profit: Mapped[float] = mapped_column(Float)
    size: Mapped[float] = mapped_column(Float)  # Kontrakte bzw. Lots
    risk_usd: Mapped[float] = mapped_column(Float)
    exit_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    exit_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    result_r: Mapped[float | None] = mapped_column(Float, nullable=True)
    result_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    #: "tp" | "sl" | "breakeven" | "manual" — BE zählt NICHT als
    #: Gewinn/Verlust für die Tageslimits (STRATEGY BE3/§6.6).
    outcome: Mapped[str | None] = mapped_column(String(20), nullable=True)
    score: Mapped[int] = mapped_column(Integer, default=0)
    score_breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
    #: Alle Level des Setups (Key Level, Leg, IFVG-TF) für das Journal.
    setup_context: Mapped[dict] = mapped_column(JSON, default=dict)

    instance: Mapped[BotInstance] = relationship(back_populates="trades")


class DailyCounter(Base):
    """Tageszähler (STRATEGY §6.6): Trades, Gewinne, Verluste, P&L."""

    __tablename__ = "daily_counters"

    id: Mapped[int] = mapped_column(primary_key=True)
    instance_id: Mapped[int] = mapped_column(ForeignKey("bot_instances.id"))
    #: Handelstag in Eastern Time (YYYY-MM-DD) — Sessiongrenzen, nicht UTC.
    trading_day: Mapped[str] = mapped_column(String(10))
    trades: Mapped[int] = mapped_column(Integer, default=0)
    wins: Mapped[int] = mapped_column(Integer, default=0)
    losses: Mapped[int] = mapped_column(Integer, default=0)
    pnl_usd: Mapped[float] = mapped_column(Float, default=0.0)


class EventLog(Base):
    """Ereignis-Feed (SPEC §9/§12): Grundlage für Telegram & Dashboard."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    instance_id: Mapped[int | None] = mapped_column(
        ForeignKey("bot_instances.id"), nullable=True
    )
    kind: Mapped[str] = mapped_column(String(30))  # ENTRY/TP_HIT/ERROR/...
    message: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
