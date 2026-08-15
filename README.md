# Application LBC/FT/FP

Application web de filtrage des clients et transactions pour la lutte contre le blanchiment de capitaux, le financement du terrorisme et le financement de la proliferation.

## 1. Resume integre du projet

But du projet :
- Creer une application de conformite qui permet d'enregistrer des clients, comptes et transactions.
- Filtrer les clients contre des listes de sanctions, PEP et watchlists.
- Generer et traiter des alertes conformite.
- Produire une demo claire pour un hackathon ou un projet etudiant.

Stack retenue :
- Frontend : Vite, React, TypeScript, Tailwind CSS.
- Backend : FastAPI, Pydantic, SQLAlchemy ou SQLModel.
- Base de donnees : PostgreSQL via Docker.
- Administration DB : pgAdmin local deja installe.
- Matching : RapidFuzz.
- Screening externe : OpenSanctions optionnel, avec mode mock pour la demo.
- Versioning : Git, GitHub, GitHub Actions.

## 2. Regles du projet

Regles techniques :
- Chaque tache doit rester terminable en 2h maximum.
- Le projet doit demarrer avec PostgreSQL via Docker.
- Aucun secret ne doit etre commite : utiliser `.env` en local et `.env.example` dans GitHub.
- Les cles API, mots de passe reels et tokens GitHub restent hors du depot.
- Le mode demo doit fonctionner sans cle OpenSanctions.
- Les changements doivent etre courts, testables et pousses regulierement sur GitHub.

Regles GitHub :
- `main` garde une version stable.
- Une tache correspond a une branche courte ou un commit clair.
- Les issues GitHub serviront a suivre les taches T01, T02, T03, etc.
- Les workflows GitHub Actions seront ajoutes avant les premieres grosses integrations.

## 3. Etapes deja faites

T01 - Structure projet :
- Dossier projet cree dans `work/lbc-ft-fp-app`.
- Arborescence creee : `backend/`, `frontend/`, `docs/`.
- Depot Git local initialise sur la branche `main`.

T02 - GitHub :
- Repository GitHub prive cree : `Aquilas2005a/lbc-ft-fp-app`.
- Remote `origin` configure.
- Commit initial pousse sur GitHub.

T03 - Documentation de demarrage :
- Ce README documente le projet, les regles, l'etat actuel et la prochaine action.
- `.gitignore` protege les fichiers locaux, caches, environnements virtuels et dependances.
- `.env.example` donne le modele des variables d'environnement.

T04 - Organisation GitHub :
- Labels GitHub crees pour organiser les taches : `task`, `mvp`, `github`, `ci`, `backend`, `database`, `docker`, `documentation`.
- Milestone creee : `MVP 1 - API utilisable`.
- Issues creees pour T04 a T15 afin de suivre les taches courtes du premier MVP.
- Le tableau GitHub Project visuel reste optionnel car il demande un scope GitHub supplementaire.

T05 - CI backend minimale :
- Workflow cree : `.github/workflows/backend-ci.yml`.
- Verification actuelle : presence du dossier `backend/`, presence de `.env.example`, disponibilite de Python.
- Le workflow a ete enrichi en T07 pour installer les dependances backend et lancer `pytest`.

T06 - CI frontend minimale :
- Workflow cree : `.github/workflows/frontend-ci.yml`.
- Verification initiale : presence du dossier `frontend/`, presence de `.env.example`, disponibilite de Node.js.
- Enrichi en T24 : le workflow installe les dependances (`npm ci`), lance le lint (`oxlint`) et le build (`tsc -b && vite build`) reels.

T07 - Squelette FastAPI :
- Application backend creee dans `backend/app`.
- Endpoint public ajoute : `/health`.
- Endpoint versionne ajoute : `/api/v1/health`.
- Documentation OpenAPI disponible via `/openapi.json` et Swagger via `/docs`.
- Tests backend ajoutes dans `backend/tests`.
- CI backend mise a jour pour executer les tests reels.

T08 - PostgreSQL avec Docker Compose :
- Fichier `docker-compose.yml` ajoute a la racine du projet.
- Service `db` base sur PostgreSQL 16 Alpine configure.
- Variables PostgreSQL lues depuis `.env` ou leurs valeurs de demonstration de `.env.example`.
- Volume Docker `postgres_data` ajoute pour conserver les donnees entre les redemarrages.
- Healthcheck `pg_isready` ajoute pour savoir quand la base est prete.

T09 - Connexion pgAdmin :
- Documentation ajoutee dans `docs/database.md` pour ajouter le serveur Docker dans pgAdmin.
- Fichier `.env` local cree avec le mot de passe de developpement et protege par `.gitignore`.
- Mot de passe du role PostgreSQL local synchronise avec `.env`, sans supprimer le volume de donnees.
- Procedure de test et de depannage ajoutee, incluant le risque de suppression avec `docker compose down -v`.

T10 - Modeles de donnees et persistance backend :
- Ajout des dependances SQLAlchemy 2.x, psycopg3, Alembic, pydantic-settings et email-validator.
- Creation des modeles ORM pour Client, Compte (Account), Transaction, Alerte (Alert) et AuditLog.
- Creation des schemas de validation/serialisation Pydantic correspondants.
- Configuration du moteur SQLAlchemy et de la dependance `get_db()` de FastAPI dans `backend/app/db`.
- Configuration lue depuis le `.env` local et URL PostgreSQL encodee pour accepter les caracteres speciaux du mot de passe.
- Montants stockes en `Decimal`/`NUMERIC(18,2)` avec contraintes de base de donnees, pour eviter les erreurs d'arrondi.
- Ajout et validation des tests unitaires backend pour les modeles, schemas et configuration.

T11 - Configurer la connexion PostgreSQL :
- Alembic initialise avec les migrations `0001_initial_tables`, `0002_align_financial_schema` et `0003_add_client_soft_delete`.
- Les migrations sont l'unique mecanisme de creation/modification des tables : FastAPI ne cree plus de tables automatiquement.
- Endpoint `/api/v1/health/db` ajoute pour verifier la vraie connexion sans exposer le detail des erreurs SQL.
- GitHub Actions demarre PostgreSQL, execute `alembic upgrade head`, puis lance les tests d'integration.
- Les tests utilisent la base dediee `lbc_test`, jamais la base de demonstration `lbc_db`.

T12 - CRUD Clients :
- Endpoints API de gestion des clients (`POST`, `GET`, `GET /{id}`, `PUT /{id}`, `DELETE /{id}`) dans `backend/app/api/clients.py`.
- Suppression logique avec `deleted_at` : les clients supprimes ne sont plus exposes par l'API, mais leurs donnees restent en base.
- Validation des donnees Pydantic et gestion des erreurs 404 / 400.

T13 - CRUD Comptes :
- Endpoints API de gestion des comptes bancaires (`POST`, `GET`, `GET /{id}`, `PUT /{id}`) dans `backend/app/api/accounts.py`.
- Validation de l'existence d'un client actif, normalisation du numero de compte et controle d'un format IBAN simple.
- Les montants restent en `Decimal` et les devises sont normalisees en codes ISO a trois lettres.

T14 - API Transactions :
- Enregistrement des mouvements financiers (`POST /transactions`, `GET /transactions`, `GET /transactions/{id}`) dans `backend/app/api/transactions.py`.
- Mise a jour du solde seulement pour une transaction `completed`, avec verrouillage du compte, devise identique et controle de solde insuffisant.
- Les types et statuts de transaction sont limites a un vocabulaire explicite pour la demo.

T15 - Seed de donnees demo :
- Script d'injection de donnees demo `backend/app/db/seed.py` (clients PEP/sanctionnes, comptes et transactions a fort montant).
- Endpoint d'administration `POST /api/v1/seed` reserve a l'environnement `development`.
- Reinitialisation et insertion realisees dans une seule transaction avec des montants `Decimal`.

T16 - Service de Matching Local RapidFuzz :
- Integration de `rapidfuzz` pour le screening fuzzy d'identite (`fuzz.token_sort_ratio` / `fuzz.WRatio`).
- Liste de reference locale pour le screening hors-ligne et endpoints `POST /api/v1/screening/match` et `POST /api/v1/screening/client/{id}`.
- Normalisation des accents, tirets, espaces et casse ; seuil par defaut de `85` configurable avec `DEFAULT_MATCH_THRESHOLD`.

T17 - Alertes automatiques et revue humaine :
- Une alerte est creee pour une transaction au-dessus de `HIGH_TRANSACTION_AMOUNT`, pour une frequence inhabituelle et pour un match de screening client.
- Les alertes sont dedupliquees, exposees par l'API (`GET /api/v1/alerts`) et leur revue exige une note ainsi qu'une transition de statut valide.
- La migration Alembic `0004_add_alert_review_fields` conserve la note, l'acteur de demonstration et la date de revue.
- Aucun match flou ne modifie automatiquement le statut de sanction d'un client et aucune alerte ne bloque une transaction : la decision reste humaine.

T18 - Adaptateur OpenSanctions optionnel :
- Le mode par defaut `SCREENING_MODE=mock` garde la demo hors ligne avec RapidFuzz et la liste locale.
- `SCREENING_MODE=opensanctions` appelle `/match/default` lorsque `OPENSANCTIONS_API_KEY` est renseignee ; `auto` utilise OpenSanctions puis revient au mode local si le fournisseur est indisponible.
- La reponse expose le fournisseur utilise (`local` ou `opensanctions`) et les resultats externes sont normalises vers le format de screening interne.
- Verification T18 : l'adaptateur etait deja teste isolement (requete/reponse simulees via `httpx.MockTransport`), mais le comportement de bascule au niveau de l'endpoint `POST /api/v1/screening/match` ne l'etait pas. Deux tests d'integration ont ete ajoutes pour couvrir `SCREENING_MODE=auto` sans cle API (repli silencieux vers `local`, statut 200) et `SCREENING_MODE=opensanctions` sans cle API (erreur explicite 503, pas de repli silencieux).

T19 - Workflow alerte :
- Les alertes suivent les statuts `OPEN`, `VALIDATED`, `REJECTED` et `ESCALATED`; chaque revue exige une note et une transition valide.
- La migration `0004_add_alert_review_fields` conserve la note, l'acteur et la date de revue, sans decision de sanction automatique.

T20 - Audit log sur les decisions :
- Les decisions de revue, alertes automatiques et actions metier sont tracees avec `X-Actor` dans `audit_logs`.
- `GET /api/v1/audit-logs` reste une consultation filtreable en lecture seule ; les index sont apportes par `0005_add_audit_log_indexes`.

T21 - Regles transactions :
- Les alertes couvrent le seuil de montant, la frequence inhabituelle et le pays de contrepartie configure dans `HIGH_RISK_COUNTRIES`.
- `counterparty_country` est valide en ISO alpha-2 et stocke via la migration `0006_tx_counterparty_country`; la reevaluation ne modifie ni solde ni statut.

T22 - Score de risque explicable :
- `POST /api/v1/clients/{client_id}/risk-assessment` calcule et persiste un score borne entre 0 et 100, avec les niveaux `LOW`, `MEDIUM` et `HIGH`.
- Les facteurs sont exposes et l'evaluation est tracee; le score est une aide a la revue humaine, jamais une decision automatique.

T23 - Tests backend principaux :
- La suite couvre les clients, comptes, transactions, screening local et optionnel, alertes, workflow, audit, scoring et regles transactionnelles.
- Les 38 tests s'executent contre la base isolee `lbc_test` (36 + 2 tests d'integration ajoutes lors de la verification T18 sur le repli de screening).

T24 - Initialisation Vite + React + Tailwind :
- Frontend initialise dans `frontend/` avec Vite, React 19, TypeScript et Tailwind CSS v4 (`@tailwindcss/vite`).
- Tokens du design "Registre de decision" poses dans `frontend/src/index.css` via `@theme` : palette (papier, encre, tampon, ocre, vert, graphite), typographie (Yeseva One en display, Noto Sans en texte, IBM Plex Mono en donnees/montants), focus clavier visible et `prefers-reduced-motion` respecte.
- Verification de contraste WCAG AA faite sur la palette : le rouge "Tampon decision" passe (6.34:1) ; l'ocre brut ne passait pas en texte (2.34:1), une variante assombrie `--color-ocre-texte` (#8A5F0F, 4.78:1) a ete ajoutee pour tout texte/bordure, l'ocre brut restant reserve aux blocs pleins.
- Assets par defaut du template Vite retires (logos React/Vite, icones reseaux sociaux) pour eviter toute confusion avec l'identite KORA.
- CI frontend enrichie : `npm ci`, `oxlint`, `tsc -b && vite build` s'executent reellement (voir T06).
- Portee volontairement minimale : navigation, layout et hero avec photo restent a construire en T25, conformement au plan.

## 4. Tache immediate apres T24

T25 - Layout, navigation et hero avec photo :
- Construire la navigation (rail lateral bureau / onglets bas mobile) et le hero pleine largeur (~50vh) avec photo de microfinance en Afrique de l'Ouest et degrade aux couleurs de la palette.




## 5. Problemes possibles et contournements

Docker installe mais daemon arrete :
- Probleme : PostgreSQL via Docker ne demarre pas si Docker Desktop est ferme.
- Contournement : lancer Docker Desktop avant `docker compose up`.

Port PostgreSQL deja utilise :
- Probleme : Docker ne peut pas publier `localhost:5432` si un autre PostgreSQL utilise deja ce port.
- Contournement : modifier `POSTGRES_PORT` dans le fichier `.env`, par exemple `POSTGRES_PORT=5433`, puis utiliser le meme port dans pgAdmin et `DATABASE_URL`.

Mot de passe de demonstration :
- Probleme : les valeurs de `.env.example` sont publiques et ne conviennent pas a un environnement reel.
- Contournement : creer un fichier `.env` local avec un mot de passe unique avant de partager ou deployer l'application.

Mot de passe modifie apres le premier lancement Docker :
- Probleme : `POSTGRES_PASSWORD` initialise PostgreSQL seulement lors de la creation du volume ; changer `.env` seul ne modifie pas un role deja cree.
- Contournement : changer le mot de passe du role explicitement, ou reinitialiser uniquement une base de demonstration vide avec `docker compose down -v`.

pgAdmin installe mais PostgreSQL absent localement :
- Probleme : pgAdmin n'est pas une base de donnees, seulement une interface.
- Contournement : utiliser PostgreSQL dans Docker et connecter pgAdmin a `localhost:5432`.

OpenSanctions peut demander une cle API :
- Probleme : la demo peut etre bloquee si la cle API manque ou si internet est instable.
- Contournement : garder `SCREENING_MODE=mock` par defaut ou utiliser `auto`, qui revient a la liste locale si OpenSanctions est indisponible. La cle reste uniquement dans `.env` sous `OPENSANCTIONS_API_KEY`.

Couverture de test du repli de screening (T18) :
- Probleme : le repli `auto` -> `local` et le refus explicite du mode `opensanctions` sans cle etaient corrects dans le code mais non verifies par un test au niveau de l'endpoint, seulement au niveau de l'adaptateur isole.
- Contournement : deux tests d'integration ont ete ajoutes dans `backend/tests/test_opensanctions.py` (`test_screening_endpoint_auto_mode_falls_back_to_local_without_api_key` et `test_screening_endpoint_opensanctions_mode_without_key_returns_503`) en surchargeant la dependance `get_settings` de FastAPI pour simuler chaque mode sans dependre de l'environnement local.

GitHub CLI installe mais parfois non visible avec `gh` :
- Probleme : le terminal peut ne pas trouver `gh` dans le PATH.
- Contournement : utiliser le chemin complet `C:\Program Files\GitHub CLI\gh.exe`.

GitHub Projects demande un scope supplementaire :
- Probleme : la commande `gh project list` demande le scope `read:project`.
- Contournement : utiliser issues + milestone pour le suivi immediat, puis lancer `gh auth refresh -s project` si un vrai tableau Project est necessaire.

CI creee avant le code applicatif :
- Probleme : il n'y a pas encore de backend FastAPI ni de frontend Vite React.
- Contournement : mettre des workflows structurels maintenant, puis les transformer en tests/builds reels aux taches T07 et T24 (fait pour les deux).

Contraste de la palette de design :
- Probleme : l'ocre brut de la palette "Registre de decision" (#C8922D) est trop clair pour du texte ou des bordures sur le fond papier (#E7EEE8), ratio WCAG 2.34:1, sous le seuil AA de 4.5:1.
- Contournement : `--color-ocre-texte` (#8A5F0F, ratio 4.78:1) est reserve au texte et aux bordures ; l'ocre brut reste utilisable uniquement pour des blocs pleins (fond colore avec texte clair dessus).

Template Vite avec assets par defaut :
- Probleme : le scaffold `create-vite` le plus recent inclut des logos React/Vite et des icones reseaux sociaux non lies au projet (`hero.png`, `vite.svg`, `react.svg`, `favicon.svg` de marque, `icons.svg`).
- Contournement : ces fichiers ont ete retires des la creation du frontend (T24) et remplaces par un favicon minimal aux couleurs KORA, avant tout autre developpement.

Versions Python multiples :
- Probleme : `python` et `py` peuvent pointer vers des versions differentes.
- Contournement : utiliser une commande explicite, par exemple `py -3.14`, puis creer un environnement virtuel dans `backend/.venv`.

Tests backend avec dependances non installees :
- Probleme : `pytest` echoue si FastAPI, httpx ou pytest ne sont pas installes.
- Contournement : installer `backend/requirements-dev.txt` dans un environnement virtuel local avant les tests.

Warning FastAPI TestClient :
- Probleme : les tests passent, mais Starlette affiche un avertissement indiquant que le support `httpx` classique est deprecie dans le TestClient.
- Contournement : garder le test actuel car il est fonctionnel, puis migrer vers `httpx2` ou vers un client de test asynchrone si l'avertissement devient bloquant.

Migrations Alembic non appliquees :
- Probleme : l'API ne cree plus de tables automatiquement, donc une nouvelle base est vide tant que les migrations ne sont pas lancees.
- Contournement : executer `alembic upgrade head` dans `backend` avant de demarrer l'API.

Tests et base de demonstration :
- Probleme : les endpoints de seed sont destructifs pour leur base cible.
- Contournement : les tests utilisent exclusivement `lbc_test`; ne jamais definir `TEST_DATABASE_URL` vers `lbc_db`.

Matching local :
- Probleme : un score RapidFuzz est un indicateur de similarite, pas une preuve de sanction ou une decision de conformite.
- Contournement : conserver le resultat comme alerte a revoir et utiliser une source officielle avant toute decision.

Alertes non bloquantes :
- Probleme : une erreur technique lors de l'enregistrement d'une alerte ne doit pas annuler une transaction deja acceptee.
- Contournement : la transaction reste enregistree ; surveiller les erreurs de persistance des alertes et les rejouer par une tache d'administration en production.

Revue manuelle demo :
- Probleme : T17 utilise l'acteur `system` car le module d'authentification n'est pas encore implemente.
- Contournement : T18 accepte provisoirement l'en-tete `X-Actor` et conserve une trace en base ; JWT remplacera ensuite cette valeur par l'utilisateur connecte.

Audit sans alerte :
- Probleme : un screening sans resultat ou une transaction ordinaire peut ne pas creer d'alerte, tout en restant une action importante de conformite.
- Contournement : T19 cree aussi un evenement d'audit metier independant de l'alerte, avec un resume sans donnees personnelles superflues.

Scoring de risque :
- Probleme : un score calcule peut sembler etre une decision de conformite s'il n'est pas explique.
- Contournement : T20 expose les facteurs et le niveau, conserve les champs de sanction comme des valeurs renseignees manuellement et n'ajoute aucun blocage automatique.

Pays a risque et migrations :
- Probleme : une liste de pays figee dans le code devient vite obsolete et une revision Alembic trop longue ne peut pas etre stockee par PostgreSQL.
- Contournement : `HIGH_RISK_COUNTRIES` est defini par la politique approuvee de l'institution et les identifiants Alembic restent inferieurs ou egaux a 32 caracteres.

## 6. Commandes utiles

Verifier Git :

```powershell
& "C:\Program Files\Git\cmd\git.exe" status --short --branch
```

Verifier GitHub :

```powershell
& "C:\Program Files\GitHub CLI\gh.exe" auth status
```

Voir le repository distant :

```powershell
& "C:\Program Files\GitHub CLI\gh.exe" repo view Aquilas2005a/lbc-ft-fp-app
```

Lister les issues du MVP :

```powershell
& "C:\Program Files\GitHub CLI\gh.exe" issue list --repo Aquilas2005a/lbc-ft-fp-app --milestone "MVP 1 - API utilisable"
```

Rafraichir les scopes GitHub pour utiliser GitHub Projects :

```powershell
& "C:\Program Files\GitHub CLI\gh.exe" auth refresh -s project
```

Demarrer plus tard PostgreSQL :

```powershell
docker compose up -d db
```

Verifier PostgreSQL :

```powershell
docker compose ps
docker compose exec -T db pg_isready -U lbc_user -d lbc_db
```

Arreter PostgreSQL sans supprimer les donnees :

```powershell
docker compose down
```

Consulter le guide pgAdmin :

```powershell
Get-Content docs/database.md
```

Installer les dependances backend :

```powershell
cd backend
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Tester le backend :

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
```

Demarrer l'API FastAPI :

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 7. Liens

- Repository GitHub : https://github.com/Aquilas2005a/lbc-ft-fp-app
- Documentation OpenSanctions matching : https://www.opensanctions.org/docs/api/matching/
- Documentation FastAPI : https://fastapi.tiangolo.com/
- Documentation React : https://react.dev/
