import os
import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import ChatBannedRights

# Config from Environment Variables
API_ID = int(os.environ.get("API_ID", "34420912"))
API_HASH = os.environ.get("API_HASH", "349f4d7dbd04aca92c2cace2da28fe14")
SESSION_STRING = os.environ.get("SESSION_STRING")

# Authorized Friends (User IDs)
ALLOWED_USERS = [
    8988599574,  # Dost 1
    8401097557   # Dost 2
]

# Target Group ID
TARGET_GROUP_ID = int(os.environ.get("TARGET_GROUP_ID", "-1003928377196"))

if not SESSION_STRING:
    raise ValueError("SESSION_STRING is missing in Railway Variables!")

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Correct Permission Sets
MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)
UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)
BAN_RIGHTS = ChatBannedRights(until_date=None, view_messages=True)
UNBAN_RIGHTS = ChatBannedRights(until_date=None, view_messages=False)

LOCK_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True
)

UNLOCK_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=False,
    send_media=False,
    send_stickers=False,
    send_gifs=False,
    send_games=False,
    send_inline=False,
    embed_links=False
)

@client.on(events.NewMessage(incoming=True))
async def handle_commands(event):
    if not event.is_private:
        return

    sender_id = event.sender_id
    if sender_id not in ALLOWED_USERS:
        return

    text = event.raw_text.strip()
    parts = text.split()
    if not parts:
        return

    cmd = parts[0].lower()

    if cmd in ["/start", "/help"]:
        msg = (
            "🛡️ **Admin Relay Tool Active**\n\n"
            "• `/ban <username/id>`\n"
            "• `/unban <username/id>`\n"
            "• `/mute <username/id>`\n"
            "• `/unmute <username/id>`\n"
            "• `/tmute <username/id> <minutes>`\n"
            "• `/lock`\n"
            "• `/unlock`\n"
            "• `/say <message>`"
        )
        await event.reply(msg)

    elif cmd == "/ban":
        if len(parts) < 2:
            await event.reply("⚠️ Format: `/ban @username` ya `/ban id`")
            return
        try:
            user = await client.get_entity(parts[1])
            await client.edit_permissions(TARGET_GROUP_ID, user, BAN_RIGHTS)
            await event.reply(f"✅ User **{user.first_name}** (`{user.id}`) ko ban kar diya gaya.")
            await client.send_message(TARGET_GROUP_ID, f"🚫 **User {user.first_name} has been banned.**")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    elif cmd == "/unban":
        if len(parts) < 2:
            await event.reply("⚠️ Format: `/unban @username` ya `/unban id`")
            return
        try:
            user = await client.get_entity(parts[1])
            await client.edit_permissions(TARGET_GROUP_ID, user, UNBAN_RIGHTS)
            await event.reply(f"✅ User **{user.first_name}** (`{user.id}`) unban ho gaya.")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    elif cmd == "/mute":
        if len(parts) < 2:
            await event.reply("⚠️ Format: `/mute @username`")
            return
        try:
            user = await client.get_entity(parts[1])
            await client.edit_permissions(TARGET_GROUP_ID, user, MUTE_RIGHTS)
            await event.reply(f"🔇 User **{user.first_name}** mute ho gaya.")
            await client.send_message(TARGET_GROUP_ID, f"🔇 **User {user.first_name} has been muted.**")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    elif cmd == "/tmute":
        if len(parts) < 3:
            await event.reply("⚠️ Format: `/tmute @username <minutes>`")
            return
        try:
            duration = int(parts[2])
            until_date = datetime.now() + timedelta(minutes=duration)
            user = await client.get_entity(parts[1])
            temp_rights = ChatBannedRights(until_date=until_date, send_messages=True)
            await client.edit_permissions(TARGET_GROUP_ID, user, temp_rights)
            await event.reply(f"⏳ User **{user.first_name}** `{duration}` min ke liye mute ho gaya.")
            await client.send_message(TARGET_GROUP_ID, f"🔇 **{user.first_name}** is muted for `{duration}` minutes.")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    elif cmd == "/unmute":
        if len(parts) < 2:
            await event.reply("⚠️ Format: `/unmute @username`")
            return
        try:
            user = await client.get_entity(parts[1])
            await client.edit_permissions(TARGET_GROUP_ID, user, UNMUTE_RIGHTS)
            await event.reply(f"🔊 User **{user.first_name}** unmute ho gaya.")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    elif cmd == "/lock":
        try:
            await client.edit_permissions(TARGET_GROUP_ID, LOCK_RIGHTS)
            await event.reply("🔒 Group lock ho gaya.")
            await client.send_message(TARGET_GROUP_ID, "🔒 **Group has been locked by Admin.**")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    elif cmd == "/unlock":
        try:
            await client.edit_permissions(TARGET_GROUP_ID, UNLOCK_RIGHTS)
            await event.reply("🔓 Group unlock ho gaya.")
            await client.send_message(TARGET_GROUP_ID, "🔓 **Group has been unlocked.**")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    elif cmd == "/say":
        if len(parts) < 2:
            await event.reply("⚠️ Format: `/say <text>`")
            return
        msg_text = text.split(None, 1)[1]
        try:
            await client.send_message(TARGET_GROUP_ID, msg_text)
            await event.reply("✅ Sent to group.")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

print("Userbot is live and listening...")
client.start()
client.run_until_disconnected()
