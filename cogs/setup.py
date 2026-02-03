"""
Cog de Setup - Commandes de configuration et création de salons/rôles
"""

import discord
from discord import app_commands
from discord.ext import commands
from config import Colors, Emojis
import logging

logger = logging.getLogger(__name__)

class Setup(commands.Cog):
    """Commandes de création et configuration du serveur"""
    
    def __init__(self, bot):
        self.bot = bot
    
    # ===== CREATEROLE =====
    @app_commands.command(name="createrole", description="Créer un rôle personnalisé")
    @app_commands.describe(
        name="Nom du rôle",
        color="Couleur en hexadécimal (ex: FF0000 pour rouge)",
        hoist="Afficher séparément dans la liste (True/False)",
        mentionable="Peut être mentionné (True/False)"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def create_role(
        self,
        interaction: discord.Interaction,
        name: str,
        color: str = None,
        hoist: bool = False,
        mentionable: bool = False
    ):
        """Crée un rôle avec des options personnalisées"""
        # Vérifier si le rôle existe déjà
        existing_role = discord.utils.get(interaction.guild.roles, name=name)
        if existing_role:
            return await interaction.response.send_message(
                f"{Emojis.ERROR} Un rôle nommé **{name}** existe déjà.",
                ephemeral=True
            )
        
        # Parser la couleur
        role_color = discord.Color.default()
        if color:
            try:
                color_value = int(color, 16)
                role_color = discord.Color(color_value)
            except ValueError:
                return await interaction.response.send_message(
                    f"{Emojis.ERROR} Couleur invalide. Utilisez le format hexadécimal (ex: FF0000).",
                    ephemeral=True
                )
        
        # Créer le rôle
        try:
            role = await interaction.guild.create_role(
                name=name,
                color=role_color,
                hoist=hoist,
                mentionable=mentionable,
                reason=f"Créé par {interaction.user}"
            )
            
            embed = discord.Embed(
                title=f"{Emojis.SUCCESS} Rôle créé",
                description=f"Le rôle {role.mention} a été créé avec succès !",
                color=role_color
            )
            
            embed.add_field(name="Nom", value=name, inline=True)
            embed.add_field(name="Couleur", value=f"#{color}" if color else "Par défaut", inline=True)
            embed.add_field(name="Affiché séparément", value="Oui" if hoist else "Non", inline=True)
            embed.add_field(name="Mentionnable", value="Oui" if mentionable else "Non", inline=True)
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"{interaction.user} a créé le rôle {name}")
            
        except discord.Forbidden:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Je n'ai pas la permission de créer des rôles.",
                ephemeral=True
            )
    
    # ===== CREATECHANNEL =====
    @app_commands.command(name="createchannel", description="Créer un salon texte ou vocal")
    @app_commands.describe(
        name="Nom du salon",
        channel_type="Type de salon",
        category="Catégorie (optionnel)"
    )
    @app_commands.choices(channel_type=[
        app_commands.Choice(name="Texte", value="text"),
        app_commands.Choice(name="Vocal", value="voice")
    ])
    @app_commands.checks.has_permissions(manage_channels=True)
    async def create_channel(
        self,
        interaction: discord.Interaction,
        name: str,
        channel_type: str,
        category: discord.CategoryChannel = None
    ):
        """Crée un salon texte ou vocal"""
        # Nettoyer le nom (minuscules, tirets)
        clean_name = name.lower().replace(" ", "-")
        
        # Vérifier si le salon existe déjà
        if channel_type == "text":
            existing = discord.utils.get(interaction.guild.text_channels, name=clean_name)
        else:
            existing = discord.utils.get(interaction.guild.voice_channels, name=name)
        
        if existing:
            return await interaction.response.send_message(
                f"{Emojis.ERROR} Un salon nommé **{name}** existe déjà.",
                ephemeral=True
            )
        
        try:
            # Créer le salon
            if channel_type == "text":
                channel = await interaction.guild.create_text_channel(
                    name=clean_name,
                    category=category,
                    reason=f"Créé par {interaction.user}"
                )
                emoji = "📝"
            else:
                channel = await interaction.guild.create_voice_channel(
                    name=name,
                    category=category,
                    reason=f"Créé par {interaction.user}"
                )
                emoji = "🔊"
            
            embed = discord.Embed(
                title=f"{Emojis.SUCCESS} Salon créé",
                description=f"{emoji} {channel.mention if channel_type == 'text' else f'**{channel.name}**'} a été créé !",
                color=Colors.SUCCESS
            )
            
            if category:
                embed.add_field(name="Catégorie", value=category.name, inline=True)
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"{interaction.user} a créé le salon {channel_type} {name}")
            
        except discord.Forbidden:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Je n'ai pas la permission de créer des salons.",
                ephemeral=True
            )
    
    # ===== PACK =====
    @app_commands.command(name="pack", description="Créer plusieurs salons en une fois")
    @app_commands.describe(
        channels="Liste de salons séparés par | (ex: 📌・règlement | 💬・chat | 🎮・gaming)",
        category_name="Nom de la catégorie à créer"
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    async def pack(
        self,
        interaction: discord.Interaction,
        channels: str,
        category_name: str = "Nouveaux Salons"
    ):
        """Crée plusieurs salons à la fois dans une nouvelle catégorie"""
        await interaction.response.defer()
        
        # Découper la chaîne
        channel_names = [name.strip() for name in channels.split("|")]
        
        if len(channel_names) < 1:
            return await interaction.followup.send(
                f"{Emojis.ERROR} Veuillez spécifier au moins un salon.",
                ephemeral=True
            )
        
        if len(channel_names) > 15:
            return await interaction.followup.send(
                f"{Emojis.ERROR} Vous ne pouvez pas créer plus de 15 salons à la fois.",
                ephemeral=True
            )
        
        try:
            # Créer la catégorie
            category = await interaction.guild.create_category(
                name=category_name,
                reason=f"Pack créé par {interaction.user}"
            )
            
            created_channels = []
            
            # Créer chaque salon
            for channel_name in channel_names:
                # Nettoyer le nom
                clean_name = channel_name.lower().replace(" ", "-")
                
                channel = await interaction.guild.create_text_channel(
                    name=clean_name,
                    category=category,
                    reason=f"Pack créé par {interaction.user}"
                )
                created_channels.append(channel)
            
            embed = discord.Embed(
                title=f"{Emojis.SUCCESS} Pack créé",
                description=f"**{len(created_channels)}** salons ont été créés dans la catégorie **{category_name}** !",
                color=Colors.SUCCESS
            )
            
            channels_list = "\n".join([f"• {ch.mention}" for ch in created_channels])
            embed.add_field(name="Salons créés", value=channels_list, inline=False)
            
            await interaction.followup.send(embed=embed)
            logger.info(f"{interaction.user} a créé un pack de {len(created_channels)} salons")
            
        except discord.Forbidden:
            await interaction.followup.send(
                f"{Emojis.ERROR} Je n'ai pas la permission de créer des salons ou des catégories.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f"{Emojis.ERROR} Une erreur s'est produite : {str(e)}",
                ephemeral=True
            )
    
    # ===== DELETECHANNEL =====
    @app_commands.command(name="deletechannel", description="Supprimer un salon")
    @app_commands.describe(channel="Le salon à supprimer")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def delete_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Supprime un salon"""
        channel_name = channel.name
        
        try:
            await channel.delete(reason=f"Supprimé par {interaction.user}")
            
            embed = discord.Embed(
                title=f"{Emojis.TRASH} Salon supprimé",
                description=f"Le salon **#{channel_name}** a été supprimé.",
                color=Colors.WARNING
            )
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"{interaction.user} a supprimé le salon {channel_name}")
            
        except discord.Forbidden:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Je n'ai pas la permission de supprimer ce salon.",
                ephemeral=True
            )
    
    # ===== DELETEROLE =====
    @app_commands.command(name="deleterole", description="Supprimer un rôle")
    @app_commands.describe(role="Le rôle à supprimer")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def delete_role(self, interaction: discord.Interaction, role: discord.Role):
        """Supprime un rôle"""
        # Vérifier que le rôle n'est pas au-dessus du rôle du bot
        if role >= interaction.guild.me.top_role:
            return await interaction.response.send_message(
                f"{Emojis.ERROR} Je ne peux pas supprimer ce rôle (il est supérieur ou égal à mon rôle).",
                ephemeral=True
            )
        
        role_name = role.name
        
        try:
            await role.delete(reason=f"Supprimé par {interaction.user}")
            
            embed = discord.Embed(
                title=f"{Emojis.TRASH} Rôle supprimé",
                description=f"Le rôle **{role_name}** a été supprimé.",
                color=Colors.WARNING
            )
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"{interaction.user} a supprimé le rôle {role_name}")
            
        except discord.Forbidden:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Je n'ai pas la permission de supprimer ce rôle.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Setup(bot))
