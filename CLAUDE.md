# Projektgedächtnis — Mech-Model Trading-Bot

Diese Datei wird von Claude Code automatisch zu Beginn jeder Session in
diesem Repo gelesen. Sie fasst den gesamten bisherigen Stand zusammen,
damit auch eine komplett neue Session (anderes Modell, neuer Chat) ohne
Rückfragen nahtlos weiterarbeiten kann. **Vollständige Details stehen in
den verlinkten Dokumenten — diese Datei ist die Kurzfassung.**

## Was das Projekt ist

Ein vollautomatischer Trading-Bot, der die 4-Schritte-Strategie von
PB Blake („Updated Mech Model 2026", aus dessen Referenzvideo) exakt
umsetzt, plus eine abgesicherte Web-Plattform zur Bedienung. Inhaber/
Nutzer: Alex (alex@detrana.ch).

**Grundsatz, der für die ganze Codebase gilt:** Keine Strategie-Regel
wird erfunden. Jede Regel im Code muss auf eine bestätigte Aussage in
`docs/STRATEGY.md` zurückführbar sein (dort mit IDs wie R2, K1, C3
referenziert). Was das Video nicht hergibt, wird als Lücke markiert,
nicht stillschweigend ergänzt.

## Prozess (vom Nutzer vorgegeben, bereits durchlaufen)

1. **Schritt 1** — Strategie-Doku ausschließlich aus dem Video → `docs/STRATEGY.md` ✅
2. **Schritt 2** — Review durch den Nutzer (Rückfragen R1–R19 beantwortet, in STRATEGY.md §14 dokumentiert) ✅
3. **Schritt 3** — Technische Spezifikation → `docs/SPEC.md` (offene Punkte F1–F7 beantwortet, in SPEC.md §17 dokumentiert) ✅
4. **Schritt 4** — Implementierung nach Meilensteinplan (SPEC §16), erst nach Freigabe — **läuft, siehe Projektstand unten**

## Dokumente (Quelle der Wahrheit)

| Datei | Inhalt |
|---|---|
| `docs/STRATEGY.md` | Vollständige Strategie: Bias/DOL, Key Levels (FVG/CISD/Rejection Block), IFVG-Bestätigung, Ausführung/Risk, Long/Short-Regeln, Invalidierung, 3 Video-Beispiele, Konfluenz-Rangfolge (§10), alle Review-Entscheidungen (§14) |
| `docs/SPEC.md` | Architektur, Punktesystem mit konkreten Gewichten (§5), Risk Engine, Broker-Adapter, Session/News-Filter, Telegram, Web-Plattform, Persistenz/Recovery, Konfigurationsparameter (§13), Backtesting, Meilensteinplan (§16), Entscheidungen F1–F7 (§17) |
| `docs/ANLEITUNG_TELEGRAM.md` | Einfache Anleitung: Telegram-Bot via BotFather erstellen |
| `docs/ANLEITUNG_SERVER.md` | Einfache Anleitung: Linux-VPS, Windows-VPS, Domain kaufen |
| `README.md` | Projektstand-Checkliste, Setup-Befehle |

## Wichtige, bereits getroffene Entscheidungen (Kurzfassung — Details in den Docs)

- **Märkte:** Micro-Risiko-Prinzip. Primär **US100/NAS100-CFD auf FTMO
  über MetaTrader 5** (Signale direkt auf den MT5-Kerzen berechnet, F3
  Option B). **MNQ via Tradovate optional** — nur falls das
  Alpha-Futures-„Zero"-Konto des Nutzers nach dessen Migration
  API-Zugang behält (F7, unklar, vor Umsetzung beim Support klären).
  Forex-Paare sind **nicht** Teil der Strategie.
- **Session:** Neue Entries nur **9:30–11:00 Uhr Eastern Time**, harter
  Cut um 11:00 (R14). Offene Positionen laufen weiter, kein Zwangs-Flat.
- **Bias:** wird **intraday laufend neu bewertet** (15m-Check), nicht
  einmal täglich fixiert (R7).
- **Risiko:** 1 % pro Trade (F2), harte Sicherheitsgrenze
  **max. 1000 $ Risiko pro Trade** (F1, nicht 1000 Punkte).
- **Tageslimits:** max. 2 Trades/Tag, 1 Gewinn → Schluss, 2 Verluste →
  Schluss; zweiter Trade nach 1 Verlust nur bei neuem Key Level, **keine**
  erhöhte Punkteschwelle dafür (R13).
- **Punktesystem:** K.o.-Gates (Bias, Key Level, höchste IFVG-Inversion,
  Session, Tageslimits) + gewichtete Konfluenzen, Summe 100, Schwelle
  Default 40 (STRATEGY §10, SPEC §5, R16 bestätigt).
- **Kein strategischer Trailing-Stop** (R12) — nur generisches,
  optionales Trailing als Zusatzfeature, Default aus.
- **Web-Plattform:** HTTPS Pflicht, Registrierung **nur mit
  Referenzcode**, den ausschließlich der Inhaber ausgibt; Rollen
  Owner/Nutzer; verschlüsselte Broker-Credentials.
- **Benachrichtigung:** Telegram bei jedem Trade-Ereignis (Entry, BE,
  TP/SL, Fehler, Tagesabschluss); Nutzer erstellt den Bot-Token selbst
  (Anleitung vorhanden).
- **Server/Hosting:** Noch nicht vorhanden. Nutzer bevorzugt, dass die
  technische Einrichtung übernommen wird; das **Mieten** (Kauf mit
  eigener Zahlungskarte) muss der Nutzer selbst tun — dafür existiert
  eine leicht verständliche Kauf-Anleitung (`docs/ANLEITUNG_SERVER.md`).
  Die komplette technische Einrichtung danach liefert das Projekt fertig
  (Docker + Setup-Skripte, Meilenstein M7).
- **Live-Handel** erst nach erfolgreicher Demo-Phase und **ausdrücklicher
  Freigabe des Nutzers** — niemals automatisch.

## Projektstand (Code)

Branch: `claude/pb-blake-trading-bot-fwaul9`

- [x] **M1** — Projektgerüst: Konfiguration (`bot/core/config.py`, alle
  SPEC-§13-Parameter mit bestätigten Defaults), Logging, Persistenz
  (`bot/persistence/`: SQLAlchemy-Modelle, idempotente Order-Keys gegen
  Doppel-Einstiege)
- [x] **M2** — Strategie-Detektoren (`bot/detectors/`): Swing (R1), FVG
  inkl. Zustände (R2), Sweep (R3), CISD (R4), Rejection Block (R5),
  IFVG-Inversion (R6, inkl. Leg-Filter C2 und Höchst-Timeframe-Auswahl
  C3/R8), SMT-Divergenz; Timeframe-Aggregation (`bot/data/aggregator.py`).
  48 Tests grün, inkl. Golden-Tests der 3 Video-Beispiele.
- [~] **M3** — läuft. Fertig: Bias-Engine (`bot/bias/engine.py`, Commit
  f1ecb99 — HTF-Bias aus jüngstem FVG je Richtung B1/R2, Gesamtbias nur
  bei TF-Übereinstimmung, 15m-Intraday-Check R7, Draw on Liquidity).
  **Noch offen in M3:** Key-Level-Manager (§4.4, K1–K8), Scoring-Engine
  (§5, Gates + Gewichte), Setup-State-Machine (§4.5, IDLE→…→CLOSED),
  Risk-Engine (§6, Sizing/Limits/Kill-Switch), Paper-Modus, Tests.
- [ ] **M4** — Backtester
- [ ] **M5** — FTMO/MT5-Bridge (primärer Broker-Adapter)
- [ ] **M6** — Tradovate-Adapter (optional, nach F7-Klärung)
- [ ] **M7** — Web-Plattform, Telegram-Anbindung, Deployment

Vor jedem größeren Schritt: kurzer Zwischenbericht an den Nutzer;
Reihenfolge der Meilensteine nicht ohne Absprache ändern.

## Arbeitsweise in diesem Projekt

- Sprache im Chat: Deutsch. Fachbegriffe (FVG, CISD, IFVG, SMT, …)
  bleiben englisch, wie im Video.
- Bei neuen Strategie-Fragen: immer zuerst in `docs/STRATEGY.md`
  nachschlagen, ob das Video dazu etwas sagt — nichts annehmen.
- Bei neuen Anforderungen (Broker, Punktesystem, Web-Plattform,
  Benachrichtigungen etc.): in `docs/SPEC.md` als eigenen Abschnitt
  ergänzen, nicht nur im Chat besprechen — die Docs sind das
  Gedächtnis, nicht der Chatverlauf.
- Commits/Pushes laufen fortlaufend auf den Feature-Branch; kein Force
  Push, keine PR ohne ausdrückliche Bitte.
