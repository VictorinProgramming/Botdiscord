import discord
from discord.ext import commands
import sqlite3
import random
import time

class XPCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logo_url = "https://i.imgur.com/xqojfhk.jpeg"
        self.banner_url = "https://i.imgur.com/YZP5zd1.png"
        
        # Cooldown para evitar spam (Usuário ganha XP apenas 1 vez por minuto)
        self.cooldowns = {} 

        # Dicionário de Cargos por Nível (Nível: "Nome Exato do Cargo")
        self.CARGOS_RECOMPENSA = {
            5: "🌱・Noob",
            15: "🔥・Ativo",
            30: "🚀・Veterano",
            50: "💎・Elite",
            80: "👑・Lenda"
        }

        # Conecta au banco de dados SQLite
        self.conn = sqlite3.connect("niveis.db")
        self.cursor = self.conn.cursor()
        self.criar_tabela()

    def criar_tabela(self):
        """Cria a tabela de XP no banco de dados se ela não existir"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                user_id INTEGER PRIMARY KEY,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()

    def criar_embed_padrao(self, titulo, description, cor=discord.Color.blurple()):
        """Gera o Embed no padrão visual Noob Até Tentar"""
        embed = discord.Embed(title=titulo, description=description, color=cor)
        embed.set_author(name="Sistema de XP & Níveis", icon_url=self.logo_url)
        embed.set_thumbnail(url=self.logo_url)
        embed.set_image(url=self.banner_url)
        embed.set_footer(text="Noob Até Tentar", icon_url=self.logo_url)
        return embed

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Aplica o cargo Noob assim que o membro entra no servidor"""
        cargo_noob = discord.utils.get(member.guild.roles, name="🌱・Noob")
        if cargo_noob:
            try:
                await member.add_roles(cargo_noob)
                print(f"Cargo inicial 🌱・Noob aplicado para {member.name}")
            except Exception as e:
                print(f"Erro ao aplicar cargo inicial em {member.name}: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Computa o XP por mensagens enviadas"""
        if message.author.bot or message.guild is None:
            return

        if message.content.startswith("!"):
            return

        user_id = message.author.id
        agora = time.time()

        if user_id in self.cooldowns and agora - self.cooldowns[user_id] < 60:
            return

        self.cooldowns[user_id] = agora

        self.cursor.execute("SELECT xp, level FROM usuarios WHERE user_id = ?", (user_id,))
        resultado = self.cursor.fetchone()

        if resultado is None:
            xp_atual = random.randint(15, 25)
            level_atual = 0
            self.cursor.execute("INSERT INTO usuarios (user_id, xp, level) VALUES (?, ?, ?)", (user_id, xp_atual, level_atual))
        else:
            xp_atual, level_atual = resultado
            xp_atual += random.randint(15, 25)
            self.cursor.execute("UPDATE usuarios SET xp = ? WHERE user_id = ?", (xp_atual, user_id))

        self.conn.commit()

        xp_necessario = 5 * (level_atual ** 2) + (50 * level_atual) + 100

        if xp_atual >= xp_necessario:
            level_atual += 1
            self.cursor.execute("UPDATE usuarios SET level = ?, xp = 0 WHERE user_id = ?", (level_atual, user_id))
            self.conn.commit()

            embed_up = self.criar_embed_padrao(
                "🚀 Nível Avançado!",
                f"Parabéns {message.author.mention}!\nVocê alcançou o **Nível {level_atual}** interagindo no nosso servidor!"
            )
            await message.channel.send(embed=embed_up, delete_after=15)

            if level_atual in self.CARGOS_RECOMPENSA:
                nome_cargo = self.CARGOS_RECOMPENSA[level_atual]
                cargo = discord.utils.get(message.guild.roles, name=nome_cargo)
                
                if cargo:
                    try:
                        await message.author.add_roles(cargo)
                        embed_cargo = self.criar_embed_padrao(
                            "👑 Novo Cargo Desbloqueado!",
                            f"Sensacional! Por atingir o nível {level_atual}, você recebeu o cargo: {cargo.mention}!",
                            discord.Color.gold()
                        )
                        await message.channel.send(embed=embed_cargo, delete_after=20)
                    except Exception as e:
                        print(f"Erro ao adicionar cargo {nome_cargo}: {e}")

    @commands.command(name="rank", aliases=["level", "xp"])
    async def rank(self, ctx, membro: discord.Member = None):
        """Mostra o nível e XP atual do usuário"""
        membro = membro or ctx.author
        try:
            await ctx.message.delete()
        except:
            pass

        self.cursor.execute("SELECT xp, level FROM usuarios WHERE user_id = ?", (membro.id,))
        resultado = self.cursor.fetchone()

        if resultado is None:
            xp, level = 0, 0
        else:
            xp, level = resultado

        xp_necessario = 5 * (level ** 2) + (50 * level) + 100

        embed_rank = self.criar_embed_padrao(
            f"📊 Status de {membro.display_name}",
            f"**Nível Atual:** `{level}`\n**XP:** `{xp}/{xp_necessario}`\n\nContinue interagindo para desbloquear novos cargos!"
        )
        if membro.avatar:
            embed_rank.set_thumbnail(url=membro.avatar.url)

        await ctx.send(embed=embed_rank, delete_after=20)

    # ==============================================================================
    # NOVO COMANDO: !top / !leaderboard
    # ==============================================================================
    @commands.command(name="top", aliases=["leaderboard", "ranking"])
    async def top(self, ctx):
        """Mostra o Top 10 membros mais ativos do servidor"""
        try:
            await ctx.message.delete()
        except:
            pass

        # Busca os 10 usuários com maior Level e maior XP no banco de dados
        self.cursor.execute("SELECT user_id, level, xp FROM usuarios ORDER BY level DESC, xp DESC LIMIT 10")
        resultados = self.cursor.fetchall()

        if not resultados:
            embed_vazio = self.criar_embed_padrao("🏆 Ranking Geral", "Ainda não há dados de ranking registrados neste servidor.")
            return await ctx.send(embed=embed_vazio, delete_after=15)

        descricao_ranking = ""
        medais = {1: "🥇", 2: "🥈", 3: "🥉"}

        for indice, (user_id, level, xp) in enumerate(resultados, start=1):
            # Tenta encontrar o membro no servidor para exibir o nome dele
            membro = ctx.guild.get_member(user_id)
            nome_usuario = membro.mention if membro else f"Membro Antigo (`{user_id}`)"
            
            # Escolhe o emoji de posição (Medalha para top 3, número para o resto)
            posicao = medais.get(indice, f"`#{indice}`")
            
            # Monta a linha do ranking de forma organizada
            descricao_ranking += f"{posicao} | {nome_usuario} — **Nível {level}** *(XP: {xp})*\n"

        embed_top = self.criar_embed_padrao(
            "🏆 Ranking Geral - Noob Até Tentar",
            f"Estes são os 10 membros mais ativos do servidor:\n\n{descricao_ranking}"
        )
        
        # Define a foto do servidor como miniatura do ranking
        if ctx.guild.icon:
            embed_top.set_thumbnail(url=ctx.guild.icon.url)

        await ctx.send(embed=embed_top, delete_after=30)

async def setup(bot):
    await bot.add_cog(XPCog(bot))