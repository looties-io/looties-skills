# L'essentiel du PCG

Ce qu'un agent comptable doit savoir par cœur, avec l'article à ouvrir quand ça compte. C'est une
carte d'orientation rédigée pour ce skill, **pas** un substitut au texte : avant d'écrire ou de
proposer un compte, le lire dans le PCG local (`scripts/fetch-sources.sh`).

## Les principes, et ce qu'ils interdisent en pratique

| principe | PCG | conséquence pour l'agent |
|---|---|---|
| Image fidèle | 121-1 | ne jamais arranger une ligne pour qu'un total « tombe juste » |
| Régularité et sincérité | 121-3 | quand on ne sait pas, on le dit et on demande ; on n'imagine jamais |
| Prudence | 121-4 | pas de TVA déductible présumée sans facture ; les charges probables se comptabilisent, les produits incertains non |
| Permanence des méthodes | 121-5 | une même nature de ligne se qualifie de la même façon d'un mois à l'autre ; un changement est une décision, consignée |
| Indépendance des exercices | Livre I | c'est le fait générateur (livraison, prestation) qui rattache une opération à un exercice, pas la date de paiement |
| Non-compensation | 112-2, 1011-5 | un débit et un crédit de même montant ne s'annulent jamais « par commodité » ; une subdivision de 512 par compte bancaire |
| Intangibilité du bilan d'ouverture | 112-2 | rien ne se corrige « avant » l'ouverture |
| Coût historique | Livre I | les actifs entrent au coût d'acquisition (prix et frais accessoires) |

## Les articles qu'un agent comptable cite le plus

| article | ce qu'il dit | pourquoi il compte |
|---|---|---|
| **1021-1** | livre-journal et grand livre sont obligatoires | toute écriture aboutit dans un journal |
| **1032-1** | tout enregistrement précise l'origine, le contenu, l'imputation et **les références de la pièce justificative** | la raison d'être d'un agent comptable |
| **1032-2** | chaque écriture s'appuie sur une pièce datée ; les opérations de même nature, même lieu, même jour peuvent être récapitulées sur une pièce unique | autorise une pièce récapitulative, sous ces conditions ; ce n'est pas une dispense pour les petits montants |
| **1011-5** | plan de comptes conforme à 1121-1 ; **la compensation des comptes est interdite** | |
| **1121-1** | le plan de comptes | la nomenclature où lire les numéros |
| **1131-1 à 1131-4** | règles de codification | pour lire un numéro qu'on ne connaît pas (ci-dessous) |
| **1214-40** | comptes fournisseurs : 401 Fournisseurs, 408 Factures non parvenues, 409 Fournisseurs débiteurs | un achat dont la facture manque à la clôture passe par 408 |
| **1214-44** | comptes de l'État : 4456 TVA déductible (une créance), 4457 TVA collectée (une dette), 4455 TVA à décaisser ; autoliquidation = deux écritures de même montant en TVA déductible et collectée | fonde la règle « pas de facture, pas de TVA récupérée » |
| **1214-45** | 455 Associés - Comptes courants ; 456 Opérations sur le capital | l'argent qu'un associé apporte ou retire |
| **1214-47** | 471 à 473 comptes d'attente : exceptionnels, soldés au plus vite, jamais laissés à la clôture | là où attend un paiement sans sa pièce |
| **1215-51** | 512 Banques : une subdivision par compte bancaire | |
| **1215-58** | 58 Virements internes : compte de passage, soldé au terme de l'opération | les mouvements entre comptes de la société |
| **611-1 et suivants** | solutions informatiques : quand un logiciel est une charge et quand c'est un actif | abonnements SaaS contre logiciel développé |

## Lire un numéro de compte qu'on ne connaît pas

- **1131-1** : huit classes de comptes à deux chiffres ; toute subdivision est permise si son numéro
  commence par celui du compte qu'elle subdivise.
- **1131-2** : un zéro terminal signifie un compte de regroupement ou global.
- **1131-3** : dans les comptes à deux chiffres, les terminaisons 1 à 8 regroupent ; 28
  (amortissements) fonctionne en sens contraire.
- **1131-4** : dans les comptes de bilan à deux chiffres, la terminaison 9 identifie les
  dépréciations (classes 2 à 5) ; **dans les comptes à trois chiffres et plus, la terminaison 9 est
  réservée aux opérations de sens contraire** du compte parent (par exemple 409, 419). Un sous-compte
  de charge ordinaire terminé par 9 occupe un emplacement réservé à un compte de sens inverse : à
  signaler à l'expert-comptable si on en trouve un.

## Les comptes qui reviennent chaque semaine (plan 2026)

Vérifier chacun dans l'art. 1121-1 avant usage ; le plan de la société ajoute ses subdivisions. La
colonne « usage courant » est une pratique répandue, pas une règle du PCG : là où plusieurs comptes
se défendent (un SaaS peut se justifier sur plus d'un), la convention de l'expert-comptable tranche.

| compte | intitulé ANC | usage courant |
|---|---|---|
| 401 / 408 / 409 | Fournisseurs / Factures non parvenues / Fournisseurs débiteurs | factures fournisseurs, factures manquantes à la clôture, remboursements fournisseurs à recevoir |
| 411 / 419 | Clients / Clients créditeurs | créances clients, un prestataire de paiement traité comme client |
| 421 | Personnel - Rémunérations dues | notes de frais des salariés |
| 4452 | TVA due intracommunautaire | TVA autoliquidée sur les achats dans l'UE |
| 44551 | TVA à décaisser | |
| 44562 / 44566 | TVA sur immobilisations / sur autres biens et services | TVA déductible |
| 44571 | TVA collectée | TVA sur ventes ou commissions |
| 455 / 4551 | Associés - Comptes courants | avances d'associés, dépenses personnelles payées par la société |
| 456 / 4561 | Associés - Opérations sur le capital / Comptes d'apport | apports en capital |
| 471 à 473 | Comptes d'attente | paiement sans sa pièce, provisoirement |
| 486 / 487 | Charges / Produits constatés d'avance | rattachement des abonnements annuels |
| 512 | Banques | une subdivision par compte |
| 58 | Virements internes | virements entre comptes de la société |
| 2183 / 205 | Matériel informatique / Concessions, licences, solutions informatiques | immobilisations : matériel, logiciels |
| 6135 | Locations mobilières | SaaS et logiciels hébergés utilisés comme service |
| 616 | Primes d'assurances | |
| 6226 | Honoraires | expert-comptable, avocat |
| 6231 | Annonces et insertions | publicité |
| 6242 | Transports sur ventes | expéditions aux clients |
| 6251 | Voyages et déplacements | déplacements, indemnités kilométriques, péages, stationnement |
| 6257 | Réceptions | |
| 626 | Frais postaux et de télécommunications | |
| 627 | Services bancaires et assimilés | frais bancaires et de prestataire de paiement |
| 6281 | Concours divers (cotisations) | adhésions |
| 641 / 645 | Rémunérations du personnel / Cotisations de sécurité sociale | paie (depuis le bulletin) |
| 706 | Prestations de services | chiffre d'affaires de services |
| 7082 | Commissions et courtages | commissions accessoires (activité principale de services : 706), selon la qualification validée |
| 768 | Autres produits financiers | intérêts d'un compte d'épargne ou de trésorerie |
