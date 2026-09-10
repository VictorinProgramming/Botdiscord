import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os

PROXY_URL = os.getenv("PROXY_URL")


# Veririca se o arquivo de cookies do Render existe no servidor
COOKIE_PATH = "/etc/secrets/cookies.txt" if os.path.exists("/etc/secretes/cookies.txt") else "cookies.txt"


YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'extractor_args': {
        'youtube':{
            'player_client': ['ios', 'android', 'mweb']
        }
    }
}

#Adiciona os cookies caso o arquivo esteja presente
if os.path.exists(COOKIE_PATH):
    YTDL_OPTIONS['cookiefile'] = COOKIE_PATH
    print(f"[MUSICA] Cookies carregados com sucesso de: {COOKIE_PATH}")
else:
    print(f"[MUSICA] ATENÇÃO: Arquivo de cookies não encontrado em: {COOKIE_PATH}")

if PROXY_URL:
    YTDL_OPTIONS['proxy'] = PROXY_URL

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

# ==============================================================================
# VIEW DE CONTROLE DE MÚSICA (BOTÕES PERSISTENTES)
# ==============================================================================
class MusicControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Pausar/Retomar", style=discord.ButtonStyle.blurple, emoji="⏯️", custom_id="btn_pause_resume")
    async def pause_resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if not vc:
            return await interaction.response.send_message("❌ Não estou em um canal de voz.", ephemeral=True)

        if vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ Música pausada!", ephemeral=True)
        elif vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ Música retomada!", ephemeral=True)
        else:
            await interaction.response.send_message("ℹ️ Nenhuma música tocando no momento.", ephemeral=True)

    @discord.ui.button(label="Pular", style=discord.ButtonStyle.gray, emoji="⏭️", custom_id="btn_skip")
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("⏭️ Música pulada!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Não há nada tocando para pular.", ephemeral=True)

    @discord.ui.button(label="Parar", style=discord.ButtonStyle.danger, emoji="⏹️", custom_id="btn_stop")
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        
        # 1. Primeiro lida com a desconexão do canal de voz, se houver
        if vc:
            vc.stop()
            await vc.disconnect()

        # 2. Responde à interação e apaga o embed do player do chat
        try:
            await interaction.message.delete()
        except discord.NotFound:
            # Caso a mensagem já tenha sido deletada por outro motivo
            pass
        except discord.Forbidden:
            # Caso o bot não tenha permissão de gerenciar mensagens no canal
            await interaction.response.send_message("⏹️ Player encerrado, mas não tenho permissão para apagar a mensagem.", ephemeral=True)
            return

        # Envia uma confirmação silenciosa (só para quem clicou ver) de que deu certo
        await interaction.response.send_message("⏹️ Player encerrado e painel removido com sucesso!", ephemeral=True)

# ==============================================================================
# COG DE MÚSICA
# ==============================================================================
class MusicaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logo_url = "https://i.imgur.com/xqojfhk.jpeg"
        self.banner_url = "https://i.imgur.com/YZP5zd1.png"

    def criar_embed_padrao(self, titulo, description, cor=discord.Color.blurple()):
        """Gera o Embed no padrão visual Noob Até Tentar"""
        embed = discord.Embed(title=titulo, description=description, color=cor)
        embed.set_author(name="Sistema de Música", icon_url=self.logo_url)
        embed.set_thumbnail(url=self.logo_url)
        embed.set_image(url=self.banner_url)
        embed.set_footer(text="Noob Até Tentar", icon_url=self.logo_url)
        return embed

    @commands.command(name="play")
    async def play(self, ctx, *, busca: str):
        """Toca uma música e envia o painel de controle"""
        try:
            await ctx.message.delete()
        except:
            pass

        if not ctx.author.voice:
            embed = self.criar_embed_padrao("Erro de Conexão", "❌ Você precisa estar em um canal de voz!", discord.Color.red())
            return await ctx.send(embed=embed, delete_after=10)

        # Conecta ou move o bot para o canal
        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()
        elif ctx.voice_client.channel != ctx.author.voice.channel:
            await ctx.voice_client.move_to(ctx.author.voice.channel)

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        msg_carregando = await ctx.send("🔍 **Buscando e processando áudio...**")

        # Extração do áudio
        loop = asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(busca, download=False))
            if 'entries' in data: data = data['entries'][0]
        except Exception as e:
            return await msg_carregando.edit(content=f"❌ Erro ao buscar música: `{e}`")

        url_audio = data['url']
        titulo_musica = data['title']
        
        # Reprodução
        player = discord.FFmpegPCMAudio(url_audio, **FFMPEG_OPTIONS)
        ctx.voice_client.play(player)

        # Embed de Sucesso com Botões
        embed_play = self.criar_embed_padrao(
            "🎵 Tocando Agora",
            f"**Música:** [{titulo_musica}]({data.get('webpage_url', '')})\n**Pedido por:** {ctx.author.mention}"
        )
        if 'thumbnail' in data: embed_play.set_thumbnail(url=data['thumbnail'])

        await msg_carregando.delete()
        await ctx.send(embed=embed_play, view=MusicControlView())

    @play.error
    async def play_error(self, ctx, error):
        """Captura erros cometidos ao executar o comando !play"""
        if isinstance(error, commands.MissingRequiredArgument):
            # Envia a resposta visual padronizada no servidor para comandos incompletos
            embed_erro = self.criar_embed_padrao(
                "⚠️ Comando Incompleto",
                "Você esqueceu de dizer qual música ou link quer tocar!\n\n**Uso Correto:**\n`!play Nome da Música` ou `!play LinkDoYouTube` Setup",
                discord.Color.orange()
            )
            await ctx.send(embed=embed_erro, delete_after=10)
            
            try:
                await ctx.message.delete()
            except:
                pass

    @commands.command(name="leave")
    async def leave(self, ctx):
        """Desconecta o bot manualmente"""
        try:
            await ctx.message.delete()
        except:
            pass

        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            embed = self.criar_embed_padrao("Desconectado", "👋 Saí do canal de voz.")
            await ctx.send(embed=embed, delete_after=10)

async def setup(bot):
    await bot.add_cog(MusicaCog(bot))