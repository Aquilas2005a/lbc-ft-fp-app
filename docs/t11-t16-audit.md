# Audit T11 a T23 et adaptateur OpenSanctions

## Regles conservees

- Une tache doit rester terminable en deux heures maximum.
- Les secrets restent dans `.env`, jamais dans Git.
- `lbc_db` est la base de demonstration ; `lbc_test` est reservee aux tests.
- Les migrations Alembic sont la source unique de la structure PostgreSQL.
- Un resultat de matching est une alerte de travail et exige une revue humaine.

## Travail trouve et ameliore

| Tache | Travail trouve | Amelioration apportee |
| --- | --- | --- |
| T11 | Alembic, health DB et connexion PostgreSQL existaient deja. | Migrations alignees avec les montants `NUMERIC(18,2)`, CI PostgreSQL reelle, suppression de `create_all`. |
| T12 | CRUD clients existant. | Suppression logique avec `deleted_at`, clients supprimes exclus des recherches et lectures. |
| T13 | CRUD comptes existant. | Validation du client actif, format IBAN simple et normalisation des devises. |
| T14 | Creation de transaction et mise a jour de solde existantes. | Verrouillage du compte, refus du solde insuffisant, devise coherente et statut explicite. |
| T15 | Seed de demonstration existant. | Montants Decimal, un seul commit, endpoint limite a `development`. |
| T16 | Matching RapidFuzz local existant. | Normalisation des noms et seuil configurable plus prudent (`85`). |

## Verification realisee

- Les migrations de `lbc_db` sont au niveau `0006_tx_counterparty_country`.
- Les colonnes `accounts.balance` et `transactions.amount` sont de type PostgreSQL `numeric`.
- `clients.deleted_at` est present.
- Les 38 tests backend passent sur `lbc_test` (2 tests d'integration ajoutes lors de la verification T18, voir ci-dessous).

## Prochaine action

T17 est termine : les alertes automatiques sont dedupliquees pour les transactions elevees, la frequence inhabituelle et les matchs de screening, puis exposees a une revue manuelle.

T18 est termine : une revue d'alerte est tracee avec l'acteur `X-Actor` dans `audit_logs`; les alertes automatiques y sont egalement enregistrees et l'API de consultation est en lecture seule.

T19 est termine : les actions metier clients, transactions et screenings sont tracees avec `X-Actor`, meme lorsqu'aucune alerte n'est creee.

T20 est termine : le score de risque client est calcule de facon deterministe, borne, explique et trace dans `audit_logs`, sans effet de blocage automatique.

L'adaptateur OpenSanctions optionnel est termine : le mode mock reste le defaut, le format officiel `/match/default` est encapsule et teste sans appel reseau reel, et `auto` retombe sur le screening local.

T21 est termine : les regles de montant, frequence et pays a risque sont dedupliquees, tracees et reutilisables sur les transactions existantes sans modifier leurs soldes ni leurs statuts.

T22 est termine : le score de risque client est borne, explique et trace sans prendre de decision automatique.

T23 est termine : 38 tests backend couvrent les parcours clients, screening, alertes, audit, score et regles de transactions sur `lbc_test`.

Verification T18 (relecture) : le code de repli `auto` -> `local` et le refus explicite du mode `opensanctions` sans cle etaient deja corrects, mais non couverts par un test au niveau de l'endpoint `POST /api/v1/screening/match` (seul l'adaptateur isole etait teste). Deux tests d'integration ont ete ajoutes dans `backend/tests/test_opensanctions.py` via une surcharge de la dependance `get_settings`. Aucune regression : les 38 tests passent.

T24 doit construire le dashboard React de conformite.

T24 est termine : Vite + React 19 + TypeScript + Tailwind CSS v4 sont initialises dans `frontend/`, avec les tokens du design "Registre de decision" (`@theme` dans `index.css`). Contraste WCAG verifie sur toute la palette ; l'ocre brut ne passait pas en texte (2.34:1), une variante `--color-ocre-texte` a ete ajoutee (4.78:1). Build (`tsc -b && vite build`) et lint (`oxlint`) passent, CI frontend mise a jour pour executer les deux reellement. Assets par defaut du template retires. Portee limitee a l'initialisation : navigation, layout et hero restent a construire en T25.

T25-T27 verifies (relecture, travail fait en dehors de cette session d'audit) : navigation par role et hero avec photo (T25), dashboard KPI avec bande de risque signature (T26), formulaire onboarding client (T27) conformes aux tokens et principes du plan. Point trouve : T27 n'appelait pas encore le backend (etat local uniquement) - corrige lors de T32.

T28-T32 termines : registre clients maitre-detail avec sceau de risque reutilise (T28), formulaire transaction sur le meme systeme de composants que T27 (T29, composants factorises dans components/form.tsx et formStyles.ts), table des alertes filtrable et ecran de decision Valider/Rejeter/Escalader avec toast reprenant le mot exact de l'action (T30-T31), client API centralise dans api/client.ts et hook useFetch partage (T32). T27 branche sur createClient a cette occasion. Verification en conditions reelles : backend + PostgreSQL demarres localement, chaine complete testee via curl avec Origin du frontend (CORS + preflight OPTIONS valides) - creation client/compte/transaction, declenchement d'une vraie alerte automatique (regle T21), puis decision de revue via PUT /alerts/{id}/review. lint et build frontend passent sans avertissement.
