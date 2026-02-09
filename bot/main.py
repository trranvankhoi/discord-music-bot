from __future__ import annotations

import logging

import discord
from discord.ext import commands

from bot.config.settings import get_settings
from bot.database.db import Database
from bot.utils.logger import setup_logging

logger = logging.getLogger(__name__)

COGS = [
    "bot.cogs.moderation",
    "bot.cogs.ai_moderation",
    "bot.cogs.system",
]


class ProfessionalBot(commands.Bot):
    def __init__(self):
        self.settings = get_settings()
        setup_logging(self.settings.log_level)

        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.guilds = True
        intents.messages = True
        intents.voice_states = True

        super().__init__(
            command_prefix=self._prefix_resolver,
            intents=intents,
            help_command=None,
            case_insensitive=True,
        )

        self.db = Database(self.settings.database_path)

    async def _prefix_resolver(self, _bot: commands.Bot, message: discord.Message):
        if not message.guild:
            return commands.when_mentioned_or(self.settings.prefix)(self, message)

        row = await self.db.fetchone("SELECT prefix FROM guild_config WHERE guild_id = ?", (message.guild.id,))
        guild_prefix = row[0] if row and row[0] else self.settings.prefix
        return commands.when_mentioned_or(guild_prefix)(self, message)

    async def setup_hook(self) -> None:
        await self.db.init()
        for ext in COGS:
            await self.load_extension(ext)
            logger.info("Loaded extension: %s", ext)
        await self.tree.sync()

    async def on_ready(self):
        logger.info("Bot online as %s (%s)", self.user, self.user.id if self.user else "?")

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("❌ Bạn không có quyền dùng lệnh này.")
            return
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(f"⏳ Lệnh đang cooldown, thử lại sau {error.retry_after:.1f}s")
            return
        if isinstance(error, commands.BadArgument):
            await ctx.reply("❌ Tham số không hợp lệ.")
            return
        logger.exception("Unhandled command error", exc_info=error)
        await ctx.reply("💥 Đã xảy ra lỗi nội bộ, xem logs để biết thêm chi tiết.")


def run() -> None:
    bot = ProfessionalBot()
    bot.run(bot.settings.token, log_handler=None)


if __name__ == "__main__":
    run()
