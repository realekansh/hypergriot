Alembic migrations

To initialize alembic (first time):
1. pip install alembic
2. from repo root run:
   alembic init db/migrations

Then edit alembic.ini and env.py to point to your DATABASE_URL and import the SQLAlchemy Base from db.session:

In db/migrations/env.py, set:
    from db.session import Base, engine
    target_metadata = Base.metadata

Create a migration after models change:
    alembic revision --autogenerate -m "create initial tables"

Apply migrations:
    alembic upgrade head

Note: If you prefer not to use Alembic yet, you can create tables directly:
    python -c "from db.session import engine, Base; Base.metadata.create_all(bind=engine)"
