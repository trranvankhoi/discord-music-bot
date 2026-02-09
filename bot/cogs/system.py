from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

import discord
from discord.ext import commands, tasks

from bot.utils.paginator import SimplePaginator

logger = logging.getLogger(__name__)


class HelpSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Moderation", description="Lệnh quản trị thành viên/chat"),
            discord.SelectOption(label="Server", description="Lệnh quản trị server/role/voice"),
            discord.SelectOption(label="System", description="Logging, config, AI"),
        ]
        super().__init__(placeholder="Chọn nhóm lệnh", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Bạn chọn: **{self.values[0]}**", ephemeral=True)


class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(HelpSelect())


class SystemCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.reminder_loop.start()

    def cog_unload(self):
        self.reminder_loop.cancel()

    @commands.hybrid_command(name="help_ui", description="Hiển thị help menu dạng UI")
    async def help_ui(self, ctx):
        pages = [
            discord.Embed(title="Help 1", description="Nhóm Member/Chat"),
            discord.Embed(title="Help 2", description="Nhóm Role/Server/Voice"),
            discord.Embed(title="Help 3", description="Nhóm Security/Config/Advanced"),
        ]
        view = SimplePaginator(pages)
        await ctx.reply(embed=pages[0], view=view)

    @commands.hybrid_command(name="remindme", description="Tạo reminder theo phút")
    async def remindme(self, ctx, minutes: int, *, content: str):
        remind_at = datetime.now(timezone.utc).timestamp() + minutes * 60
        await self.bot.db.execute(
            "INSERT INTO reminders(guild_id, user_id, remind_at, message) VALUES (?, ?, datetime(?,'unixepoch'), ?)",
            (ctx.guild.id, ctx.author.id, remind_at, content),
        )
        await ctx.reply(f"⏰ Đã đặt nhắc nhở sau {minutes} phút.")

    @tasks.loop(seconds=30)
    async def reminder_loop(self):
        await self.bot.wait_until_ready()
        rows = await self.bot.db.fetchall(
            "SELECT id, guild_id, user_id, message FROM reminders WHERE remind_at <= CURRENT_TIMESTAMP"
        )
        for reminder_id, guild_id, user_id, msg in rows:
            guild = self.bot.get_guild(guild_id)
            if guild:
                user = guild.get_member(user_id)
                if user:
                    try:
                        await user.send(f"🔔 Nhắc nhở: {msg}")
                    except discord.Forbidden:
                        logger.warning("Không thể gửi DM reminder cho %s", user_id)
            await self.bot.db.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))


async def setup(bot: commands.Bot):
    await bot.add_cog(SystemCog(bot))
