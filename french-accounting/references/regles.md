# Règles

Leçons générales tirées de l'exploitation d'un agent comptable dans une petite société commerciale
française. Chaque règle dit quoi faire et pourquoi. Là où le bon
traitement dépend de la société, la règle le dit : cette partie relève de la convention de
l'expert-comptable, pas de ce fichier.

## 1. Pas de facture, pas de TVA déduite

Toute écriture s'appuie sur une pièce justificative (PCG 1032-1) ; c'est vrai pour toutes les lignes.
La TVA ajoute un enjeu : le droit à déduction suppose de remplir des conditions de fond, d'exigibilité
et de justification. Pour une TVA française facturée par le fournisseur, cela passe par la détention
de la facture : sans elle, ne pas déduire ; l'obtenir, puis examiner avec l'expert-comptable les
régularisations possibles. Pour une prestation autoliquidée, vérifier les conditions de fond,
l'exigibilité et la déclaration de l'opération et de la TVA : l'absence de facture ne bloque pas, à
elle seule, la déduction, mais la pièce reste due au titre du PCG 1032-1. Graduer les pièces manquantes en conséquence (SKILL.md, étape 2).

Une devise étrangère ou une forme juridique comme `Inc.`, `LLC`, `Ltd`, `Corp.` dans le libellé
bancaire signale un fournisseur étranger, pas une absence de TVA : une prestation achetée hors de
France est souvent autoliquidée. Ces indices servent à orienter la vérification, jamais à décider du
traitement de TVA.

## 2. Le traitement de TVA : la nature de l'opération, puis l'adresse de l'entité qui facture

Le traitement dépend de la nature de l'opération (bien ou service), de sa territorialité, des
établissements concernés et des régimes particuliers. Pour les **prestations de services courantes
entre assujettis** (logiciels, abonnements, services en ligne), qui relèvent de la règle générale,
l'adresse de l'entité qui facture est l'indice principal. La lire **sur la facture**, pas sur le
libellé bancaire : une marque qu'on croit américaine peut facturer depuis l'Irlande, et inversement.
Le tableau ci-dessous ne vaut que pour ces prestations ; les achats de biens (acquisitions
intracommunautaires, importations) ont leurs propres règles.

| entité qui facture | ce qui se passe en général | ce que fait l'agent |
|---|---|---|
| France | TVA française sur la facture, déductible si la facture est conforme | comptabiliser le taux imprimé sur la facture |
| autre État membre de l'UE | pas de TVA sur la facture ; le preneur français autoliquide (TVA due et TVA déductible du même montant, neutre pour une société qui déduit intégralement) | comptabiliser avec le code d'autoliquidation du logiciel prévu par la convention |
| hors UE | la TVA française est en général due par autoliquidation elle aussi ; une TVA étrangère imprimée sur la facture n'est **jamais** de la TVA déductible française | constater l'autoliquidation ; la convention précise les comptes et le paramétrage du logiciel |

La règle de droit (lieu de la prestation, autoliquidation) est la même pour tous ; les **comptes** et
le **paramétrage du logiciel** pour chaque cas sont la décision de l'expert-comptable. La demander
une fois, la consigner en convention, l'appliquer à tous les fournisseurs de la zone. Une adresse
illisible est une question, jamais une supposition.

Vérifier ce que le logiciel génère réellement pour chaque code de TVA (comptes mouvementés, montants)
et soumettre tout écart à l'expert-comptable au lieu de supposer.

## 3. Ne jamais écraser l'expert-comptable, ne jamais inventer

Les libellés, comptes et catégories de l'expert-comptable sont à lui. L'agent n'en écrase aucun, ne
crée ni fournisseur ni compte qui lui appartient, ne désarchive aucune pièce, ne valide aucune
période. Quand aucune convention ne couvre une ligne, la ligne est **bloquée** et devient une question
avec un compte proposé et l'article du PCG qui le fonde.

Une fois des conventions établies, l'agent peut comptabiliser sous convention, à condition que
**chaque** écriture figure dans un mail de contrôle groupé envoyé à l'expert-comptable. Les erreurs
se corrigent à la main, et la correction devient une convention corrigée (une nouvelle ligne, même
clé) pour que l'erreur ne se reproduise pas.

## 4. Les conventions sont des données

Une convention est un enregistrement : une clé, un fournisseur (tel que nommé dans le logiciel), un
compte de charge, un traitement de TVA, le pays de l'entité qui facture, qui a décidé, quand, et les
mots de l'expert-comptable qui la fondent. En ajout seul ; un changement est un nouvel
enregistrement avec la même clé. Faire une fois la correspondance entre les numéros complétés de
l'expert-comptable et ceux du logiciel (`613500000` → `6135`) et garder les deux.

Un juste milieu utile, une fois la confiance établie : pour un **nouveau fournisseur**, l'agent peut
enregistrer lui-même la convention quand la règle de TVA par zone tranche la TVA et qu'un
fournisseur comparable tranche le compte, puis comptabiliser **et** prévenir l'expert-comptable dans
le récapitulatif de contrôle suivant. Une adresse illisible ou une nature de dépense sans précédent
part toujours d'abord à l'expert-comptable.

## 5. Paiements, factures et dates

- **Facture reçue avant le débit** : comptabiliser la facture contre le fournisseur (401), soldé à
  l'arrivée du débit, sans attendre le paiement. La charge se rattache à la période de livraison ou
  de prestation ; constater les régularisations nécessaires à la clôture (486, 408). Le 408 ne sert
  qu'à une facture **non encore reçue** à la clôture.
- **Paiement sans facture** : attendre en compte d'attente (471) et relancer le dirigeant jusqu'à
  l'arrivée de la pièce. Le 471 doit être vide à la clôture (PCG 1214-47).
- **Les avoirs se comptabilisent toujours** et se relient à leur remboursement. Un remboursement
  fournisseur va au compte du fournisseur, jamais à un associé ni en attente, et l'avoir
  correspondant se réclame.
- **Un remboursement rattachable à une vente identifiée** se rattache à l'opération d'origine et en
  corrige aussi la TVA.
- **Un débit et un remboursement de même montant à quelques jours** chez un même fournisseur :
  passer les deux au compte fournisseur et les lettrer ensemble ; ne pas les compenser.
- **Les fournisseurs en facturation électronique** peuvent déposer leurs factures directement dans le
  logiciel comptable plusieurs jours après le débit. Leur laisser un délai de grâce (un mois) avant
  de réclamer, puis signaler que la facture électronique annoncée n'est jamais arrivée.

## 6. Les associés et les premiers mois de la société

- L'argent qu'un associé apporte est une avance en compte courant (455), sauf apport en capital
  (456) : l'expert-comptable les passe à la main ; l'agent n'y touche pas.
- Les dépenses payées à titre personnel pour le compte de la société, notamment avant son
  immatriculation, et les opérations antérieures reprises par la société relèvent en général du
  compte courant de l'associé (455). L'expert-comptable décide et comptabilise.
- Une facture établie au nom personnel du dirigeant pose un problème de déduction de TVA : la
  signaler à l'expert-comptable et en demander la rectification au fournisseur, sans conclure seul.
- Aucune écriture ne peut être datée avant le début du premier exercice : dater les écritures
  d'ouverture de son premier jour.

## 7. Prestataires de paiement et places de marché

- Qualifier d'abord le modèle économique : vente pour son compte, commissions d'intermédiaire,
  abonnement. La TVA sur des commissions se calcule sur la commission **brute**, pas sur le versement
  net. Le compte de produit dépend de cette qualification, validée par l'expert-comptable (706 pour
  l'activité principale de services, 7082 pour des commissions accessoires).
- Un versement de prestataire de paiement est un montant **net** qui mêle ventes, commissions, frais,
  remboursements et parfois des virements depuis la banque de la société. Ne jamais comptabiliser la
  ligne bancaire en chiffre d'affaires.
- Comptabiliser le mois par une opération diverse (OD) construite depuis **l'API du prestataire**
  (clé en lecture seule), datée du dernier jour du mois : créance sur le prestataire (411), produit
  HT et TVA collectée (44571), frais (627), rechargements internes par 58. Le solde comptable du
  compte du prestataire doit correspondre au solde justifié chez le prestataire ; lettrer les
  opérations effectivement dénouées.
- **Rapprocher au centime** avec la banque avant d'écrire ; au moindre écart, ne rien écrire et le
  signaler. Une ligne agrégée peut cacher un rechargement depuis la banque de la société.
- Les écritures issues de la banque sont souvent impossibles à modifier via l'API du logiciel, et
  rattacher un client à une ligne bancaire peut ne pas déplacer sa contrepartie : reclasser par OD.

## 8. Indemnités kilométriques, péages et stationnement

- **L'indemnité kilométrique** suit le barème officiel de l'année (BOFiP `BOI-BAREME-000001`), lu
  pour l'année en cours, jamais de mémoire, et se calcule sur le kilométrage professionnel annuel de
  chaque véhicule. Compte 6251 ; contrepartie 455 pour un dirigeant associé,
  421 pour un salarié.
- Aucun tiers ne la facture, mais la société **se doit une pièce** : un état de frais kilométriques
  avec date, motif professionnel, trajet, kilomètres, puissance fiscale et barème appliqué. Sans lui,
  le versement peut être requalifié en rémunération.
- Le barème couvre déjà carburant, assurance, entretien, pneumatiques et dépréciation. Rembourser l'un
  d'eux en plus déduit deux fois la même charge : signaler tout débit de ce type pour le même véhicule
  et les mêmes déplacements déjà indemnisés.
- **Péages et stationnement ne sont pas couverts** par le barème : remboursés au réel, sur facture
  d'un tiers, avec une TVA dont l'expert-comptable confirme la déductibilité.

## 9. Les chiffres ne viennent jamais de la mémoire

Taux de TVA, barème kilométrique, seuils : lus à la source officielle pour l'année, ou demandés. Le
PCG donne le compte, pas le montant.

## 10. Une consigne seule ne garantit pas le respect d'une règle

Toute règle qui compte (pas de destinataire par défaut, le délai minimal entre deux mails,
l'avertissement IA sur chaque mail, aucune écriture sans convention) doit être imposée **dans le
code, au seul point de passage**, et non décrite dans une consigne que l'agent peut contourner. La
prose explique pourquoi ; le code rend le mauvais chemin indisponible.
