"""
Cog de Sécurité - Protection anti-raid et sécurité du serveur
"""

import discord
from discord import app_commands
from discord.ext import commands
import database
from config import Colors, Emojis
import logging
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

class Security(commands.Cog):
    """Fonctionnalités de sécurité et anti-raid"""
    
    def __init__(self, bot):
        self.bot = bot
        self.join_tracker = defaultdict(list)  # guild_id -> liste de timestamps
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Détecte les raids potentiels"""
        try:
            # Vérifier si l'anti-raid est activé
            config = await database.get_guild_config(member.guild.id)
            if not config or not config.get('antiraid_enabled'):
                return
            
            # Ajouter le join au tracker
            now = datetime.now()
            self.join_tracker[member.guild.id].append(now)
            
            # Nettoyer les anciens joins (> 10 secondes)
            cutoff = now - timedelta(seconds=10)
            self.join_tracker[member.guild.id] = [
                ts for ts in self.join_tracker[member.guild.id] 
                if ts > cutoff
            ]
            
            # Vérifier si raid détecté (5+ joins en 10 secondes)
            if len(self.join_tracker[member.guild.id]) >= 5:
                await self._handle_raid(member.guild)
                
        except Exception as e:
            logger.error(f"Erreur dans on_member_join: {e}")
    
    async def _handle_raid(self, guild: discord.Guild):
        """Gère un raid détecté"""
        try:
            # Lock le serveur (désactiver les invitations)
            # Note: On ne peut pas vraiment "lock" un serveur,
            # mais on peut désactiver toutes les invitations
            
            invites = await guild.invites()
            for invite in invites:
                try:
                    await invite.delete(reason="Protection anti-raid")
                except:
                    pass
            
            # Créer un embed de notification
            embed = discord.Embed(
                title="🚨 RAID DÉTECTÉ",
                description=f"**5+ membres** ont rejoint en moins de 10 secondes.\n\n"
                           f"**Actions prises:**\n"
                           f"✅ Toutes les invitations ont été supprimées\n"
                           f"⚠️ Utilisez `/unlock` pour réactiver les invitations",
                color=Colors.ERROR
            )
            embed.timestamp = datetime.now()
            
            # Envoyer au canal de logs
            await database.send_mod_log(self.bot, guild.id, embed)
            
            # Notifier le propriétaire
            try:
                owner = guild.owner
                if owner:
                    await owner.send(embed=embed)
            except:
                pass
            
            logger.warning(f"Raid détecté sur {guild.name}")
            
            # Réinitialiser le tracker
            self.join_tracker[guild.id].clear()
            
        except Exception as e:
            logger.error(f"Erreur lors de la gestion du raid: {e}")
    
    @app_commands.command(name="antiraid", description="Activer/désactiver la protection anti-raid")
    @app_commands.describe(enabled="True pour activer, False pour désactiver")
    @app_commands.checks.has_permissions(administrator=True)
    async def antiraid(self, interaction: discord.Interaction, enabled: bool):
        """Active ou désactive la protection anti-raid"""
        try:
            await database.update_guild_config(
                interaction.guild.id,
                antiraid_enabled=enabled
            )
            
            status = "activée" if enabled else "désactivée"
            embed = discord.Embed(
                title=f"{Emojis.SUCCESS} Protection Anti-Raid {status.capitalize()}",
                description=f"La protection anti-raid a été **{status}**.\n\n"
                           f"{'🛡️ Le bot surveillera les jointures suspectes.' if enabled else '⚠️ Le serveur est désormais vulnérable aux raids.'}",
                color=Colors.SUCCESS if enabled else Colors.WARNING
            )
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"{interaction.user} a {status} l'anti-raid")
            
        except Exception as e:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Erreur: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="unlock", description="Réactiver les invitations après un raid")
    @app_commands.checks.has_permissions(administrator=True)
    async def unlock(self, interaction: discord.Interaction):
        """Permet de créer de nouvelles invitations après un lock"""
        embed = discord.Embed(
            title=f"{Emojis.SUCCESS} Serveur Déverrouillé",
            description="Vous pouvez maintenant créer de nouvelles invitations.\n\n"
                       "**Conseil:** Surveillez les nouveaux membres pendant quelques minutes.",
            color=Colors.SUCCESS
        )
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"{interaction.user} a déverrouillé le serveur")

async def setup(bot):
    await bot.add_cog(Security(bot))
