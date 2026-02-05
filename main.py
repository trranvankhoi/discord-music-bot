import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import asyncio
import os

# ===== KEEP ALIVE (HOSTING) =====
from flask import Flask
from threading import Thread

app = Flask("")

@app.route("/")
def home():
    return "Bot is alive!"

def run_web():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ===============================

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ===== MUSIC STORAGE =====
queues = {}

# ===== YTDLP CONFIG =====
ytdlp_format_options = {
    "format": "bestaudio/best",
    "quiet": True
}

ffmpeg_options = {
    "options": "-vn"
}

ytdl = yt_dlp.YoutubeDL(ytdlp_format_options)

# ===== GET AUDIO =====
async def get_audio(url):
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
    
    if "entries" in data:
        data = data["entries"][0]

    return data["url"], data["title"]

# ===== JOIN VOICE =====
async def ensure_voice(interaction):
    if not interaction.user.voice:
        await interaction.response.send_message("❌ Bạn phải vào voice trước", ephemeral=True)
        return None

    channel = interaction.user.voice.channel

    if interaction.guild.voice_client:
        return interaction.guild.voice_client
    else:
        return await channel.connect()

# ===== PLAY NEXT =====
async def play_next(guild):
    if guild.id not in queues or len(queues[guild.id]) == 0:
        return

    vc = guild.voice_client
    url = queues[guild.id].pop(0)

    stream_url, title = await get_audio(url)

    source = discord.FFmpegPCMAudio(stream_url, **ffmpeg_options)

    def after_play(err):
        fut = play_next(guild)
        asyncio.run_coroutine_threadsafe(fut, bot.loop)

    vc.play(source, after=after_play)

# ===== EVENTS =====
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

# ===== SLASH COMMANDS =====

@bot.tree.command(name="play", description="Phát nhạc từ YouTube")
async def play(interaction: discord.Interaction, url: str):

    vc = await ensure_voice(interaction)
    if not vc:
        return

    if interaction.guild.id not in queues:
        queues[interaction.guild.id] = []

    queues[interaction.guild.id].append(url)

    await interaction.response.send_message(f"🎵 Đã thêm vào queue")

    if not vc.is_playing():
        await play_next(interaction.guild)

# =====================

@bot.tree.command(name="skip", description="Bỏ bài hiện tại")
async def skip(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await interaction.response.send_message("⏭ Đã skip")
    else:
        await interaction.response.send_message("❌ Không có nhạc")

# =====================

@bot.tree.command(name="stop", description="Dừng và rời voice")
async def stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc:
        queues[interaction.guild.id] = []
        await vc.disconnect()
        await interaction.response.send_message("🛑 Đã dừng bot")

# =====================

keep_alive()
bot.run(TOKEN)
