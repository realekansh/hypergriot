import asyncio
from datetime import datetime, timezone
import logging

from db.session import SessionLocal
from db import models
from services.action_service import perform_action

# Configure logger
logger = logging.getLogger("unban_worker")
logging.basicConfig(level=logging.INFO)

CHECK_INTERVAL = 15  # seconds between scans

async def process_expired_bans(client):
    """
    Find expired bans (end_ts <= now and active=True) and unban them.
    Uses action_service.perform_action to centralize logic.
    """
    while True:
        try:
            now = datetime.now(timezone.utc)
            with SessionLocal() as db:
                expired = db.query(models.Ban).filter(models.Ban.active == True, models.Ban.end_ts != None, models.Ban.end_ts <= now).all()
                for b in expired:
                    logger.info(f"Unbanning user {b.user_id} from chat {b.chat_id} (ban id {b.id})")
                    # perform unban via action_service (synchronous call inside event loop)
                    try:
                        res = perform_action(client=client, chat_id=b.chat_id, issuer_id=None, target_user_id=b.user_id, action="unban")
                        if res.get("ok"):
                            # mark DB record inactive
                            b.active = False
                            db.add(b)
                            db.commit()
                    except Exception as e:
                        logger.exception("Failed to unban: %s", e)
        except Exception:
            logger.exception("Error scanning expired bans")
        await asyncio.sleep(CHECK_INTERVAL)

async def process_expired_mutes(client):
    """
    Find expired mutes and unmute them.
    """
    while True:
        try:
            now = datetime.now(timezone.utc)
            with SessionLocal() as db:
                expired = db.query(models.Mute).filter(models.Mute.active == True, models.Mute.end_ts != None, models.Mute.end_ts <= now).all()
                for m in expired:
                    logger.info(f"Unmuting user {m.user_id} in chat {m.chat_id} (mute id {m.id})")
                    try:
                        res = perform_action(client=client, chat_id=m.chat_id, issuer_id=None, target_user_id=m.user_id, action="unmute")
                        if res.get("ok"):
                            m.active = False
                            db.add(m)
                            db.commit()
                    except Exception as e:
                        logger.exception("Failed to unmute: %s", e)
        except Exception:
            logger.exception("Error scanning expired mutes")
        await asyncio.sleep(CHECK_INTERVAL)

# Export an async runner to be called with a running pyrogram Client
async def run_unban_workers(client):
    await asyncio.gather(
        process_expired_bans(client),
        process_expired_mutes(client),
    )

if __name__ == "__main__":
    print("Run scheduler.py with your pyrogram client to execute workers.")
