"""
Cog de Suggestions - Système de suggestions pour le serveur
"""

import discord
from discord import app_commands
from discord.ext import commands
import database
from config import Colors, Emojis
import logging
import aiosqlite
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "data" / "bot.db"

class Suggestions(commands.Cog):
    """Système de suggestions pour la communauté"""
    
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self._init_table())
    
    async def _init_table(self):
        """Initialise la table des suggestions"""
        await self.bot.wait_until_ready()
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    message_id INTEGER,
                    channel_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    reviewed_by INTEGER,
                    review_reason TEXT
                )
            """)
            await db.commit()
    
    @app_commands.command(name="suggest", description="Proposer une suggestion")
    @app_commands.describe(suggestion="Votre suggestion")
    async def suggest(self, interaction: discord.Interaction, suggestion: str):
        """Créer une nouvelle suggestion"""
        if len(suggestion) < 10:
            return await interaction.response.send_message(
                f"{Emojis.ERROR} La suggestion doit faire au moins 10 caractères.",
                ephemeral=True
            )
        
        if len(suggestion) > 1000:
            return await interaction.response.send_message(
                f"{Emojis.ERROR} La suggestion ne peut pas dépasser 1000 caractères.",
                ephemeral=True
            )
        
        try:
            # Créer l'embed de suggestion
            embed = discord.Embed(
                title="💡 Nouvelle Suggestion",
                description=suggestion,
                color=Colors.INFO
            )
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url
            )
            embed.set_footer(text=f"ID: {interaction.user.id}")
            embed.timestamp = discord.utils.utcnow()
            
            # Poster dans le canal actuel
            msg = await interaction.channel.send(embed=embed)
            
            # Ajouter les réactions
            await msg.add_reaction("✅")  # Approve
            await msg.add_reaction("❌")  # Deny
            
            # Enregistrer dans la BD
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute(
                    "INSERT INTO suggestions (guild_id, user_id, content, message_id, channel_id) VALUES (?, ?, ?, ?, ?)",
                    (interaction.guild.id, interaction.user.id, suggestion, msg.id, interaction.channel.id)
                )
                await db.commit()
            
            await interaction.response.send_message(
                f"{Emojis.SUCCESS} Votre suggestion a été postée !",
                ephemeral=True
            )
            logger.info(f"{interaction.user} a créé une suggestion")
            
        except Exception as e:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Erreur: {str(e)}",
                ephemeral=True
            )
            logger.error(f"Erreur dans suggest: {e}")
    
    @app_commands.command(name="suggestions", description="Voir toutes les suggestions")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def suggestions_list(self, interaction: discord.Interaction):
        """Liste toutes les suggestions du serveur"""
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    "SELECT * FROM suggestions WHERE guild_id = ? ORDER BY created_at DESC LIMIT 10",
                    (interaction.guild.id,)
                ) as cursor:
                    suggestions = await cursor.fetchall()
            
            if not suggestions:
                return await interaction.response.send_message(
                    f"{Emojis.INFO} Aucune suggestion pour le moment.",
                    ephemeral=True
                )
            
            embed = discord.Embed(
                title="📋 Suggestions du Serveur",
                description=f"Dernières {len(suggestions)} suggestions",
                color=Colors.INFO
            )
            
            status_emojis = {
                'pending': '⏳',
                'approved': '✅',
                'denied': '❌'
            }
            
            for sugg in suggestions:
                status = status_emojis.get(sugg['status'], '❓')
                content = sugg['content'][:100] + ('...' if len(sugg['content']) > 100 else '')
                member = interaction.guild.get_member(sugg['user_id'])
                author = member.display_name if member else f"ID: {sugg['user_id']}"
                
                embed.add_field(
                    name=f"{status} #{sugg['id']} - {author}",
                    value=content,
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Erreur: {str(e)}",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Suggestions(bot))
