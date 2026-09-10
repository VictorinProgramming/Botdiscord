import discord
from discord.ext import commands

class BotoesCargos(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cliques_usuarios = {}

    async def gerenciar_cargo(self, interaction: discord.Interaction, role_id: int):
        role = interaction.guild.get_role(role_id)
        if not role:
            await interaction.response.send_message("❌ Cargo não encontrado no servidor. Fale com um Administrador.", ephemeral=True)
            return

        user_id = interaction.user.id

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            mensagem_resposta = f"🟥 O cargo {role.mention} foi removido de você!"
        else:
            await interaction.user.add_roles(role)
            mensagem_resposta = f"🟩 O cargo {role.mention} foi adicionado com sucesso!"

        self.cliques_usuarios[user_id] = self.cliques_usuarios.get(user_id, 0) + 1
        cliques_atuais = self.cliques_usuarios[user_id]

        if cliques_atuais >= 4:
            await interaction.response.send_message(f"{mensagem_resposta}\n✨ Você atingiu o limite de 4 escolhas!", ephemeral=True)
            try:
                await interaction.message.delete()
                self.cliques_usuarios.pop(user_id, None)
            except discord.HTTPException:
                pass
        else:
            restantes = 4 - cliques_atuais
            await interaction.response.send_message(f"{mensagem_resposta}\nVocê ainda pode selecionar mais {restantes} cargo(s).", ephemeral=True)

    @discord.ui.button(label="Programadores", style=discord.ButtonStyle.gray, emoji="👨🏽‍💻", custom_id="btn_programador")
    async def btn_programador(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.gerenciar_cargo(interaction, 1507964006701469749)

    @discord.ui.button(label="Gamers", style=discord.ButtonStyle.blurple, emoji="🎮", custom_id="btn_gamers")
    async def btn_gamers(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.gerenciar_cargo(interaction, 1507964007162712199)

    @discord.ui.button(label="Streamers", style=discord.ButtonStyle.green, emoji="📽️", custom_id="btn_streamers")
    async def btn_streamers(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.gerenciar_cargo(interaction, 1507964008089784420)

    @discord.ui.button(label="Influencers", style=discord.ButtonStyle.grey, emoji="🤳🏽", custom_id="btn_influencers")
    async def btn_influencers(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.gerenciar_cargo(interaction, 1507964008840429670)

    @discord.ui.button(label="Home Office", style=discord.ButtonStyle.blurple, emoji="💻", custom_id="btn_homeoffice")
    async def btn_homeoffice(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.gerenciar_cargo(interaction, 1507964010090201211)


class CargosCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logo_admin_url = "https://i.imgur.com/xqojfhk.jpeg"
        self.banner_url = "https://i.imgur.com/YZP5zd1.png"

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Disparado quando o membro aceita as regras/conclui a triagem do servidor"""
        if before.pending and not after.pending:
            ID_CANAL_BOAS_VINDAS = 1507955755125440665
            ID_CANAL_CARGOS = 1508800415649501275

            channel_boas_vindas = self.bot.get_channel(ID_CANAL_BOAS_VINDAS)
            channel_cargos = self.bot.get_channel(ID_CANAL_CARGOS)

            if channel_boas_vindas:
                embed_welcome = discord.Embed(
                    title="👑Seja Bem Vindo !!!👑",
                    description=(
                        "╔════════════════════════╗\n"
                        "     👋 Bem-vindo(a)\n"
                        "╚════════════════════════╝\n\n"
                        f"Olá {after.mention} 🚀\n\n"
                        "Agora você faz parte da nossa comunidade!\n\n"
                        "👨🏽‍💻 Programadores\n🎮 Gamers\n📽️ Streamers\n🤳🏽 Influencers\n💻 Home Office\n\n"
                        "━━━━━━━━━━━━━━━━━━\n\n"
                        "📜 Leia as regras\n🎨 Escolha seus cargos\n💬 Apresente-se no chat\n\n"
                        "━━━━━━━━━━━━━━━━━━\n\n"
                        "✨ Aproveite sua estadia!"
                    ),
                    color=discord.Color.green()
                )
                embed_welcome.set_author(name="Administrador", icon_url=self.logo_admin_url)
                embed_welcome.set_image(url=self.banner_url)
                embed_welcome.set_footer(text="Noob Até Tentar", icon_url=self.logo_admin_url)
                
                if after.avatar:
                    embed_welcome.set_thumbnail(url=after.avatar.url)
                else:
                    embed_welcome.set_thumbnail(url=self.logo_admin_url)

                await channel_boas_vindas.send(embed=embed_welcome, delete_after=900)

            if channel_cargos:
                embed_roles = discord.Embed(
                    title="👑Escolha seu Cargo !!!👑",
                    description=(
                        f"Olá {after.mention} 🚀\n\n"
                        "Agora você faz parte da nossa comunidade!\n\n"
                        "👨🏽‍💻 Programadores\n🎮 Gamers\n📽️ Streamers\n🤳🏽 Influencers\n💻 Home Office\n\n"
                        "━━━━━━━━━━━━━━━━━━\n\n"
                        "📜 Leia as regras\n🎨 Escolha seus cargos\n💬 Apresente-se no chat\n\n"
                        "━━━━━━━━━━━━━━━━━━\n\n"
                        "╔════════════════════════╗\n"
                        "     👋 Bem-vindo(a)\n"
                        "╚════════════════════════╝"
                    ),
                    color=discord.Color.green()
                )
                embed_roles.set_author(name="Administrador", icon_url=self.logo_admin_url)
                embed_roles.set_image(url=self.banner_url)
                embed_roles.set_footer(text="Noob Até Tentar", icon_url=self.logo_admin_url)
                
                if after.avatar:
                    embed_roles.set_thumbnail(url=after.avatar.url)
                else:
                    embed_roles.set_thumbnail(url=self.logo_admin_url)

                await channel_cargos.send(embed=embed_roles, view=BotoesCargos())

    @commands.command(name="addcargo")
    @commands.has_permissions(manage_roles=True)
    async def addcargo(self, ctx, user: discord.Member, cargo: discord.Role):
        try: await ctx.message.delete()
        except: pass

        if cargo in user.roles:
            await ctx.send(f"❌ O usuário {user.mention} já possui o cargo {cargo.mention}.", delete_after=10)
            return  

        # Proteção contra erros de hierarquia (403 Forbidden)
        try:
            await user.add_roles(cargo)
        except discord.Forbidden:
            return await ctx.send(
                f"❌ Erro de Permissão: O cargo {cargo.mention} está acima do cargo do Bot na hierarquia! "
                f"Mova o cargo do Bot para o topo nas configurações do servidor.", 
                delete_after=20
            )

        embed = discord.Embed(
            title="O cargo foi adicionado com Sucesso✅ !", 
            description=f"Adicionando o cargo {cargo.mention} ao usuário {user.mention}...\n\nAgora pode Aproveitar os benefícios do cargo", 
            color=discord.Color.green()
        )
        embed.set_author(name="Administrador", icon_url=self.logo_admin_url)
        embed.set_image(url=self.banner_url)
        embed.set_footer(text="Noob Até Tentar", icon_url=self.logo_admin_url)
        
        if user.avatar:
            embed.set_thumbnail(url=user.avatar.url)
        else:
            embed.set_thumbnail(url=self.logo_admin_url)

        await ctx.send(embed=embed, delete_after=15)

    @commands.command(name="remcargo")
    @commands.has_permissions(manage_roles=True)
    async def remcargo(self, ctx, user: discord.Member, cargo: discord.Role):
        try: await ctx.message.delete()
        except: pass

        if cargo not in user.roles:
            await ctx.send(f"❌ O usuário {user.mention} não possui o cargo {cargo.mention} para ser removido.", delete_after=10)
            return  

        # Proteção contra erros de hierarquia (403 Forbidden)
        try:
            await user.remove_roles(cargo)
        except discord.Forbidden:
            return await ctx.send(
                f"❌ Erro de Permissão: O cargo {cargo.mention} está acima do cargo do Bot na hierarquia! "
                f"Mova o cargo do Bot para o topo nas configurações do servidor.", 
                delete_after=20
            )
        
        embed = discord.Embed(
            title="O cargo foi removido com Sucesso✅ !", 
            description=f"Removendo o cargo {cargo.mention} do usuário {user.mention}...\n\nAgora não pode mais aproveitar os benefícios do cargo", 
            color=discord.Color.red()
        )
        embed.set_author(name="Administrador", icon_url=self.logo_admin_url)
        embed.set_image(url=self.banner_url)
        embed.set_footer(text="Noob Até Tentar", icon_url=self.logo_admin_url)
        
        if user.avatar:
            embed.set_thumbnail(url=user.avatar.url)
        else:
            embed.set_thumbnail(url=self.logo_admin_url)

        await ctx.send(embed=embed, delete_after=15)

async def setup(bot):
    await bot.add_cog(CargosCog(bot))