# PROJET_MODELISATION_COMPTABLE_V01 — Contexte projet

> Document de contexte destiné à un assistant IA (Cursor). À lire avant toute modification.
> Les positions de cellules reflètent la version V02.01 (_21) ; à revérifier dans le fichier si une formule ne trouve pas sa cible.

---

## 1. Objectif

Modèle **Google Sheets** de la comptabilité d'un **magasin de jeux vidéo fictif** (ventes de jeux et de consoles, animations facturées, achats fournisseurs, immobilisations, financement).

But **pédagogique** : apprendre la comptabilité générale (niveau bac pro → BTS) puis le contrôle de gestion, en construisant soi-même toute la chaîne :

```
Saisies → Écritures → Journal → Balance → Compte de résultat / Bilan → Analyses
```

Tout est **automatique et piloté par deux dates** (début et fin de période) : changer les dates recalcule les statuts, les stocks, les amortissements, la balance, le CR et le bilan.

Le propriétaire apprend : **expliquer les notions comptables, pas seulement livrer des formules**.

---

## 2. Environnement technique (contraintes importantes)

- **Google Sheets, locale française** :
  - séparateur d'arguments `;` et décimales `,` ;
  - noms de fonctions en français : `SI`, `SIERREUR`, `SOMME.SI.ENS`, `RECHERCHEV`, `EQUIV`, `ARRONDI`, `ESTNUM`, `CNUM`, `SUPPRESPACE`, `GAUCHE`, `DROITE`, `LIGNES`, `FIN.MOIS`, `MOIS.DECALER`, `NO.SEMAINE.ISO`, `SOMMEPROD`, `VRAI` / `FAUX` ;
  - restent en anglais : `LET`, `LAMBDA`, `MAP`, `SCAN`, `REDUCE`, `FILTER`, `SORT`, `UNIQUE`, `VSTACK`, `HSTACK`, `CHOOSECOLS`, `CHOOSEROWS`, `SEQUENCE`, `ARRAYFORMULA`, `IMPORTRANGE`, `TO_TEXT`, `REGEXEXTRACT`.
- **Pièges déjà rencontrés (à ne pas reproduire)** :
  1. `TAKE` / `DROP` **n'existent pas** dans Sheets → utiliser `CHOOSEROWS(x; SEQUENCE(n))`.
  2. Les noms de variables `LET` / `LAMBDA` ne doivent **pas** ressembler à une cellule (`d0`, `c1`…) **ni** à une fonction FR (`jours`, `mois`, `nb`, `lignes`, `gauche`, `droite`…).
  3. Dans un `FILTER`, `VRAI > 0` **et** `FAUX > 0` renvoient VRAI → toujours forcer les masques en nombre : `masque*1>0`.
  4. Toute opération sur des colonnes entières (`a-b`, `x + SCAN(...)`) dans un `LET` doit être enveloppée dans `ARRAYFORMULA`, sinon seule la 1re ligne est calculée.
  5. `SOMME.SI.ENS` avec une **liste** de critères à l'intérieur d'un `MAP` ne vectorise pas → passer par des colonnes d'aide ligne à ligne.
  6. Les comptes du plan comptable doivent être des **nombres** (pas du texte), sinon `RECHERCHEV` échoue partout.
  7. Les formules longues se collent dans une cellule **vidée** (Suppr), jamais en éditant l'ancienne formule.
  8. Les sorties en *spill* ont besoin de cellules libres en dessous et à droite (`#REF!` sinon).

---

## 3. Onglets (V02)

| Onglet | Rôle | Structure |
|---|---|---|
| `00-Main dashboard` | **Dates de période** et graphiques | B2 = début, B3 = fin. Tous les onglets lisent ces dates en B1/B2. |
| `00.01-Suivi Hebdo` | Indicateurs hebdomadaires | En-têtes ligne 6 : Semaine, Date début, Date fin, Nbr jeux, Nbr consoles, CA total, CA marchandises, CA services, CA consoles, CA jeux, CA Nintendo / Sony / Microsoft, coût d'achat vendu, marge, taux de marque, taux de marge |
| `01-Plan comptable` | Référentiel des comptes | A Compte (nombre), B Intitulé, C Classe, D Destination (`Bilan – Actif`, `Bilan – Passif`, `CR – Charges`, `CR – Produits`) |
| `10_Ventes_Marchandises` | Saisie des ventes | En-têtes ligne 7, données ligne 8. Colonnes : Code, Date Facture, Produit, Quantité, Prix unitaire HT, Prix total HT, Tx TVA, Montant taxe, Prix TTC, Statut facture, Statut paiement, Stock restant, **M Coût au CUMP** |
| `11-Ventes services` | Animations facturées (706) | En-têtes ligne 6 : Code, Date facture, Service, Jours, PU, Prix total HT, Taux TVA, Montant taxe, Prix TTC, Condition paiement, Date paiement, Statut facture, Statut paiement |
| `20-Achat Marchandises` | Commandes fournisseurs (607) | En-têtes ligne 6 : Date commande, Produit, Quantité, Fournisseur, Code, Condition paiement, Prix achat unitaire HT, Montant ligne HT, Tx TVA, TVA, TTC, Date de paiement, Statut facture, Statut paiement, Nature |
| `21-Autres charges` | Charges externes (613, 623, 626, 6063…) | En-têtes ligne 11 : Date facture, Fournisseur, Libellé, Compte, Montant HT, Taux TVA, Condition paiement, TVA, TTC, Date de paiement, Statut facture, Statut paiement |
| `23-Immobilisations` | Investissements (21xx) | En-têtes ligne 11 : Date acquisition, Fournisseur, Bien, Compte, Condition paiement, Durée (ans), Montant HT, Taux TVA, TVA, TTC, Date de paiement, Statut facture, Statut paiement, Amort. avant période, Dotation période, Amort. cumulés, VNC |
| `24 - Plan amortissement` | Plan mensuel généré | Formule en A5 (en-têtes ligne 5, données ligne 6). Une ligne par bien et par mois : Bien, Compte, Début, Fin, Dotation du mois, Cumul, VNC, Statut, Date écriture, Dotation comptabilisée |
| `30-Stocks` | Stocks par produit | En-têtes ligne 8 : Fournisseur, Produit, Qté SI, Valeur SI, Qté achetée, Achats HT, Qté vendue, Stock final, CUMP, Valeur SF, Contrôle, Taux d'écoulement. F1 = SF total, F2 = SI total |
| `31_Gamme_Produits` | Catalogue | Fournisseur, Produit, Prix achat HT, Prix vente HT, TVA, TTC, Délai de paiement |
| `40-Financement` | Apports et emprunt | Apports : en-têtes ligne 11 (Compte, Date, Type, Tiers, Montant, Statut). Paramètres emprunt D32:D37. Échéancier : en-têtes ligne 42 |
| `59-Ecriture` | **Moteur d'écritures** (14 blocs) | Voir §4 |
| `60-Journal` | Journal général | En-têtes ligne 5 (Date, Journal, Compte, Intitulé, Libellé, Débit, Crédit), formule en A6 |
| `61-Tresorerie` | Trésorerie jour par jour | E1 = solde d'ouverture. En-têtes ligne 9 : B Date, C Encaissements, D Décaissements, E Flux net, F Solde, G Seuil=0, H Valeur du stock |
| `62-Balance` | Balance | En-têtes ligne 4 : Compte, Intitulé, Destination, Solde à la clôture, Mouvements de la période, Avant la période |
| `63-Compte de résultat` | CR en tableau (charges / produits face à face) | Formule en A9 |
| `64-Bilan` | Bilan en tableau (actif / passif face à face) | Formule en A9 |

---

## 4. Le moteur d'écritures (`59-Ecriture`)

Chaque flux génère ses écritures dans un **bloc de 7 colonnes** : `Date | Journal | Compte | Intitulé | Libellé | Débit | Crédit`.
- Titre en ligne 2, en-têtes en ligne 3, **formule en ligne 4**.
- Une colonne vide sépare deux blocs.

**Principe de chaque bloc** :
- `LET` + `LAMBDA col(nom)` qui retrouve les colonnes **par le nom de l'en-tête** (`EQUIV` sur la ligne d'en-têtes de la source) : déplacer une colonne dans la source ne casse rien ;
- `FILTER` sur le statut (« Facturé » / « Payé ») ;
- `LAMBDA ligne(compte; texte; débit; crédit)` qui construit une ligne d'écriture, avec l'intitulé repris du plan comptable ;
- `VSTACK` des lignes débit / crédit.

| N° | Bloc | Plage | Source | Écriture |
|---|---|---|---|---|
| 01 | Ventes de jeux | D4:J | 10_Ventes | 512 / 707 + 44571 (vente au comptant) |
| 02 | Factures d'animations | L4:R | 11-Ventes services | 411 / 706 + 44571 |
| 03 | Encaissements d'animations | T4:Z | 11-Ventes services | 512 / 411 |
| 04 | Factures d'achat | AB4:AH | 20-Achats | 607 + 44566 / 401 |
| 05 | Paiements fournisseurs | AJ4:AP | 20-Achats | 401 / 512 |
| 06 | (inutilisé) | AR4:AX | — | — |
| 07 | Apports | AZ4:BF | 40-Financement | 512 / 1013, 131, 164 |
| 08 | Échéances d'emprunt | BH4:BN | 40-Financement | 661 + 164 / 512 |
| 09 | Stocks ouverture / clôture | BP4:BV | 30-Stocks | 37 / 6037 (SI à début−1, annulation à début, SF à fin) |
| 10 | Factures de charges | BX4:CD | 21-Autres charges | 6xx + 44566 / 401 |
| 11 | Paiements des charges | CF4:CL | 21-Autres charges | 401 / 512 |
| 12 | Factures d'immobilisations | CN4:CT | 23-Immobilisations | 21xx + 44562 / 404 |
| 13 | Paiements d'immobilisations | CV4:DB | 23-Immobilisations | 404 / 512 |
| 14 | Dotations aux amortissements | DD4:DJ | 24 - Plan amortissement | 6811 / 2818 (une écriture par mois) |
| 15 | *(prévu)* Liquidation TVA | DL4:DR | 25-TVA | 44571 / 44566, 44562, 44551 ou 44567 |
| 16 | *(prévu)* Paiement TVA | DT4:DZ | 25-TVA | 44551 / 512 |

**Journal** (`60-Journal`!A6) : `SORT(FILTER(VSTACK(tous les blocs); date<>""); 1; 1)`. **Chaque nouveau bloc doit être ajouté au `VSTACK`**.

---

## 5. Règles de gestion

- **Période** : `début` et `fin` viennent du dashboard.
  - « Solde à la clôture » = cumul de toutes les écritures ≤ fin. C'est le bilan, la « photo ».
  - « Mouvements de la période » = écritures entre début et fin. C'est le CR, le « film ».
  - « Avant la période » = la différence entre les deux.
- **Statuts** : `Facturé` si date ≤ fin ; `Payé` si date de paiement ≤ fin. Seules les lignes facturées ou payées génèrent des écritures.
- **Conditions de paiement** : `AR` (comptant), sinon « N jours » ; le nombre est extrait par `REGEXEXTRACT`.
- **TVA** : comptabilité d'engagement (TVA à la facture). Collectée 44571, déductible biens et services 44566, sur immobilisations 44562.
- **Stocks** : inventaire intermittent en comptabilité (37 / 6037 à la clôture), valorisation au **CUMP HT**. Inventaire permanent pour le suivi (stock restant, valeur jour par jour).
  - Coût de sortie d'une vente = quantité × (Σ achats HT ≤ date ÷ Σ quantités achetées ≤ date).
- **Immobilisations** : seuil de 500 € HT. Amortissement linéaire au **prorata temporis jour**, base 365 jours, découpé par mois dans le plan d'amortissement.
- **Emprunt** : seuls les intérêts (661) sont une charge ; le remboursement du capital diminue 164.
- **CR et bilan** : lisent uniquement `62-Balance`, classent les comptes par classe / racine :
  - classes 6 / 7 au CR (exploitation, financier 66 / 76, exceptionnel 67 / 77, impôt 69) ;
  - classes 1 à 5 au bilan ;
  - le résultat est calculé et ajouté aux capitaux propres (antérieur + période).

## 6. Contrôles à garder verts

- Journal : total débit = total crédit.
- Balance : somme des soldes = 0.
- Bilan : total actif − total passif = 0.
- `30-Stocks` : SI + achats − (quantités vendues × CUMP) − SF = 0 ; SF = solde du compte 37.
- Trésorerie : solde final = solde du compte 512.
- Plan d'amortissement : Σ dotations comptabilisées = Σ amortissements cumulés de `23-Immobilisations`.

---

## 7. Plan comptable utilisé

1013, 131, 164 · 2135, 2183, 2184, 2188, 2818 · 37 · 401, 404, 411, 421, 431, 44562, 44566, 44571 · 512 · 6037, 6063, 607, 613, 616, 623, 626, 627, 641, 645, 661, 6811 · 706, 707.

À ajouter selon la feuille de route : 44551, 44567 (TVA), 2181 (agencements), 275 (dépôt de garantie), 614, 615, 530 (caisse), 437 (cotisations), 108 / 120 (résultat).

---

## 8. Feuille de route

1. **TVA** : onglet `25-TVA` (une ligne par mois : collectée, déductible B&S, déductible immos, crédit antérieur, solde, à payer / crédit reporté via `SCAN`), blocs 15 et 16.
2. **Salaires** : onglet `22-Salaires` (641, 645, 421, 431), blocs de paie et de paiement.
3. **Architecture en 3 couches**, chacune ne lisant que la précédente :
   - `PROJET_MODELISATION_COMPTABLE_V01 – 1 Saisie` : référentiels (gamme, plan comptable) + colonnes saisies uniquement.
   - `PROJET_MODELISATION_COMPTABLE_V01 – 2 Moteur` (protégé) : colonnes calculées en `ARRAYFORMULA`, stocks, amortissements, écritures, journal, balance, CR, bilan, TVA, trésorerie, et un onglet **`90-EXPORT`** de forme stable (balance mensuelle comptes × mois, ventes par mois × produit, paramètres).
   - `PROJET_MODELISATION_COMPTABLE_V01 – 3…5` Analyses, via `IMPORTRANGE` sur `90-EXPORT` uniquement :
     - **Analyse financière** : SIG, CAF, bilan fonctionnel (FRNG, BFR, TN), ratios ;
     - **Comptabilité de gestion** : charges fixes / variables (colonne « Comportement » dans le plan comptable), marge sur coût variable, seuil de rentabilité, point mort ; coût complet par centres d'analyse (Approvisionnement, Vente, Animation, Administration) ;
     - **Pilotage** : budgets, scénarios (pessimiste / central / optimiste), plan de trésorerie prévisionnel, écarts réel / budget (quantité, prix), tableau de bord avec clignotants.
   - **Non-régression** : avec les mêmes dates, la nouvelle version doit redonner exactement les mêmes totaux (journal, balance, résultat, bilan) que la V02.

---

## 9. Consignes pour l'assistant

- Respecter la syntaxe **Sheets FR** et les pièges du §2.
- Ne jamais déplacer de colonnes dans `59-Ecriture` ; un nouveau bloc = les 7 colonnes suivantes + ajout au `VSTACK` du journal.
- Retrouver les colonnes **par nom d'en-tête**, pas par lettre, dès que possible.
- Après chaque changement, donner les **valeurs de contrôle attendues** (§6).
- Expliquer la **notion comptable** derrière chaque formule, au niveau bac pro / BTS.
