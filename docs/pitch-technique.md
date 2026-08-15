# KORA — pitch technique

## Thèse
KORA transforme la conformité LBC/FT/FP en un **registre de décision exploitable sur le terrain** : vérifier, décider, tracer.

## Architecture
- **Frontend** : React + TypeScript + Tailwind CSS v4, avec navigation par rôle et composants orientés dossier.
- **Backend** : FastAPI + SQLAlchemy + PostgreSQL, migrations Alembic et API versionnée `/api/v1`.
- **Analyse** : RapidFuzz pour le screening local, OpenSanctions optionnel, score de risque explicable et IsolationForest sur données simulées pour le bonus IA.
- **Exploitation** : Docker Compose regroupe PostgreSQL, API FastAPI et frontend Nginx.

## Identité produit
Palette : `papier #E7EEE8`, `encre #17324D`, `tampon #9B2948`, `ocre #C8922D`, `vert #3F7057`, avec `ocre-texte #8A5F0F` pour le texte lisible. Typographies : Yeseva One pour les titres, Noto Sans pour le texte, IBM Plex Mono pour les données.

## Démo en 90 secondes
1. Ouvrir le tableau superviseur et lire la bande de risque.
2. Ouvrir les alertes, sélectionner une alerte puis justifier la décision.
3. Créer ou consulter un client et enregistrer un mouvement.
4. Exporter les alertes ou transactions en CSV.
5. Montrer le graphique de criticité, la timeline de risque et le endpoint IA simulé.
6. Terminer par `docker compose up --build` pour montrer le déploiement reproductible.
