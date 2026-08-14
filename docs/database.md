# PostgreSQL et pgAdmin

## Objectif

PostgreSQL s'execute dans Docker Compose. pgAdmin est l'interface locale qui permet d'explorer et d'administrer cette base ; il ne remplace pas PostgreSQL.

## Demarrer et verifier la base

Depuis la racine du projet :

```powershell
docker compose up -d db
docker compose ps
docker compose exec -T db pg_isready -U lbc_user -d lbc_db
```

Le statut attendu est `healthy` et le port expose est `localhost:5432`.

## Ajouter le serveur dans pgAdmin

Dans pgAdmin, creer un serveur avec les valeurs suivantes :

| Champ pgAdmin | Valeur |
| --- | --- |
| General > Name | `LBC FT FP - local` |
| Connection > Host name/address | `localhost` |
| Connection > Port | valeur de `POSTGRES_PORT` dans `.env` (par defaut `5432`) |
| Connection > Maintenance database | valeur de `POSTGRES_DB` dans `.env` (par defaut `lbc_db`) |
| Connection > Username | valeur de `POSTGRES_USER` dans `.env` (par defaut `lbc_user`) |
| Connection > Password | valeur de `POSTGRES_PASSWORD` dans `.env` |
| SSL | `Prefer` (valeur par defaut) |

Le fichier `.env` est local et ignore par Git. Ne pas recopier son mot de passe dans les issues, commits, captures d'ecran ou documentation versionnee.

## Verification dans pgAdmin

Une fois connecte, ouvrir `Databases > lbc_db > Schemas > public`, puis lancer dans le Query Tool :

```sql
SELECT current_database() AS database, current_user AS user;
```

Le resultat attendu est `lbc_db` et `lbc_user`.

## Depannage

| Probleme | Verification | Contournement |
| --- | --- | --- |
| La connexion est refusee | `docker compose ps` | Demarrer Docker Desktop puis `docker compose up -d db`. |
| Le port 5432 est deja pris | `docker compose ps` ou le message Docker | Definir `POSTGRES_PORT=5433` dans `.env`, recreer le conteneur, puis utiliser `5433` dans pgAdmin et `DATABASE_URL`. |
| Le mot de passe est refuse | Verifier le champ de mot de passe dans pgAdmin | Utiliser la valeur locale de `POSTGRES_PASSWORD`. Les variables Compose ne changent pas automatiquement le mot de passe d'une base deja initialisee. |
| pgAdmin ne se lance pas | Verifier son installation Windows | PostgreSQL reste utilisable avec `docker compose exec -T db psql ...`; reinstaller ou ouvrir pgAdmin ensuite. |

## Regle sur les donnees Docker

`docker compose down` arrete et retire le conteneur, mais conserve le volume `postgres_data`. Ne pas utiliser `docker compose down -v` sauf pour recommencer avec une base vide : cette commande supprime les donnees locales.
