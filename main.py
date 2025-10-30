import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls import GroupCallFactory

# Environment Variables
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
SESSION_STRING = os.environ["SESSION_STRING"]

# Clients
bot = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = PyTgCalls(Client("vc_player", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING))

# Global
group_call = None

@bot.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text("Hey! /play <song> se VC mein gaana bajao!")

@bot.on_message(filters.command("play") & filters.group)
async def play_song(client: Client, message: Message):
    global group_call
    chat_id = message.chat.id
    query = " ".join(message.text.split()[1:])
    if not query:
        await message.reply_text("Song name do! /play shape of you")
        return

    await message.reply_text("VC join aur gaana baj raha hai...")

    # Join VC if not already
    if not group_call:
        group_call = user.create_call(chat_id)
        await group_call.start()

    # Download & play
    import yt_dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.%(ext)s',
        'noplaylist': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)
            title = info['entries'][0]['title']
            filepath = ydl.prepare_filename(info['entries'][0])
        await group_call.play(GroupCallFactory(filepath))
        await message.reply_text(f"Now playing: **{title}**")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@bot.on_message(filters.command("stop"))
async def stop_song(client: Client, message: Message):
    global group_call
    if group_call:
        await group_call.stop()
        group_call = None
        await message.reply_text("VC left!")
    else:
        await message.reply_text("Koi gaana nahi baj raha!")

async def main():
    await bot.start()
    await user.start()
    print("Bot aur Userbot dono LIVE hai!")
    await asyncio.Event().wait()  # Keep alive

if __name__ == "__main__":
    asyncio.run(main())
