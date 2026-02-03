"""
Gestion de la base de données SQLite pour le bot Discord
"""

import aiosqlite
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "data" / "bot.db"

# ===== INITIALISATION =====
async def init_db():
    """Initialise la base de données et crée les tables"""
    DB_PATH.parent.mkdir(exist_ok=True)
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Table des avertissements
        await db.execute("""
            CREATE TABLE IF NOT EXISTS warns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des logs de modération
        await db.execute("""
            CREATE TABLE IF NOT EXISTS mod_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                action_type TEXT NOT NULL,
                moderator_id INTEGER NOT NULL,
                target_id INTEGER NOT NULL,
                reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des niveaux/XP
        await db.execute("""
            CREATE TABLE IF NOT EXISTS levels (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 0,
                last_message DATETIME,
                PRIMARY KEY (guild_id, user_id)
            )
        """)
        
        # Table des tickets
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                ticket_number INTEGER,
                status TEXT DEFAULT 'open',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                closed_at DATETIME
            )
        """)
        
        # Table de configuration des serveurs
        await db.execute("""
            CREATE TABLE IF NOT EXISTS guild_config (
                guild_id INTEGER PRIMARY KEY,
                log_channel_id INTEGER,
                ticket_category_id INTEGER,
                automod_enabled BOOLEAN DEFAULT 0,
                antilink_enabled BOOLEAN DEFAULT 0,
                leveling_enabled BOOLEAN DEFAULT 1,
                antiraid_enabled BOOLEAN DEFAULT 0
            )
        """)
        
        # Table des actions temporaires (tempban, tempmute)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS temporary_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                action_type TEXT NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT,
                expires_at DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des statistiques de messages
        await db.execute("""
            CREATE TABLE IF NOT EXISTS message_stats (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                message_count INTEGER DEFAULT 0,
                last_message_at DATETIME,
                PRIMARY KEY (guild_id, user_id)
            )
        """)
        
        # Table des logs d'activité
        await db.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                activity_type TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des sessions vocales
        await db.execute("""
            CREATE TABLE IF NOT EXISTS voice_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                join_time DATETIME NOT NULL,
                leave_time DATETIME,
                duration_seconds INTEGER
            )
        """)
        
        # Table de l'historique des messages avec timestamps
        await db.execute("""
            CREATE TABLE IF NOT EXISTS message_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Créer des index pour optimiser les requêtes par période
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_voice_sessions_time 
            ON voice_sessions(guild_id, user_id, join_time)
        """)
        
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_message_logs_time 
            ON message_logs(guild_id, user_id, timestamp)
        """)
        
        await db.commit()
        logger.info("Base de données initialisée avec succès")

# ===== WARNS =====
async def add_warn(guild_id: int, user_id: int, moderator_id: int, reason: str = None):
    """Ajoute un avertissement"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO warns (guild_id, user_id, moderator_id, reason) VALUES (?, ?, ?, ?)",
            (guild_id, user_id, moderator_id, reason)
        )
        await db.commit()

async def get_warns(guild_id: int, user_id: int):
    """Récupère tous les avertissements d'un utilisateur"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM warns WHERE guild_id = ? AND user_id = ? ORDER BY timestamp DESC",
            (guild_id, user_id)
        ) as cursor:
            return await cursor.fetchall()

async def get_warn_count(guild_id: int, user_id: int):
    """Compte les avertissements d'un utilisateur"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM warns WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

# ===== LOGS DE MODÉRATION =====
async def add_mod_log(guild_id: int, action_type: str, moderator_id: int, target_id: int, reason: str = None):
    """Ajoute un log de modération"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO mod_logs (guild_id, action_type, moderator_id, target_id, reason) VALUES (?, ?, ?, ?, ?)",
            (guild_id, action_type, moderator_id, target_id, reason)
        )
        await db.commit()

# ===== NIVEAUX/XP =====
async def add_xp(guild_id: int, user_id: int, xp: int):
    """Ajoute de l'XP à un utilisateur"""
    async with aiosqlite.connect(DB_PATH) as db:
        from config import Config
        
        # Vérifier si l'utilisateur existe
        async with db.execute(
            "SELECT xp, level FROM levels WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id)
        ) as cursor:
            result = await cursor.fetchone()
        
        if result:
            new_xp = result[0] + xp
            new_level = Config.LEVEL_FORMULA(new_xp)
            old_level = result[1]
            
            await db.execute(
                "UPDATE levels SET xp = ?, level = ?, last_message = ? WHERE guild_id = ? AND user_id = ?",
                (new_xp, new_level, datetime.now(), guild_id, user_id)
            )
            await db.commit()
            
            # Retourne True si level up
            return new_level > old_level, new_level
        else:
            # Créer l'utilisateur
            await db.execute(
                "INSERT INTO levels (guild_id, user_id, xp, level, last_message) VALUES (?, ?, ?, ?, ?)",
                (guild_id, user_id, xp, 0, datetime.now())
            )
            await db.commit()
            return False, 0

async def get_level_data(guild_id: int, user_id: int):
    """Récupère les données de niveau d'un utilisateur"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM levels WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id)
        ) as cursor:
            return await cursor.fetchone()

async def get_leaderboard(guild_id: int, limit: int = 10):
    """Récupère le classement des membres"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM levels WHERE guild_id = ? ORDER BY xp DESC LIMIT ?",
            (guild_id, limit)
        ) as cursor:
            return await cursor.fetchall()

async def set_level(guild_id: int, user_id: int, level: int):
    """Définit le niveau d'un utilisateur"""
    from config import Config
    xp = Config.XP_FORMULA(level)
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO levels (guild_id, user_id, xp, level, last_message) VALUES (?, ?, ?, ?, ?)",
            (guild_id, user_id, xp, level, datetime.now())
        )
        await db.commit()

# ===== TICKETS =====
async def create_ticket(guild_id: int, channel_id: int, user_id: int):
    """Crée un nouveau ticket"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Obtenir le prochain numéro de ticket
        async with db.execute(
            "SELECT MAX(ticket_number) FROM tickets WHERE guild_id = ?",
            (guild_id,)
        ) as cursor:
            result = await cursor.fetchone()
            next_number = (result[0] or 0) + 1
        
        await db.execute(
            "INSERT INTO tickets (guild_id, channel_id, user_id, ticket_number) VALUES (?, ?, ?, ?)",
            (guild_id, channel_id, user_id, next_number)
        )
        await db.commit()
        return next_number

async def close_ticket(channel_id: int):
    """Ferme un ticket"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE tickets SET status = 'closed', closed_at = ? WHERE channel_id = ?",
            (datetime.now(), channel_id)
        )
        await db.commit()

async def get_ticket(channel_id: int):
    """Récupère les informations d'un ticket"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM tickets WHERE channel_id = ?",
            (channel_id,)
        ) as cursor:
            return await cursor.fetchone()

# ===== CONFIGURATION DES SERVEURS =====
async def get_guild_config(guild_id: int):
    """Récupère la configuration d'un serveur"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM guild_config WHERE guild_id = ?",
            (guild_id,)
        ) as cursor:
            result = await cursor.fetchone()
            if not result:
                # Créer une config par défaut
                await db.execute(
                    "INSERT INTO guild_config (guild_id) VALUES (?)",
                    (guild_id,)
                )
                await db.commit()
                return await get_guild_config(guild_id)
            return result

async def update_guild_config(guild_id: int, **kwargs):
    """Met à jour la configuration d'un serveur"""
    async with aiosqlite.connect(DB_PATH) as db:
        # S'assurer que le serveur existe
        await get_guild_config(guild_id)
        
        # Construire la requête de mise à jour
        fields = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [guild_id]
        
        await db.execute(
            f"UPDATE guild_config SET {fields} WHERE guild_id = ?",
            values
        )
        await db.commit()

# ===== ACTIONS TEMPORAIRES =====
async def add_temp_action(guild_id: int, user_id: int, action_type: str, moderator_id: int, expires_at: datetime, reason: str = None):
    """Ajoute une action temporaire (tempban, tempmute)"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO temporary_actions (guild_id, user_id, action_type, moderator_id, expires_at, reason) VALUES (?, ?, ?, ?, ?, ?)",
            (guild_id, user_id, action_type, moderator_id, expires_at, reason)
        )
        await db.commit()

async def get_expired_actions():
    """Récupère toutes les actions expirées"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM temporary_actions WHERE expires_at <= ?",
            (datetime.now(),)
        ) as cursor:
            return await cursor.fetchall()

async def remove_temp_action(action_id: int):
    """Supprime une action temporaire"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM temporary_actions WHERE id = ?",
            (action_id,)
        )
        await db.commit()

async def get_user_temp_action(guild_id: int, user_id: int, action_type: str):
    """Récupère une action temporaire spécifique pour un utilisateur"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM temporary_actions WHERE guild_id = ? AND user_id = ? AND action_type = ?",
            (guild_id, user_id, action_type)
        ) as cursor:
            return await cursor.fetchone()

async def send_mod_log(bot, guild_id: int, embed):
    """Envoie un log de modération dans le canal configuré"""
    try:
        config = await get_guild_config(guild_id)
        if not config or not config['log_channel_id']:
            return  # Pas de canal de logs configuré
        
        import discord
        guild = bot.get_guild(guild_id)
        if not guild:
            return
        
        log_channel = guild.get_channel(config['log_channel_id'])
        if log_channel:
            await log_channel.send(embed=embed)
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du log de modération: {e}")

# ===== ANALYTICS =====
async def increment_message_count(guild_id: int, user_id: int):
    """Incrémente le compteur de messages d'un utilisateur"""
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.now()
        # Incrémenter le compteur total
        await db.execute("""
            INSERT INTO message_stats (guild_id, user_id, message_count, last_message_at)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(guild_id, user_id) DO UPDATE SET
                message_count = message_count + 1,
                last_message_at = ?
        """, (guild_id, user_id, now, now))
        
        # Logger le timestamp pour les stats par période
        await db.execute("""
            INSERT INTO message_logs (guild_id, user_id, timestamp)
            VALUES (?, ?, ?)
        """, (guild_id, user_id, now))
        
        await db.commit()

async def log_activity(guild_id: int, user_id: int, activity_type: str):
    """Enregistre une activité utilisateur"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO activity_logs (guild_id, user_id, activity_type) VALUES (?, ?, ?)",
            (guild_id, user_id, activity_type)
        )
        await db.commit()

async def get_user_stats(guild_id: int, user_id: int):
    """Récupère les statistiques d'un utilisateur"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM message_stats WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id)
        ) as cursor:
            return await cursor.fetchone()

async def get_activity_leaderboard(guild_id: int, limit: int = 10):
    """Récupère le classement d'activité"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM message_stats WHERE guild_id = ? ORDER BY message_count DESC LIMIT ?",
            (guild_id, limit)
        ) as cursor:
            return await cursor.fetchall()

# ===== VOICE SESSIONS =====
async def log_voice_join(guild_id: int, user_id: int):
    """Enregistre l'entrée d'un utilisateur dans un canal vocal"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO voice_sessions (guild_id, user_id, join_time)
            VALUES (?, ?, ?)
        """, (guild_id, user_id, datetime.now()))
        await db.commit()

async def log_voice_leave(guild_id: int, user_id: int):
    """Enregistre la sortie d'un utilisateur d'un canal vocal"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Trouver la dernière session ouverte (sans leave_time)
        async with db.execute("""
            SELECT id, join_time FROM voice_sessions 
            WHERE guild_id = ? AND user_id = ? AND leave_time IS NULL
            ORDER BY join_time DESC LIMIT 1
        """, (guild_id, user_id)) as cursor:
            session = await cursor.fetchone()
        
        if session:
            leave_time = datetime.now()
            join_time = datetime.fromisoformat(session[1])
            duration = int((leave_time - join_time).total_seconds())
            
            await db.execute("""
                UPDATE voice_sessions 
                SET leave_time = ?, duration_seconds = ?
                WHERE id = ?
            """, (leave_time, duration, session[0]))
            await db.commit()

async def get_voice_time(guild_id: int, user_id: int, hours: int = None):
    """
    Calcule le temps vocal d'un utilisateur
    hours: None pour total, 24 pour 24h, 168 pour 7 jours
    """
    async with aiosqlite.connect(DB_PATH) as db:
        if hours is None:
            # Temps total
            async with db.execute("""
                SELECT SUM(duration_seconds) FROM voice_sessions
                WHERE guild_id = ? AND user_id = ? AND leave_time IS NOT NULL
            """, (guild_id, user_id)) as cursor:
                result = await cursor.fetchone()
                return result[0] or 0
        else:
            # Temps sur une période
            from datetime import timedelta
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            async with db.execute("""
                SELECT SUM(duration_seconds) FROM voice_sessions
                WHERE guild_id = ? AND user_id = ? 
                AND leave_time IS NOT NULL 
                AND join_time >= ?
            """, (guild_id, user_id, cutoff_time)) as cursor:
                result = await cursor.fetchone()
                return result[0] or 0

async def get_message_count_period(guild_id: int, user_id: int, hours: int):
    """
    Compte les messages d'un utilisateur sur une période
    hours: 24 pour 24h, 168 pour 7 jours
    """
    from datetime import timedelta
    async with aiosqlite.connect(DB_PATH) as db:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        async with db.execute("""
            SELECT COUNT(*) FROM message_logs
            WHERE guild_id = ? AND user_id = ? AND timestamp >= ?
        """, (guild_id, user_id, cutoff_time)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def get_voice_leaderboard_7d(guild_id: int, limit: int = 10):
    """Récupère le classement vocal sur 7 jours"""
    from datetime import timedelta
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cutoff_time = datetime.now() - timedelta(days=7)
        
        async with db.execute("""
            SELECT user_id, SUM(duration_seconds) as total_seconds
            FROM voice_sessions
            WHERE guild_id = ? AND leave_time IS NOT NULL AND join_time >= ?
            GROUP BY user_id
            ORDER BY total_seconds DESC
            LIMIT ?
        """, (guild_id, cutoff_time, limit)) as cursor:
            return await cursor.fetchall()

async def get_message_leaderboard_7d(guild_id: int, limit: int = 10):
    """Récupère le classement messages sur 7 jours"""
    from datetime import timedelta
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cutoff_time = datetime.now() - timedelta(days=7)
        
        async with db.execute("""
            SELECT user_id, COUNT(*) as message_count
            FROM message_logs
            WHERE guild_id = ? AND timestamp >= ?
            GROUP BY user_id
            ORDER BY message_count DESC
            LIMIT ?
        """, (guild_id, cutoff_time, limit)) as cursor:
            return await cursor.fetchall()

async def get_user_voice_rank_7d(guild_id: int, user_id: int):
    """Récupère le rang vocal d'un utilisateur sur 7 jours"""
    from datetime import timedelta
    async with aiosqlite.connect(DB_PATH) as db:
        cutoff_time = datetime.now() - timedelta(days=7)
        
        # Obtenir le total de secondes de l'utilisateur
        async with db.execute("""
            SELECT SUM(duration_seconds) as total_seconds
            FROM voice_sessions
            WHERE guild_id = ? AND user_id = ? AND leave_time IS NOT NULL AND join_time >= ?
        """, (guild_id, user_id, cutoff_time)) as cursor:
            user_result = await cursor.fetchone()
            user_seconds = user_result[0] if user_result and user_result[0] else 0
        
        # Compter combien d'utilisateurs ont plus de temps
        async with db.execute("""
            SELECT COUNT(DISTINCT user_id) as rank
            FROM (
                SELECT user_id, SUM(duration_seconds) as total_seconds
                FROM voice_sessions
                WHERE guild_id = ? AND leave_time IS NOT NULL AND join_time >= ?
                GROUP BY user_id
                HAVING total_seconds > ?
            )
        """, (guild_id, cutoff_time, user_seconds)) as cursor:
            rank_result = await cursor.fetchone()
            rank = rank_result[0] + 1 if rank_result else 1
        
        # Compter le total d'utilisateurs actifs
        async with db.execute("""
            SELECT COUNT(DISTINCT user_id) as total
            FROM voice_sessions
            WHERE guild_id = ? AND leave_time IS NOT NULL AND join_time >= ?
        """, (guild_id, cutoff_time)) as cursor:
            total_result = await cursor.fetchone()
            total = total_result[0] if total_result else 0
        
        return rank, total

async def get_user_message_rank_7d(guild_id: int, user_id: int):
    """Récupère le rang messages d'un utilisateur sur 7 jours"""
    from datetime import timedelta
    async with aiosqlite.connect(DB_PATH) as db:
        cutoff_time = datetime.now() - timedelta(days=7)
        
        # Obtenir le nombre de messages de l'utilisateur
        async with db.execute("""
            SELECT COUNT(*) as message_count
            FROM message_logs
            WHERE guild_id = ? AND user_id = ? AND timestamp >= ?
        """, (guild_id, user_id, cutoff_time)) as cursor:
            user_result = await cursor.fetchone()
            user_count = user_result[0] if user_result else 0
        
        # Compter combien d'utilisateurs ont plus de messages
        async with db.execute("""
            SELECT COUNT(DISTINCT user_id) as rank
            FROM (
                SELECT user_id, COUNT(*) as message_count
                FROM message_logs
                WHERE guild_id = ? AND timestamp >= ?
                GROUP BY user_id
                HAVING message_count > ?
            )
        """, (guild_id, cutoff_time, user_count)) as cursor:
            rank_result = await cursor.fetchone()
            rank = rank_result[0] + 1 if rank_result else 1
        
        # Compter le total d'utilisateurs actifs
        async with db.execute("""
            SELECT COUNT(DISTINCT user_id) as total
            FROM message_logs
            WHERE guild_id = ? AND timestamp >= ?
        """, (guild_id, cutoff_time)) as cursor:
            total_result = await cursor.fetchone()
            total = total_result[0] if total_result else 0
        
        return rank, total
