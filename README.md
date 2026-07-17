# Mech-Model Trading-Bot

Automatisierter Trading-Bot nach der 4-Schritte-Strategie von PB Blake
(„Updated Mech Model 2026") — inklusive Punktesystem, Risk-Engine,
FTMO/MT5-Anbindung und Web-Plattform.

## Dokumentation

| Dokument | Inhalt |
|---|---|
| [docs/STRATEGY.md](docs/STRATEGY.md) | Vollständige Strategie-Dokumentation (aus dem Referenzvideo, alle Regeln vom Inhaber bestätigt) |
| [docs/SPEC.md](docs/SPEC.md) | Technische Spezifikation (Architektur, Scoring, Risk, Broker, Web) |
| [docs/ANLEITUNG_TELEGRAM.md](docs/ANLEITUNG_TELEGRAM.md) | Telegram-Bot erstellen (einfach erklärt) |
| [docs/ANLEITUNG_SERVER.md](docs/ANLEITUNG_SERVER.md) | Server & Domain kaufen (einfach erklärt) |

## Projektstand

- [x] Schritt 1: Strategie dokumentiert
- [x] Schritt 2: Review durch den Inhaber (R1–R19)
- [x] Schritt 3: Technische Spezifikation (F1–F7)
- [ ] Schritt 4: Implementierung nach Meilensteinplan (SPEC §16)
  - [x] M1: Projektgerüst (Config, DB, Logging)
  - [x] M2: Strategie-Detektoren + Tests
  - [ ] M3: Bias/Key-Level/State-Machine/Scoring (Paper-Modus)
  - [ ] M4: Backtester
  - [ ] M5: FTMO/MT5-Bridge (primär)
  - [ ] M6: Tradovate (optional, nach API-Bestätigung)
  - [ ] M7: Web-Plattform, Telegram, Deployment

## Entwicklung

```bash
# Abhängigkeiten installieren (Python >= 3.11)
pip install -e ".[dev]"

# Tests ausführen
pytest
```

## Aufbau

```
bot/
├── core/         # Basistypen (Candle, Timeframe), Konfiguration, Logging
├── data/         # Kerzen-Serien und Timeframe-Aggregation
├── detectors/    # Strategie-Detektoren (Swing, FVG, Sweep, CISD,
│                 # Rejection Block, IFVG, SMT) — reine, testbare Funktionen
└── persistence/  # SQLAlchemy-Modelle und DB-Zugriff
tests/            # Unit- und Golden-Tests (Szenarien aus dem Referenzvideo)
```

⚠️ **Hinweis:** Live-Handel erst nach erfolgreicher Demo-Phase und
ausdrücklicher Freigabe des Inhabers (SPEC §16).
