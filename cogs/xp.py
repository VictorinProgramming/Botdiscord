import discord
from discord.ext import commands
import sqlite3
import math
import random

class XPCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logo_url = "https://i.imgur.com/xqojfhk.jpeg"
        self.banner_url = "https://i.imgur.com/YZP5zd1.png"
        
        self.conn = sqlite3.connect("niveis.db")
        self.cursor = self.conn.cursor()
        self.criar_tabela_xp()

    def criar_tabela_xp(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios_xp (
                user_id INTEGER PRIMARY KEY,
                guild_id INTEGER,
                xp INTEGER DEFAULT 0,
                nivel INTEGER DEFAULT 1
            )
        """)
        self.conn.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        user_id = message.author.id
        guild_id = message.guild.id
        
        # Ganho aleatório de XP por mensagem enviada (entre 15 e 25 XP)
        ganho_xp = random.randint(15, 25)

        self.cursor.execute("SELECT xp, nivel FROM usuarios_xp WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
        resultado = self.cursor.fetchone()

        if resultado:
            xp_atual, nivel_atual = resultado
            novo_xp = xp_atual + ganho_xp
            
            # Fórmula de cálculo de nível: Precisa de 100 * (nivel ^ 1.5) XP para subir
            xp_necessario = math.floor(100 * (nivel_atual ** 1.5))

            if novo_xp >= xp_necessario:
                novo_nivel = nivel_atual + 1
                self.cursor.execute("UPDATE usuarios_xp SET xp = ?, nivel = ? WHERE user_id = ? AND guild_id = ?", (novo_xp, novo_nivel, user_id, guild_id))
                self.conn.commit()

                # Mensagem de parabéns ao subir de nível
                embed_levelup = discord.Embed(
                    title="🎉 Subida de Nível!",
                    description=f"Parabéns {message.author.mention}! Você avançou para o **Nível {novo_nivel}**! 🚀",
                    color=discord.Color.gold()
                )
                embed_levelup.set_thumbnail(url=message.author.avatar.url if message.author.avatar else self.logo_url)
                await message.channel.send(embed=embed_levelup, delete_after=15)
            else:
                self.cursor.execute("UPDATE usuarios_xp SET xp = ? WHERE user_id = ? AND guild_id = ?", (novo_xp, user_id, guild_id))
                self.conn.commit()
        else:
            self.cursor.execute("INSERT INTO usuarios_xp (user_id, guild_id, xp, nivel) VALUES (?, ?, ?, ?)", (user_id, guild_id, ganho_xp, 1))
            self.conn.commit()

    @commands.command(name="rank", aliases=["nivel", "level", "xp"])
    async def rank(self, ctx, membro: discord.Member = None):
        try:
            await ctx.message.delete()
        except Exception:
            pass

        membro = membro or ctx.author
        user_id = membro.id
        guild_id = ctx.guild.id

        self.cursor.execute("SELECT xp, nivel FROM usuarios_xp WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
        resultado = self.cursor.fetchone()

        if not resultado:
            xp_atual, nivel_atual = 0, 1
        else:
            xp_atual, nivel_atual = resultado

        xp_necessario = math.floor(100 * (nivel_atual ** 1.5))

        embed = discord.Embed(
            title=f"📊 Status de Nível: {membro.display_name}",
            description=f"Consulte o progresso de experiência na comunidade **Noob Até Tentar**.",
            color=discord.Color.blurple()
        )
        embed.add_field(name="⭐ Nível Atual", value=f"`{nivel_atual}`", inline=True)
        embed.add_field(name="✨ Experiência (XP)", value=f"`{xp_atual} / {xp_necessario} XP`", inline=True)
        
        embed.set_author(name="Sistema de Níveis", icon_url=self.logo_url)
        embed.set_thumbnail(url=membro.avatar.url if membro.avatar else self.logo_url)
        embed.set_image(url=self.banner_url)
        embed.set_footer(text="Noob Até Tentar", icon_url=self.logo_url)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(XPCog(bot))