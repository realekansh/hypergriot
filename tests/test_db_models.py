from db import models
from datetime import datetime, timezone

def test_modlog_crud(db_session):
    # create one
    m = models.ModLog(
        chat_id = -1001,
        moderator_id = 12345,
        action = "TEST",
        target_user = 54321,
        reason = "unit test",
        metadata_json = {"k":"v"},
        created_at = datetime.now(timezone.utc)
    )
    db_session.add(m)
    db_session.commit()

    # query back
    row = db_session.query(models.ModLog).filter(models.ModLog.chat_id == -1001).first()
    assert row is not None
    assert row.action == "TEST"
    assert getattr(row, "metadata_json", {}) == {"k":"v"}
