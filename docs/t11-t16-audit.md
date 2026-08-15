# Audit T11 a T17

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

- Les migrations de `lbc_db` sont au niveau `0004_add_alert_review_fields`.
- Les colonnes `accounts.balance` et `transactions.amount` sont de type PostgreSQL `numeric`.
- `clients.deleted_at` est present.
- Les 30 tests backend passent sur `lbc_test`.

## Prochaine action

T17 est termine : les alertes automatiques sont dedupliquees pour les transactions elevees, la frequence inhabituelle et les matchs de screening, puis exposees a une revue manuelle.

T18 doit rendre la revue entierement tracable dans `audit_logs` et preparer l'identite de l'agent de conformite.
