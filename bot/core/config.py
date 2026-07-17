"""Konfigurationssystem des Bots.

Alle Parameter aus SPEC §13 als validierte Pydantic-Modelle mit den vom
Inhaber bestätigten Defaults. Die Konfiguration kann aus einer YAML-Datei
geladen werden (``load_config``); später (M7) wird sie zusätzlich
versioniert in der Datenbank gehalten und über das Web-UI bearbeitet.

Jede Abweichung von den Defaults gilt pro Bot-Instanz (= pro verbundenem
Broker-Konto), nie global.
"""

from __future__ import annotations

from datetime import time
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, model_validator


class ScoreWeights(BaseModel):
    """Punktwerte des Konfluenz-Scorings (SPEC §5.2, Rangfolge R16).

    Die Feldnamen entsprechen den Rängen 1–10 aus STRATEGY §10.2.
    Summe der Defaults = 100.
    """

    bias_all_timeframes_aligned: int = Field(default=20, ge=0)
    key_level_fvg_plus_cisd: int = Field(default=18, ge=0)
    cisd_multi_timeframe: int = Field(default=15, ge=0)
    smt_divergence: int = Field(default=12, ge=0)
    key_level_htf_sponsorship: int = Field(default=10, ge=0)
    obvious_dol: int = Field(default=8, ge=0)
    key_level_in_discount_premium: int = Field(default=6, ge=0)
    rejection_block_extra: int = Field(default=5, ge=0)
    liquidity_sweep_before_reversal: int = Field(default=4, ge=0)
    inversion_at_least_1m: int = Field(default=2, ge=0)

    @property
    def maximum(self) -> int:
        """Maximal erreichbare Punktzahl (Summe aller Gewichte)."""
        return sum(getattr(self, name) for name in type(self).model_fields)


class NewsFilterConfig(BaseModel):
    """Optionaler ForexFactory-News-Filter (SPEC §8).

    Kein Bestandteil des Videos (STRATEGY §12) — reine Zusatzfunktion.
    """

    enabled: bool = False
    block_before_min: int = Field(default=5, ge=0)
    block_after_min: int = Field(default=5, ge=0)
    min_impact: str = "high"
    currencies: list[str] = Field(default_factory=lambda: ["USD"])


class BotConfig(BaseModel):
    """Vollständige Konfiguration einer Bot-Instanz (SPEC §13)."""

    # --- Markt & Konto ---------------------------------------------------
    #: Gehandelte Symbole. MT5/FTMO: z. B. "US100"; Tradovate: "MNQ" (R18/F7).
    markets: list[str] = Field(default_factory=lambda: ["US100"])
    #: Vergleichssymbol für SMT (STRATEGY §2.10); MT5: Index-CFD desselben
    #: Brokers (z. B. "US500"), Futures-Setup: "ES".
    smt_reference_symbol: str = "US500"

    # --- Risiko (SPEC §6) ------------------------------------------------
    risk_per_trade_pct: float = Field(default=1.0, gt=0, le=5)  # F2
    rr_min: float = Field(default=1.0, gt=0)  # T1
    rr_max: float = Field(default=3.0, gt=0)  # T1
    max_trade_risk_usd: float = Field(default=1000.0, gt=0)  # F1
    max_daily_loss_pct: float = Field(default=2.0, gt=0)
    max_drawdown_pct: float = Field(default=8.0, gt=0)
    #: Zusätzliches Prop-Firm-Tageslimit in USD (None = deaktiviert).
    prop_daily_loss_usd: float | None = None
    max_concurrent_trades: int = Field(default=1, ge=1)

    # --- Tageslimits (STRATEGY §6.6) ------------------------------------
    max_trades_per_day: int = Field(default=2, ge=1)  # F1(Video)
    stop_after_win: bool = True  # F2(Video): 1 Gewinn → Schluss
    stop_after_losses: int = Field(default=2, ge=1)  # F4(Video)

    # --- Session (STRATEGY §6.7, Z1/Z2) ---------------------------------
    #: Entry-Fenster in Eastern Time; harter Cut um session_end (R14).
    session_start: time = time(9, 30)
    session_end: time = time(11, 0)
    session_timezone: str = "America/New_York"

    # --- Strategie-Struktur ----------------------------------------------
    max_key_levels: int = Field(default=3, ge=1)  # §4.4: max. 2–3 Level
    bias_timeframes: list[str] = Field(default_factory=lambda: ["D1", "H4", "H1"])
    bias_check_timeframe: str = "M15"  # 15m-Gegencheck (B6/R7)
    keylevel_timeframes: list[str] = Field(
        default_factory=lambda: ["M3", "M5", "M15", "M30", "H1", "H4"]
    )
    entry_timeframes: list[str] = Field(
        default_factory=lambda: ["M1", "M2", "M3", "M4", "M5"]
    )
    use_30s: bool = False  # D7: 30s nur für Fortgeschrittene
    allow_lower_tf_inversion: bool = False  # R8-Option
    use_external_leg: bool = False  # C7: konservative Leg-Variante

    # --- Ausführung (STRATEGY §6.1–6.5) ----------------------------------
    sl_mode: str = "swing"  # S1/R9; Alternativen: "body", "fvg"
    sl_buffer_ticks: int = Field(default=0, ge=0)
    be_offset_ticks: int = Field(default=0, ge=0)
    breakeven_enabled: bool = True  # BE1/R11
    trailing_enabled: bool = False  # R12: kein Strategie-Bestandteil

    # --- Scoring (SPEC §5) ----------------------------------------------
    score_threshold: int = Field(default=40, ge=0)
    score_weights: ScoreWeights = Field(default_factory=ScoreWeights)

    # --- Filter & Benachrichtigung ---------------------------------------
    news_filter: NewsFilterConfig = Field(default_factory=NewsFilterConfig)
    #: Ereignisse, die Benachrichtigungen auslösen (SPEC §9); leere Liste
    #: bedeutet: alle Ereignisse senden.
    notify_events: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_consistency(self) -> "BotConfig":
        if self.rr_min > self.rr_max:
            raise ValueError("rr_min darf nicht größer als rr_max sein")
        if self.session_start >= self.session_end:
            raise ValueError("session_start muss vor session_end liegen")
        if self.score_threshold > self.score_weights.maximum:
            raise ValueError(
                "score_threshold übersteigt die maximal erreichbare Punktzahl "
                f"({self.score_weights.maximum})"
            )
        return self


def load_config(path: str | Path) -> BotConfig:
    """Lädt eine Bot-Konfiguration aus einer YAML-Datei.

    Nicht gesetzte Felder erhalten die bestätigten Defaults aus SPEC §13.
    Ungültige Werte lösen eine aussagekräftige ``ValidationError`` aus —
    der Bot startet dann bewusst NICHT (Fail-Fast statt Handel mit
    falschen Parametern).
    """
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return BotConfig.model_validate(raw)
