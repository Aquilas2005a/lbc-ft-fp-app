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

## 4. Tache immediate a faire apres T03

T04 - Creer le tableau GitHub Issues/Project :
- Creer une issue GitHub par tache progressive.
- Ajouter au minimum les issues T04 a T10 pour organiser le debut.
- Prioriser les taches backend et Docker avant l'interface.

Objectif immediat :
- Avoir une vision claire du travail dans GitHub.
- Permettre a chaque etudiant de prendre une tache courte sans confusion.

## 5. Problemes possibles et contournements

Docker installe mais daemon arrete :
- Probleme : PostgreSQL via Docker ne demarre pas si Docker Desktop est ferme.
- Contournement : lancer Docker Desktop avant `docker compose up`.

pgAdmin installe mais PostgreSQL absent localement :
- Probleme : pgAdmin n'est pas une base de donnees, seulement une interface.
- Contournement : utiliser PostgreSQL dans Docker et connecter pgAdmin a `localhost:5432`.

OpenSanctions peut demander une cle API :
- Probleme : la demo peut etre bloquee si la cle API manque ou si internet est instable.
- Contournement : garder un mode mock avec une petite liste locale de noms a risque.

GitHub CLI installe mais parfois non visible avec `gh` :
- Probleme : le terminal peut ne pas trouver `gh` dans le PATH.
- Contournement : utiliser le chemin complet `C:\Program Files\GitHub CLI\gh.exe`.

Versions Python multiples :
- Probleme : `python` et `py` peuvent pointer vers des versions differentes.
- Contournement : utiliser une commande explicite, par exemple `py -3.14`, puis creer un environnement virtuel dans `backend/.venv`.

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

Demarrer plus tard PostgreSQL :

```powershell
docker compose up -d db
```

## 7. Liens

- Repository GitHub : https://github.com/Aquilas2005a/lbc-ft-fp-app
- Documentation OpenSanctions matching : https://www.opensanctions.org/docs/api/matching/
- Documentation FastAPI : https://fastapi.tiangolo.com/
- Documentation React : https://react.dev/

