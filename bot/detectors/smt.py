"""SMT — Smart-Money-Divergenz zwischen zwei korrelierten Indizes.

STRATEGY §2.10: Bullische SMT, wenn am Referenz-Tief nur EINER der beiden
Indizes (z. B. US100 vs. US500 bzw. NQ vs. ES) das Tief sweept und der
andere nicht. Bärische SMT spiegelbildlich an Referenz-Hochs.

Verwendung: Konfluenz am Key Level (§10 Rang 4) — keine eigenständige
Einstiegsbedingung. Sweep-Definition gemäß R3 (Wick-Durchstich genügt).
"""

from __future__ import annotations

from dataclasses import dataclass

from bot.core.models import Candle, Direction
from bot.detectors.swing import SwingKind
from bot.detectors.sweep import is_swept


@dataclass(frozen=True, slots=True)
class SMTSignal:
    """Eine erkannte SMT-Divergenz."""

    direction: Direction
    #: True, wenn das Primärsymbol (das gehandelte) das Level NICHT
    #: gesweept hat (der „stärkere" Index) — im Video der bevorzugte Fall
    #: („ES took it out, NASDAQ didn't").
    primary_held: bool


def detect_smt(
    primary: list[Candle],
    reference: list[Candle],
    primary_level: float,
    reference_level: float,
    kind: SwingKind,
    start_primary: int = 0,
    start_reference: int = 0,
) -> SMTSignal | None:
    """Prüft auf SMT-Divergenz an zueinander gehörenden Referenz-Levels.

    :param primary: Kerzen des gehandelten Symbols (z. B. US100).
    :param reference: Kerzen des Vergleichssymbols (z. B. US500).
    :param primary_level / reference_level: die korrespondierenden
        Swing-Preise beider Symbole (gleicher struktureller Punkt).
    :param kind: LOW → Test auf bullische SMT, HIGH → bärische SMT.
    :return: Signal, wenn genau EINES der Symbole das Level gesweept hat;
        ``None``, wenn beide oder keines sweepen (keine Divergenz).
    """
    primary_swept = is_swept(primary, primary_level, kind, start_primary)
    reference_swept = is_swept(reference, reference_level, kind, start_reference)

    if primary_swept == reference_swept:
        return None  # beide oder keiner → keine Divergenz

    direction = Direction.BULLISH if kind is SwingKind.LOW else Direction.BEARISH
    return SMTSignal(direction=direction, primary_held=not primary_swept)
