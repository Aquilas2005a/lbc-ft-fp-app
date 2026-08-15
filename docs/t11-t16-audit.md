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
- Les 36 tests backend passent sur `lbc_test`.

## Prochaine action

T17 est termine : les alertes automatiques sont dedupliquees pour les transactions elevees, la frequence inhabituelle et les matchs de screening, puis exposees a une revue manuelle.

T18 est termine : une revue d'alerte est tracee avec l'acteur `X-Actor` dans `audit_logs`; les alertes automatiques y sont egalement enregistrees et l'API de consultation est en lecture seule.

T19 est termine : les actions metier clients, transactions et screenings sont tracees avec `X-Actor`, meme lorsqu'aucune alerte n'est creee.

T20 est termine : le score de risque client est calcule de facon deterministe, borne, explique et trace dans `audit_logs`, sans effet de blocage automatique.

L'adaptateur OpenSanctions optionnel est termine : le mode mock reste le defaut, le format officiel `/match/default` est encapsule et teste sans appel reseau reel, et `auto` retombe sur le screening local.

T21 est termine : les regles de montant, frequence et pays a risque sont dedupliquees, tracees et reutilisables sur les transactions existantes sans modifier leurs soldes ni leurs statuts.

T22 est termine : le score de risque client est borne, explique et trace sans prendre de decision automatique.

T23 est termine : 36 tests backend couvrent les parcours clients, screening, alertes, audit, score et regles de transactions sur `lbc_test`.

T24 doit construire le dashboard React de conformite.
