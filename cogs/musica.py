import discord
from discord.ext import commands
import yt_dlp
import asyncio

# Configuração robusta do yt-dlp utilizando o arquivo de cookies para evitar bloqueios do YouTube
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'cookiefile': 'cookies.txt'
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        
        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class MusicaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logo_url = "https://i.imgur.com/xqojfhk.jpeg"
        self.banner_url = "https://i.imgur.com/YZP5zd1.png"

    @commands.command(name="play", aliases=["tocar", "p"])
    async def play(self, ctx, *, query: str):
        if not ctx.author.voice:
            return await ctx.send("❌ Você precisa estar em um canal de voz para reproduzir músicas!", delete_after=10)

        canal_voz = ctx.author.voice.channel
        
        if ctx.voice_client is None:
            await canal_voz.connect()
        elif ctx.voice_client.channel != canal_voz:
            await ctx.voice_client.move_to(canal_voz)

        try:
            await ctx.message.delete()
        except Exception:
            pass

        async with ctx.typing():
            try:
                player = await YTDLSource.from_url(query, loop=self.bot.loop, stream=True)
                if ctx.voice_client.is_playing():
                    ctx.voice_client.stop()
                
                ctx.voice_client.play(player, after=lambda e: print(f'Erro no player de áudio: {e}') if e else None)
            except Exception as e:
                return await ctx.send(f"❌ Não foi possível carregar a música. Erro: `{e}`", delete_after=15)

        embed = discord.Embed(
            title="🎶 Tocando Agora",
            description=f"**[{player.title}]({player.data.get('webpage_url')})**",
            color=discord.Color.green()
        )
        embed.set_author(name="Sistema de Música", icon_url=self.logo_url)
        embed.set_thumbnail(url=self.logo_url)
        embed.set_image(url=self.banner_url)
        embed.set_footer(text=f"Requisitado por {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else self.logo_url)

        await ctx.send(embed=embed, delete_after=30)

    @commands.command(name="stop", aliases=["parar", "disconnect", "sair"])
    async def stop(self, ctx):
        try:
            await ctx.message.delete()
        except Exception:
            pass

        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("⏹️ Reprodução encerrada e bot desconectado do canal de voz.", delete_after=10)
        else:
            await ctx.send("❌ O bot não está conectado a nenhum canal de voz no momento.", delete_after=10)


async def setup(bot):
    await bot.add_cog(MusicaCog(bot))