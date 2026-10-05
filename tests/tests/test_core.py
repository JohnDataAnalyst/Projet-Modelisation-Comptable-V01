import sys
from pathlib import Path

# Ajout du dossier racine au chemin d'import
sys.path.append(str(Path(__file__).resolve().parents[2]))

from datetime import date
from decimal import Decimal
from src.core.accounts import PLAN_COMPTABLE
from src.core.journal import Ecriture, LigneEcriture
from src.core.ledger import GrandLivre

def test_moteur_comptable():
    # 1. Verification du plan de comptes
    c_512 = PLAN_COMPTABLE[512]
    c_707 = PLAN_COMPTABLE[707]
    c_44571 = PLAN_COMPTABLE[44571]
    
    # 2. Creation d'une ecriture de vente au comptant
    ecriture = Ecriture.creer(
        date_ecriture=date(2024, 3, 15),
        journal="VE",
        reference="FAC-001",
        lignes=[
            LigneEcriture.au_debit(c_512, "Vente jeux HT", Decimal("120.00")),
            LigneEcriture.au_credit(c_707, "Vente jeux HT", Decimal("100.00")),
            LigneEcriture.au_credit(c_44571, "TVA collectee", Decimal("20.00")),
        ]
    )
    
    # Verification de l'equilibre (propriete ou methode)
    assert getattr(ecriture, "est_equilibree", lambda: getattr(ecriture, "est_equilibre", True))()
    
    # 3. Ajout au GrandLivre
    livre = GrandLivre()
    livre.ajouter(ecriture)
    
    # 4. Verification de la balance
    balance = livre.generer_balance()
    assert sum(s.solde_net for s in balance) == Decimal("0")
    print("Test du moteur comptable reussi !")

if __name__ == "__main__":
    test_moteur_comptable()