"""
Cog d'Auto-Modération - Détection automatique de spam et contenus indésirables
"""

import discord
from discord.ext import commands
from discord import app_commands
from collections import defaultdict, deque
from datetime import datetime, timedelta
from config import Config, Colors, Emojis
import database
import logging

logger = logging.getLogger(__name__)

class AutoMod(commands.Cog):
    """Auto-modération pour détecter et punir automatiquement"""
    
    def __init__(self, bot):
        self.bot = bot
        # Tracking des messages pour détection de spam
        self.message_history = defaultdict(lambda: deque(maxlen=Config.SPAM_THRESHOLD))
        # Tracking des violations
        self.violations = defaultdict(int)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Écoute tous les messages pour auto-modération"""
        # Ignorer les bots et les DMs
        if message.author.bot or not message.guild:
            return
        
        # Ignorer les admins/modos
        if message.author.guild_permissions.administrator or message.author.guild_permissions.manage_messages:
            return
        
        # Vérifier si l'auto-mod est activée
        config = await database.get_guild_config(message.guild.id)
        if not config['automod_enabled']:
            return
        
        # === DÉTECTION DE SPAM ===
        if await self._check_spam(message):
            await self._handle_spam(message)
            return
        
        # === DÉTECTION DE LIENS ===
        if config['antilink_enabled'] and await self._check_links(message):
            await self._handle_links(message)
            return
        
        # === DÉTECTION DE MENTIONS MASSIVES ===
        if await self._check_mass_mentions(message):
            await self._handle_mass_mentions(message)
            return
    
    async def _check_spam(self, message: discord.Message) -> bool:
        """Détecte le spam (messages identiques répétés)"""
        user_messages = self.message_history[message.author.id]
        user_messages.append({
            'content': message.content.lower(),
            'timestamp': datetime.now()
        })
        
        # Vérifier si les X derniers messages sont identiques
        if len(user_messages) >= Config.SPAM_THRESHOLD:
            recent = [msg for msg in user_messages 
                     if (datetime.now() - msg['timestamp']).seconds < Config.SPAM_TIME_WINDOW]
            
            if len(recent) >= Config.SPAM_THRESHOLD:
                contents = [msg['content'] for msg in recent]
                if len(set(contents)) == 1:  # Tous identiques
                    return True
        
        return False
    
    async def _check_links(self, message: discord.Message) -> bool:
        """Détecte les liens dans les messages"""
        link_patterns = ['http://', 'https://', 'www.', '.com', '.net', '.org', '.gg']
        return any(pattern in message.content.lower() for pattern in link_patterns)
    
    async def _check_mass_mentions(self, message: discord.Message) -> bool:
        """Détecte les mentions massives"""
        total_mentions = len(message.mentions) + len(message.role_mentions)
        return total_mentions >= Config.MENTION_THRESHOLD
    
    async def _handle_spam(self, message: discord.Message):
        """Gère la détection de spam"""
        try:
            # Supprimer les messages récents de l'utilisateur
            def check(m):
                return (m.author == message.author and 
                       (datetime.now() - m.created_at).seconds < Config.SPAM_TIME_WINDOW)
            
            deleted = await message.channel.purge(limit=20, check=check)
            
            # Incrémenter les violations
            self.violations[message.author.id] += 1
            violations = self.violations[message.author.id]
            
            # Actions progressives
            if violations == 1:
                # Premier avertissement
                embed = discord.Embed(
                    title=f"{Emojis.WARNING} Anti-Spam",
                    description=f"{message.author.mention}, merci de ne pas spammer. ({len(deleted)} messages supprimés)",
                    color=Colors.WARNING
                )
                await message.channel.send(embed=embed, delete_after=10)
                
            elif violations == 2:
                # Mute 5 minutes
                await message.author.timeout(
                    timedelta(minutes=5),
                    reason="Auto-mod: Spam répété"
                )
                await message.channel.send(
                    f"{Emojis.MUTE} {message.author.mention} a été mute pour 5 minutes (spam répété).",
                    delete_after=10
                )
                await database.add_warn(message.guild.id, message.author.id, self.bot.user.id, "Auto-mod: Spam")
                
            elif violations >= 3:
                # Kick
                await message.author.kick(reason="Auto-mod: Spam excessif")
                await message.channel.send(
                    f"{Emojis.KICK} {message.author.mention} a été expulsé pour spam excessif."
                )
                await database.add_mod_log(
                    message.guild.id,
                    "KICK",
                    self.bot.user.id,
                    message.author.id,
                    "Auto-mod: Spam excessif"
                )
            
            logger.info(f"Auto-mod: Spam détecté de {message.author} ({violations} violations)")
            
        except discord.Forbidden:
            logger.warning(f"Auto-mod: Permissions insuffisantes pour modérer {message.author}")
    
    async def _handle_links(self, message: discord.Message):
        """Gère la détection de liens"""
        try:
            await message.delete()
            
            embed = discord.Embed(
                title=f"{Emojis.WARNING} Anti-Liens",
                description=f"{message.author.mention}, les liens ne sont pas autorisés dans ce serveur.",
                color=Colors.WARNING
            )
            await message.channel.send(embed=embed, delete_after=10)
            
            logger.info(f"Auto-mod: Lien supprimé de {message.author}")
            
        except discord.Forbidden:
            pass
    
    async def _handle_mass_mentions(self, message: discord.Message):
        """Gère les mentions massives"""
        try:
            await message.delete()
            
            # Mute immédiat 10 minutes
            await message.author.timeout(
                timedelta(minutes=10),
                reason="Auto-mod: Mentions massives"
            )
            
            embed = discord.Embed(
                title=f"{Emojis.MUTE} Mentions Massives",
                description=f"{message.author.mention} a été mute pour 10 minutes (mentions massives).",
                color=Colors.ERROR
            )
            await message.channel.send(embed=embed)
            
            await database.add_warn(
                message.guild.id,
                message.author.id,
                self.bot.user.id,
                "Auto-mod: Mentions massives"
            )
            
            logger.info(f"Auto-mod: Mentions massives de {message.author}")
            
        except discord.Forbidden:
            pass
    
    # ===== COMMANDES DE CONFIGURATION =====
    @app_commands.command(name="automod", description="Activer/désactiver l'auto-modération")
    @app_commands.describe(enabled="Activer (True) ou désactiver (False)")
    @app_commands.checks.has_permissions(administrator=True)
    async def automod_toggle(self, interaction: discord.Interaction, enabled: bool):
        """Active ou désactive l'auto-modération"""
        await database.update_guild_config(interaction.guild.id, automod_enabled=enabled)
        
        status = "activée" if enabled else "désactivée"
        emoji = Emojis.SUCCESS if enabled else Emojis.ERROR
        
        embed = discord.Embed(
            title=f"{emoji} Auto-Modération",
            description=f"L'auto-modération a été **{status}**.",
            color=Colors.SUCCESS if enabled else Colors.WARNING
        )
        
        if enabled:
            embed.add_field(
                name="Fonctionnalités",
                value="• Détection de spam\n• Protection mentions massives\n• Filtrage de liens (si activé)",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"{interaction.user} a {status} l'auto-modération")
    
    @app_commands.command(name="antilink", description="Activer/désactiver le filtre anti-liens")
    @app_commands.describe(enabled="Activer (True) ou désactiver (False)")
    @app_commands.checks.has_permissions(administrator=True)
    async def antilink_toggle(self, interaction: discord.Interaction, enabled: bool):
        """Active ou désactive le filtre anti-liens"""
        await database.update_guild_config(interaction.guild.id, antilink_enabled=enabled)
        
        status = "activé" if enabled else "désactivé"
        emoji = Emojis.SUCCESS if enabled else Emojis.ERROR
        
        embed = discord.Embed(
            title=f"{emoji} Anti-Liens",
            description=f"Le filtre anti-liens a été **{status}**.",
            color=Colors.SUCCESS if enabled else Colors.WARNING
        )
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"{interaction.user} a {status} l'anti-liens")

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
