import os
import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient, events, functions
from telethon.tl.types import ChatBannedRights

# Config from Railway Environment Variables
API_ID = int(os.environ.get("API_ID", "34420912"))
API_HASH = os.environ.get("API_HASH", "349f4d7dbd04aca92c2cace2da28fe14")
SESSION_STRING = os.environ.get("SESSION_STRING")

# Target Group ID
TARGET_GROUP_ID = int(os.environ.get("TARGET_GROUP_ID", "-1003928377196"))

# Yahan doston ki Telegram User IDs daalein
# Agar dost ko apni ID nahi pata, toh wo PM me "/id" bhej kar check kar sakta hai
ALLOWED_USERS = [
    8988599574,  # Dost 1
    8401097557   # Dost 2
]

if not SESSION_STRING:
    raise ValueError("SESSION_STRING is missing in Railway Variables!")

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Permission sets
MUTE_USER = ChatBannedRights(until_date=None, send_messages=True)
UNMUTE_USER = ChatBannedRights(until_date=None, send_messages=False)
BAN_USER = ChatBannedRights(until_date=None, view_messages=True)
UNBAN_USER = ChatBannedRights(until_date=None, view_messages=False)

GROUP_LOCK = ChatBannedRights(
    until_date=None,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True
)

GROUP_UNLOCK = ChatBannedRights(
    until_date=None,
    send_messages=False,
    send_media=False,
    send_stickers=False,
    send_gifs=False,
    send_games=False,
    send_inline=False,
    embed_links=False
)

async def resolve_target(client, identifier):
    if str(identifier).lstrip('-').isdigit():
        return await client.get_entity(int(identifier))
    return await client.get_entity(identifier)

@client.on(events.NewMessage(incoming=True))
async def handle_commands(event):
    if not event.is_private:
        return

    sender_id = event.sender_id
    raw_text = event.raw_text.strip()

    # --- ID Check Command (Har koi apni ID dekh sake) ---
    if raw_text.lower() in ["/id", "/myid"]:
        await event.reply(f"🆔 **Aapki Asli Telegram ID hai:** `{sender_id}`")
        return

    # Authorized user check
    if sender_id not in ALLOWED_USERS:
        return

    parts = raw_text.split()
    if not parts:
        return

    cmd = parts[0].lower()

    # --- 1. /cmm (DIRECT GROUP MESSAGE/COMMAND RELAY) ---
    if cmd == "/cmm":
        if len(parts) < 2:
            await event.reply("⚠️ **Format:** `/cmm <kuch bhi message ya command>`\n*Example:* `/cmm /lock` ya `/cmm Hello guys`")
            return
        # /cmm ke baad ka saara text nikaalo
        relay_payload = raw_text.split(None, 1)[1]
        try:
            await client.send_message(TARGET_GROUP_ID, relay_payload)
            await event.reply(f"✅ **Group me bhej diya:**\n`{relay_payload}`")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    # --- 2. /lock (Group chat band karega) ---
    elif cmd == "/lock":
        try:
            group_peer = await client.get_input_entity(TARGET_GROUP_ID)
            await client(functions.messages.EditChatDefaultBannedRightsRequest(
                peer=group_peer,
                banned_rights=GROUP_LOCK
            ))
            await event.reply("🔒 Group lock ho gaya.")
            await client.send_message(TARGET_GROUP_ID, "🔒 **Group has been locked by Admin.**")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    # --- 3. /unlock (Group chat kholega) ---
    elif cmd == "/unlock":
        try:
            group_peer = await client.get_input_entity(TARGET_GROUP_ID)
            await client(functions.messages.EditChatDefaultBannedRightsRequest(
                peer=group_peer,
                banned_rights=GROUP_UNLOCK
            ))
            await event.reply("🔓 Group unlock ho gaya.")
            await client.send_message(TARGET_GROUP_ID, "🔓 **Group has been unlocked.**")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    # --- 4. /ban ---
    elif cmd == "/ban":
        if len(parts) < 2:
            await event.reply("⚠️ Format: `/ban @username` ya `/ban UserID`")
            return
        try:
            user = await resolve_target(client, parts[1])
            await client.edit_permissions(TARGET_GROUP_ID, user, BAN_USER)
            await event.reply(f"✅ User **{user.first_name}** (`{user.id}`) ban ho gaya.")
            await client.send_message(TARGET_GROUP_ID, f"🚫 **User {user.first_name} has been banned.**")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    # --- 5. /unban ---
    elif cmd == "/unban":
        if len(parts) < 2:
            await event.reply("⚠️ Format: `/unban @username` ya `/unban UserID`")
            return
        try:
            user = await resolve_target(client, parts[1])
            await client.edit_permissions(TARGET_GROUP_ID, user, UNBAN_USER)
            await event.reply(f"✅ User **{user.first_name}** (`{user.id}`) unban ho gaya.")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    # --- 6. /mute ---
    elif cmd == "/mute":
        if len(parts) < 2:
            await event.reply("⚠️ Format: `/mute @username` ya `/mute UserID`")
            return
        try:
            user = await resolve_target(client, parts[1])
            await client.edit_permissions(TARGET_GROUP_ID, user, MUTE_USER)
            await event.reply(f"🔇 User **{user.first_name}** mute ho gaya.")
            await client.send_message(TARGET_GROUP_ID, f"🔇 **User {user.first_name} has been muted.**")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    # --- 7. /unmute ---
    elif cmd == "/unmute":
        if len(parts) < 2:
            await event.reply("⚠️ Format: `/unmute @username` ya `/unmute UserID`")
            return
        try:
            user = await resolve_target(client, parts[1])
            await client.edit_permissions(TARGET_GROUP_ID, user, UNMUTE_USER)
            await event.reply(f"🔊 User **{user.first_name}** unmute ho gaya.")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    # --- 8. /help ---
    elif cmd in ["/help", "/start"]:
        msg = (
            "🛡️ **Admin Relay Control**\n\n"
            "• `/cmm <kuch bhi>` - Exact message/command group me send karega\n"
            "• `/lock` - Group band karega\n"
            "• `/unlock` - Group kholega\n"
            "• `/ban <username/id>` - User ban\n"
            "• `/unban <username/id>` - User unban\n"
            "• `/mute <username/id>` - User mute\n"
            "• `/unmute <username/id>` - User unmute\n"
            "• `/id` - Check your Telegram ID"
        )
        await event.reply(msg)

print("Userbot is live...")
client.start()
client.run_until_disconnected()
