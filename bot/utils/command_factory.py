from __future__ import annotations

import logging
from collections.abc import Callable

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)



def register_stub_command(
    cog_cls,
    *,
    name: str,
    description: str,
    permission: str | None = None,
    cooldown: tuple[int, float] = (2, 5.0),
):
    """Tạo nhanh lệnh hybrid command có thông báo và log."""

    async def _impl(self, ctx, *, detail: str = ""):
        if permission and not getattr(ctx.author.guild_permissions, permission, False) and not await self.bot.is_owner(ctx.author):
            await ctx.reply(f"❌ Bạn thiếu quyền `{permission}` để dùng lệnh `{name}`.")
            return

        await self.log_mod_action(ctx.guild.id if ctx.guild else 0, name, getattr(ctx.author, "id", 0), detail)
        embed = discord.Embed(
            title=f"✅ {name}",
            description=f"{description}\nChi tiết: {detail or 'Không có'}",
            color=discord.Color.blurple(),
        )
        await ctx.reply(embed=embed)

    _impl.__name__ = f"cmd_{name}"
    command = commands.hybrid_command(name=name, description=description)(_impl)
    command = commands.cooldown(cooldown[0], cooldown[1], commands.BucketType.user)(command)
    setattr(cog_cls, _impl.__name__, command)
