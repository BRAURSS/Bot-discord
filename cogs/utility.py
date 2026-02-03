"""
Cog Utilitaires - Commandes d'information et outils pratiques
"""

import discord
from discord import app_commands
from discord.ext import commands
from config import Colors, Emojis
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Utility(commands.Cog):
    """Commandes utilitaires et d'information"""
    
    def __init__(self, bot):
        self.bot = bot
    
    # ===== PING =====
    @app_commands.command(name="ping", description="Vérifier la latence du bot")
    async def ping(self, interaction: discord.Interaction):
        """Affiche la latence du bot"""
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latence: **{latency}ms**",
            color=Colors.SUCCESS if latency < 200 else Colors.WARNING
        )
        
        await interaction.response.send_message(embed=embed)
    
    # ===== SERVERINFO =====
    @app_commands.command(name="serverinfo", description="Informations sur le serveur")
    async def serverinfo(self, interaction: discord.Interaction):
        """Affiche les informations du serveur"""
        guild = interaction.guild
        
        # Statistiques des membres
        total_members = guild.member_count
        humans = len([m for m in guild.members if not m.bot])
        bots = total_members - humans
        
        # Statistiques des salons
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        # Autres stats
        roles = len(guild.roles)
        emojis = len(guild.emojis)
        
        embed = discord.Embed(
            title=f"📊 Informations sur {guild.name}",
            color=Colors.INFO,
            timestamp=datetime.now()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Propriétaire
        embed.add_field(
            name="👑 Propriétaire",
            value=guild.owner.mention if guild.owner else "Inconnu",
            inline=True
        )
        
        # Date de création
        created_at = guild.created_at.strftime("%d/%m/%Y")
        embed.add_field(
            name="📅 Créé le",
            value=created_at,
            inline=True
        )
        
        # Membres
        embed.add_field(
            name=f"👥 Membres ({total_members})",
            value=f"👤 Humains: {humans}\n🤖 Bots: {bots}",
            inline=True
        )
        
        # Salons
        embed.add_field(
            name=f"💬 Salons ({text_channels + voice_channels})",
            value=f"📝 Texte: {text_channels}\n🔊 Vocal: {voice_channels}\n📁 Catégories: {categories}",
            inline=True
        )
        
        # Autres
        embed.add_field(
            name="🎭 Rôles",
            value=str(roles),
            inline=True
        )
        
        embed.add_field(
            name="😀 Emojis",
            value=str(emojis),
            inline=True
        )
        
        # Boost
        if guild.premium_subscription_count:
            embed.add_field(
                name=f"✨ Niveau de boost {guild.premium_tier}",
                value=f"{guild.premium_subscription_count} boost(s)",
                inline=True
            )
        
        embed.set_footer(text=f"ID: {guild.id}")
        
        await interaction.response.send_message(embed=embed)
    
    # ===== USERINFO =====
    @app_commands.command(name="userinfo", description="Informations sur un utilisateur")
    @app_commands.describe(member="Le membre à examiner (vous par défaut)")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        """Affiche les informations d'un utilisateur"""
        member = member or interaction.user
        
        embed = discord.Embed(
            title=f"👤 Informations sur {member.display_name}",
            color=member.color if member.color != discord.Color.default() else Colors.INFO,
            timestamp=datetime.now()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        
        # Nom et discriminateur
        embed.add_field(
            name="🏷️ Nom complet",
            value=str(member),
            inline=True
        )
        
        # Surnom
        if member.nick:
            embed.add_field(
                name="✏️ Surnom",
                value=member.nick,
                inline=True
            )
        
        # Création du compte
        created = member.created_at.strftime("%d/%m/%Y à %H:%M")
        embed.add_field(
            name="📅 Compte créé le",
            value=created,
            inline=False
        )
        
        # Arrivée sur le serveur
        joined = member.joined_at.strftime("%d/%m/%Y à %H:%M")
        embed.add_field(
            name="📆 A rejoint le",
            value=joined,
            inline=False
        )
        
        # Rôles (max 10)
        roles = [role.mention for role in member.roles[1:]][:10]  # Exclure @everyone
        if roles:
            embed.add_field(
                name=f"🎭 Rôles ({len(member.roles) - 1})",
                value=" ".join(roles) if roles else "Aucun",
                inline=False
            )
        
        # Badges
        badges = []
        if member.premium_since:
            badges.append("✨ Booster")
        if member.guild_permissions.administrator:
            badges.append("👑 Administrateur")
        if member.bot:
            badges.append("🤖 Bot")
        
        if badges:
            embed.add_field(
                name="🏅 Badges",
                value=" • ".join(badges),
                inline=False
            )
        
        embed.set_footer(text=f"ID: {member.id}")
        
        await interaction.response.send_message(embed=embed)
    
    # ===== AVATAR =====
    @app_commands.command(name="avatar", description="Afficher l'avatar d'un utilisateur")
    @app_commands.describe(member="Le membre (vous par défaut)")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        """Affiche l'avatar d'un utilisateur"""
        member = member or interaction.user
        
        embed = discord.Embed(
            title=f"Avatar de {member.display_name}",
            color=member.color if member.color != discord.Color.default() else Colors.INFO
        )
        
        embed.set_image(url=member.display_avatar.url)
        embed.add_field(
            name="🔗 Lien",
            value=f"[Cliquez ici]({member.display_avatar.url})",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    # ===== POLL =====
    @app_commands.command(name="poll", description="Créer un sondage")
    @app_commands.describe(
        question="La question du sondage",
        option1="Option 1",
        option2="Option 2",
        option3="Option 3 (optionnel)",
        option4="Option 4 (optionnel)",
        option5="Option 5 (optionnel)"
    )
    async def poll(
        self,
        interaction: discord.Interaction,
        question: str,
        option1: str,
        option2: str,
        option3: str = None,
        option4: str = None,
        option5: str = None
    ):
        """Crée un sondage avec réactions"""
        options = [option1, option2]
        if option3:
            options.append(option3)
        if option4:
            options.append(option4)
        if option5:
            options.append(option5)
        
        # Emojis de réaction
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        
        # Créer l'embed
        embed = discord.Embed(
            title=f"{Emojis.POLL} {question}",
            color=Colors.INFO,
            timestamp=datetime.now()
        )
        
        description = ""
        for i, option in enumerate(options):
            description += f"\n{emojis[i]} {option}"
        
        embed.description = description
        embed.set_footer(text=f"Sondage créé par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        
        # Ajouter les réactions
        for i in range(len(options)):
            await message.add_reaction(emojis[i])
        
        logger.info(f"{interaction.user} a créé un sondage: {question}")
    
    # ===== EMBED CREATOR =====
    @app_commands.command(name="embed", description="Créer un embed personnalisé")
    @app_commands.describe(
        title="Titre de l'embed",
        description="Description de l'embed",
        color="Couleur (hex sans #, ex: FF0000 pour rouge)"
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def create_embed(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        color: str = None
    ):
        """Crée un embed personnalisé"""
        try:
            # Parser la couleur
            if color:
                color_value = int(color, 16)
                embed_color = discord.Color(color_value)
            else:
                embed_color = Colors.DEFAULT
            
            embed = discord.Embed(
                title=title,
                description=description,
                color=embed_color,
                timestamp=datetime.now()
            )
            
            embed.set_footer(text=f"Créé par {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"{interaction.user} a créé un embed: {title}")
            
        except ValueError:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Couleur invalide. Utilisez le format hexadécimal (ex: FF0000).",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Utility(bot))
