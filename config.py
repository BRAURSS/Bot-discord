"""
Configuration centralisée pour le bot Discord
"""

import discord

# ===== COULEURS =====
class Colors:
    """Couleurs pour les embeds"""
    SUCCESS = discord.Color.green()
    ERROR = discord.Color.red()
    WARNING = discord.Color.orange()
    INFO = discord.Color.blue()
    DEFAULT = discord.Color.blurple()

# ===== EMOJIS =====
class Emojis:
    """Emojis personnalisés"""
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    LOADING = "⏳"
    LOCK = "🔒"
    UNLOCK = "🔓"
    BAN = "🔨"
    KICK = "👢"
    MUTE = "🔇"
    UNMUTE = "🔊"
    WARN = "⚠️"
    LEVEL_UP = "⬆️"
    TICKET = "🎫"
    POLL = "📊"
    TRASH = "🗑️"

# ===== CONFIGURATION =====
class Config:
    """Configuration générale"""
    # XP System
    XP_MIN = 5
    XP_MAX = 15
    XP_COOLDOWN = 60  # secondes entre chaque gain d'XP
    
    # Auto-modération
    SPAM_THRESHOLD = 5  # messages identiques en X secondes
    SPAM_TIME_WINDOW = 10  # secondes
    MENTION_THRESHOLD = 5  # mentions max par message
    
    # Tickets
    TICKET_CATEGORY_NAME = "🎫 Tickets"
    TICKET_LOG_CHANNEL = "ticket-logs"
    
    # Leveling
    LEVEL_FORMULA = lambda xp: int(0.1 * (xp ** 0.5))
    XP_FORMULA = lambda level: int((level / 0.1) ** 2)

# ===== MESSAGES =====
class Messages:
    """Messages prédéfinis"""
    NO_PERMISSION = f"{Emojis.ERROR} Vous n'avez pas la permission d'utiliser cette commande."
    MISSING_ARGS = f"{Emojis.WARNING} Arguments manquants. Utilisez `/help <commande>` pour plus d'infos."
    USER_NOT_FOUND = f"{Emojis.ERROR} Utilisateur introuvable."
    ROLE_NOT_FOUND = f"{Emojis.ERROR} Rôle introuvable."
    CHANNEL_NOT_FOUND = f"{Emojis.ERROR} Salon introuvable."
    ERROR_OCCURRED = f"{Emojis.ERROR} Une erreur s'est produite. Veuillez réessayer."
    SUCCESS = f"{Emojis.SUCCESS} Opération effectuée avec succès !"
