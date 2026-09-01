import os
import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient, events, functions
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

# Permission sets for Individual Users
MUTE_USER = ChatBannedRights(until_date=None, send_messages=True)
UNMUTE_USER = ChatBannedRights(until_date=None, send_messages=False)
BAN_USER = ChatBannedRights(until_date=None, view_messages=True)
UNBAN_USER = ChatBannedRights(until_date=None, view_messages=False)

# Group-wide permissions (Lock / Unlock All)
GROUP_LOCK_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True
)

GROUP_UNLOCK_RIGHTS = ChatBannedRights(
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
            "• `/lock` ya `/lock all` - Group lock kar dega\n"
            "• `/unlock` ya `/unlock all` - Group unlock karega\n"
            "• `/ban <user>` - User ban\n"
            "• `/unban <user>` - User unban\n"
            "• `/mute <user>` - User mute\n"
            "• `/tmute <user> <minutes>` - Temp mute\n"
            "• `/unmute <user>` - User unmute\n"
            "• `/say <text>` - Group me announcement"
        )
        await event.reply(msg)

    # --- LOCK GROUP ---
    elif cmd == "/lock":
        try:
            group_peer = await client.get_input_entity(TARGET_GROUP_ID)
            await client(functions.messages.EditChatDefaultBannedRightsRequest(
                peer=group_peer,
                banned_rights=GROUP_LOCK_RIGHTS
            ))
            await event.reply("🔒 Group lock ho chuka hai.")
            await client.send_message(TARGET_GROUP_ID, "🔒 **Group has been locked by Admin.**")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    # --- UNLOCK GROUP ---
    elif cmd == "/unlock":
        try:
            group_peer = await client.get_input_entity(TARGET_GROUP_ID)
            await client(functions.messages.EditChatDefaultBannedRightsRequest(
                peer=group_peer,
                banned_rights=GROUP_UNLOCK_RIGHTS
            ))
            await event.reply("🔓 Group unlock ho chuka hai.")
            await client.send_message(TARGET_GROUP_ID, "🔓 **Group has been unlocked.**")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    # --- BAN ---
    elif cmd == "/ban":
        if len(parts) < 2:
            await event.reply("⚠️ Format: `/ban @username` ya `/ban id`")
            return
        try:
            user = await client.get_entity(parts[1])
            await client.edit_permissions(TARGET_GROUP_ID, user, BAN_USER)
            await event.reply(f"✅ User **{user.first_name}** (`{user.id}`) ban ho gaya.")
            await client.send_message(TARGET_GROUP_ID, f"🚫 **User {user.first_name} has been banned.**")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    # --- UNBAN ---
    elif cmd == "/unban":
        if len(parts) < 2:
            await event.reply("⚠️ Format: `/unban @username` ya `/unban id`")
            return
        try:
            user = await client.get_entity(parts[1])
            await client.edit_permissions(TARGET_GROUP_ID, user, UNBAN_USER)
            await event.reply(f"✅ User **{user.first_name}** (`{user.id}`) unban ho gaya.")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    # --- MUTE ---
    elif cmd == "/mute":
        if len(parts) < 2:
            await event.reply("⚠️ Format: `/mute @username`")
            return
        try:
            user = await client.get_entity(parts[1])
            await client.edit_permissions(TARGET_GROUP_ID, user, MUTE_USER)
            await event.reply(f"🔇 User **{user.first_name}** mute ho gaya.")
            await client.send_message(TARGET_GROUP_ID, f"🔇 **User {user.first_name} has been muted.**")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    # --- TEMP MUTE ---
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

    # --- UNMUTE ---
    elif cmd == "/unmute":
        if len(parts) < 2:
            await event.reply("⚠️ Format: `/unmute @username`")
            return
        try:
            user = await client.get_entity(parts[1])
            await client.edit_permissions(TARGET_GROUP_ID, user, UNMUTE_USER)
            await event.reply(f"🔊 User **{user.first_name}** unmute ho gaya.")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    # --- SAY / ANNOUNCE ---
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
