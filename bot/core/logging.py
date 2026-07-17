"""Zentrales Logging (SPEC §12).

Strukturierte JSON-Logs für den Betrieb (maschinell auswertbar, z. B.
warum ein Setup verworfen wurde) und lesbare Konsolen-Logs für die
Entwicklung. Jede Strategie-Entscheidung wird mit Kontextfeldern geloggt
(Regel-ID, Symbol, Timeframe, Preise), nie als Freitext allein.
"""

from __future__ import annotations

import logging
import sys

import structlog


def setup_logging(*, json_output: bool = True, level: int = logging.INFO) -> None:
    """Initialisiert structlog einmalig beim Prozessstart.

    :param json_output: True = JSON-Zeilen (Produktion/Auswertung),
        False = farbige Konsole (Entwicklung).
    :param level: Minimales Log-Level.
    """
    logging.basicConfig(stream=sys.stdout, level=level, format="%(message)s")

    renderer: structlog.types.Processor
    if json_output:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Liefert einen benannten strukturierten Logger."""
    return structlog.get_logger(name)
