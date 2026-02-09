from __future__ import annotations

import discord



def ok_embed(title: str, description: str) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=discord.Color.green())
    return embed



def error_embed(message: str) -> discord.Embed:
    return discord.Embed(title="Lỗi", description=message, color=discord.Color.red())
