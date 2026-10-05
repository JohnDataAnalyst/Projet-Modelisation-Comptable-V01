"""Écritures en partie double (journal général).

Principe fondamental du PCG : toute écriture comporte au moins une ligne
au débit et une ligne au crédit, et Total Débit == Total Crédit.
Sans cette égalité, le journal, la balance et le bilan seraient faux.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Sequence

from .accounts import Compte, get_compte

CENTIME = Decimal("0.01")
ZERO = Decimal("0.00")


def _montant(valeur: Decimal | int | str | float) -> Decimal:
    """Convertit un montant en Decimal arrondi au centime (demi-pair supérieur)."""
    montant = Decimal(str(valeur)).quantize(CENTIME, rounding=ROUND_HALF_UP)
    if montant < ZERO:
        raise ValueError("Un montant débité ou crédité ne peut pas être négatif.")
    return montant


class EcritureInvalide(ValueError):
    """L'écriture ne respecte pas la partie double ou la structure d'une ligne."""


@dataclass(frozen=True)
class LigneEcriture:
    """Une ligne du journal : un seul côté mouvementé (débit XOR crédit).

    Colonnes alignées sur ``60-Journal`` : Compte, Libellé, Débit, Crédit.
    """

    compte: Compte
    libelle: str
    debit: Decimal
    credit: Decimal

    def __post_init__(self) -> None:
        debit = _montant(self.debit)
        credit = _montant(self.credit)
        object.__setattr__(self, "debit", debit)
        object.__setattr__(self, "credit", credit)
        if not self.libelle.strip():
            raise EcritureInvalide("Le libellé d'une ligne d'écriture ne peut pas être vide.")
        if debit == ZERO and credit == ZERO:
            raise EcritureInvalide(
                f"La ligne du compte {self.compte.numero} n'a ni débit ni crédit."
            )
        if debit > ZERO and credit > ZERO:
            raise EcritureInvalide(
                f"La ligne du compte {self.compte.numero} ne peut pas être à la fois "
                "débitée et créditée (une ligne = un seul sens)."
            )

    @property
    def est_debit(self) -> bool:
        return self.debit > ZERO

    @classmethod
    def au_debit(
        cls,
        compte: Compte | int,
        libelle: str,
        montant: Decimal | int | str | float,
    ) -> LigneEcriture:
        """Emploi : on débite un actif, une charge, ou on diminue un passif."""
        compte_obj = compte if isinstance(compte, Compte) else get_compte(compte)
        return cls(compte=compte_obj, libelle=libelle, debit=_montant(montant), credit=ZERO)

    @classmethod
    def au_credit(
        cls,
        compte: Compte | int,
        libelle: str,
        montant: Decimal | int | str | float,
    ) -> LigneEcriture:
        """Ressource : on crédite un passif, un produit, ou on diminue un actif."""
        compte_obj = compte if isinstance(compte, Compte) else get_compte(compte)
        return cls(compte=compte_obj, libelle=libelle, debit=ZERO, credit=_montant(montant))


@dataclass(frozen=True)
class Ecriture:
    """Ensemble de lignes d'un même fait générateur, à une date donnée.

    ``journal`` reprend le code du journal d'origine (VE, HA, BQ, OD…).
    ``reference`` identifie la pièce (facture, échéance, code produit).
    """

    date: date
    journal: str
    reference: str
    lignes: tuple[LigneEcriture, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        lignes = tuple(self.lignes)
        object.__setattr__(self, "lignes", lignes)
        if not self.journal.strip():
            raise EcritureInvalide("Le code journal est obligatoire.")
        if len(lignes) < 2:
            raise EcritureInvalide(
                "Une écriture doit comporter au moins deux lignes (un débit et un crédit)."
            )
        if not any(ligne.est_debit for ligne in lignes):
            raise EcritureInvalide("Une écriture doit comporter au moins une ligne au débit.")
        if not any(not ligne.est_debit for ligne in lignes):
            raise EcritureInvalide("Une écriture doit comporter au moins une ligne au crédit.")
        if self.total_debit != self.total_credit:
            raise EcritureInvalide(
                f"Partie double non respectée (réf. {self.reference}) : "
                f"débit {self.total_debit} ≠ crédit {self.total_credit}."
            )

    @property
    def total_debit(self) -> Decimal:
        return sum((ligne.debit for ligne in self.lignes), ZERO)

    @property
    def total_credit(self) -> Decimal:
        return sum((ligne.credit for ligne in self.lignes), ZERO)

    @classmethod
    def creer(
        cls,
        date_ecriture: date,
        journal: str,
        reference: str,
        lignes: Sequence[LigneEcriture],
    ) -> Ecriture:
        """Construit une écriture après validation de la partie double."""
        return cls(
            date=date_ecriture,
            journal=journal,
            reference=reference,
            lignes=tuple(lignes),
        )
