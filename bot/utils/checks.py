from __future__ import annotations

from functools import wraps

from discord.ext import commands



def permission_checker(*perms: str):
    """Decorator kiểm tra quyền cho cả prefix/hybrid command."""

    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx: commands.Context, *args, **kwargs):
            if await self.bot.is_owner(ctx.author):
                return await func(self, ctx, *args, **kwargs)

            missing = [perm for perm in perms if not getattr(ctx.author.guild_permissions, perm, False)]
            if missing:
                await ctx.reply(f"❌ Bạn thiếu quyền: {', '.join(missing)}")
                return
            return await func(self, ctx, *args, **kwargs)

        return wrapper

    return decorator
