"""Tests für das Konfigurationssystem (SPEC §13)."""

import pytest
from pydantic import ValidationError

from bot.core.config import BotConfig, ScoreWeights, load_config


def test_defaults_match_spec():
    cfg = BotConfig()
    assert cfg.markets == ["US100"]
    assert cfg.risk_per_trade_pct == 1.0  # F2
    assert cfg.max_trade_risk_usd == 1000.0  # F1
    assert (cfg.rr_min, cfg.rr_max) == (1.0, 3.0)  # T1
    assert cfg.max_trades_per_day == 2  # F1 (Video §6.6)
    assert cfg.stop_after_win and cfg.stop_after_losses == 2
    assert str(cfg.session_start) == "09:30:00" and str(cfg.session_end) == "11:00:00"
    assert cfg.use_30s is False  # D7
    assert cfg.allow_lower_tf_inversion is False  # R8
    assert cfg.trailing_enabled is False  # R12
    assert cfg.breakeven_enabled is True  # R11
    assert cfg.score_threshold == 40
    assert cfg.news_filter.enabled is False


def test_score_weights_sum_to_100():
    assert ScoreWeights().maximum == 100  # SPEC §5.2


def test_invalid_rr_window_rejected():
    with pytest.raises(ValidationError):
        BotConfig(rr_min=2.0, rr_max=1.0)


def test_threshold_above_maximum_rejected():
    with pytest.raises(ValidationError):
        BotConfig(score_threshold=101)


def test_session_order_validated():
    with pytest.raises(ValidationError):
        BotConfig(session_start="11:00", session_end="09:30")


def test_load_config_from_yaml(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text(
        "risk_per_trade_pct: 0.5\n"
        "markets: [MNQ]\n"
        "score_weights:\n"
        "  smt_divergence: 14\n",
        encoding="utf-8",
    )
    cfg = load_config(path)
    assert cfg.risk_per_trade_pct == 0.5
    assert cfg.markets == ["MNQ"]
    assert cfg.score_weights.smt_divergence == 14
    # Nicht überschriebene Defaults bleiben erhalten:
    assert cfg.max_trade_risk_usd == 1000.0


def test_empty_yaml_gives_defaults(tmp_path):
    path = tmp_path / "empty.yaml"
    path.write_text("", encoding="utf-8")
    assert load_config(path) == BotConfig()
