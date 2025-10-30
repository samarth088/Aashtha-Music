# main.py

from pyrogram import Client, filters, idle
from pyrogram.types import Message
import os
import asyncio
from pytgcalls import GroupCallFactory

# === ENV VARS ===
API_ID = int(os.environ.get("22219296"))
API_HASH = os.environ.get("525192292aa8adcdc641d9c7093c35f8")
BOT_TOKEN = os.environ.get("8363287733:AAHfyD9lmXbcO02HUZuFzN6Va4Hg-ESR3Yg")
SESSION_STRING = os.environ.get("BQFTCiAAsTdQ2xiR4R1zi8-I_gPvAXfQJbR9wZ__qU0bNqpWdPkV9vYJH1WFK5vCCwz95wpxxSvz7oTNEhdijPSU-it7jNMU6Tx71g8dB-GeWb4dGK-Fn7qVo5tTJXoGC38hfW7WsrpXrtPa6Lsu2A4iz0EQE_5Dmd54KlPDBWgEqZKt4A2JIbISP2L21J2gv1tN7Zn4wAKmNDYiMdwKKovijZMIuanMYVK-UF8aephZ5-2ixIJxxGUM9GgP50QWsMShQLmBPLAHGFnrA-bbJjI-yc2EvJ-1xBhV3YAMwmEMwXLshHKLz6PK32YROkGysGtMqRS_ehEvt-iY8bXbxj2BNx3bKQAAAAHo7gw5AQ")

# === CLIENTS ===
bot = Client("music_bot", api_id=22219296, api_hash=525192292aa8adcdc641d9c7093c35f8, bot_token=8363287733:AAHfyD9lmXbcO02HUZuFzN6Va4Hg-ESR3Yg)
user = Client("vc_player", api_id=25823347, api_hash=API_HASH, session_string=BQFTCiAAsTdQ2xiR4R1zi8-I_gPvAXfQJbR9wZ__qU0bNqpWdPkV9vYJH1WFK5vCCwz95wpxxSvz7oTNEhdijPSU-it7jNMU6Tx71g8dB-GeWb4dGK-Fn7qVo5tTJXoGC38hfW7WsrpXrtPa6Lsu2A4iz0EQE_5Dmd54KlPDBWgEqZKt4A2JIbISP2L21J2gv1tN7Zn4wAKmNDYiMdwKKovijZMIuanMYVK-UF8aephZ5-2ixIJxxGUM9GgP50QWsMShQLmBPLAHGFnrA-bbJjI-yc2EvJ-1xBhV3YAMwmEMwXLshHKLz6PK32YROkGysGtMqRS_ehEvt-iY8bXbxj2BNx3bKQAAAAHo7gw5AQ)

# === VC SETUP ===
group_call = None

# =============================================
# 1. USERBOT COMMANDS (Private mein chalayenge)
# =============================================
@user.on_message(filters.command("joinvc") & filters.private)
async def join_vc(client: Client, message: Message):
    global group_call
    if group_call and group_call.is_connected:
        await message.reply("Already in VC!")
        return
    
    try:
        chat_id = int(message.text.split()[1])
        group_call = GroupCallFactory(user).get_group_call()
        await group_call.start(chat_id)
        await message.reply(f"VC join ho gaya: {chat_id}")
    except Exception as e:
        await message.reply(f"Error: {e}\nUsage: /joinvc -1001234567890")

@user.on_message(filters.command("play") & filters.private)
async def play_song(client: Client, message: Message):
    global group_call
    if not group_call or not group_call.is_connected:
        await message.reply("Pehle /joinvc karo!")
        return
    
    query = " ".join(message.text.split()[1:])
    if not query:
        await message.reply("Song name do!")
        return

    await message.reply("Searching aur downloading...")

    import yt_dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.%(ext)s',
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)
            title = info['entries'][0]['title']
        
        await group_call.play("song.mp3")
        await message.reply(f"Now playing: **{title}**")
    except Exception as e:
        await message.reply(f"Error: {e}")

# =============================================
# 2. BOT COMMANDS (Group mein chalega) → BONUS WALA YAHAN!
# =============================================
@bot.on_message(filters.command("play") & filters.group)
async def smart_play(client: Client, message: Message):
    chat_id = message.chat.id
    query = " ".join(message.text.split()[1:])
    
    if not query:
        await message.reply("Usage: /play shape of you")
        return
    
    await message.reply("Gaana shuru ho raha hai VC mein...")

    # Auto join + play
    await user.send_message("me", f"/joinvc {chat_id}")
    await asyncio.sleep(4)  # Wait for join
    await user.send_message("me", f"/play {query}")

# =============================================
# 3. START BOTH CLIENTS
# =============================================
async def main():
    await bot.start()
    await user.start()
    print("Bot aur Userbot dono LIVE hai!")
    await idle()

if __name__ == "__main__":
    bot.run(main())
