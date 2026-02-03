"""
Bot Discord Polyvalent
Modération • Auto-Modération • Utilitaires • Leveling • Tickets • Setup
"""

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
from pathlib import Path
import database
from config import Colors, Emojis

# ===== CONFIGURATION DU LOGGING =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ===== CHARGEMENT DES VARIABLES D'ENVIRONNEMENT =====
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("❌ Token Discord manquant dans le fichier .env")

# ===== CONFIGURATION DU BOT =====
intents = discord.Intents.default()
intents.message_content = True  # Nécessaire pour auto-mod et leveling
intents.members = True          # Nécessaire pour les infos membres
intents.messages = True         # Nécessaire pour l'auto-mod

class DiscordBot(commands.Bot):
    """Classe principale du bot"""
    
    def __init__(self):
        super().__init__(
            command_prefix="!",  # Prefix pour les commandes classiques (optionnel)
            intents=intents,
            help_command=None  # Désactiver l'aide par défaut
        )
    
    async def setup_hook(self):
        """Appelé lors de l'initialisation"""
        # Initialiser la base de données
        await database.init_db()
        logger.info("✅ Base de données initialisée")
        
        # Charger tous les cogs
        cogs_dir = Path(__file__).parent / "cogs"
        
        if not cogs_dir.exists():
            logger.error("❌ Dossier 'cogs' introuvable")
            return
        
        for file in cogs_dir.glob("*.py"):
            if file.name.startswith("_"):
                continue
            
            try:
                cog_name = f"cogs.{file.stem}"
                await self.load_extension(cog_name)
                logger.info(f"✅ Cog chargé: {file.stem}")
            except Exception as e:
                logger.error(f"❌ Erreur lors du chargement de {file.stem}: {e}")
        
        # Synchroniser les commandes slash
        try:
            synced = await self.tree.sync()
            logger.info(f"✅ {len(synced)} commandes slash synchronisées")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la synchronisation des commandes: {e}")
    
    async def on_ready(self):
        """Appelé quand le bot est prêt"""
        logger.info("=" * 50)
        logger.info(f"🤖 Bot connecté en tant que {self.user}")
        logger.info(f"📊 ID: {self.user.id}")
        logger.info(f"🌐 Serveurs: {len(self.guilds)}")
        logger.info(f"👥 Utilisateurs: {sum(g.member_count for g in self.guilds)}")
        logger.info("=" * 50)
        
        # Définir le statut
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="votre serveur | /help"
            ),
            status=discord.Status.online
        )
    
    async def on_guild_join(self, guild: discord.Guild):
        """Appelé quand le bot rejoint un serveur"""
        logger.info(f"➕ Bot ajouté au serveur: {guild.name} (ID: {guild.id})")
        
        # Créer la config du serveur
        await database.get_guild_config(guild.id)
    
    async def on_guild_remove(self, guild: discord.Guild):
        """Appelé quand le bot quitte un serveur"""
        logger.info(f"➖ Bot retiré du serveur: {guild.name} (ID: {guild.id})")
    
    async def on_command_error(self, ctx, error):
        """Gestion des erreurs des commandes classiques"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignorer les commandes inexistantes
        
        logger.error(f"Erreur de commande: {error}")

# ===== GESTION D'ERREURS GLOBALE DES SLASH COMMANDS =====
async def on_app_command_error(interaction: discord.Interaction, error):
    """Gestion globale des erreurs des commandes slash"""
    
    if isinstance(error, discord.app_commands.MissingPermissions):
        embed = discord.Embed(
            title=f"{Emojis.ERROR} Permission manquante",
            description="Vous n'avez pas la permission d'utiliser cette commande.",
            color=Colors.ERROR
        )
        
    elif isinstance(error, discord.app_commands.BotMissingPermissions):
        embed = discord.Embed(
            title=f"{Emojis.ERROR} Permission manquante (Bot)",
            description="Je n'ai pas les permissions nécessaires pour effectuer cette action.",
            color=Colors.ERROR
        )
        
    elif isinstance(error, discord.app_commands.CommandOnCooldown):
        embed = discord.Embed(
            title=f"{Emojis.LOADING} Cooldown",
            description=f"Cette commande est en cooldown. Réessayez dans {error.retry_after:.1f}s",
            color=Colors.WARNING
        )
        
    else:
        embed = discord.Embed(
            title=f"{Emojis.ERROR} Erreur",
            description=f"Une erreur s'est produite:\n```{str(error)}```",
            color=Colors.ERROR
        )
        logger.error(f"Erreur de commande slash: {error}", exc_info=error)
    
    # Envoyer le message d'erreur
    try:
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
    except:
        pass

# ===== COMMANDE D'AIDE CUSTOM =====
@commands.hybrid_command(name="help", description="Afficher l'aide du bot")
async def help_command(ctx):
    """Affiche l'aide du bot"""
    embed = discord.Embed(
        title="📚 Aide du Bot",
        description="Voici toutes les catégories de commandes disponibles:",
        color=Colors.INFO
    )
    
    embed.add_field(
        name="🔨 Modération",
        value="`/ban` `/kick` `/mute` `/unmute` `/warn` `/warnings` `/clear`",
        inline=False
    )
    
    embed.add_field(
        name="🤖 Auto-Modération",
        value="`/automod` `/antilink`",
        inline=False
    )
    
    embed.add_field(
        name="🛠️ Utilitaires",
        value="`/ping` `/serverinfo` `/userinfo` `/avatar` `/poll` `/embed`",
        inline=False
    )
    
    embed.add_field(
        name="📊 Leveling",
        value="`/rank` `/leaderboard` `/setlevel` `/leveling`",
        inline=False
    )
    
    embed.add_field(
        name="🎫 Tickets",
        value="`/ticketsetup` `/close` `/add` `/remove`",
        inline=False
    )
    
    embed.add_field(
        name="⚙️ Setup",
        value="`/createrole` `/createchannel` `/pack` `/deletechannel` `/deleterole`",
        inline=False
    )
    
    embed.set_footer(text="Utilisez /help <commande> pour plus d'informations")
    
    await ctx.send(embed=embed)

# ===== LANCEMENT DU BOT =====
def main():
    """Fonction principale"""
    bot = DiscordBot()
    
    # Enregistrer le gestionnaire d'erreurs global
    bot.tree.on_error = on_app_command_error
    
    # Ajouter la commande d'aide
    bot.add_command(help_command)
    
    try:
        logger.info("🚀 Démarrage du bot...")
        bot.run(TOKEN)
    except KeyboardInterrupt:
        logger.info("⏹️ Arrêt du bot par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur critique: {e}")

if __name__ == "__main__":
    main()
