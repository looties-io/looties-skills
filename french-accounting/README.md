# french-accounting

Un skill pour tenir la comptabilité d'une société française avec un agent IA, selon le Plan
comptable général (PCG) et sous le contrôle de votre expert-comptable.

Fait partie de [looties-skills](https://github.com/looties-io/looties-skills), des skills d'agent
open source publiés par [Looties](https://looties.io).

## Le constat de départ

Nous avons fait tourner un agent comptable sur notre propre comptabilité pendant plusieurs mois : il
lisait les factures d'un libellé mail, les rapprochait des lignes bancaires, écrivait à notre
expert-comptable, et a fini par passer des écritures. Presque toutes les erreurs qu'il pouvait
commettre avaient la même forme :

> **L'agent comblait un vide avec son propre jugement, là où il fallait celui de l'expert-comptable.**

Un numéro de compte plausible, tiré de mémoire. Un code TVA choisi parce que le logiciel en exigeait
un. Une décision ponctuelle transformée en motif, qui faisait taire la dépense légitime suivante. Un
surveillant de réponses qui faisait confiance à tout un domaine. Ce qui a marché, c'est l'inverse :
lire chaque compte dans le PCG, demander une fois à l'expert-comptable, consigner sa réponse en
convention, l'appliquer, et le laisser contrôler chaque écriture dans un récapitulatif groupé.

## Ce qu'il fait

- **Hiérarchie des sources :** le PCG est la vérité absolue, les conventions de l'expert-comptable
  choisissent à l'intérieur, une décision sur une ligne ne se généralise jamais, les cours
  expliquent, l'agent ne fait que proposer.
- **Met le PCG sur le disque :** `scripts/fetch-sources.sh` télécharge le PCG consolidé auprès de
  l'ANC et en extrait le texte, pour que chaque numéro de compte soit à un grep.
- **Range chaque ligne bancaire** (rapprochable, à réclamer, pièce interne, sans facture attendue) et gradue ce
  qui manque selon la TVA en jeu.
- **Rapproche les pièces par l'arithmétique** (montant au centime, fenêtre de dates, rapprochements
  ambigus signalés).
- **Des règles générales** pour la TVA selon l'adresse de facturation, remboursements et avoirs,
  comptes d'attente, virements internes, comptes d'associés, indemnités kilométriques et versements
  des prestataires de paiement.
- **Un guide de mise en service** pour le faire tourner en agent autonome avec accès mail, qui gagne ses
  droits d'écriture par phases (observer, demander, saisir sous convention, étendre les
  conventions), avec trois canaux de mail qui gardent votre expert-comptable disposé à répondre.

**Pour qui :** les fondateurs et dirigeants de petites sociétés françaises qui tiennent leur
comptabilité dans un logiciel avec un expert-comptable, et veulent qu'un agent fasse la paperasse.

## Ni conseil juridique, ni conseil fiscal

Ce skill vous aide à tenir la comptabilité de **votre propre société**. En France, tenir ou réviser
la comptabilité d'un tiers à titre de prestation est réservé aux experts-comptables (ordonnance
n° 45-2138). L'agent propose et applique ce que décide votre expert-comptable ; il ne le remplace
pas. Les chiffres fiscaux (taux de TVA, barème kilométrique, seuils) changent chaque année : le skill
demande à l'agent de les lire à la source officielle, jamais de mémoire.

## Installation

```bash
npx skills@latest add looties-io/looties-skills --skill french-accounting
```

Puis téléchargez les sources une fois :

```bash
bash <dossier-des-skills>/french-accounting/scripts/fetch-sources.sh   # dans ~/.accounting-sources
```

`pdftotext` (poppler) est recommandé pour que l'agent puisse chercher dans le texte.

## Utilisation

```
Utilise $french-accounting pour me dire lesquelles de ces lignes bancaires ont vraiment besoin d'une facture, et sur quel compte va chacune.
```

Pour mettre en place l'agent autonome, collez dans Claude Code ou Codex la consigne qui termine
[references/onboarding.md](references/onboarding.md).

## Contenu

```
french-accounting/
|-- SKILL.md                     <- la méthode que l'agent charge
|-- README.md                    <- ce fichier
|-- references/
|   |-- sources.md               <- hiérarchie des sources, où trouver chacune, licences
|   |-- pcg-essentiel.md         <- principes, articles clés, codification, comptes courants
|   |-- sans-justificatif.md     <- les lignes sans facture fournisseur attendue, et comment les reconnaître
|   |-- regles.md                <- règles comptables générales apprises en production
|   `-- onboarding.md            <- phases, canaux et registres de l'agent autonome
|-- scripts/fetch-sources.sh     <- télécharge le PCG et en extrait le texte
|-- agents/openai.yaml           <- métadonnées d'interface pour les environnements d'agents
`-- evals/evals.json             <- consignes de déclenchement réalistes
```

## Les sources et leurs licences

Le skill ne redistribue aucun texte tiers. `fetch-sources.sh` télécharge le PCG (règlement ANC
n° 2014-03, version consolidée) auprès de l'Autorité des normes comptables. Deux cours universitaires
français sont cités en lecture facultative, sous leurs propres conditions : le cours des Mines Paris
PSL de Frédéric Kletz et François Engel (à lire en ligne) et le cours AUNEGe de Céline Averseng
(CC BY-NC-ND 4.0, usage personnel). Voir [references/sources.md](references/sources.md).

## Licence

Le script est sous licence MIT, voir [LICENSE](../LICENSE). Le texte du skill (SKILL.md, README.md et
`references/`) est sous licence [Creative Commons Attribution 4.0
International](https://creativecommons.org/licenses/by/4.0/deed.fr) (CC BY 4.0) : réutilisez-le et
adaptez-le, en citant Looties.
