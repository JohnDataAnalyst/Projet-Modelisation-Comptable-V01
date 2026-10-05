"""Référentiel des comptes (PCG français) du magasin de jeux vidéo.

Règle PCG : le premier chiffre du numéro de compte désigne la classe
(1 capitaux, 2 immobilisations, 3 stocks, 4 tiers, 5 financiers,
6 charges, 7 produits). La destination oriente le compte vers le
bilan (classes 1 à 5) ou le compte de résultat (classes 6 et 7).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Destination(str, Enum):
    """Affectation du compte aux états financiers (onglet 01-Plan comptable)."""

    BILAN_ACTIF = "Bilan – Actif"
    BILAN_PASSIF = "Bilan – Passif"
    CR_CHARGES = "CR – Charges"
    CR_PRODUITS = "CR – Produits"


@dataclass(frozen=True)
class Compte:
    """Compte du plan comptable.

    Le numéro est un entier (contrainte historique Sheets : ``RECHERCHEV``
    échoue si le compte est stocké en texte).
    """

    numero: int
    libelle: str
    destination: Destination

    @property
    def classe(self) -> int:
        """Classe PCG : premier chiffre du numéro de compte."""
        return int(str(self.numero)[0])

    def __post_init__(self) -> None:
        if self.numero <= 0:
            raise ValueError("Le numéro de compte doit être un entier strictement positif.")
        if not self.libelle.strip():
            raise ValueError("Le libellé du compte ne peut pas être vide.")
        classe = int(str(self.numero)[0])
        if classe not in range(1, 8):
            raise ValueError(
                f"Classe {classe} invalide pour le compte {self.numero} "
                "(le PCG n'utilise que les classes 1 à 7 en comptabilité générale)."
            )


def _compte(numero: int, libelle: str, destination: Destination) -> Compte:
    return Compte(numero=numero, libelle=libelle, destination=destination)


# Plan utilisé dans le modèle pédagogique (§7 du document de contexte),
# y compris les comptes prévus par la feuille de route (TVA, salaires, caisse…).
PLAN_COMPTABLE: dict[int, Compte] = {
    c.numero: c
    for c in (
        # Classe 1 — Capitaux (passif)
        _compte(1013, "Capital souscrit, appelé, versé", Destination.BILAN_PASSIF),
        _compte(108, "Compte de l'exploitant", Destination.BILAN_PASSIF),
        _compte(120, "Résultat de l'exercice (bénéfice)", Destination.BILAN_PASSIF),
        _compte(131, "Subventions d'investissement", Destination.BILAN_PASSIF),
        _compte(164, "Emprunts auprès des établissements de crédit", Destination.BILAN_PASSIF),
        # Classe 2 — Immobilisations (actif ; 28 = amortissements, contra-actif)
        _compte(2135, "Installations générales, agencements, aménagements des constructions", Destination.BILAN_ACTIF),
        _compte(2181, "Installations générales, agencements, aménagements divers", Destination.BILAN_ACTIF),
        _compte(2183, "Matériel de bureau et matériel informatique", Destination.BILAN_ACTIF),
        _compte(2184, "Mobilier", Destination.BILAN_ACTIF),
        _compte(2188, "Autres immobilisations corporelles", Destination.BILAN_ACTIF),
        _compte(275, "Dépôts et cautionnements versés", Destination.BILAN_ACTIF),
        _compte(2818, "Amortissements des autres immobilisations corporelles", Destination.BILAN_ACTIF),
        # Classe 3 — Stocks (actif)
        _compte(37, "Stocks de marchandises", Destination.BILAN_ACTIF),
        # Classe 4 — Tiers
        _compte(401, "Fournisseurs", Destination.BILAN_PASSIF),
        _compte(404, "Fournisseurs d'immobilisations", Destination.BILAN_PASSIF),
        _compte(411, "Clients", Destination.BILAN_ACTIF),
        _compte(421, "Personnel - Rémunérations dues", Destination.BILAN_PASSIF),
        _compte(431, "Sécurité sociale", Destination.BILAN_PASSIF),
        _compte(437, "Autres organismes sociaux", Destination.BILAN_PASSIF),
        _compte(44551, "TVA à décaisser", Destination.BILAN_PASSIF),
        _compte(44562, "TVA déductible sur immobilisations", Destination.BILAN_ACTIF),
        _compte(44566, "TVA déductible sur autres biens et services", Destination.BILAN_ACTIF),
        _compte(44567, "Crédit de TVA à reporter", Destination.BILAN_ACTIF),
        _compte(44571, "TVA collectée", Destination.BILAN_PASSIF),
        # Classe 5 — Financiers (actif)
        _compte(512, "Banques", Destination.BILAN_ACTIF),
        _compte(530, "Caisse", Destination.BILAN_ACTIF),
        # Classe 6 — Charges (compte de résultat)
        _compte(6037, "Variation des stocks de marchandises", Destination.CR_CHARGES),
        _compte(6063, "Fournitures d'entretien et de petit équipement", Destination.CR_CHARGES),
        _compte(607, "Achats de marchandises", Destination.CR_CHARGES),
        _compte(613, "Locations", Destination.CR_CHARGES),
        _compte(614, "Charges locatives et de copropriété", Destination.CR_CHARGES),
        _compte(615, "Entretien et réparations", Destination.CR_CHARGES),
        _compte(616, "Primes d'assurances", Destination.CR_CHARGES),
        _compte(623, "Publicité, publications, relations publiques", Destination.CR_CHARGES),
        _compte(626, "Frais postaux et de télécommunications", Destination.CR_CHARGES),
        _compte(627, "Services bancaires et assimilés", Destination.CR_CHARGES),
        _compte(641, "Rémunérations du personnel", Destination.CR_CHARGES),
        _compte(645, "Charges de sécurité sociale et de prévoyance", Destination.CR_CHARGES),
        _compte(661, "Charges d'intérêts", Destination.CR_CHARGES),
        _compte(6811, "Dotations aux amortissements des immobilisations", Destination.CR_CHARGES),
        # Classe 7 — Produits (compte de résultat)
        _compte(706, "Prestations de services", Destination.CR_PRODUITS),
        _compte(707, "Ventes de marchandises", Destination.CR_PRODUITS),
    )
}


class CompteInconnu(KeyError):
    """Le numéro demandé n'existe pas dans le plan pédagogique."""


def get_compte(numero: int) -> Compte:
    """Retourne le compte du plan, ou lève ``CompteInconnu``."""
    try:
        return PLAN_COMPTABLE[numero]
    except KeyError as exc:
        raise CompteInconnu(
            f"Compte {numero} absent du plan comptable pédagogique."
        ) from exc
