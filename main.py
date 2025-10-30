import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls, GroupCallFactory
import yt_dlp

# Environment Variables
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
SESSION_STRING = os.environ["SESSION_STRING"]

# Clients
bot = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
userbot = Client("vc_player", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
caller = PyTgCalls(userbot)

# Global Group Call Factory
group_call_factory = GroupCallFactory(caller)
group_call = None  # Will hold the active call

@bot.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text("Hey! /play <song> se VC mein gaana bajao!")

@bot.on_message(filters.command("play") & filters.group)
async def play_song(client: Client, message: Message):
    global group_call
    chat_id = message.chat.id
    query = " ".join(message.command[1:])  # Better way to get query
    if not query:
        await message.reply_text("Song name do! `/play shape of you`", parse_mode="markdown")
        return

    await message.reply_text("VC join aur gaana baj raha hai...")

    # Create or reuse group call
    if not group_call:
        group_call = group_call_factory.get_group_call()
        await group_call.start(chat_id)

    # Download song
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'extract_audio': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        os.makedirs("downloads", exist_ok=True)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)
            video = info['entries'][0]
            title = video['title']
            duration = video.get('duration', 0)
            file_path = ydl.prepare_filename(video).rsplit(".", 1)[0] + ".mp3"

        # Play the file
        await group_call.play(file_path)
        await message.reply_text(f"**Now Playing:** `{title}`\n**Duration:** `{duration}s`", parse_mode="markdown")

    except Exception as e:
        await message.reply_text(f"Error: `{str(e)}`", parse_mode="markdown")
        if group_call:
            await group_call.stop()
            group_call = None

@bot.on_message(filters.command("stop"))
async def stop_song(client: Client, message: Message):
    global group_call
    if group_call and group_call.is_connected:
        await group_call.stop()
        group_call = None
        await message.reply_text("VC छोड़ा और गाना बंद!")
    else:
        await message.reply_text("Koi gaana nahi baj raha!")

async def main():
    await asyncio.gather(
        bot.start(),
        userbot.start(),
        caller.start()
    )
    print("Bot aur Userbot LIVE हैं! VC Music Player Ready!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
