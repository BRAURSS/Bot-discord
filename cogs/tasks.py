"""
Cog de Tâches en Arrière-Plan
Gère les actions automatiques : unban temporaire, backup, etc.
"""

import discord
from discord.ext import commands, tasks
import database
import logging
from datetime import datetime
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)

class Tasks(commands.Cog):
    """Tâches automatisées en arrière-plan"""
    
    def __init__(self, bot):
        self.bot = bot
        self.check_temp_actions.start()
        self.backup_database.start()
    
    def cog_unload(self):
        """Arrête les tâches lors du déchargement"""
        self.check_temp_actions.cancel()
        self.backup_database.cancel()
    
    @tasks.loop(minutes=1)
    async def check_temp_actions(self):
        """Vérifie et exécute les actions temporaires expirées"""
        try:
            expired_actions = await database.get_expired_actions()
            
            for action in expired_actions:
                guild = self.bot.get_guild(action['guild_id'])
                if not guild:
                    await database.remove_temp_action(action['id'])
                    continue
                
                if action['action_type'] == 'TEMPBAN':
                    try:
                        # Débannir l'utilisateur
                        user = await self.bot.fetch_user(action['user_id'])
                        await guild.unban(user, reason="Tempban expiré")
                        
                        # Log
                        await database.add_mod_log(
                            guild.id,
                            "AUTO_UNBAN",
                            self.bot.user.id,
                            user.id,
                            "Tempban expiré"
                        )
                        
                        logger.info(f"Auto-unban: {user} dans {guild.name}")
                        
                    except discord.NotFound:
                        logger.warning(f"Utilisateur {action['user_id']} non trouvé pour unban")
                    except discord.Forbidden:
                        logger.error(f"Pas la permission de unban dans {guild.name}")
                    except Exception as e:
                        logger.error(f"Erreur lors du auto-unban: {e}")
                
                # Supprimer l'action de la base de données
                await database.remove_temp_action(action['id'])
                
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des actions temporaires: {e}")
    
    @check_temp_actions.before_loop
    async def before_check_temp_actions(self):
        """Attend que le bot soit prêt avant de démarrer"""
        await self.bot.wait_until_ready()
        logger.info("✅ Tâche check_temp_actions démarrée")
    
    @tasks.loop(hours=24)
    async def backup_database(self):
        """Crée une sauvegarde quotidienne de la base de données"""
        try:
            db_path = Path(__file__).parent.parent / "data" / "bot.db"
            backup_dir = Path(__file__).parent.parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            # Nom du fichier de backup avec date
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"bot_backup_{timestamp}.db"
            
            # Copier la base de données
            shutil.copy2(db_path, backup_path)
            
            # Garder seulement les 7 derniers backups
            backups = sorted(backup_dir.glob("bot_backup_*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
            for old_backup in backups[7:]:
                old_backup.unlink()
                logger.info(f"Ancien backup supprimé: {old_backup.name}")
            
            logger.info(f"✅ Backup créé: {backup_path.name}")
            
        except Exception as e:
            logger.error(f"Erreur lors du backup de la base de données: {e}")
    
    @backup_database.before_loop
    async def before_backup_database(self):
        """Attend que le bot soit prêt avant de démarrer"""
        await self.bot.wait_until_ready()
        logger.info("✅ Tâche backup_database démarrée")

async def setup(bot):
    await bot.add_cog(Tasks(bot))
