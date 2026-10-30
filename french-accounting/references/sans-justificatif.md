# Les lignes sans facture attendue

Le logiciel comptable signale la plupart des lignes bancaires comme « pièce manquante ». Une bonne
partie n'aura jamais de facture fournisseur, et ce sont elles qui laissent l'écran rouge en
permanence. Elles ont pourtant un justificatif (relevé, bulletin de paie, déclaration, PCG 1032-1),
qu'il faut conserver. Le travail de
l'agent est de cesser de les compter comme du travail, de dire pourquoi, et de laisser
l'expert-comptable fixer leur compte une fois, par convention.

Le signalement lui-même est souvent **en lecture seule via l'API** du logiciel : l'agent ne peut pas
marquer une ligne « aucune facture attendue ». Ne pas faire comme si. Un rôle qui a l'air d'avoir vidé
la liste alors que la liste est toujours là, c'est le pire résultat possible.

## Les motifs sûrs (sur le libellé bancaire)

| motif | justificatif à conserver | compte généralement retenu |
|---|---|---|
| intérêts, « rémunération » | le relevé bancaire | 768 |
| paie, « salaire » | le bulletin de paie | 641 / 421 |
| URSSAF, DGFiP, « impôts », « TVA », « Trésor public » | la déclaration | 43x / 44x |
| frais bancaires, « agios », « commission d'intervention » | le relevé bancaire | 627 |
| un rechargement du solde de la société chez son prestataire de paiement (entité exacte **et** libellé exact) | le relevé du prestataire (l'argent reste dans la société) | 58 |
| apport en capital | les actes et relevés ; mouvement passé par l'expert-comptable | 456 / 455 |

Garder ce tableau **prudent**. Chaque motif retire des lignes de la liste d'un humain : il doit être
sans ambiguïté. N'ajouter un motif que quand la même ligne est apparue plusieurs fois dans de vrais
rapports ; une règle gagne sa place parce qu'on l'a observée, pas parce qu'on l'a imaginée.

## Les motifs trouvés par l'arithmétique, pas par le libellé

**Les virements internes.** Chaque banque libelle son propre mouvement (« Dépôt », « Retrait », la
marque de la contrepartie), si bien qu'aucun motif de libellé ne les attrape tous, et qu'un critère
trop large (« Retrait ») avale de vrais retraits d'espèces. Rapprocher plutôt sur la forme : **même jour,
montants égaux et opposés, sur deux comptes différents détenus par la société**. Cette règle ne
demande aucun entretien quand les libellés changent et s'étend à tout nouveau compte. Passer par 58,
qui doit se solder à zéro.

**La pré-autorisation de carte et sa libération.** Un petit débit et son crédit égal sur le **même**
compte, le même jour, chez le même commerçant. La forme est identique à celle d'un vrai achat
remboursé le jour même, qui exige sa facture **et** son avoir. Un plafond de montant ne suffit pas à
les distinguer : exiger que les données du prestataire ou de la banque confirment la nature de
pré-autorisation ; sinon, laisser la paire à l'examen d'un humain.

## Le sens compte

- **Un encaissement non rapproché se réclame, il ne se cache pas.** L'argent qui entre n'a en général
  pas de facture fournisseur, et la tentation est de ranger tout crédit en « sans facture attendue ». Une règle
  qui cache tout un sens de flux ne pourra jamais signaler le jour où elle commence à cacher quelque
  chose de réel. Un crédit n'arrive en « sans facture attendue » qu'en correspondant à un motif nommé.
- **Un virement reçu d'un associé** (crédit) est très probablement une avance en compte courant (455)
  et peut faire l'objet d'un motif sur le nom exact de l'associé. **De l'argent qui part vers un
  associé** (débit) peut être un remboursement de compte courant, un salaire ou un remboursement de
  frais, trois comptes différents : il attend toujours un humain.

## Règles et décisions

Une **règle** est un motif qui se généralise et vit dans le code. Une **décision** est le jugement
d'un humain sur une ligne et vit dans des données, indexée par identifiant de transaction, en ajout
seul, avec auteur et date. Trois verdicts ont couvert ce que nous avons rencontré : `no_doc` (aucune
facture fournisseur attendue ; justificatif pertinent conservé), `personal` (pas une charge de la société, à reclasser au compte courant de
l'associé), `chase` (forcer une ligne à rester réclamée contre une règle qui l'aurait attrapée à
tort). Les décisions sont consultées avant toute règle.

Ne jamais transformer une décision en règle : « cet achat chez le magasin X était personnel » écrit
comme un motif sur X fait taire l'achat suivant, légitime, chez X.

## Ce que l'agent demande une fois à l'expert-comptable

1. Sur quel compte va chaque motif « sans facture attendue » dans **son** plan (le tableau ci-dessus donne les
   comptes par défaut du PCG, pas son plan).
2. S'il veut que ces lignes soient catégorisées, ou laissées signalées et traitées à la clôture.
3. Quel justificatif il retient quand aucune facture n'existe (relevé, bulletin, déclaration).
4. Comment se rattachent avoirs et remboursements (à la facture d'origine, ou comme ligne propre).

Tant qu'il n'a pas répondu, l'agent rapporte et propose. Ses réponses deviennent des conventions.
