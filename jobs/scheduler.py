import asyncio
import os
from pyrogram import Client
from dotenv import load_dotenv
from jobs.unban_worker import run_unban_workers
from jobs.purge_worker import run_purge_worker
import logging

load_dotenv()
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jobs.scheduler")

async def main():
    # start a pyrogram client (bot)
    app = Client("hypergriot-jobs", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
    async with app:
        logger.info("Jobs client started")
        # run workers concurrently
        await asyncio.gather(
            run_unban_workers(app),
            run_purge_worker(app),
        )

if __name__ == "__main__":
    asyncio.run(main())
