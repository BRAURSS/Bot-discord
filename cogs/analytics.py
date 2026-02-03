"""
Cog d'Analytics - Statistiques et activité des utilisateurs
"""

import discord
from discord import app_commands
from discord.ext import commands
import database
from config import Colors, Emojis
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Analytics(commands.Cog):
    """Système d'analytics et de statistiques"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Track les messages pour les statistiques"""
        # Ne pas compter les messages du bot et en DM
        if message.author.bot or not message.guild:
            return
        
        try:
            # Incrémenter le compteur de messages
            await database.increment_message_count(message.guild.id, message.author.id)
        except Exception as e:
            logger.error(f"Erreur lors du tracking de message: {e}")
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Track l'activité vocale"""
        try:
            # Rejoindre un vocal
            if before.channel is None and after.channel is not None:
                await database.log_activity(member.guild.id, member.id, "VOICE_JOIN")
                await database.log_voice_join(member.guild.id, member.id)
            
            # Quitter un vocal
            elif before.channel is not None and after.channel is None:
                await database.log_activity(member.guild.id, member.id, "VOICE_LEAVE")
                await database.log_voice_leave(member.guild.id, member.id)
        except Exception as e:
            logger.error(f"Erreur lors du tracking vocal: {e}")
    
    @app_commands.command(name="stats", description="Voir les statistiques d'un membre")
    @app_commands.describe(member="Le membre (optionnel, vous par défaut)")
    async def stats(self, interaction: discord.Interaction, member: discord.Member = None):
        """Affiche les statistiques d'un membre"""
        target = member or interaction.user
        
        try:
            # Récupérer les stats de base
            stats = await database.get_user_stats(interaction.guild.id, target.id)
            
            # Récupérer les stats de messages par période
            msg_24h = await database.get_message_count_period(interaction.guild.id, target.id, 24)
            msg_7d = await database.get_message_count_period(interaction.guild.id, target.id, 168)
            
            # Récupérer les stats vocales
            voice_total = await database.get_voice_time(interaction.guild.id, target.id, None)
            voice_24h = await database.get_voice_time(interaction.guild.id, target.id, 24)
            voice_7d = await database.get_voice_time(interaction.guild.id, target.id, 168)
            
            # Récupérer les rangs
            msg_rank, msg_total = await database.get_user_message_rank_7d(interaction.guild.id, target.id)
            voice_rank, voice_total = await database.get_user_voice_rank_7d(interaction.guild.id, target.id)
            
            # Vérifier s'il y a des données à afficher
            total_messages = stats['message_count'] if stats else 0
            has_data = total_messages > 0 or voice_total > 0
            
            if not has_data:
                return await interaction.response.send_message(
                    f"{Emojis.INFO} Aucune statistique disponible pour {target.mention}.",
                    ephemeral=True
                )
            
            # Créer l'embed
            embed = discord.Embed(
                title=f"📊 Statistiques de {target.display_name}",
                color=Colors.INFO
            )
            embed.set_thumbnail(url=target.display_avatar.url)
            
            # Fonction helper pour formater le temps
            def format_time(seconds):
                if seconds == 0:
                    return "0min"
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                if hours > 0:
                    return f"{hours}h {minutes}min"
                return f"{minutes}min"
            
            # Messages
            msg_value = f"**Total:** {total_messages:,} messages\n"
            msg_value += f"**24h:** {msg_24h:,} messages\n"
            msg_value += f"**7j:** {msg_7d:,} messages"
            if msg_total > 0:
                msg_value += f"\n**Rang (7j):** #{msg_rank}/{msg_total}"
            
            embed.add_field(
                name="💬 Messages",
                value=msg_value,
                inline=True
            )
            
            # Temps Vocal
            voice_value = f"**Total:** {format_time(voice_total)}\n"
            voice_value += f"**24h:** {format_time(voice_24h)}\n"
            voice_value += f"**7j:** {format_time(voice_7d)}"
            if voice_total > 0:
                voice_value += f"\n**Rang (7j):** #{voice_rank}/{voice_total}"
            
            embed.add_field(
                name="🎤 Temps Vocal",
                value=voice_value,
                inline=True
            )
            
            # Dernière activité
            if stats and stats['last_message_at']:
                last_msg = datetime.fromisoformat(stats['last_message_at'])
                time_ago = datetime.now() - last_msg
                
                if time_ago.days > 0:
                    ago_str = f"il y a {time_ago.days} jour(s)"
                elif time_ago.seconds > 3600:
                    ago_str = f"il y a {time_ago.seconds // 3600} heure(s)"
                else:
                    ago_str = f"il y a {time_ago.seconds // 60} minute(s)"
                
                embed.add_field(
                    name="⏰ Dernière activité",
                    value=ago_str,
                    inline=False
                )
            
            # Informations additionnelles
            embed.add_field(
                name="📅 Membre depuis",
                value=f"<t:{int(target.joined_at.timestamp())}:R>",
                inline=False
            )
            
            embed.set_footer(text=f"ID: {target.id}")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Erreur: {str(e)}",
                ephemeral=True
            )
            logger.error(f"Erreur dans stats: {e}")
    
    @app_commands.command(name="activityboard", description="Classement d'activité du serveur")
    @app_commands.describe(limit="Nombre de résultats (max 25)")
    async def activityboard(self, interaction: discord.Interaction, limit: int = 10):
        """Affiche le classement d'activité par messages"""
        try:
            # Limiter entre 5 et 25
            limit = max(5, min(limit, 25))
            
            # Classement des messages
            stats = await database.get_activity_leaderboard(interaction.guild.id, limit=limit)
            
            if not stats:
                return await interaction.response.send_message(
                    f"{Emojis.INFO} Aucune statistique disponible.",
                    ephemeral=True
                )
            
            embed = discord.Embed(
                title="🏆 Classement d'Activité - Messages",
                description=f"Top {len(stats)} des membres les plus actifs",
                color=Colors.SUCCESS
            )
            
            medals = ["🥇", "🥈", "🥉"]
            
            for idx, stat in enumerate(stats, 1):
                member = interaction.guild.get_member(stat['user_id'])
                if not member:
                    continue
                
                medal = medals[idx-1] if idx <= 3 else f"`#{idx}`"
                
                embed.add_field(
                    name=f"{medal} {member.display_name}",
                    value=f"💬 **{stat['message_count']:,}** messages",
                    inline=False
                )
            
            embed.set_footer(text=f"Serveur: {interaction.guild.name}")
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Erreur: {str(e)}",
                ephemeral=True
            )
            logger.error(f"Erreur dans activityboard: {e}")

async def setup(bot):
    await bot.add_cog(Analytics(bot))
