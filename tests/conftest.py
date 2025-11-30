import sys, os
# ensure project root is first on sys.path so local packages shadow site-packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
# ensure an event loop exists during pytest collection so libraries like pyrogram (sync shim)
# don't crash when imported. This creates a fresh loop for the main thread.
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())


import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import models
from db.session import Base as BaseFromSession

# Create an in-memory sqlite engine for tests
TEST_DB_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")

@pytest.fixture(scope="session")
def engine():
    eng = create_engine(TEST_DB_URL, echo=False)
    # Use the declarative Base from your project to create tables
    BaseFromSession.metadata.create_all(bind=eng)
    return eng

@pytest.fixture()
def db_session(engine):
    Session = sessionmaker(bind=engine)
    s = Session()
    try:
        yield s
    finally:
        s.close()