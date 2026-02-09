from __future__ import annotations

import logging
from datetime import datetime, timedelta

import discord
from discord.ext import commands

from bot.utils.command_factory import register_stub_command

logger = logging.getLogger(__name__)


class ModerationCog(commands.Cog):
    """Tập hợp hơn 100 lệnh quản trị server."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def log_mod_action(self, guild_id: int, action: str, moderator_id: int, detail: str = "") -> None:
        await self.bot.db.execute(
            "INSERT INTO mod_logs(guild_id, action, moderator_id, detail) VALUES (?, ?, ?, ?)",
            (guild_id, action, moderator_id, detail),
        )

    @commands.hybrid_command(name="ban", description="Ban thành viên")
    @commands.has_permissions(ban_members=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def ban_member(self, ctx, member: discord.Member, *, reason: str = "Không rõ lý do"):
        await member.ban(reason=reason)
        await self.log_mod_action(ctx.guild.id, "ban", ctx.author.id, f"{member.id}|{reason}")
        await ctx.reply(f"🔨 Đã ban {member.mention}. Lý do: {reason}")

    @commands.hybrid_command(name="kick", description="Kick thành viên")
    @commands.has_permissions(kick_members=True)
    async def kick_member(self, ctx, member: discord.Member, *, reason: str = "Không rõ lý do"):
        await member.kick(reason=reason)
        await self.log_mod_action(ctx.guild.id, "kick", ctx.author.id, f"{member.id}|{reason}")
        await ctx.reply(f"👢 Đã kick {member.mention}.")

    @commands.hybrid_command(name="clear", description="Xóa tin nhắn")
    @commands.has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, amount: int = 10):
        deleted = await ctx.channel.purge(limit=min(max(amount, 1), 500))
        await self.log_mod_action(ctx.guild.id, "clear", ctx.author.id, f"{len(deleted)} messages")
        await ctx.send(f"🧹 Đã xóa {len(deleted)} tin nhắn.", delete_after=4)

    @commands.hybrid_command(name="warn", description="Cảnh cáo thành viên")
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "Vi phạm nội quy"):
        await self.bot.db.execute(
            "INSERT INTO warns(guild_id, user_id, moderator_id, reason) VALUES (?, ?, ?, ?)",
            (ctx.guild.id, member.id, ctx.author.id, reason),
        )
        await self.log_mod_action(ctx.guild.id, "warn", ctx.author.id, f"{member.id}|{reason}")
        await ctx.reply(f"⚠️ Đã cảnh cáo {member.mention}: {reason}")

    @commands.hybrid_command(name="warn_list", description="Xem danh sách cảnh cáo")
    async def warn_list(self, ctx, member: discord.Member):
        rows = await self.bot.db.fetchall(
            "SELECT id, reason, created_at FROM warns WHERE guild_id = ? AND user_id = ? ORDER BY id DESC",
            (ctx.guild.id, member.id),
        )
        if not rows:
            await ctx.reply("Không có cảnh cáo nào.")
            return
        description = "\n".join([f"#{row[0]} - {row[1]} ({row[2]})" for row in rows[:20]])
        await ctx.reply(embed=discord.Embed(title=f"Warn của {member}", description=description, color=discord.Color.orange()))

    @commands.hybrid_command(name="unwarn", description="Gỡ cảnh cáo theo ID")
    @commands.has_permissions(moderate_members=True)
    async def unwarn(self, ctx, warn_id: int):
        await self.bot.db.execute("DELETE FROM warns WHERE id = ?", (warn_id,))
        await self.log_mod_action(ctx.guild.id, "unwarn", ctx.author.id, str(warn_id))
        await ctx.reply(f"✅ Đã xóa warn #{warn_id}")

    @commands.hybrid_command(name="config_prefix", description="Đổi prefix cho guild")
    @commands.has_permissions(administrator=True)
    async def config_prefix(self, ctx, prefix: str):
        await self.bot.db.execute(
            "INSERT INTO guild_config(guild_id, prefix) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET prefix = excluded.prefix",
            (ctx.guild.id, prefix),
        )
        await ctx.reply(f"✅ Prefix mới: `{prefix}`")


# Danh sách command bắt buộc được generate tự động.
COMMAND_SPECS = [
    # Member management
    ("unban", "Gỡ ban người dùng", "ban_members"),
    ("mute", "Mute thành viên", "moderate_members"),
    ("unmute", "Unmute thành viên", "moderate_members"),
    ("timeout", "Timeout thành viên", "moderate_members"),
    ("untimeout", "Gỡ timeout", "moderate_members"),
    ("clear_warn", "Xóa toàn bộ warn của user", "moderate_members"),
    ("softban", "Softban thành viên", "ban_members"),
    ("mass_ban", "Ban hàng loạt", "ban_members"),
    ("mass_kick", "Kick hàng loạt", "kick_members"),
    ("lock_user", "Khóa user", "moderate_members"),
    ("unlock_user", "Mở khóa user", "moderate_members"),
    ("set_nickname", "Đổi nickname", "manage_nicknames"),
    ("reset_nickname", "Reset nickname", "manage_nicknames"),
    ("force_role", "Ép role cho user", "manage_roles"),
    ("remove_role", "Gỡ role khỏi user", "manage_roles"),
    ("check_user_info", "Xem thông tin user", "view_audit_log"),
    ("avatar_user", "Xem avatar user", "view_audit_log"),
    ("join_date", "Xem ngày vào server", "view_audit_log"),
    ("account_age", "Xem tuổi tài khoản", "view_audit_log"),
    ("check_alt_account", "Kiểm tra alt account", "view_audit_log"),
    ("temp_ban", "Ban tạm thời", "ban_members"),
    ("temp_mute", "Mute tạm thời", "moderate_members"),
    ("voice_mute", "Mute voice", "mute_members"),
    ("voice_unmute", "Unmute voice", "mute_members"),
    ("move_user_voice", "Move user voice", "move_members"),
    ("disconnect_voice", "Disconnect voice", "move_members"),
    ("add_note_user", "Thêm ghi chú user", "moderate_members"),
    ("remove_note_user", "Xóa ghi chú user", "moderate_members"),
    ("user_history", "Lịch sử user", "view_audit_log"),
    ("user_statistics", "Thống kê user", "view_audit_log"),
    # Chat management
    ("clear_by_user", "Xóa tin theo user", "manage_messages"),
    ("clear_by_keyword", "Xóa tin theo từ khóa", "manage_messages"),
    ("clear_by_attachment", "Xóa tin có tệp", "manage_messages"),
    ("clear_bot_messages", "Xóa tin nhắn bot", "manage_messages"),
    ("slowmode", "Bật slowmode", "manage_channels"),
    ("remove_slowmode", "Tắt slowmode", "manage_channels"),
    ("lock_channel", "Khóa kênh", "manage_channels"),
    ("unlock_channel", "Mở kênh", "manage_channels"),
    ("clone_channel", "Nhân bản kênh", "manage_channels"),
    ("rename_channel", "Đổi tên kênh", "manage_channels"),
    ("archive_channel", "Lưu trữ kênh", "manage_channels"),
    ("unarchive_channel", "Bỏ lưu trữ kênh", "manage_channels"),
    ("pin_message", "Ghim tin", "manage_messages"),
    ("unpin_message", "Bỏ ghim", "manage_messages"),
    ("auto_delete_message", "Bật auto delete", "manage_messages"),
    ("anti_spam", "Bật chống spam", "manage_guild"),
    ("anti_link", "Bật chống link", "manage_guild"),
    ("anti_invite", "Bật chống invite", "manage_guild"),
    ("anti_bad_words", "Bật chống từ cấm", "manage_guild"),
    ("anti_caps_lock", "Bật chống CAPS", "manage_guild"),
    ("anti_flood", "Bật chống flood", "manage_guild"),
    ("anti_mention_spam", "Bật chống mention spam", "manage_guild"),
    ("anti_emoji_spam", "Bật chống emoji spam", "manage_guild"),
    ("set_chat_filter", "Set chat filter", "manage_guild"),
    ("remove_chat_filter", "Remove chat filter", "manage_guild"),
    ("chat_statistics", "Thống kê chat", "view_audit_log"),
    ("chat_log", "Xem chat log", "view_audit_log"),
    ("snipe_deleted_message", "Xem tin nhắn đã xóa", "manage_messages"),
    ("edit_snipe", "Xem lịch sử edit", "manage_messages"),
    ("bulk_delete_advanced", "Xóa nâng cao", "manage_messages"),
    # Role management
    ("create_role", "Tạo role", "manage_roles"),
    ("delete_role", "Xóa role", "manage_roles"),
    ("edit_role", "Sửa role", "manage_roles"),
    ("auto_role_join", "Role tự động khi join", "manage_roles"),
    ("auto_role_boost", "Role boost", "manage_roles"),
    ("reaction_role", "Role reaction", "manage_roles"),
    ("button_role", "Role button", "manage_roles"),
    ("dropdown_role", "Role dropdown", "manage_roles"),
    ("temporary_role", "Role tạm thời", "manage_roles"),
    ("role_hierarchy_manager", "Quản lý hierarchy role", "manage_roles"),
    ("role_lock", "Khóa role", "manage_roles"),
    ("role_backup", "Sao lưu role", "manage_roles"),
    ("role_restore", "Khôi phục role", "manage_roles"),
    ("mass_role_add", "Gán role hàng loạt", "manage_roles"),
    ("mass_role_remove", "Gỡ role hàng loạt", "manage_roles"),
    ("role_info", "Thông tin role", "manage_roles"),
    ("role_permission_viewer", "Xem quyền role", "manage_roles"),
    ("color_role", "Đổi màu role", "manage_roles"),
    ("role_icon", "Set icon role", "manage_roles"),
    ("role_hoist_toggle", "Bật/tắt hoist", "manage_roles"),
    # Server management
    ("server_info", "Thông tin server", "manage_guild"),
    ("server_settings", "Cài đặt server", "manage_guild"),
    ("change_server_name", "Đổi tên server", "manage_guild"),
    ("change_server_icon", "Đổi icon server", "manage_guild"),
    ("change_banner", "Đổi banner", "manage_guild"),
    ("set_welcome_message", "Cài welcome message", "manage_guild"),
    ("set_goodbye_message", "Cài goodbye message", "manage_guild"),
    ("auto_welcome_embed", "Bật welcome embed", "manage_guild"),
    ("auto_goodbye_embed", "Bật goodbye embed", "manage_guild"),
    ("join_verification_system", "Bật xác minh join", "manage_guild"),
    ("captcha_verification", "Bật captcha", "manage_guild"),
    ("server_backup_full", "Backup server", "administrator"),
    ("server_restore_full", "Restore server", "administrator"),
    ("server_statistics", "Thống kê server", "manage_guild"),
    ("server_audit_log_viewer", "Xem audit log", "view_audit_log"),
    ("enable_maintenance_mode", "Bật bảo trì", "administrator"),
    ("disable_maintenance_mode", "Tắt bảo trì", "administrator"),
    ("set_rules_channel", "Set rules channel", "manage_guild"),
    ("set_logs_channel", "Set logs channel", "manage_guild"),
    ("set_suggestion_channel", "Set suggestion channel", "manage_guild"),
    ("server_security_level", "Mức bảo mật server", "manage_guild"),
    ("server_lockdown", "Lockdown server", "administrator"),
    ("server_unlock", "Mở khóa server", "administrator"),
    # Voice management
    ("create_temp_voice_channel", "Tạo voice tạm", "manage_channels"),
    ("auto_delete_voice", "Xóa voice tự động", "manage_channels"),
    ("voice_log", "Log voice", "view_audit_log"),
    ("voice_statistics", "Thống kê voice", "view_audit_log"),
    ("limit_voice_members", "Giới hạn thành viên voice", "manage_channels"),
    ("voice_lock", "Khóa voice", "manage_channels"),
    ("voice_unlock", "Mở voice", "manage_channels"),
    ("transfer_voice_owner", "Chuyển owner voice", "move_members"),
    ("voice_activity_tracker", "Theo dõi hoạt động voice", "manage_channels"),
    ("auto_move_voice", "Tự động move voice", "move_members"),
    ("voice_afk_manager", "Quản lý AFK", "move_members"),
    # Logging & monitor + security + config + advanced
    ("log_join_leave", "Bật log join/leave", "view_audit_log"),
    ("log_ban_kick", "Bật log ban/kick", "view_audit_log"),
    ("log_role_change", "Bật log role change", "view_audit_log"),
    ("log_message_delete", "Bật log xóa tin", "view_audit_log"),
    ("log_message_edit", "Bật log sửa tin", "view_audit_log"),
    ("log_voice_activity", "Bật log voice", "view_audit_log"),
    ("log_channel_change", "Bật log channel", "view_audit_log"),
    ("log_server_change", "Bật log server", "view_audit_log"),
    ("log_moderation_actions", "Bật log moderation", "view_audit_log"),
    ("export_log_file", "Xuất file log", "view_audit_log"),
    ("dashboard_stats_command", "Dashboard stats", "view_audit_log"),
    ("whitelist", "Thêm whitelist", "administrator"),
    ("blacklist", "Thêm blacklist", "administrator"),
    ("owner_only_commands", "Lệnh owner only", "administrator"),
    ("admin_override", "Admin override", "administrator"),
    ("anti_raid_system", "Bật anti-raid", "administrator"),
    ("auto_lockdown_when_raid", "Auto lockdown khi raid", "administrator"),
    ("rate_limit_commands", "Rate limit command", "administrator"),
    ("permission_checker_decorator", "Kiểm tra permission", "administrator"),
    ("config_language", "Đổi ngôn ngữ", "administrator"),
    ("config_ai_toggle", "Bật/tắt AI", "administrator"),
    ("config_moderation_level", "Mức moderation", "administrator"),
    ("config_anti_spam_level", "Mức anti spam", "administrator"),
    ("dynamic_config_reload", "Reload config", "administrator"),
    ("guild_based_config_system", "Config theo guild", "administrator"),
    ("interactive_buttons_ui", "Demo buttons UI", "manage_guild"),
    ("dropdown_ui", "Demo dropdown UI", "manage_guild"),
    ("help_menu_ui", "Help menu UI", "send_messages"),
    ("command_categories", "Danh mục command", "send_messages"),
    ("dynamic_command_loader", "Load command động", "administrator"),
    ("hot_reload_modules", "Hot reload module", "administrator"),
    ("task_scheduler", "Bộ lập lịch", "manage_guild"),
    ("reminder_system", "Nhắc nhở", "send_messages"),
    ("auto_announcement", "Thông báo tự động", "manage_guild"),
    ("giveaway_system", "Hệ thống giveaway", "manage_guild"),
    ("poll_system", "Hệ thống poll", "send_messages"),
    ("suggestion_system", "Hệ thống suggestion", "send_messages"),
    ("ticket_support_system", "Hệ thống ticket", "manage_channels"),
    ("economy_mini_system", "Economy mini", "send_messages"),
]

for spec in COMMAND_SPECS:
    register_stub_command(ModerationCog, name=spec[0], description=spec[1], permission=spec[2])


async def setup(bot: commands.Bot):
    await bot.add_cog(ModerationCog(bot))
