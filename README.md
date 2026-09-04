# Flag Translator Bot

Bot simples para traduzir mensagens no Discord usando reações de bandeira.
Reaja com 🇧🇷 para português, 🇺🇸 para inglês, 🇪🇸 para espanhol e assim por diante.

## Como executar

1. Crie uma aplicação no [Discord Developer Portal](https://discord.com/developers/applications).
2. Na aba **Bot**, ative o intent privilegiado **Message Content Intent**.
3. Convide o bot com os escopos `bot` e `applications.commands`. Dê permissão para ver canais, ler o histórico e enviar mensagens.
4. Instale Python 3.11 ou mais recente e execute `pip install -r requirements.txt`.
5. Defina `DISCORD_TOKEN` no ambiente da hospedagem ou do terminal.
6. Execute `python bot.py`.

Use `/idiomas` no Discord para ver todas as bandeiras aceitas.

> A tradução usa um endpoint público do Google Translate; requer internet e está sujeita à disponibilidade do serviço.

## Publicar no GitHub

O arquivo `.env` está ignorado pelo Git. Nunca publique o token do bot. Se um token já tiver sido exposto, gere outro no Developer Portal antes de publicar.

```bash
git init
git add .
git commit -m "feat: add reaction-based Discord translator"
```

## Licença

MIT
