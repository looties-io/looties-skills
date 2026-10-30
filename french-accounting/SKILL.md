---
name: french-accounting
description: "À utiliser quand un agent tient, révise ou prépare la comptabilité d'une société française selon le Plan comptable général (PCG) : qualifier des lignes bancaires, choisir un compte PCG, réclamer un justificatif manquant, savoir si la TVA est récupérable, rapprocher factures et transactions, comptabiliser un remboursement, un avoir, un virement interne, un compte courant d'associé, des indemnités kilométriques ou les versements d'un prestataire de paiement, ou écrire à l'expert-comptable. Aussi pour mettre en place un agent comptable autonome avec accès mail, qui gagne ses droits d'écriture par paliers sous le contrôle d'un expert-comptable. Déclencheurs : \"quel compte pour\", \"compte PCG\", \"justificatif manquant\", \"TVA récupérable\", \"rapprochement bancaire\", \"avoir\", \"virement interne\", \"compte courant d'associé\", \"frais kilométriques\", \"versement Stripe\", \"agent comptable\". Pas pour les IFRS, les comptes consolidés, la paie, les déclarations fiscales, ni la tenue des comptes d'autrui."
license: MIT AND CC-BY-4.0
metadata:
  author: Looties
  version: "1.0.0"
---

# Comptabilité française (PCG)

Un agent qui tient une comptabilité française n'est utile que tant qu'il n'invente aucun jugement.
Trois choses le garantissent. Tout numéro de compte se lit dans le PCG, jamais de mémoire. Tout
jugement qui revient à l'expert-comptable lui est demandé, consigné une fois sous forme de
convention, puis appliqué. Et les droits d'écriture de l'agent se gagnent par paliers, sous le
contrôle de l'expert-comptable, au lieu d'être accordés le premier jour.

Ce skill rassemble la méthode et les règles tirées de plusieurs mois d'exploitation d'un tel agent
sur une vraie société. Les textes qui font foi (le PCG et son plan de comptes) sont téléchargés chez
leur éditeur par `scripts/fetch-sources.sh`. Le script télécharge la version configurée : vérifier
qu'elle est toujours la version consolidée en vigueur, et la renouveler chaque année (`PCG_URL`,
`FORCE=1`).

> **Périmètre et responsabilité.** Ce skill aide un dirigeant à tenir la comptabilité de **sa propre
> société**, sous la supervision d'un expert-comptable. En France, tenir ou réviser la comptabilité
> d'un tiers à titre de prestation est réservé à la profession (ordonnance n° 45-2138, art. 2 et 20).
> L'agent propose, consigne et applique ; l'expert-comptable décide. Rien ici n'est un conseil
> fiscal ou juridique.

## Hiérarchie des sources (jamais inversée)

1. **Le PCG** (règlement ANC n° 2014-03, version consolidée en vigueur) et **son plan de comptes**
   (art. 1121-1). Source absolue de vérité pour tout numéro de compte et toute règle
   d'enregistrement. Quand quoi que ce soit le contredit, le PCG l'emporte, sans discussion.
2. **Les réponses écrites de l'expert-comptable**, consignées en conventions. Elles choisissent
   *à l'intérieur* du PCG (quelle subdivision, quel traitement de TVA pour ce fournisseur) ; elles ne
   le contredisent jamais.
3. **La décision d'un humain sur une ligne précise.** Elle prime sur tout motif pour cette seule
   ligne et ne se généralise jamais.
4. **Les cours** (cours universitaires de comptabilité générale française). Savoir général, pour
   comprendre et expliquer, jamais pour contredire 1 à 3.
5. **Le raisonnement de l'agent.** En dernier. Il produit des propositions, jamais des écritures.

Les chiffres fiscaux (taux de TVA, barème kilométrique, seuils) **ne sont pas** dans le PCG. Ils
changent chaque année et se lisent à leur source officielle ou se demandent, **jamais de mémoire**.

## Aide-mémoire

| Vous devez | Aller à |
|---|---|
| Installer le PCG en local et trouver un article | Étape 0, [references/sources.md](references/sources.md) |
| Savoir sur quel compte va une ligne | Étape 4, [references/pcg-essentiel.md](references/pcg-essentiel.md) |
| Savoir si une ligne a besoin d'une pièce | Étape 1, [references/sans-justificatif.md](references/sans-justificatif.md) |
| Savoir à quel point une pièce manquante est urgente | Étape 2 |
| Comptabiliser TVA, remboursement, virement, indemnités kilométriques, versement d'un prestataire de paiement | [references/regles.md](references/regles.md) |
| Écrire à l'expert-comptable sans lui faire perdre son temps | Étape 6 |
| Faire tourner l'agent en autonomie avec accès mail | [references/onboarding.md](references/onboarding.md) |

## Étapes

### 0. Avoir les sources sur le disque

Lancer `scripts/fetch-sources.sh` (cible par défaut `~/.accounting-sources`). Il télécharge le PCG
consolidé auprès de l'Autorité des normes comptables et en extrait le texte avec `pdftotext`, si bien
que `grep -n "Art. 1214-44" ~/.accounting-sources/pcg/PCG.txt` répond à « que dit le PCG » en un
appel. Le plan de comptes est l'article 1121-1 du même texte. Les cours facultatifs sont listés dans
[references/sources.md](references/sources.md).

**Pourquoi :** un agent qui cite « compte 6xxx » de mémoire a raison la plupart du temps, et tort
précisément dans les cas qui comptent. Lire l'article coûte un grep.

### 1. Ranger chaque ligne bancaire dans une catégorie

Partir de la liste des transactions bancaires sans justificatif dans le logiciel comptable, pas de la boîte
mail. Cette liste est finie et sait dire « terminé » ; une boîte mail est un flux sans fin.

| catégorie | sens | se clôt par |
|---|---|---|
| **rapprochable** | la pièce existe et a été trouvée | joindre et rapprocher |
| **à réclamer** | la pièce existe et n'a pas été trouvée | un humain, ou une recherche plus large |
| **pièce interne** | aucun tiers ne la facturera, mais la société se doit une pièce (état de frais kilométriques, note de frais) | la société la rédige |
| **sans facture attendue** | aucune facture fournisseur n'existera ; le justificatif est le relevé, le bulletin de paie ou la déclaration (intérêts, virement interne, frais bancaires, paie, prélèvement fiscal) | un compte fixé par convention, et le justificatif pertinent conservé |

Toute écriture s'appuie sur une pièce justificative (PCG 1032-1) : « sans facture attendue » ne veut
pas dire sans justificatif. Dans le doute, une ligne reste **à réclamer**. Une erreur dans ce sens
coûte une ligne de plus à lire ; une ligne rangée à tort **sans facture attendue** est un
justificatif manquant que personne ne voit avant la clôture.

### 2. Graduer ce qui manque selon la TVA en jeu

Toutes les pièces manquantes sont dues, mais toutes ne coûtent pas la même chose. La déduction d'une
TVA française facturée par le fournisseur (4456) suppose de détenir la facture. Donc :

- **critique** : un débit vers un fournisseur facturant de la TVA française, au-dessus d'un petit
  seuil choisi par le dirigeant (5 EUR a bien fonctionné). En tête du rapport.
- **à suivre** : les autres pièces manquantes (pas de TVA française facturée, ou montant sous le
  seuil). Listées, sans alerte. Une devise étrangère ou un fournisseur hors UE ne veut pas dire
  « pas de TVA » : vérifier si l'opération est autoliquidée, et que l'autoliquidation est bien
  constatée et déclarée.
- **rien à réclamer** : la catégorie sans facture attendue. Comptée, son justificatif conservé.

Le seuil est un confort du dirigeant, pas une règle comptable : une ligne à 3 EUR porte de la TVA en
droit exactement comme une ligne à 1 000 EUR. Une pièce obtenue tard peut souvent régulariser une
déduction ; c'est à voir avec l'expert-comptable, pas à présumer.

### 3. Rapprocher les pièces par l'arithmétique

Une pièce correspond à une ligne bancaire quand **le montant concorde au centime près** et que la
date bancaire tombe dans une fenêtre autour de la date de la pièce (quelques jours avant, environ
deux semaines après). Le domaine de l'expéditeur est un bonus, jamais un substitut. **Deux candidats
à égalité, c'est aucun des deux** : joindre la mauvaise facture est une erreur silencieuse qu'on
découvre des mois plus tard. Dédoublonner auprès du logiciel comptable (en enregistrant
l'identifiant du message comme référence externe) plutôt que dans un fichier d'état local qui peut
être effacé.

### 4. Qualifier la ligne : compte et code TVA

1. Existe-t-il une **décision** pour cette ligne précise ? L'appliquer.
2. Existe-t-il une **convention** pour ce fournisseur ou ce motif ? Appliquer exactement son compte
   et son code TVA.
3. Sinon, la ligne est **bloquée** et devient une question à l'expert-comptable, avec un compte
   proposé, lu dans le PCG, et l'article qui le fonde. Rien ne se comptabilise sur une supposition.

Le traitement de TVA dépend de la nature de l'opération (bien ou service), de sa territorialité et
des régimes particuliers. Pour les prestations de services courantes entre assujettis, **l'adresse
de l'entité qui facture, lue sur la facture** (pas le libellé bancaire) est l'indice principal :
France, autre État membre de l'UE, ou hors UE. La façon de comptabiliser chaque cas revient à
l'expert-comptable et se consigne une fois en convention (voir
[references/regles.md](references/regles.md)).

### 5. N'écrire que ce que la phase en cours autorise

Les droits de l'agent grandissent par phases (observer, demander, proposer, comptabiliser sous
convention) ; voir [references/onboarding.md](references/onboarding.md). Dans toutes les phases,
**jamais** : écraser un libellé ou un compte posé par l'expert-comptable, inventer un code TVA, créer
ou désarchiver ce qui appartient à l'expert-comptable, toucher aux mouvements d'associés ou de capital
qu'il passe à la main, ni valider une période.

### 6. Parler aux humains sur des canaux séparés

| canal | à qui | contenu | cadence |
|---|---|---|---|
| relance | le dirigeant seul | pièces manquantes, rapprochements ambigus, erreurs techniques | au plus une fois par semaine |
| expertise | expert-comptable + dirigeant | quel compte, quelle convention, améliorations | seulement quand l'ensemble des **questions** ouvertes change, et pas plus d'une fois tous les quelques jours |
| contrôle | expert-comptable + dirigeant | un récapitulatif de toutes les écritures passées sous convention | un mail par lot, au plus quotidien |

**Il n'y a pas de destinataire par défaut** : un défaut aurait pour effet d'écrire à
l'expert-comptable pour un ticket de caisse manquant. Les pièces manquantes, c'est le travail du
dirigeant, jamais celui de l'expert-comptable. Chaque mail indique qu'il a été rédigé par une IA.
Placer le délai minimal entre deux envois au seul point de passage de tous les envois, pour qu'aucun
appelant (y compris un autre agent) ne puisse le contourner.

### 7. Consigner chaque échange dans un journal

Chaque mail envoyé (échecs compris) et chaque réponse reçue est ajouté à un journal d'échange, jamais
modifié. Avant d'écrire à l'expert-comptable, l'agent le relit : une question déjà tranchée ne se
repose pas, et une réponse devient une convention.

## Pièges fréquents

- **Une surveillance des mails sur un domaine entier.** Un domaine regroupe d'autres personnes que
  l'expert-comptable ; un message sans rapport peut être pris pour le sien, et l'agent répondre ou
  recopier un fil qui ne le concerne pas. Limiter la surveillance aux **adresses autorisées** et aux
  **fils ouverts par l'agent**.
- **Une décision ponctuelle devenue un motif.** « Cet achat chez le magasin X était personnel » est
  devenu une expression régulière sur X, qui a fait taire l'achat suivant, légitime, TVA comprise.
  Les décisions vivent dans des données, indexées par identifiant de transaction ; seuls les motifs
  observés à répétition deviennent des règles.
- **Des virements internes libellés différemment de chaque côté.** « Dépôt », « Retrait », le nom de
  la contrepartie : aucun motif de libellé n'attrapait tous les mouvements, et un critère trop large
  aurait avalé de vrais retraits d'espèces. Rapprocher sur **même jour, montants égaux et opposés, deux
  comptes détenus par la société**.
- **Un versement de prestataire de paiement cachait un rechargement.** Une ligne bancaire agrégée
  mêlait commissions et rechargement depuis la banque de la société. Rapprocher chaque mois **au
  centime** depuis l'API du prestataire avant d'écrire quoi que ce soit ; au moindre écart, ne rien
  écrire et signaler.
- **TVA enregistrée à zéro.** Un premier circuit d'import enregistrait des factures à TVA française
  avec une TVA nulle, ce qui perd la déduction. Ventiler le TTC en HT + TVA dès que la convention
  indique un taux français.
- **Des numéros de compte complétés de zéros.** L'expert-comptable écrit `613500000`, le logiciel
  contient `6135`. Faire la correspondance une fois dans la convention, telle quelle, et garder
  les deux.
- **Les écritures issues de la banque sont souvent en lecture seule via l'API.** Reclasser par une
  opération diverse (OD) au lieu de tenter de les modifier.
- **Les fournisseurs en facturation électronique livrent tard.** Certaines factures arrivent dans le
  logiciel comptable plusieurs jours après le débit, sans passer par le mail. Leur laisser un délai
  de grâce avant de réclamer, puis signaler.
- **Une description de skill avec `: ` non protégé** a cassé le YAML, et l'environnement a ignoré le
  skill sans rien dire. Mettre les descriptions entre guillemets.

## Vérification

Le travail est terminé quand :

- chaque numéro de compte écrit ou proposé a été lu dans le texte local du PCG (article cité) ;
- chaque écriture découle d'une convention ou d'une décision, et figure dans un récapitulatif de
  contrôle envoyé ;
- chaque écart restant est dans une catégorie avec un motif, et chaque ligne critique figure dans une
  relance ;
- le journal contient chaque mail et chaque réponse de la période, et aucune question du dernier
  mail d'expertise n'y avait déjà été tranchée ;
- aucun chiffre fiscal (taux, barème, seuil) n'a été écrit sans sa source officielle.
