import discord
from discord.ext import commands
import sqlite3
from aiohttp import web
import asyncio
import datetime
import time

class SegurancaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logo_url = "https://i.imgur.com/xqojfhk.jpeg"
        self.banner_url = "https://i.imgur.com/YZP5zd1.png"
        
        # --- Lista de Canais Permitidos para o comando !infoid ---
        self.CANAIS_PERMITIDOS = [
            1508871694083690629, # Canal do Dono
            1509265359956348958, # Audit Log
            1509265262850080849  # Member Logs
        ]

        # Configurações de Rede para o validador de IP
        self.REDIRECT_URI = "http://localhost:5000/callback"
        
        # Conecta ao banco de dados SQLite
        self.conn = sqlite3.connect("niveis.db")
        self.cursor = self.conn.cursor()
        self.criar_tabelas()
        
        # Inicia o servidor Web em segundo plano junto com o bot
        self.bot.loop.create_task(self.iniciar_servidor_web())

    def criar_tabelas(self):
        """Cria a tabela de segurança no banco se não existir"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS verificacoes (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                ip_address TEXT,
                data_verificacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def criar_embed_padrao(self, titulo, descricao, cor=discord.Color.blurple()):
        """Gera o Embed no padrão visual oficial Noob Até Tentar"""
        embed = discord.Embed(title=titulo, description=descricao, color=cor)
        embed.set_author(name="Segurança Extrema", icon_url=self.logo_url)
        embed.set_thumbnail(url=self.logo_url)
        embed.set_image(url=self.banner_url)
        embed.set_footer(text="Noob Até Tentar", icon_url=self.logo_url)
        return embed

    # ==============================================================================
    # SERVIDOR WEB INTEGRADO (Captura o IP e envia para os canais de Log)
    # ==============================================================================
    async def iniciar_servidor_web(self):
        app = web.Application()
        app.router.add_get('/callback', self.handle_callback)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 5000)
        await site.start()
        print("🌐 Servidor de captura de IP rodando na porta 5000!")

    async def handle_callback(self, request):
        ip_cliente = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_id = request.query.get('id')
        username = request.query.get('user', 'Desconhecido')

        if not user_id:
            return web.Response(text="Erro: Parâmetros inválidos.", status=400)

        user_id = int(user_id)

        self.cursor.execute("INSERT OR REPLACE INTO verificacoes (user_id, username, ip_address) VALUES (?, ?, ?)", 
                            (user_id, username, ip_cliente))
        self.conn.commit()

        self.cursor.execute("SELECT user_id, username FROM verificacoes WHERE ip_address = ? AND user_id != ?", (ip_cliente, user_id))
        alts = self.cursor.fetchall()
        texto_alts = "🟢 Nenhuma outra conta vinculada a este IP." if not alts else "\n".join([f"⚠️ <@{u[0]}> (`{u[1]}`)" for u in alts])

        embed_log = self.criar_embed_padrao(
            "🚨 Conta Verificada via IP",
            f"**Usuário:** <@{user_id}>\n"
            f"**ID:** `{user_id}`\n"
            f"**IP Capturado:** `{ip_cliente}`\n\n"
            f"**Histórico de Contas com mesmo IP:**\n{texto_alts}",
            discord.Color.red() if alts else discord.Color.green()
        )

        # Envia os logs automáticos de IP para os canais de log configurados
        for canal_id in [1509265262850080849, 1509265359956348958]:
            canal = self.bot.get_channel(canal_id)
            if canal:
                try:
                    await canal.send(embed=embed_log)
                except Exception as e:
                    print(f"Erro ao enviar log para o canal {canal_id}: {e}")

        return web.Response(text="✅ Verificação Concluída com Sucesso! Pode fechar esta aba e voltar ao Discord.", content_type='text/html', charset='utf-8')

    # ==============================================================================
    # COMANDO PÚBLICO: !verificar
    # ==============================================================================
    @commands.command(name="verificar")
    async def verificar(self, ctx):
        """Envia o link de validação de IP na DM do usuário"""
        try:
            await ctx.message.delete()
        except:
            pass

        link_verificacao = f"http://localhost:5000/callback?id={ctx.author.id}&user={ctx.author.name}"

        embed = self.criar_embed_padrao(
            "🔒 Verificação de Segurança",
            f"Olá {ctx.author.mention},\n\nPara garantir a integridade do **Noob Até Tentar** e mitigar o uso de contas alternativas abusivas, precisamos validar seu acesso.\n\n"
            f"Clique no link abaixo para concluir:\n🔗 **[CLIQUE AQUI PARA SE VERIFICAR]({link_verificacao})**"
        )
        
        try:
            await ctx.author.send(embed=embed)
        except discord.Forbidden:
            await ctx.send(f"❌ {ctx.author.mention}, preciso que abra suas mensagens diretas (DM) para receber o link!", delete_after=10)

    # ==============================================================================
    # COMANDO SEGURANÇA: !infoid <@Membro ou ID> (Permitido em 3 canais de Staff)
    # ==============================================================================
    @commands.command(name="infoid", aliases=["userinfo", "dossie"])
    async def infoid(self, ctx, membro: discord.Member = None):
        """Puxa o dossiê avançado com todos os dados de um usuário do Discord"""
        # Modificação crítica: O comando agora verifica se o canal atual está dentro da lista permitida
        if ctx.channel.id not in self.CANAIS_PERMITIDOS:
            return 

        try:
            await ctx.message.delete()
        except:
            pass

        membro = membro or ctx.author

        criado_em = membro.created_at.strftime("%d/%m/%Y às %H:%M:%S")
        entrou_em = membro.joined_at.strftime("%d/%m/%Y às %H:%M:%S") if membro.joined_at else "Desconhecido"
        
        cargos = [cargo.mention for cargo in membro.roles if cargo != ctx.guild.default_role]
        lista_cargos = ", ".join(cargos) if cargos else "Nenhum cargo atribuído."

        status_traduzido = {
            discord.Status.online: "🟢 Online",
            discord.Status.idle: "🌙 Ausente",
            discord.Status.dnd: "🔴 Não Perturbar / Ocupado",
            discord.Status.offline: "⚫ Offline / Invisível"
        }
        status_atual = status_traduzido.get(membro.status, "⚫ Desconhecido")

        e_bot = "🤖 Sim" if membro.bot else "👤 Não (Conta Humana)"

        tempo_existencia = datetime.datetime.now(datetime.timezone.utc) - membro.created_at
        conta_suspeita = "⚠️ **CONTA RECENTE (Menos de 30 dias!)**" if tempo_existencia.days < 30 else "🟢 Conta Antiga / Segura"

        embed_dossie = discord.Embed(
            title=f"🔍 Dossiê Avançado: {membro.name}",
            description=f"Todos os dados coletados via API do Discord para o usuário {membro.mention}.",
            color=discord.Color.red() if tempo_existencia.days < 30 else discord.Color.blurple()
        )
        
        embed_dossie.add_field(name="🆔 ID do Usuário", value=f"`{membro.id}`", inline=False)
        embed_dossie.add_field(name="🏷️ Tag Global / Nome", value=f"`{membro.name}`", inline=True)
        embed_dossie.add_field(name="Nickname no Servidor", value=f"`{membro.display_name}`", inline=True)
        
        embed_dossie.add_field(name="🤖 É Bot?", value=e_bot, inline=True)
        embed_dossie.add_field(name="⚡ Status de Presença", value=status_atual, inline=True)
        embed_dossie.add_field(name="🛡️ Avaliação de Risco", value=conta_suspeita, inline=True)
        
        embed_dossie.add_field(name="📅 Conta Criada Em", value=f"`{criado_em}`", inline=False)
        embed_dossie.add_field(name="📥 Entrou no Servidor Em", value=f"`{entrou_em}`", inline=False)
        
        embed_dossie.add_field(name="🎖️ Cargos Atuais", value=lista_cargos, inline=False)

        if membro.avatar:
            embed_dossie.set_thumbnail(url=membro.avatar.url)
        
        embed_dossie.set_image(url=self.banner_url)
        embed_dossie.set_footer(text=f"Noob Até Tentar • Logs do Dono", icon_url=self.logo_url)

        await ctx.send(embed=embed_dossie)

async def setup(bot):
    await bot.add_cog(SegurancaCog(bot))