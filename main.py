import discord
from discord.ext import commands
import os

# 1. Configuração Global do Proxy Corporativo
PROXY_URL = os.getenv("PROXY_URL")

if PROXY_URL:
    os.environ['HTTP_PROXY'] = PROXY_URL
    os.environ['HTTPS_PROXY'] = PROXY_URL
    os.environ['http_proxy'] = PROXY_URL
    os.environ['https_proxy'] = PROXY_URL


class NoobAteTentar(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        # 2. Adicionado o parâmetro 'proxy=PROXY_URL' na inicialização do Bot
        kwargs ={
            "command_prefix": "!",
            "case_insensitive": True,
            "intents" : intents
        }
        if PROXY_URL:
            kwargs ["proxy"] = PROXY_URL

        super() .__init__(**kwargs)

    async def setup_hook(self):
        # 1. Carrega todas as Views de forma persistente
        from cogs.cargos import BotoesCargos
        from cogs.tickets import DropdownView, BotaoFecharTicket
        from cogs.musica import MusicControlView

        self.add_view(BotoesCargos())
        self.add_view(DropdownView())
        self.add_view(BotaoFecharTicket())
        self.add_view(MusicControlView())

        # 2. Varre a pasta 'cogs' e liga todos os módulos dinamicamente
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
    raise ValueError("O Tolen 'DISCORD_TOKEN' não foi configurado nas variáveis de ambiente!")

# Executa o bot com o seu Token original corrigido
bot.run(TOKEN)

