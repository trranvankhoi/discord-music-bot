import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import asyncio
import os

# ===== FFmpeg portable =====
import imageio_ffmpeg
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

# ===== Flask keep alive =====
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    app.run(host="0.0.0.0", port=8080)

Thread(target=run_web).start()


# ===== Discord Setup =====
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ===== Queue =====
queues = {}

def get_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = []
    return queues[guild_id]


# ===== YT-DLP =====
ydl_opts = {
    'format': 'bestaudio',
    'noplaylist': True,
    'quiet': True
}


async def get_audio_url(query):
    loop = asyncio.get_event_loop()

    def extract():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)

            if "entries" in info:
                info = info["entries"][0]

            return info["url"], info["title"]

    return await loop.run_in_executor(None, extract)


# ===== Voice =====
async def ensure_voice(interaction):
    if interaction.user.voice is None:
        await interaction.response.send_message("Bạn chưa vào voice!", ephemeral=True)
        return None

    channel = interaction.user.voice.channel
    vc = interaction.guild.voice_client

    if vc is None:
        vc = await channel.connect()
    elif vc.channel != channel:
        await vc.move_to(channel)

    return vc


async def play_next(guild):
    queue = get_queue(guild.id)

    if not queue:
        return

    vc = guild.voice_client

    url, title = queue.pop(0)

    source = discord.FFmpegPCMAudio(
        url,
        executable=FFMPEG_PATH,
        before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        options="-vn"
    )

    def after(err):
        asyncio.run_coroutine_threadsafe(play_next(guild), bot.loop)

    vc.play(source, after=after)


# ===== Events =====
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")


# ===== Slash Commands =====
@bot.tree.command(name="play", description="Phát nhạc")
async def play(interaction: discord.Interaction, query: str):

    vc = await ensure_voice(interaction)
    if vc is None:
        return

    await interaction.response.send_message("Đang tìm nhạc...")

    url, title = await get_audio_url(query)

    queue = get_queue(interaction.guild.id)
    queue.append((url, title))

    if not vc.is_playing():
        await play_next(interaction.guild)

    await interaction.followup.send(f"🎵 Đã thêm: {title}")


@bot.tree.command(name="skip")
async def skip(interaction: discord.Interaction):
    vc = interaction.guild.voice_client

    if vc and vc.is_playing():
        vc.stop()
        await interaction.response.send_message("⏭️ Skip")
    else:
        await interaction.response.send_message("Không có nhạc")


@bot.tree.command(name="leave")
async def leave(interaction: discord.Interaction):
    vc = interaction.guild.voice_client

    if vc:
        await vc.disconnect()
        await interaction.response.send_message("👋 Rời voice")
    else:
        await interaction.response.send_message("Bot chưa vào voice")


# ===== RUN BOT =====
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
