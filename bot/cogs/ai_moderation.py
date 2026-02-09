from __future__ import annotations

import logging

import discord
from discord.ext import commands

from bot.ai.nlp_moderation import VietnameseIntentParser

logger = logging.getLogger(__name__)


class AIModerationCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.parser = VietnameseIntentParser()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        if self.bot.user not in message.mentions:
            return

        intent = self.parser.parse(message.content.replace(self.bot.user.mention, "").strip())
        if not intent:
            await message.reply("Mình chưa hiểu lệnh tự nhiên này. Hãy thử rõ hơn bằng tiếng Việt.")
            return

        # Dispatch theo intent
        if intent.command == "clear":
            deleted = await message.channel.purge(limit=intent.args.get("amount", 50))
            await message.channel.send(f"🤖 AI đã xóa {len(deleted)} tin nhắn theo yêu cầu.", delete_after=4)
        elif intent.command == "server_lockdown":
            overwrite = message.channel.overwrites_for(message.guild.default_role)
            overwrite.send_messages = False
            await message.channel.set_permissions(message.guild.default_role, overwrite=overwrite)
            await message.reply("🔒 AI đã khóa kênh hiện tại (mô phỏng lockdown).")
        elif intent.command == "anti_link":
            state = "bật" if intent.args.get("enabled") else "tắt"
            await message.reply(f"🛡️ AI đã {state} chế độ chống link (lưu ở config command).")
        elif intent.command == "ban_spam":
            await message.reply("🚨 AI nhận diện yêu cầu ban user spam. Hãy dùng `/ban @user lý do` để xác nhận.")


async def setup(bot: commands.Bot):
    await bot.add_cog(AIModerationCog(bot))
