"""
Cog de Leveling - Système de niveaux et XP
"""

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import database
from config import Config, Colors, Emojis
import random
import logging

logger = logging.getLogger(__name__)

class Leveling(commands.Cog):
    """Système de niveaux basé sur l'activité"""
    
    def __init__(self, bot):
        self.bot = bot
        # Cache pour le cooldown XP
        self.xp_cooldowns = {}
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Gagne de l'XP en envoyant des messages"""
        # Ignorer les bots et DMs
        if message.author.bot or not message.guild:
            return
        
        # Vérifier si le leveling est activé
        config = await database.get_guild_config(message.guild.id)
        if not config['leveling_enabled']:
            return
        
        # Vérifier le cooldown
        user_id = message.author.id
        now = datetime.now()
        
        if user_id in self.xp_cooldowns:
            last_xp = self.xp_cooldowns[user_id]
            if (now - last_xp).total_seconds() < Config.XP_COOLDOWN:
                return  # Encore en cooldown
        
        # Donner de l'XP
        xp_gain = random.randint(Config.XP_MIN, Config.XP_MAX)
        leveled_up, new_level = await database.add_xp(message.guild.id, message.author.id, xp_gain)
        
        # Mettre à jour le cooldown
        self.xp_cooldowns[user_id] = now
        
        # Si level up, envoyer un message
        if leveled_up:
            embed = discord.Embed(
                title=f"{Emojis.LEVEL_UP} LEVEL UP!",
                description=f"Bravo {message.author.mention} ! Tu es maintenant **niveau {new_level}** !",
                color=Colors.SUCCESS
            )
            
            await message.channel.send(embed=embed, delete_after=10)
            logger.info(f"{message.author} a atteint le niveau {new_level}")
    
    # ===== RANK =====
    @app_commands.command(name="rank", description="Voir votre niveau et XP")
    @app_commands.describe(member="Le membre à vérifier (vous par défaut)")
    async def rank(self, interaction: discord.Interaction, member: discord.Member = None):
        """Affiche le niveau et l'XP d'un utilisateur"""
        member = member or interaction.user
        
        data = await database.get_level_data(interaction.guild.id, member.id)
        
        if not data:
            return await interaction.response.send_message(
                f"{Emojis.INFO} **{member.display_name}** n'a pas encore gagné d'XP.",
                ephemeral=True
            )
        
        level = data['level']
        xp = data['xp']
        
        # Calculer l'XP nécessaire pour le prochain niveau
        current_level_xp = Config.XP_FORMULA(level)
        next_level_xp = Config.XP_FORMULA(level + 1)
        xp_for_next = next_level_xp - current_level_xp
        current_xp = xp - current_level_xp
        
        # Calculer le pourcentage
        progress_percent = int((current_xp / xp_for_next) * 100)
        
        # Barre de progression
        filled = "█" * (progress_percent // 10)
        empty = "░" * (10 - (progress_percent // 10))
        progress_bar = f"[{filled}{empty}] {progress_percent}%"
        
        embed = discord.Embed(
            title=f"📊 Niveau de {member.display_name}",
            color=member.color if member.color != discord.Color.default() else Colors.INFO
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.add_field(
            name="🎖️ Niveau",
            value=f"**{level}**",
            inline=True
        )
        
        embed.add_field(
            name="✨ XP Total",
            value=f"**{xp}**",
            inline=True
        )
        
        embed.add_field(
            name="📈 Progression",
            value=f"{current_xp}/{xp_for_next} XP\n{progress_bar}",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    # ===== LEADERBOARD =====
    @app_commands.command(name="leaderboard", description="Voir le classement du serveur")
    @app_commands.describe(limit="Nombre de personnes à afficher (max 20)")
    async def leaderboard(self, interaction: discord.Interaction, limit: int = 10):
        """Affiche le classement des membres les plus actifs"""
        if limit < 1 or limit > 20:
            return await interaction.response.send_message(
                f"{Emojis.ERROR} Veuillez spécifier un nombre entre 1 et 20.",
                ephemeral=True
            )
        
        data = await database.get_leaderboard(interaction.guild.id, limit)
        
        if not data:
            return await interaction.response.send_message(
                f"{Emojis.INFO} Aucune donnée de classement disponible.",
                ephemeral=True
            )
        
        embed = discord.Embed(
            title=f"🏆 Classement de {interaction.guild.name}",
            description=f"Top {len(data)} membres les plus actifs",
            color=Colors.INFO
        )
        
        medals = ["🥇", "🥈", "🥉"]
        
        for i, row in enumerate(data, 1):
            member = interaction.guild.get_member(row['user_id'])
            if not member:
                continue
            
            medal = medals[i-1] if i <= 3 else f"**#{i}**"
            
            embed.add_field(
                name=f"{medal} {member.display_name}",
                value=f"Niveau {row['level']} • {row['xp']} XP",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    # ===== SETLEVEL (ADMIN) =====
    @app_commands.command(name="setlevel", description="Définir le niveau d'un membre (admin)")
    @app_commands.describe(
        member="Le membre",
        level="Le nouveau niveau"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setlevel(self, interaction: discord.Interaction, member: discord.Member, level: int):
        """Définit manuellement le niveau d'un membre"""
        if level < 0:
            return await interaction.response.send_message(
                f"{Emojis.ERROR} Le niveau doit être positif.",
                ephemeral=True
            )
        
        await database.set_level(interaction.guild.id, member.id, level)
        
        embed = discord.Embed(
            title=f"{Emojis.SUCCESS} Niveau modifié",
            description=f"{member.mention} est maintenant **niveau {level}**.",
            color=Colors.SUCCESS
        )
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"{interaction.user} a défini le niveau de {member} à {level}")
    
    # ===== TOGGLE LEVELING =====
    @app_commands.command(name="leveling", description="Activer/désactiver le système de niveaux")
    @app_commands.describe(enabled="Activer (True) ou désactiver (False)")
    @app_commands.checks.has_permissions(administrator=True)
    async def leveling_toggle(self, interaction: discord.Interaction, enabled: bool):
        """Active ou désactive le système de niveaux"""
        await database.update_guild_config(interaction.guild.id, leveling_enabled=enabled)
        
        status = "activé" if enabled else "désactivé"
        emoji = Emojis.SUCCESS if enabled else Emojis.ERROR
        
        embed = discord.Embed(
            title=f"{emoji} Système de Niveaux",
            description=f"Le système de niveaux a été **{status}**.",
            color=Colors.SUCCESS if enabled else Colors.WARNING
        )
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"{interaction.user} a {status} le système de niveaux")

async def setup(bot):
    await bot.add_cog(Leveling(bot))
