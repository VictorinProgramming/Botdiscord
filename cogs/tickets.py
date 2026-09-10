import discord
from discord.ext import commands

class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(value="suporte", label="Suporte", description="Abra um ticket para suporte geral", emoji="🛠️"),
            discord.SelectOption(value="duvidas", label="Dúvidas", description="Abra um ticket para tirar suas dúvidas", emoji="❓"),
            discord.SelectOption(value="reclamacoes", label="Reclamações", description="Abra um ticket para fazer uma reclamação", emoji="⚠️"),
            discord.SelectOption(value="outros", label="Outros", description="Abra um ticket para outros assuntos", emoji="📋"),
            discord.SelectOption(value="feedback", label="Feedback", description="Abra um ticket para dar feedbacks sobre o servidor", emoji="💬"),
            discord.SelectOption(value="parcerias", label="Parcerias", description="Abra um ticket para falar sobre parcerias", emoji="🤝"),
            discord.SelectOption(value="reportar_usuario", label="Reportar Usuário", description="Abra um ticket para reportar um usuário", emoji="🚨"),
            discord.SelectOption(value="sugestoes", label="Sugestões", description="Abra um ticket para dar sugestões para o servidor", emoji="💡"),
            discord.SelectOption(value="eventos", label="Eventos", description="Abra um ticket para falar sobre eventos no servidor", emoji="🎉")
        ]
        super().__init__(
            placeholder="Selecione o tipo do seu ticket...", 
            min_values=1, 
            max_values=1, 
            options=options,
            custom_id="persistent_view:dropdown_help"
        )

    async def callback(self, interaction: discord.Interaction):
        tipo_ticket = self.values[0].replace("_", " ").title()
        guild = interaction.guild
        user = interaction.user

        await interaction.response.defer(ephemeral=True)

        ID_CATEGORIA_TICKETS = 1509190555203145949
        categoria = guild.get_channel(ID_CATEGORIA_TICKETS)

        ID_CARGO_SUPORTE = 1508862398101061702 
        cargo_suporte = guild.get_role(ID_CARGO_SUPORTE)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, embed_links=True)
        }

        if cargo_suporte:
            overwrites[cargo_suporte] = discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, embed_links=True)

        nome_canal = f"🎫-{self.values[0]}-{user.name}"
        channel = await guild.create_text_channel(name=nome_canal, overwrites=overwrites, category=categoria)

        embed_ticket = discord.Embed(
            title=f"Atendimento: {tipo_ticket}",
            description=f"Olá {user.mention},\nBem-vindo ao seu espaço de suporte individual.\n\nDescreva detalhadamente o seu problema ou dúvida para que a nossa equipe possa te auxiliar o mais rápido possível.",
            color=discord.Color.yellow()
        )
        embed_ticket.set_footer(text="Para encerrar este atendimento e salvar os logs, clique no botão abaixo.")
        
        await channel.send(content=f"{user.mention} | Atendimento iniciado.", embed=embed_ticket, view=BotaoFecharTicket())

        await guild.fetch_channels()
        channel_atualizado = guild.get_channel(channel.id)
        mencao_canal = channel_atualizado.mention if channel_atualizado else f"#{nome_canal}"

        # Envia a resposta temporária e limpa em 5 segundos
        resposta = await interaction.followup.send(f"✅ Seu ticket de **{tipo_ticket}** foi aberto com sucesso em {mencao_canal}!", ephemeral=True)
        try:
            await resposta.delete(delay=5)
        except:
            pass


class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Dropdown())


class BotaoFecharTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Fechar Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="btn_fechar_ticket")
    async def btn_fechar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        channel = interaction.channel
        
        ID_CANAL_LOGS = 1509263026015043584
        canal_logs = guild.get_channel(ID_CANAL_LOGS)

        texto_log = ""
        async for mensagem in channel.history(limit=200, oldest_first=True):
            conteudo = mensagem.content if mensagem.content else "[Anexo/Embed sem texto]"
            texto_log += f"[{mensagem.created_at.strftime('%d/%m/%Y %H:%M')}] {mensagem.author.name}: {conteudo}\n"

        if not texto_log:
            texto_log = "Nenhuma mensagem enviada pelos usuários neste ticket."

        if len(texto_log) > 950:
            texto_log = texto_log[:950] + "\n... (Histórico muito longo, cortado para manter a estrutura do Log)"

        if canal_logs:
            embed_log = discord.Embed(
                title=f"📋 Log de Ticket Fechado - {channel.name}",
                color=discord.Color.red(),
                timestamp=interaction.created_at
            )
            embed_log.add_field(name="Ticket deletado por", value=interaction.user.mention, inline=True)
            embed_log.add_field(name="Canal Original", value=f"`{channel.name}`", inline=True)
            embed_log.add_field(name="Histórico de Conversa", value=f"```text\n{texto_log}```", inline=False)
            embed_log.set_footer(text="Noob Até Tentar - Central de Logs", icon_url="https://i.imgur.com/xqojfhk.jpeg")

            await canal_logs.send(embed=embed_log)

        try:
            await channel.delete(reason=f"Ticket fechado por {interaction.user.name}")
        except discord.HTTPException:
            pass


class TicketsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ticket")
    @commands.has_permissions(administrator=True)
    async def enviar_painel_ticket(self, ctx):
        try: await ctx.message.delete()
        except: pass

        embed_painel = discord.Embed(
            title="🎫 Central de Atendimento - Noob Até Tentar",
            description="Precisa de ajuda ou quer falar com a nossa administração?\n\nSelecione a categoria correspondente à sua necessidade no menu dropdown abaixo para abrir um canal privado de atendimento.",
            color=discord.Color.gold()
        )
        embed_painel.set_author(name="Suporte Técnico", icon_url="https://i.imgur.com/xqojfhk.jpeg")
        embed_painel.set_thumbnail(url="https://i.imgur.com/xqojfhk.jpeg")
        embed_painel.set_image(url="https://i.imgur.com/YZP5zd1.png")
        embed_painel.set_footer(text="Sistema de Suporte Automático", icon_url="https://i.imgur.com/xqojfhk.jpeg")

        await ctx.send(embed=embed_painel, view=DropdownView())

async def setup(bot):
    await bot.add_cog(TicketsCog(bot))