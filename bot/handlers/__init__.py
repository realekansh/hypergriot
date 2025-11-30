# handlers package initializer
# When adding handlers, import them here so registration side-effects occur.
from . import moderation
from . import help
# append a global handler to call anti_raid on new messages
from pyrogram import Client, filters
from . import moderation  # existing import
from services import anti_raid

@Client.on_message(filters.group & ~filters.edited)
async def _global_message_monitor(client, message):
    try:
        await anti_raid.process_message_event(client, message)
    except Exception:
        # swallow errors so we don't crash on unhandled errors
        pass
