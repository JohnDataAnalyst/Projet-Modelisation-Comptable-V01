"""Journal général, grand livre et balance.

Le journal général est le registre chronologique des écritures (onglet
``60-Journal``). Le grand livre reclasse les mêmes mouvements par compte.
La balance (``62-Balance``) en est la synthèse : pour chaque compte,
soldes et mouvements sur la période définie par deux dates.

Contrôles à conserver (§6) :
- journal : total débit = total crédit ;
- balance : somme des soldes nets = 0.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from .accounts import Compte, Destination, get_compte
from .journal import ZERO, Ecriture, LigneEcriture


@dataclass(frozen=True)
class SoldeCompte:
    """Cumul des mouvements d'un compte sur un sous-ensemble d'écritures."""

    compte: Compte
    total_debit: Decimal
    total_credit: Decimal

    @property
    def solde_net(self) -> Decimal:
        """Débit − crédit. Positif = solde débiteur, négatif = solde créditeur."""
        return self.total_debit - self.total_credit

    @property
    def solde_debiteur(self) -> Decimal:
        return self.solde_net if self.solde_net > ZERO else ZERO

    @property
    def solde_crediteur(self) -> Decimal:
        return -self.solde_net if self.solde_net < ZERO else ZERO


@dataclass(frozen=True)
class LigneBalance:
    """Une ligne de balance, calquée sur ``62-Balance``.

    - Solde à la clôture : toutes les écritures de date ≤ fin (le bilan, « la photo »).
    - Mouvements de la période : écritures entre début et fin (le CR, « le film »).
    - Avant la période : différence des deux.
    """

    compte: Compte
    solde_cloture: Decimal
    mouvements_periode: Decimal
    avant_periode: Decimal

    @property
    def intitule(self) -> str:
        return self.compte.libelle

    @property
    def destination(self) -> Destination:
        return self.compte.destination


class GrandLivre:
    """Journal général + grand livre.

    On n'accepte que des ``Ecriture`` déjà équilibrées : le registre ne peut
    pas rompre la partie double une fois les pièces validées.
    """

    def __init__(self) -> None:
        self._ecritures: list[Ecriture] = []

    def ajouter(self, ecriture: Ecriture) -> None:
        """Enregistre une écriture dans l'ordre de saisie (tri chronologique à la lecture)."""
        self._ecritures.append(ecriture)

    @property
    def journal(self) -> tuple[Ecriture, ...]:
        """Écritures triées par date, puis par référence (équivalent du ``SORT`` Sheets)."""
        return tuple(sorted(self._ecritures, key=lambda e: (e.date, e.journal, e.reference)))

    def lignes_journal(self) -> list[tuple[date, str, Compte, str, Decimal, Decimal]]:
        """Lignes aplaties : Date, Journal, Compte, Libellé, Débit, Crédit."""
        plat: list[tuple[date, str, Compte, str, Decimal, Decimal]] = []
        for ecriture in self.journal:
            for ligne in ecriture.lignes:
                plat.append(
                    (
                        ecriture.date,
                        ecriture.journal,
                        ligne.compte,
                        ligne.libelle,
                        ligne.debit,
                        ligne.credit,
                    )
                )
        return plat

    def total_debit(self) -> Decimal:
        return sum((e.total_debit for e in self._ecritures), ZERO)

    def total_credit(self) -> Decimal:
        return sum((e.total_credit for e in self._ecritures), ZERO)

    def est_equilibre(self) -> bool:
        return self.total_debit() == self.total_credit()

    def _ecritures_filtrees(
        self,
        date_debut: date | None = None,
        date_fin: date | None = None,
    ) -> list[Ecriture]:
        selection: list[Ecriture] = []
        for ecriture in self._ecritures:
            if date_debut is not None and ecriture.date < date_debut:
                continue
            if date_fin is not None and ecriture.date > date_fin:
                continue
            selection.append(ecriture)
        return selection

    def soldes(
        self,
        date_debut: date | None = None,
        date_fin: date | None = None,
    ) -> dict[int, SoldeCompte]:
        """Soldes par numéro de compte sur la fenêtre de dates (bornes incluses)."""
        cumuls: dict[int, tuple[Decimal, Decimal]] = {}
        comptes: dict[int, Compte] = {}
        for ecriture in self._ecritures_filtrees(date_debut, date_fin):
            for ligne in ecriture.lignes:
                numero = ligne.compte.numero
                comptes[numero] = ligne.compte
                debit_cumul, credit_cumul = cumuls.get(numero, (ZERO, ZERO))
                cumuls[numero] = (debit_cumul + ligne.debit, credit_cumul + ligne.credit)
        return {
            numero: SoldeCompte(
                compte=comptes[numero],
                total_debit=debit,
                total_credit=credit,
            )
            for numero, (debit, credit) in sorted(cumuls.items())
        }

    def solde_compte(
        self,
        numero: int,
        date_debut: date | None = None,
        date_fin: date | None = None,
    ) -> SoldeCompte:
        """Solde d'un compte du plan, même s'il n'a pas encore bougé (soldes à 0)."""
        existants = self.soldes(date_debut, date_fin)
        if numero in existants:
            return existants[numero]
        return SoldeCompte(compte=get_compte(numero), total_debit=ZERO, total_credit=ZERO)

    def balance(self, date_debut: date, date_fin: date) -> list[LigneBalance]:
        """Balance pédagogique : clôture, période, avant-période.

        La somme des soldes de clôture doit rester nulle (partie double).
        """
        if date_debut > date_fin:
            raise ValueError("La date de début de période ne peut pas être postérieure à la fin.")
        cloture = self.soldes(date_fin=date_fin)
        periode = self.soldes(date_debut=date_debut, date_fin=date_fin)
        numeros = sorted(set(cloture) | set(periode))
        lignes: list[LigneBalance] = []
        for numero in numeros:
            compte = cloture[numero].compte if numero in cloture else periode[numero].compte
            solde_cloture = cloture[numero].solde_net if numero in cloture else ZERO
            mouvements = periode[numero].solde_net if numero in periode else ZERO
            lignes.append(
                LigneBalance(
                    compte=compte,
                    solde_cloture=solde_cloture,
                    mouvements_periode=mouvements,
                    avant_periode=solde_cloture - mouvements,
                )
            )
        return lignes

    def somme_soldes_cloture(self, date_fin: date) -> Decimal:
        """Doit valoir 0 : contrôle vert de la balance."""
        return sum((solde.solde_net for solde in self.soldes(date_fin=date_fin).values()), ZERO)


# Alias pédagogique : le journal général est le même registre, lu chronologiquement.
JournalGeneral = GrandLivre


def ligne_debit(compte: int | Compte, libelle: str, montant: Decimal | int | str) -> LigneEcriture:
    return LigneEcriture.au_debit(compte, libelle, montant)


def ligne_credit(compte: int | Compte, libelle: str, montant: Decimal | int | str) -> LigneEcriture:
    return LigneEcriture.au_credit(compte, libelle, montant)
