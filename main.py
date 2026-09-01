import os
import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import ChatBannedRights

# --- CONFIGURATION (Environment Variables) ---
API_ID = int(os.environ.get("API_ID", "34420912"))
API_HASH = os.environ.get("API_HASH", "349f4d7dbd04aca92c2cace2da28fe14")
SESSION_STRING = os.environ.get("SESSION_STRING")

# Verified Doston ki Telegram User IDs
ALLOWED_USERS = [
    8988599574,  # Dost 1
    8401097557   # Dost 2
]

# Target Group ID
TARGET_GROUP_ID = int(os.environ.get("TARGET_GROUP_ID", "-1003928377196"))

if not SESSION_STRING:
    raise ValueError("SESSION_STRING environment variable set nahi hai!")

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Permission sets
MUTE_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=True
)

UNMUTE_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=False
)

LOCK_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_link_previews=True
)

UNLOCK_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=False,
    send_media=False,
    send_stickers=False,
    send_gifs=False,
    send_games=False,
    send_inline=False,
    embed_link_previews=False
)

@client.on(events.NewMessage(incoming=True))
async def handle_commands(event):
    # Sirf Private Message (DM) me command sunega
    if not event.is_private:
        return

    sender_id = event.sender_id

    # Non-authorized users check
    if sender_id not in ALLOWED_USERS:
        return

    text = event.raw_text.strip()
    parts = text.split()
    if not parts:
        return

    cmd = parts[0].lower()

    # --- /help ---
    if cmd == "/help" or cmd == "/start":
        msg = (
            "🛡️ **Admin Relay Tool Active**\n\n"
            "**Available Commands:**\n"
            "• `/ban <username/id>` - Ban user from group\n"
            "• `/unban <username/id>` - Unban user\n"
            "• `/mute <username/id>` - Mute user\n"
            "• `/unmute <username/id>` - Unmute user\n"
            "• `/tmute <username/id> <minutes>` - Temporary mute\n"
            "• `/lock` - Lock group chat (everyone muted)\n"
            "• `/unlock` - Unlock group chat\n"
            "• `/say <message>` - Send announcement to group"
        )
        await event.reply(msg)

    # --- /ban ---
    elif cmd == "/ban":
        if len(parts) < 2:
            await event.reply("⚠️ **Format:** `/ban @username` ya `/ban 12345678`")
            return
        target = parts[1]
        try:
            user = await client.get_entity(target)
            await client.edit_permissions(TARGET_GROUP_ID, user, view_messages=False)
            await event.reply(f"✅ User **{user.first_name}** (`{user.id}`) ko ban kar diya gaya.")
            await client.send_message(TARGET_GROUP_ID, f"🚫 **User {user.first_name} has been banned.**")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    # --- /unban ---
    elif cmd == "/unban":
        if len(parts) < 2:
            await event.reply("⚠️ **Format:** `/unban @username` ya `/unban 12345678`")
            return
        target = parts[1]
        try:
            user = await client.get_entity(target)
            await client.edit_permissions(TARGET_GROUP_ID, user, ChatBannedRights(until_date=None, view_messages=False))
            await event.reply(f"✅ User **{user.first_name}** (`{user.id}`) unban ho gaya.")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    # --- /mute ---
    elif cmd == "/mute":
        if len(parts) < 2:
            await event.reply("⚠️ **Format:** `/mute @username`")
            return
        target = parts[1]
        try:
            user = await client.get_entity(target)
            await client.edit_permissions(TARGET_GROUP_ID, user, MUTE_RIGHTS)
            await event.reply(f"🔇 User **{user.first_name}** mute ho gaya.")
            await client.send_message(TARGET_GROUP_ID, f"🔇 **User {user.first_name} has been muted.**")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    # --- /tmute (Temp Mute) ---
    elif cmd == "/tmute":
        if len(parts) < 3:
            await event.reply("⚠️ **Format:** `/tmute @username 10` (10 minutes ke liye)")
            return
        target = parts[1]
        try:
            duration = int(parts[2])
            until_date = datetime.now() + timedelta(minutes=duration)
            user = await client.get_entity(target)
            temp_rights = ChatBannedRights(until_date=until_date, send_messages=True)
            await client.edit_permissions(TARGET_GROUP_ID, user, temp_rights)
            await event.reply(f"⏳ User **{user.first_name}** ko `{duration}` minute ke liye mute kiya gaya.")
            await client.send_message(TARGET_GROUP_ID, f"🔇 **{user.first_name}** is muted for `{duration}` minutes.")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    # --- /unmute ---
    elif cmd == "/unmute":
        if len(parts) < 2:
            await event.reply("⚠️ **Format:** `/unmute @username`")
            return
        target = parts[1]
        try:
            user = await client.get_entity(target)
            await client.edit_permissions(TARGET_GROUP_ID, user, UNMUTE_RIGHTS)
            await event.reply(f"🔊 User **{user.first_name}** unmute ho gaya.")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    # --- /lock ---
    elif cmd == "/lock":
        try:
            await client.edit_permissions(TARGET_GROUP_ID, ChatBannedRights(until_date=None, send_messages=True))
            await event.reply("🔒 Group lock kar diya gaya.")
            await client.send_message(TARGET_GROUP_ID, "🔒 **Group has been locked by Admin.**")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    # --- /unlock ---
    elif cmd == "/unlock":
        try:
            await client.edit_permissions(TARGET_GROUP_ID, UNLOCK_RIGHTS)
            await event.reply("🔓 Group unlock kar diya gaya.")
            await client.send_message(TARGET_GROUP_ID, "🔓 **Group has been unlocked.**")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

    # --- /say (Relay message directly to group) ---
    elif cmd == "/say":
        if len(parts) < 2:
            await event.reply("⚠️ **Format:** `/say <message text>`")
            return
        broadcast_msg = text.split(None, 1)[1]
        try:
            await client.send_message(TARGET_GROUP_ID, broadcast_msg)
            await event.reply("✅ Message group me bhej diya gaya.")
        except Exception as e:
            await event.reply(f"❌ Error: `{str(e)}`")

print("Userbot is running and connected...")
client.start()
client.run_until_disconnected()
