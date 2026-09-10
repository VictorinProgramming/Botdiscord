import os
import discord
from discord.ext import commands

# 1. Configuração Global do Proxy Corporativo
PROXY_URL = os.getenv("PROXY_URL")

if PROXY_URL:
    os.environ['HTTP_PROXY'] = PROXY_URL
    os.environ['HTTPS_PROXY'] = PROXY_URL
    os.environ['http_proxy'] = PROXY_URL
    os.environ['https_proxy'] = PROXY_URL


def criar_arquivo_cookies():
    # Usando o caractere de tabulação real dentro das strings brutas
    linhas = [
        "# Netscape HTTP Cookie File",
        "# https://curl.haxx.se/rfc/cookie_spec.html",
        "# This is a generated file! Do not edit.",
        ".youtube.com\tTRUE\t/\tTRUE\t1789050077\tGPS\t1",
        ".youtube.com\tTRUE\t/\tTRUE\t1820584278\t__Secure-1PSIDTS\tsidts-CjQBXMw41Sgx0lWo2uINyNMlIuam19MBQzR1dJ5uKwbs_yRAGl5xfME0M_6kgPcd9drlYvk_EAA",
        ".youtube.com\tTRUE\t/\tTRUE\t1820584278\t__Secure-3PSIDTS\tsidts-CjQBXMw41Sgx0lWo2uINyNMlIuam19MBQzR1dJ5uKwbs_yRAGl5xfME0M_6kgPcd9drlYvk_EAA",
        ".youtube.com\tTRUE\t/\tTRUE\t1823608278\t__Secure-3PAPISID\th2sFfB9o99rIryl-/A1pWeJktNC5r25-we",
        ".youtube.com\tTRUE\t/\tTRUE\t1823608278\t__Secure-3PSID\tg.a000CQk6VEQOAG4rS3Bh5ELbbgE6rGuwXNx35VxtTpHLg8kLHtIgbkArHDsnju6srypdp_ZnqgACgYKAV0SARESFQHGX2MihSGIytd0EaAJFQkGAEZ4qBoVAUF8yKrd0ct4sz07jJ8sGFVe8o-L0076",
        ".youtube.com\tTRUE\t/\tTRUE\t1823608279\tLOGIN_INFO\tAFmmF2swRQIgXwI6aRRawgHkydLJEL6n3WLcdXVwscFgxodhmusDyj4CIQDmeHfhB9UVGh-8Jd6rsoozef5Hm_pHiH9EoKcj0wsLkQ:QUQ3MjNmeXh4Tmx0VkRqTUxESE5lZ2Q0V0tpS2NhVXFqS0JsS3FlOUlNa1ZnWElBX0JzdEtXeEVJT3BaSV9nM1lDMTgxbWc0bjdwN2dlZXNsUGZpR0xscnNWYWsxVzh0TjhVVHhEMWk3TXBGNmstcDZJandmajRLazB2dzNjSmNEcG5FOFA0ZE9tUGl1Q0JCckFKdF95X3V4VWxkWUxEMm1R",
        ".youtube.com\tTRUE\t/\tTRUE\t1823608286\tPREF\ttz=America.Sao_Paulo",
        ".youtube.com\tTRUE\t/\tTRUE\t1820584328\t__Secure-3PSIDCC\tAKEyXzX3Tvi3kdrtSvY4v6AAJ18aHs5QBPiVrqFSOFLtPkmrZHCPxufjhPP6TdfCpJM_bo79SA",
        ".youtube.com\tTRUE\t/\tTRUE\t0\tYSC\tzsjCqMY7WGA",
        ".youtube.com\tTRUE\t/\tTRUE\t1804600285\tVISITOR_INFO1_LIVE\tkkyD7RjtZDc",
        ".youtube.com\tTRUE\t/\tTRUE\t1804600285\tVISITOR_PRIVACY_METADATA\tCgJCUhIEGgAgXw%3D%3D",
        ".youtube.com\tTRUE\t/\tTRUE\t1804600279\t__Secure-YNID\t21.YT=ke7NG7-9iragxnKb_ltlqGPUkZNw7MKOxuZibFihI1nCX985Ts5UJfFd-ceAOZ1pvNESw7tGBrI4_2_CIzTW2TtjQtu9s6jPQMagaZA2ZcwzCkaw5MdQaIr559T4pvOiezsbFd4xVw_MG_VYt62iaDb2NSAZEHIqUOk_FYngIf-zO7pbUivwY3E3V6tICtJweL-eCfhX-p9rRjvXnc1K3axGvWDRK6VDid9UxH39BXEYP_km3aCMqv6xH6jVEvBmHpUfWHORgvPmOxOfb_2BxC9iosoCRwJFKM2ylkHbXDwIcl5KkvnEvgtA58_25Mi52N6t08Y_P2HEsJ10eI37FQ",
        ".youtube.com\tTRUE\t/\tTRUE\t1804600279\t__Secure-ROLLOUT_TOKEN\tCPfm5P3F-7-lKBCa0aqYlOSWAxis28CYlOSWAw%3D%3D"
    ]
    
    with open("cookies.txt", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(linhas) + "\n")
    print("✅ Arquivo cookies.txt gerado com tabulações reais!")


class NoobAteTentar(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        kwargs = {
            "command_prefix": "!",
            "case_insensitive": True,
            "intents": intents
        }
        if PROXY_URL:
            kwargs["proxy"] = PROXY_URL

        super().__init__(**kwargs)

    async def setup_hook(self):
        # 1. Gera o arquivo de cookies antes de carregar os cogs
        criar_arquivo_cookies()

        # 2. Carrega todas as Views de forma persistente
        from cogs.cargos import BotoesCargos
        from cogs.tickets import DropdownView, BotaoFecharTicket
        from cogs.musica import MusicControlView

        self.add_view(BotoesCargos())
        self.add_view(DropdownView())
        self.add_view(BotaoFecharTicket())
        self.add_view(MusicControlView())

        # 3. Varre a pasta 'cogs' e liga todos os módulos dinamicamente
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')

        print("Views persistentes e Cogs carregados com sucesso!")

    async def on_ready(self):
        print(f"Bot {self.user} ligado com sucesso via Proxy!")


# Instancia o bot
bot = NoobAteTentar()

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("O Token 'DISCORD_TOKEN' não foi configurado nas variáveis de ambiente!")

bot.run(TOKEN)