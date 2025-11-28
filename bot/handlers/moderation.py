# bot/handlers/moderation.py
from pyrogram import Client, filters
from bot.commands import command
from bot.utils import resolve_user, is_admin, parse_time_to_seconds, human_readable
from services import action_service
import asyncio

# Helpers
async def resolve_target(client, message, args):
    # If reply, prefer replied user
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user, message.reply_to_message.message_id, args
    if not args:
        return None, None, args
    target_identifier = args.pop(0)
    target = await resolve_user(client, message.chat.id, target_identifier)
    return target, None, args

async def check_permissions(client, chat_id, issuer_id, target_id):
    # basic checks: issuer must be admin and issuer must outrank target (simple)
    if not await is_admin(client, chat_id, issuer_id):
        return False, "You must be an admin to use this."
    # don't allow moderating chat owner via bot; check target's status
    try:
        tmember = await client.get_chat_member(chat_id, target_id)
        if tmember.status in ("creator",):
            return False, "Cannot moderate chat owner."
        # if target is admin, block (unless issuer is creator) - simple policy
        if tmember.status == "administrator":
            issuer_member = await client.get_chat_member(chat_id, issuer_id)
            if issuer_member.status != "creator":
                return False, "Cannot moderate another admin (owner only)."
    except Exception:
        # if we can't fetch member, continue (user may not be in chat)
        pass
    return True, None

# BAN variants
@Client.on_message(filters.command(["ban", "sban", "dban", "tban"]) & filters.group)
async def ban_handler(client: Client, message):
    cmd = message.command[0].lower()
    args = message.command[1:]
    # parse reason/time
    reason = None
    duration = None
    # dban must be reply
    if cmd == "dban" and not message.reply_to_message:
        return await message.reply_text("Use /dban as a reply to the offending message.")

    # resolve target
    target, replied_msg_id, remaining = await resolve_target(client, message, args)
    if not target:
        return await message.reply_text("Target not found. Use reply or provide @username or user id.")

    # special: tban requires a duration as next arg
    if cmd == "tban":
        if not remaining:
            return await message.reply_text("Usage: /tban <user|reply> <time> [reason]")
        duration = remaining.pop(0)
        reason = " ".join(remaining) if remaining else None
    else:
        reason = " ".join(remaining) if remaining else None

    # permissions
    ok, error = await check_permissions(client, message.chat.id, message.from_user.id, target.id)
    if not ok:
        return await message.reply_text(error)

    # delete message if dban
    message_id_deleted = None
    if cmd == "dban" and message.reply_to_message:
        try:
            message_id_deleted = message.reply_to_message.message_id
            await client.delete_messages(message.chat.id, message_id_deleted)
        except Exception:
            message_id_deleted = None

    # perform action
    action = "ban" if cmd == "ban" or cmd == "dban" else "tban"
    if cmd == "sban":
        # silent ban
        pass

    res = await action_service.perform_action(client=client, chat_id=message.chat.id, issuer_id=message.from_user.id, target_user_id=target.id, action=action if cmd!="sban" else "ban", duration=duration, reason=reason, silent=(cmd=="sban"))
    if not res.get("ok"):
        return await message.reply_text(f"Failed: {res.get('error')}")
    if cmd != "sban":
        if action == "tban":
            try:
                secs = parse_time_to_seconds(duration)
                await message.reply_text(f"Banned {target.mention} for {human_readable(secs)}. Reason: {reason or '-'}")
            except Exception:
                await message.reply_text(f"Banned {target.mention}. Reason: {reason or '-'}")
        else:
            await message.reply_text(f"Banned {target.mention}. Reason: {reason or '-'}")
    else:
        # silent: try DM issuer
        try:
            await client.send_message(message.from_user.id, f"Silent ban performed: {target.mention}. Reason: {reason or '-'}")
        except Exception:
            pass

# unban
@Client.on_message(filters.command("unban") & filters.group)
async def unban_handler(client: Client, message):
    args = message.command[1:]
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    else:
        if not args:
            return await message.reply_text("Usage: /unban <user>")
        target = await resolve_user(client, message.chat.id, args[0])
    if not target:
        return await message.reply_text("Target not found.")
    ok, error = await check_permissions(client, message.chat.id, message.from_user.id, target.id)
    if not ok:
        return await message.reply_text(error)
    res = await action_service.perform_action(client=client, chat_id=message.chat.id, issuer_id=message.from_user.id, target_user_id=target.id, action="unban")
    if not res.get("ok"):
        return await message.reply_text(f"Failed: {res.get('error')}")
    await message.reply_text(f"Unbanned {target.mention}.")

# MUTE variants
@Client.on_message(filters.command(["mute","tmute","smute","dmute"]) & filters.group)
async def mute_handler(client: Client, message):
    cmd = message.command[0].lower()
    args = message.command[1:]
    if cmd == "dmute" and not message.reply_to_message:
        return await message.reply_text("Use /dmute as a reply to the offending message.")
    target, replied_msg_id, remaining = await resolve_target(client, message, args)
    if not target:
        return await message.reply_text("Target not found.")
    duration = None
    reason = None
    if cmd == "tmute":
        if not remaining:
            return await message.reply_text("Usage: /tmute <user|reply> <time> [reason]")
        duration = remaining.pop(0)
        reason = " ".join(remaining) if remaining else None
    else:
        reason = " ".join(remaining) if remaining else None

    ok, error = await check_permissions(client, message.chat.id, message.from_user.id, target.id)
    if not ok:
        return await message.reply_text(error)

    message_id_deleted = None
    if cmd == "dmute" and message.reply_to_message:
        try:
            message_id_deleted = message.reply_to_message.message_id
            await client.delete_messages(message.chat.id, message_id_deleted)
        except Exception:
            message_id_deleted = None

    action = "mute" if cmd in ("mute","smute","dmute") else "tmute"
    res = await action_service.perform_action(client=client, chat_id=message.chat.id, issuer_id=message.from_user.id, target_user_id=target.id, action=action if cmd!="smute" else "mute", duration=duration, reason=reason, silent=(cmd=="smute"))
    if not res.get("ok"):
        return await message.reply_text(f"Failed: {res.get('error')}")
    if cmd != "smute":
        if action == "tmute":
            try:
                secs = parse_time_to_seconds(duration)
                await message.reply_text(f"Muted {target.mention} for {human_readable(secs)}. Reason: {reason or '-'}")
            except Exception:
                await message.reply_text(f"Muted {target.mention}. Reason: {reason or '-'}")
        else:
            await message.reply_text(f"Muted {target.mention}. Reason: {reason or '-'}")
    else:
        try:
            await client.send_message(message.from_user.id, f"Silent mute performed: {target.mention}. Reason: {reason or '-'}")
        except Exception:
            pass

# unmute
@Client.on_message(filters.command("unmute") & filters.group)
async def unmute_handler(client: Client, message):
    args = message.command[1:]
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    else:
        if not args:
            return await message.reply_text("Usage: /unmute <user>")
        target = await resolve_user(client, message.chat.id, args[0])
    if not target:
        return await message.reply_text("Target not found.")
    ok, error = await check_permissions(client, message.chat.id, message.from_user.id, target.id)
    if not ok:
        return await message.reply_text(error)
    res = await action_service.perform_action(client=client, chat_id=message.chat.id, issuer_id=message.from_user.id, target_user_id=target.id, action="unmute")
    if not res.get("ok"):
        return await message.reply_text(f"Failed: {res.get('error')}")
    await message.reply_text(f"Unmuted {target.mention}.")

# KICK variants
@Client.on_message(filters.command(["kick","kuck","skick","dkick"]) & filters.group)
async def kick_handler(client: Client, message):
    cmd = message.command[0].lower()
    args = message.command[1:]
    if cmd == "dkick" and not message.reply_to_message:
        return await message.reply_text("Use /dkick as a reply to the offending message.")
    target, replied_msg_id, remaining = await resolve_target(client, message, args)
    if not target:
        return await message.reply_text("Target not found.")
    reason = " ".join(remaining) if remaining else None
    ok, error = await check_permissions(client, message.chat.id, message.from_user.id, target.id)
    if not ok:
        return await message.reply_text(error)

    message_id_deleted = None
    if cmd == "dkick" and message.reply_to_message:
        try:
            message_id_deleted = message.reply_to_message.message_id
            await client.delete_messages(message.chat.id, message_id_deleted)
        except Exception:
            message_id_deleted = None

    res = await action_service.perform_action(client=client, chat_id=message.chat.id, issuer_id=message.from_user.id, target_user_id=target.id, action="kick", reason=reason, silent=(cmd=="skick"))
    if not res.get("ok"):
        return await message.reply_text(f"Failed: {res.get('error')}")
    if cmd != "skick":
        await message.reply_text(f"Kicked {target.mention}. Reason: {reason or '-'}")
    else:
        try:
            await client.send_message(message.from_user.id, f"Silent kick performed: {target.mention}. Reason: {reason or '-'}")
        except:
            pass

# PURGE (simple)
@Client.on_message(filters.command("purge") & filters.group)
async def purge_handler(client: Client, message):
    # support: /purge 50  OR reply to message to delete from replied->now
    args = message.command[1:]
    if message.reply_to_message:
        start_id = message.reply_to_message.message_id
        async for m in client.iter_history(message.chat.id, offset_id=message.message_id, reverse=False):
            # iterate between start and now - simple approach (can be improved)
            break
        # For now: simple reply
        return await message.reply_text("Purge by range not implemented in this placeholder. Use the purge worker or admin UI.")
    else:
        count = 50
        if args and args[0].isdigit():
            count = min(500, int(args[0]))
        # gather message ids
        mids = []
        async for m in client.iter_history(message.chat.id, limit=count+1):
            if m.message_id == message.message_id:
                continue
            mids.append(m.message_id)
        if not mids:
            return await message.reply_text("No messages to purge.")
        # delete in batches
        BATCH = 100
        deleted = 0
        for i in range(0, len(mids), BATCH):
            batch = mids[i:i+BATCH]
            try:
                await client.delete_messages(message.chat.id, batch)
                deleted += len(batch)
            except Exception:
                # try one-by-one
                for mid in batch:
                    try:
                        await client.delete_messages(message.chat.id, mid)
                        deleted += 1
                    except Exception:
                        pass
        await message.reply_text(f"Purged {deleted} messages.")
