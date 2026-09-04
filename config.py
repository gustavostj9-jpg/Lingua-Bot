"""Configuração do bot de tradução."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Language:
    code: str
    name: str


TOKEN = os.getenv("DISCORD_TOKEN")

FLAG_LANGUAGES = {
    "🇧🇷": Language("pt", "Português"),
    "🇺🇸": Language("en", "English"),
    "🇬🇧": Language("en", "English"),
    "🇪🇸": Language("es", "Español"),
    "🇫🇷": Language("fr", "Français"),
    "🇩🇪": Language("de", "Deutsch"),
    "🇮🇹": Language("it", "Italiano"),
    "🇯🇵": Language("ja", "日本語"),
    "🇰🇷": Language("ko", "한국어"),
    "🇨🇳": Language("zh-CN", "中文"),
    "🇷🇺": Language("ru", "Русский"),
}
