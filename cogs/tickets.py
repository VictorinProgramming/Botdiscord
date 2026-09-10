import discord
from discord.ext import commands
import asyncio

class BotaoFecharTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Fechar Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="btn_fechar_ticket")
    async def fechar_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 **Fechando este ticket em 5 segundos...**", ephemeral=False)
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete()
        except Exception as e:
            print(f"Erro ao deletar canal de ticket: {e}")


class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Suporte Técnico", description="Problemas com o bot, site ou ferramentas.", emoji="🛠️", value="suporte"),
            discord.SelectOption(label="Denúncias", description="Reportar infrações de regras ou usuários mal-intencionados.", emoji="🚨", value="denuncia"),
            discord.SelectOption(label="Parcerias", description="Propostas de parcerias e divulgações.", emoji="🤝", value="parceria"),
            discord.SelectOption(label="Financeiro / Doações", description="Dúvidas sobre apoios ou pagamentos.", emoji="💳", value="financeiro")
        ]
        super().__init__(placeholder="Selecione o motivo do seu atendimento...", min_values=1, max_values=1, options=options, custom_id="dropdown_tickets")

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        categoria_id = 1507955755125440669  # ID opcional de uma categoria de canais de tickets (ajuste se necessário)
        categoria = guild.get_channel(categoria_id) if categoria_id else None

        # Configura permissões do canal privado do ticket
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }

        # Dá acesso também a cargos de staff/administração se necessário
        cargo_staff = guild.get_role(1507964006701469749)  # Ex: Cargo de Programador/Staff
        if cargo_staff:
            overwrites[cargo_staff] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        nome_canal = f"ticket-{self.values[0]}-{interaction.user.name}"
        
        # Evita duplicidade de canais abertos pelo mesmo usuário com o mesmo tema
        existing_channel = discord.utils.get(guild.text_channels, name=nome_canal.lower())
        if existing_channel:
            return await interaction.response.send_message(f"❌ Você já possui um ticket aberto em {existing_channel.mention}!", ephemeral=True)

        canal_ticket = await guild.create_text_channel(nome_canal, category=categoria, overwrites=overwrites)

        embed = discord.Embed(
            title=f"🎫 Ticket: {self.values[0].capitalize()}",
            description=(
                f"Olá {interaction.user.mention},\n\n"
                "Sua solicitação foi aberta com sucesso! Nossa equipe foi acionada e responderá em breve.\n\n"
                "Descreva detalhadamente o seu problema ou dúvida para agilizar o atendimento."
            ),
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Noob Até Tentar • Sistema de Tickets")

        await canal_ticket.send(content=interaction.user.mention, embed=embed, view=BotaoFecharTicket())
        await interaction.response.send_message(f"✅ Seu ticket foi criado com sucesso em {canal_ticket.mention}!", ephemeral=True)


class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


class TicketsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logo_url = "https://i.imgur.com/xqojfhk.jpeg"
        self.banner_url = "https://i.imgur.com/YZP5zd1.png"

    @commands.command(name="painelticket", aliases=["ticket", "suporte"])
    @commands.has_permissions(administrator=True)
    async def painelticket(self, ctx):
        try:
            await ctx.message.delete()
        except Exception:
            pass

        embed = discord.Embed(
            title="🎟️ Central de Atendimento - Noob Até Tentar",
            description=(
                "Precisa de ajuda, quer relatar um problema ou propor uma parceria?\n\n"
                "👇 **Selecione a categoria desejada no menu abaixo para abrir um canal privado com a nossa equipe:**"
            ),
            color=discord.Color.green()
        )
        embed.set_author(name="Administrador", icon_url=self.logo_url)
        embed.set_thumbnail(url=self.logo_url)
        embed.set_image(url=self.banner_url)
        embed.set_footer(text="Noob Até Tentar", icon_url=self.logo_url)

        await ctx.send(embed=embed, view=DropdownView())


async def setup(bot):
    await bot.add_cog(TicketsCog(bot))