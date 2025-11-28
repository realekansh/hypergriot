Extras — handy dev scripts for HyperGriot
----------------------------------------

Files:
- scripts/start-dev.sh   : Creates sqlite tables (if using sqlite) and runs the web dashboard.
- scripts/backup_db.sh   : Simple timestamped backup for sqlite DB (copies hypergriot.db).
- extras/export_modlogs.py : Dump modlogs to JSON for offline analysis or migration.
- extras/.env.example    : Example env file. Copy to project root as .env and edit.

Quick usage:
1) Copy env example:
   cp extras/.env.example .env
   # edit .env with nano or your editor

2) Start dev dashboard:
   ./scripts/start-dev.sh

3) Create DB backup:
   ./scripts/backup_db.sh

4) Export modlogs:
   python extras/export_modlogs.py --out mymodlogs.json

Notes:
- These are dev helpers. For production use proper backup strategies (pg_dump for Postgres, rotated storage).
- The scripts assume you run them from the repo root.
