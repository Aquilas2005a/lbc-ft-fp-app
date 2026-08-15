# Audit T11 a T16

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

- Les migrations de `lbc_db` sont au niveau `0003_add_client_soft_delete`.
- Les colonnes `accounts.balance` et `transactions.amount` sont de type PostgreSQL `numeric`.
- `clients.deleted_at` est present.
- Les 18 tests backend passent sur `lbc_test`.

## Prochaine action

T17 doit creer les alertes automatiquement pour les transactions elevees et les matchs de screening, avec un statut de revue humaine. Les alertes ne doivent pas bloquer ou sanctionner un client sans validation manuelle.
