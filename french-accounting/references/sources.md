# Sources

Ce que l'agent lit, dans quel ordre d'autorité, et comment se procurer chaque source.

## La hiérarchie

| rang | source | rôle | comment l'obtenir |
|---|---|---|---|
| 1 | **Plan comptable général**, règlement ANC n° 2014-03, version consolidée en vigueur | source absolue de vérité : principes, fonctionnement des comptes, plan de comptes (art. 1121-1) | `scripts/fetch-sources.sh` le télécharge sur anc.gouv.fr |
| 2 | **Les réponses écrites de l'expert-comptable** | conventions : quelle subdivision, quel traitement de TVA, pour cette société | le journal d'échange et le registre des conventions ([onboarding.md](onboarding.md)) |
| 3 | **Les décisions sur une ligne** | la décision d'un humain sur une transaction | le registre des décisions |
| 4 | **Les cours** | savoir général, pour comprendre et expliquer | voir plus bas |
| 5 | le raisonnement de l'agent | propositions seulement | — |

Un cours ne contredit jamais le PCG. Si un cours et le PCG divergent, le cours est daté ou simplifie ;
le PCG l'emporte.

## Le PCG

Éditeur : Autorité des normes comptables (ANC). Le texte consolidé est republié chaque 1er janvier,
environ 180 pages. URL utilisée par défaut par le script (à remplacer par `PCG_URL` quand l'ANC
publie une nouvelle année) :

```
https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Plans%20comptables/2026/PCG--1er-janvier-2026.pdf
```

Son organisation, pour qu'une recherche tombe juste :

- **Livre I** (art. 111 à 515) : principes (121-1 à 121-5), définition et évaluation des actifs,
  passifs, charges et produits.
- **Livre II** (art. 611 à 760) : opérations spécifiques. Rarement utile, sauf **611 (solutions
  informatiques)** : quand un logiciel est une charge et quand c'est une immobilisation
  incorporelle.
- **Livre III** (art. 811 à 911) : modèles de bilan, de compte de résultat et d'annexe.
- **Livre IV** (art. 1011 à 1231) : **tenue des comptes**. Organisation, pièces justificatives, plan
  de comptes (1121-1), règles de codification (1131-1 à 1131-4) et fonctionnement de chaque compte
  (1211-x à 1227-x). C'est le livre où vit un agent comptable.

Chercher dans le texte extrait :

```bash
grep -n "^Art. 1121-1" ~/.accounting-sources/pcg/PCG.txt      # début du plan de comptes
grep -n "^Art. 1214-44" -A40 ~/.accounting-sources/pcg/PCG.txt # fonctionnement des comptes de TVA
grep -n "Fournisseurs - Factures non parvenues" ~/.accounting-sources/pcg/PCG.txt
```

## Les chiffres fiscaux ne sont pas dans le PCG

Le PCG donne le **compte**, jamais le **montant**. Ceux-ci se lisent à leur source pour l'année
concernée, ou se demandent à l'expert-comptable :

- taux et règles de TVA : Code général des impôts et BOFiP (bofip.impots.gouv.fr) ;
- barème kilométrique : arrêté annuel, publié au BOFiP sous `BOI-BAREME-000001` ;
- seuils (régimes micro, franchise en base de TVA, petits matériels) : BOFiP.

## Les cours (facultatifs, savoir général)

Deux cours universitaires français ont servi à former l'agent d'origine. Aucun n'est redistribué ici ;
chacun reste soumis aux conditions de ses auteurs.

| cours | auteurs | ce qu'il apporte | où | conditions |
|---|---|---|---|---|
| Cours de comptabilité générale, Mines Paris PSL | Frédéric Kletz, François Engel | l'architecture : histoire et normalisation, nomenclature, principes, lecture du bilan et du compte de résultat, commentaires fiscaux par poste | à lire en ligne : `https://direns.minesparis.psl.eu/Sites/ComptaG/co/comptagenerale_ULcg00.html` | celles des auteurs ; lire en ligne, ne pas copier |
| Comptabilité générale, AUNEGe / IAE de Montpellier | Céline Averseng | le geste : écritures d'achat et de vente, TVA, réductions, transport, avoirs, stocks, amortissements, cessions, provisions, régularisations de clôture | `https://moodle.luniversitenumerique.fr/course/view.php?id=1034` (la plupart des leçons demandent un compte gratuit) | CC BY-NC-ND 4.0 : usage personnel, non commercial, sans modification |

Pour utiliser les leçons AUNEGe, téléchargez vous-même les PDF dans
`~/.accounting-sources/courses/aunege/` puis relancez `scripts/fetch-sources.sh` : il extrait le
texte de chaque PDF qu'il y trouve, pour la recherche. Gardez-les pour votre usage ; ne les
republiez pas. Pour un usage commercial, obtenez l'autorisation des titulaires des droits : le
téléchargement local ne l'accorde pas.
