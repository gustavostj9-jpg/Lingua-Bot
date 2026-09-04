"""Bot do Discord que traduz mensagens ao receber reações de bandeira."""

import asyncio
import logging

import aiohttp
import discord

from config import FLAG_LANGUAGES, TOKEN

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("flag-translator")

TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"
ERROR_MARKERS = ("Error 500", "Server Error", "That's an error", "<!DOCTYPE html")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True


class TranslationBot(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)
        self._translations_in_progress: set[tuple[int, str]] = set()

    async def setup_hook(self) -> None:
        await self.tree.sync()

    async def on_ready(self) -> None:
        logger.info("Conectado como %s (%s)", self.user, self.user.id if self.user else "?")

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        if not self.user or payload.user_id == self.user.id:
            return

        emoji = str(payload.emoji)
        target = FLAG_LANGUAGES.get(emoji)
        if target is None:
            return

        job = (payload.message_id, target.code)
        if job in self._translations_in_progress:
            return

        self._translations_in_progress.add(job)
        try:
            channel = self.get_channel(payload.channel_id) or await self.fetch_channel(payload.channel_id)
            if not isinstance(channel, (discord.TextChannel, discord.Thread)):
                return

            message = await channel.fetch_message(payload.message_id)
            if message.author.bot or not message.content.strip():
                return

            same_language_reactions = sum(
                reaction.count
                for reaction in message.reactions
                if FLAG_LANGUAGES.get(str(reaction.emoji)) == target
            )
            if same_language_reactions > 1:
                return

            translated = await translate_text(message.content, target.code)

            header = f"{emoji} **{target.name}** · mensagem de {message.author.mention}\n"
            for index, chunk in enumerate(split_message(translated, 2000 - len(header))):
                await message.reply(
                    header + chunk if index == 0 else chunk,
                    mention_author=False,
                    allowed_mentions=discord.AllowedMentions.none(),
                )
        except discord.Forbidden:
            logger.warning("Sem permissão para ler ou responder no canal %s", payload.channel_id)
        except TranslationError:
            logger.warning("Serviço de tradução indisponível para a mensagem %s", payload.message_id)
            await message.reply(
                "⚠️ Não consegui traduzir agora. Tente remover a bandeira e reagir novamente em alguns segundos.",
                mention_author=False,
            )
        except Exception:
            logger.exception("Falha ao traduzir a mensagem %s", payload.message_id)
        finally:
            self._translations_in_progress.discard(job)


class TranslationError(RuntimeError):
    """Indica que o serviço não devolveu uma tradução válida."""


async def translate_text(text: str, target: str) -> str:
    """Traduz com tentativas curtas e rejeita páginas de erro do provedor."""
    params = {
        "client": "gtx",
        "sl": "auto",
        "tl": target,
        "dt": "t",
        "q": text,
    }
    timeout = aiohttp.ClientTimeout(total=15)

    for attempt in range(3):
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(TRANSLATE_URL, params=params) as response:
                    response.raise_for_status()
                    data = await response.json(content_type=None)
                    translated = "".join(part[0] for part in data[0] if part and part[0]).strip()
                    if translated and not any(marker.lower() in translated.lower() for marker in ERROR_MARKERS):
                        return translated
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError, TypeError, IndexError):
            logger.info("Tentativa de tradução %s/3 falhou", attempt + 1)

        if attempt < 2:
            await asyncio.sleep(attempt + 1)

    raise TranslationError("O provedor não retornou uma tradução válida.")


def split_message(text: str, limit: int) -> list[str]:
    """Divide texto sem ultrapassar o limite do Discord."""
    chunks: list[str] = []
    remaining = text.strip()
    while len(remaining) > limit:
        cut = remaining.rfind("\n", 0, limit + 1)
        if cut < limit // 2:
            cut = remaining.rfind(" ", 0, limit + 1)
        if cut < limit // 2:
            cut = limit
        chunks.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()
    if remaining:
        chunks.append(remaining)
    return chunks


bot = TranslationBot()


@bot.tree.command(name="idiomas", description="Mostra as bandeiras aceitas para tradução.")
async def languages(interaction: discord.Interaction) -> None:
    lines = [f"{flag}  {language.name}" for flag, language in FLAG_LANGUAGES.items()]
    await interaction.response.send_message(
        "Reaja a qualquer mensagem com uma destas bandeiras:\n\n" + "\n".join(lines),
        ephemeral=True,
    )


def run() -> None:
    if not TOKEN:
        raise RuntimeError("Defina DISCORD_TOKEN no ambiente antes de iniciar o bot.")
    bot.run(TOKEN, log_handler=None)


if __name__ == "__main__":
    run()
