"""
Cog de Configuration - Commandes de configuration du serveur
"""

import discord
from discord import app_commands
from discord.ext import commands
import database
from config import Colors, Emojis
import logging

logger = logging.getLogger(__name__)

class Configuration(commands.Cog):
    """Commandes de configuration du bot"""
    
    def __init__(self, bot):
        self.bot = bot
    
    # ===== SETLOGCHANNEL =====
    @app_commands.command(name="setlogchannel", description="Définir le canal des logs de modération")
    @app_commands.describe(channel="Le canal pour les logs de modération")
    @app_commands.checks.has_permissions(administrator=True)
    async def setlogchannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Configure le canal des logs de modération"""
        try:
            await database.update_guild_config(
                interaction.guild.id,
                log_channel_id=channel.id
            )
            
            embed = discord.Embed(
                title=f"{Emojis.SUCCESS} Canal de logs configuré",
                description=f"Les logs de modération seront envoyés dans {channel.mention}",
                color=Colors.SUCCESS
            )
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"{interaction.user} a configuré le canal de logs: {channel.name}")
            
            # Envoyer un message de test
            test_embed = discord.Embed(
                title="📋 Logs de Modération Activés",
                description="Ce canal recevra désormais tous les logs de modération.",
                color=Colors.INFO
            )
            test_embed.set_footer(text=f"Configuré par {interaction.user}")
            await channel.send(embed=test_embed)
            
        except Exception as e:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Erreur lors de la configuration: {str(e)}",
                ephemeral=True
            )
            logger.error(f"Erreur setlogchannel: {e}")

async def setup(bot):
    await bot.add_cog(Configuration(bot))
