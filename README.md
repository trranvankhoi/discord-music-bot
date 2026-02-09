# Discord Professional Server Manager Bot (Python)

Bot quản trị Discord chuyên nghiệp, hỗ trợ **slash commands + prefix commands**, có logging, database SQLite, cooldown, permission system, parser AI moderation tiếng Việt và kiến trúc module dễ mở rộng.

## Tính năng chính

- Hơn **100 lệnh quản trị** được đăng ký dưới dạng hybrid commands (dùng được cả `/` và prefix).
- Quản lý thành viên, chat, role, server, voice, security, logging, config, advanced system.
- AI moderation hiểu câu tiếng Việt theo kiểu ngôn ngữ tự nhiên khi mention bot.
- Lưu dữ liệu vào SQLite (`warns`, `notes`, `mod_logs`, `guild_config`, `reminders`, ...).
- Logging chuẩn production với rotating file.
- Prefix cấu hình theo từng guild.
- Cooldown chống spam lệnh.

## Cấu trúc mã nguồn

```bash
bot/
 ├── main.py
 ├── cogs/
 │   ├── moderation.py
 │   ├── ai_moderation.py
 │   └── system.py
 ├── utils/
 │   ├── logger.py
 │   ├── checks.py
 │   ├── embeds.py
 │   ├── paginator.py
 │   └── command_factory.py
 ├── database/
 │   └── db.py
 ├── ai/
 │   └── nlp_moderation.py
 ├── config/
 │   └── settings.py
 └── logs/
```

## Cài đặt

### 1) Yêu cầu

- Python 3.10+
- Discord bot token

### 2) Cài dependencies

```bash
pip install -r requirements.txt
```

### 3) Tạo file `.env`

```bash
cp .env.example .env
```

Sau đó cập nhật token bot trong `.env`:

```env
DISCORD_TOKEN=your_discord_bot_token_here
BOT_PREFIX=!
BOT_LANGUAGE=vi
AI_ENABLED=true
DATABASE_PATH=bot/database/bot.db
LOG_LEVEL=INFO
```

### 4) Chạy bot

```bash
python main.py
```

## Ví dụ AI Moderation (Natural Language)

Mention bot và nhập câu tiếng Việt:

- `@bot xóa toàn bộ chat`
- `@bot khóa server`
- `@bot bật chống link`
- `@bot ban user spam`

Bot sẽ parse intent và thực thi flow moderation phù hợp.

## Danh sách lệnh

Bot đã có hơn 100 command (đa số từ danh sách bắt buộc) gồm:

- Member moderation: `ban`, `kick`, `warn`, `unwarn`, `warn_list`, `mute`, `timeout`, `temp_ban`, ...
- Chat moderation: `clear`, `clear_by_user`, `slowmode`, `anti_spam`, `anti_link`, ...
- Role management: `create_role`, `reaction_role`, `mass_role_add`, ...
- Server management: `server_info`, `server_lockdown`, `set_logs_channel`, ...
- Voice management: `voice_lock`, `voice_unlock`, `voice_statistics`, ...
- Logging & security: `export_log_file`, `anti_raid_system`, `whitelist`, `blacklist`, ...
- Advanced system: `help_ui`, `remindme`, `giveaway_system`, `ticket_support_system`, ...

## Lưu ý production

- Cần bật `MESSAGE CONTENT INTENT` trong Discord Developer Portal.
- Nên cấu hình quyền bot phù hợp (Ban Members, Manage Roles, Manage Channels, ...).
- Dùng PM2/systemd/docker để chạy ổn định 24/7.
