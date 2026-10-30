# Guide de mise en service : faire tourner l'agent comptable

Le skill seul répond à des questions. Ce guide en fait un **agent** qui travaille sur votre
comptabilité chaque nuit, lit vos factures par mail, écrit à votre expert-comptable et gagne le droit
de passer des écritures. Ce n'est pas un paquet qui s'installe et s'oublie : il dépend de votre
logiciel comptable, de vos flux bancaires et de votre boîte mail. Vous le construisez avec Claude Code
ou Codex à partir de ce guide.

Comptez plusieurs semaines entre la lecture seule et la saisie sous le contrôle de l'expert-comptable.
C'est le bon rythme : l'essentiel de la valeur des premières semaines, ce sont les réponses de
l'expert-comptable.

## Avant de commencer

Il vous faut :

- un **expert-comptable** d'accord pour recevoir quelques mails d'une IA et y répondre (prévenez-le
  d'abord ; chaque mail dira qu'il a été rédigé par une IA) ;
- un logiciel comptable doté d'une **API** qui liste les transactions bancaires, les factures
  fournisseurs et les écritures (l'agent d'origine tournait sur l'un d'eux ; tout logiciel aux points
  d'accès comparables convient) ;
- un **libellé ou dossier mail** où arrivent les factures, et le droit de ne lire que celui-là ;
- une machine où une tâche planifiée peut tourner chaque nuit (un petit serveur, ou votre propre
  ordinateur) ;
- `scripts/fetch-sources.sh` lancé une fois, pour avoir le PCG sur le disque.

Identifiants : gardez chaque jeton dans des variables d'environnement ou un coffre à secrets, jamais
dans des fichiers que l'agent écrit ni dans ses consignes. Utilisez **deux accès mail** : l'un qui ne
peut que lire le libellé des factures, l'autre qui ne peut qu'envoyer. Un accès en lecture seule ne
peut pas envoyer, et un accès en envoi seul ne peut pas lire votre boîte.

## Les phases

L'agent passe à la phase suivante sur des **preuves**, pas sur le calendrier. Inscrivez la phase en
cours dans une seule valeur de configuration que chaque chemin d'écriture vérifie.

| phase | durée type | l'agent peut | critère de sortie |
|---|---|---|---|
| **0. Observer** | quelques jours | lire transactions et factures, produire un recensement (catégories, nombres, montants), **essais à blanc seulement** | le recensement correspond à ce que vous voyez dans le logiciel ; vous comprenez les catégories |
| **1. Demander** | 2 à 4 semaines | joindre et rapprocher les pièces trouvées (montant et date concordent, aucun rapprochement ambigu) ; envoyer des relances à vous et des questions à l'expert-comptable | l'expert-comptable a répondu aux questions de structure (comptes des lignes sans facture attendue, TVA par zone, remboursements, mouvements d'associés) et ses réponses sont consignées en conventions |
| **2. Saisir sous convention** | jusqu'à la confiance | comptabiliser compte et TVA **seulement** là où une convention couvre le fournisseur ; chaque écriture dans un mail de contrôle groupé | plusieurs récapitulatifs de contrôle sans correction de l'expert-comptable |
| **3. Étendre les conventions** | en continu | enregistrer lui-même la convention d'un nouveau fournisseur quand la zone de TVA et un fournisseur comparable la tranchent, comptabiliser, et prévenir dans le récapitulatif suivant | — |

Revenir en arrière tient en un changement de configuration. Faites-le dès qu'un récapitulatif
appelle des corrections que vous n'attendiez pas.

## Les trois canaux

| canal | destinataires | contenu | délai minimal entre deux envois |
|---|---|---|---|
| relance | vous | pièces manquantes (critiques d'abord), rapprochements ambigus, fournisseurs inconnus, liens de portail à récupérer, erreurs techniques | une fois par semaine |
| expertise | expert-comptable + vous | quel compte pour une nature de ligne récurrente, quel traitement de TVA, une convention à fixer, une amélioration | seulement quand l'ensemble des **questions** change, et pas dans les 3 jours qui suivent le précédent |
| contrôle | expert-comptable + vous | chaque écriture passée sous convention : pièce, compte, code TVA, convention appliquée, identifiant d'écriture | un mail par lot, au plus quotidien |

Les règles qui gardent l'expert-comptable disposé à répondre :

- **Jamais** écrire à l'expert-comptable pour une pièce manquante. C'est votre travail, pas le sien.
- **Pas de destinataire par défaut.** Chaque envoi nomme son canal.
- L'empreinte qui décide si le mail d'expertise doit repartir se calcule à partir des seules
  **questions encore ouvertes**, jamais de la liste des pièces manquantes, et exclut les sujets déjà
  tranchés. Sinon une facture
  manquante de plus fait un « nouveau » mail, et le canal redevient quotidien par la porte de
  derrière.
- Le **délai minimal vit dans l'unique fonction d'envoi**, pour qu'un second agent (une revue, un
  surveillant de réponses) ne puisse pas le contourner. Seule une passe explicitement demandée par un
  humain peut passer outre.
- Enregistrer l'horodatage d'un envoi **après** confirmation du fournisseur de messagerie : une panne
  ne doit pas consommer le délai.

## Le cadre des mails

Fixé dans le code, pas dans une consigne :

- la langue de travail de votre expert-comptable ;
- l'agent se présente comme l'assistant IA de votre société et signe du nom de la société ;
- chaque mail se termine par un avertissement, par exemple : *« Cet email est envoyé en autonomie par
  une IA dans une démarche expérimentale et peut comporter des inexactitudes. »*

## Surveiller les réponses sans risque

- Autoriser des **adresses d'expéditeur exactes** (votre expert-comptable, vous), jamais un domaine.
  Les cabinets appartiennent à des groupes ; un collègue de votre expert-comptable n'est pas votre
  expert-comptable.
- Ne suivre que les **fils ouverts par l'agent**. Ne répondre que dans un tel fil, et seulement quand
  l'expert-comptable a écrit en dernier.
- Retirer le texte cité des réponses avant de les enregistrer, sinon le journal double à chaque
  échange et l'agent relit ses propres phrases comme si l'expert-comptable les avait écrites.

## Le journal, les conventions et les décisions

Trois fichiers en ajout seul, la mémoire de l'agent :

| fichier | un enregistrement par | champs clés |
|---|---|---|
| `journal/<AAAA-MM>.jsonl` | mail envoyé (échecs compris) ou réponse reçue | horodatage, canal, destinataires, objet, identifiant de fil, texte |
| `conventions.jsonl` | décision sur un fournisseur ou un motif | clé, fournisseur, compte, code TVA, pays, decided_by, date, citation |
| `decisions.jsonl` | décision sur une transaction | identifiant de transaction, verdict (`no_doc`, `personal`, `chase`), motif, auteur, date |

Une correction est un nouvel enregistrement, jamais une modification. Avant d'écrire à
l'expert-comptable, l'agent relit le journal : une question déjà tranchée ne se repose pas.

Tenez un miroir lisible (une note par mois) **régénéré entièrement** depuis les fichiers sources à
chaque écriture, et non complété : un miroir complété diverge la première fois que le dossier est
réinitialisé.

## Ce qui tourne, et quand

Partager le travail de nuit en deux :

1. **Un traitement automatisé, sans modèle de langage.** De l'arithmétique seulement : lister les transactions, les ranger,
   rapprocher les pièces par montant et date, graduer la gravité, comptabiliser ce que les
   conventions permettent, préparer les mails. Il doit continuer de tourner quand l'inférence est en
   panne. Un échec est un code de sortie non nul, visible dans votre planificateur ; jamais un saut
   silencieux.
2. **Une revue, avec un modèle de langage.** Elle lit le rapport du traitement automatisé, le journal et le PCG ; lit les
   PDF des factures (la seule tâche qui exige vraiment un modèle) ; rédige les questions d'expertise
   avec l'article du PCG pour chaque compte proposé ; vérifie qu'un travail n'est pas déjà fait avant
   d'écrire.

## À coller dans Claude Code ou Codex

```text
Utilise le skill $french-accounting. Je veux mettre en place un agent comptable pour ma propre
société, en suivant references/onboarding.md. Mon logiciel comptable est <nom>, les factures arrivent
dans le libellé mail <libellé>, mon expert-comptable est <nom, adresse exacte>, mes comptes bancaires
sont <liste>.

Commence en phase 0 : lance scripts/fetch-sources.sh, puis construis un recensement en lecture seule
des transactions bancaires sans justificatif, rangées selon l'étape 1 de SKILL.md et graduées selon
l'étape 2. N'envoie aucun mail et n'écris rien dans le logiciel comptable. Propose-moi, pour
relecture, la configuration (phase, canaux, destinataires, délais entre envois), les trois registres
et le programme de nuit, ainsi que le premier mail d'expertise à mon expert-comptable, avec les questions de
structure de references/sans-justificatif.md et la question de TVA par zone de references/regles.md.
```

Relisez vous-même son premier mail d'expertise avant qu'il parte. Ce mail donne le ton de toute la
relation.
