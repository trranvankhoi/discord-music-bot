from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ParsedIntent:
    command: str
    args: dict


class VietnameseIntentParser:
    """Parser ngôn ngữ tự nhiên tiếng Việt theo rule-based cho moderation."""

    def parse(self, text: str) -> ParsedIntent | None:
        lower = text.lower().strip()

        if "xóa toàn bộ chat" in lower or "clear chat" in lower:
            return ParsedIntent(command="clear", args={"amount": 100})
        if "khóa server" in lower:
            return ParsedIntent(command="server_lockdown", args={})
        if "bật chống link" in lower:
            return ParsedIntent(command="anti_link", args={"enabled": True})
        if "tắt chống link" in lower:
            return ParsedIntent(command="anti_link", args={"enabled": False})
        if "ban" in lower and "spam" in lower:
            return ParsedIntent(command="ban_spam", args={})
        return None
