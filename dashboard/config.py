"""
Configuration du Dashboard Web
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration de l'application Flask"""
    
    # Flask
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Discord OAuth2
    DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
    DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
    DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI", "http://localhost:5000/callback")
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_TOKEN")
    
    # Discord OAuth2 Scopes
    DISCORD_OAUTH_SCOPES = ["identify", "guilds"]
    
    # Database
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "bot.db")
    
    # Session
    SESSION_TYPE = "filesystem"
    PERMANENT_SESSION_LIFETIME = 3600 * 24 * 7  # 7 jours
    
    # App
    DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"
    HOST = os.getenv("FLASK_HOST", "localhost")
    PORT = int(os.getenv("FLASK_PORT", "5000"))
