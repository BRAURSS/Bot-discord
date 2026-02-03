"""
Application Flask principale du Dashboard
"""

from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from flask_session import Session
import os
import sys
import sqlite3
from datetime import datetime

# Ajouter le répertoire parent au path pour importer database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# ===== HELPER FUNCTIONS =====

def get_bot_guilds():
    """Récupère la liste des serveurs où le bot est présent"""
    import requests
    
    if not Config.DISCORD_BOT_TOKEN:
        return []
    
    try:
        headers = {"Authorization": f"Bot {Config.DISCORD_BOT_TOKEN}"}
        response = requests.get("https://discord.com/api/users/@me/guilds", headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erreur lors de la récupération des serveurs du bot: {e}")
        return []

# Session management
Session(app)

# ===== ROUTES PUBLIQUES =====

@app.route("/")
def index():
    """Page d'accueil"""
    if "discord_user" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/login")
def login():
    """Redirection vers Discord OAuth2"""
    discord_auth_url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={Config.DISCORD_CLIENT_ID}"
        f"&redirect_uri={Config.DISCORD_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={'%20'.join(Config.DISCORD_OAUTH_SCOPES)}"
    )
    return redirect(discord_auth_url)

@app.route("/callback")
def callback():
    """Callback OAuth2 Discord"""
    import requests
    
    code = request.args.get("code")
    if not code:
        return redirect(url_for("index"))
    
    # Échanger le code contre un token
    data = {
        "client_id": Config.DISCORD_CLIENT_ID,
        "client_secret": Config.DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": Config.DISCORD_REDIRECT_URI,
    }
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    try:
        # Obtenir le token
        r = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
        r.raise_for_status()
        token_data = r.json()
        
        access_token = token_data["access_token"]
        
        # Obtenir les infos utilisateur
        headers = {"Authorization": f"Bearer {access_token}"}
        user_response = requests.get("https://discord.com/api/users/@me", headers=headers)
        user_response.raise_for_status()
        user_data = user_response.json()
        
        # Obtenir les serveurs de l'utilisateur
        guilds_response = requests.get("https://discord.com/api/users/@me/guilds", headers=headers)
        guilds_response.raise_for_status()
        guilds_data = guilds_response.json()
        
        # Stocker dans la session
        session["discord_user"] = user_data
        session["discord_guilds"] = guilds_data
        session["access_token"] = access_token
        session.permanent = True
        
        return redirect(url_for("dashboard"))
        
    except Exception as e:
        print(f"Erreur OAuth2: {e}")
        return redirect(url_for("index"))

@app.route("/logout")
def logout():
    """Déconnexion"""
    session.clear()
    return redirect(url_for("index"))

# ===== ROUTES PROTÉGÉES =====

def login_required(f):
    """Décorateur pour protéger les routes"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "discord_user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/dashboard")
@login_required
def dashboard():
    """Dashboard principal - sélection serveur"""
    user = session.get("discord_user")
    guilds = session.get("discord_guilds", [])
    
    # Récupérer les serveurs où le bot est présent
    bot_guilds = get_bot_guilds()
    bot_guild_ids = {int(g["id"]) for g in bot_guilds}
    
    # Filtrer les serveurs où l'utilisateur a des permissions d'admin ET où le bot est présent
    admin_guilds = [
        g for g in guilds 
        if (int(g.get("permissions", 0)) & 0x8) == 0x8  # Administrator permission
        and int(g["id"]) in bot_guild_ids  # Bot is present in guild
    ]
    
    return render_template("dashboard.html", user=user, guilds=admin_guilds)

@app.route("/guild/<int:guild_id>")
@login_required
def guild_dashboard(guild_id):
    """Dashboard d'un serveur spécifique"""
    user = session.get("discord_user")
    guilds = session.get("discord_guilds", [])
    
    # Vérifier que l'utilisateur a accès à ce serveur
    guild = next((g for g in guilds if int(g["id"]) == guild_id), None)
    if not guild:
        return "Serveur non trouvé", 404
    
    # Vérifier permissions admin
    if (int(guild.get("permissions", 0)) & 0x8) != 0x8:
        return "Permissions insuffisantes", 403
    
    # Vérifier que le bot est présent dans ce serveur
    bot_guilds = get_bot_guilds()
    bot_guild_ids = {int(g["id"]) for g in bot_guilds}
    if guild_id not in bot_guild_ids:
        return "Le bot n'est pas présent sur ce serveur", 404
    
    return render_template("guild.html", user=user, guild=guild, guild_id=guild_id)

@app.route("/guild/<int:guild_id>/moderation")
@login_required
def guild_moderation(guild_id):
    """Panel de modération d'un serveur"""
    user = session.get("discord_user")
    guilds = session.get("discord_guilds", [])
    
    guild = next((g for g in guilds if int(g["id"]) == guild_id), None)
    if not guild or (int(guild.get("permissions", 0)) & 0x8) != 0x8:
        return "Accès refusé", 403
    
    # Vérifier que le bot est présent dans ce serveur
    bot_guilds = get_bot_guilds()
    bot_guild_ids = {int(g["id"]) for g in bot_guilds}
    if guild_id not in bot_guild_ids:
        return "Le bot n'est pas présent sur ce serveur", 404
    
    return render_template("moderation.html", user=user, guild=guild, guild_id=guild_id)

@app.route("/guild/<int:guild_id>/settings")
@login_required
def guild_settings(guild_id):
    """Paramètres d'un serveur"""
    user = session.get("discord_user")
    guilds = session.get("discord_guilds", [])
    
    guild = next((g for g in guilds if int(g["id"]) == guild_id), None)
    if not guild or (int(guild.get("permissions", 0)) & 0x8) != 0x8:
        return "Accès refusé", 403
    
    # Vérifier que le bot est présent dans ce serveur
    bot_guilds = get_bot_guilds()
    bot_guild_ids = {int(g["id"]) for g in bot_guilds}
    if guild_id not in bot_guild_ids:
        return "Le bot n'est pas présent sur ce serveur", 404
    
    return render_template("settings.html", user=user, guild=guild, guild_id=guild_id)

# ===== API ENDPOINTS =====

@app.route("/api/guild/<int:guild_id>/stats")
@login_required
def api_guild_stats(guild_id):
    """Stats d'un serveur"""
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Stats générales
        cursor.execute("SELECT COUNT(*) as total FROM message_stats WHERE guild_id = ?", (guild_id,))
        active_users = cursor.fetchone()["total"]
        
        cursor.execute("SELECT SUM(message_count) as total FROM message_stats WHERE guild_id = ?", (guild_id,))
        total_messages = cursor.fetchone()["total"] or 0
        
        cursor.execute("SELECT COUNT(*) as total FROM mod_logs WHERE guild_id = ?", (guild_id,))
        mod_actions = cursor.fetchone()["total"]
        
        conn.close()
        
        return jsonify({
            "success": True,
            "stats": {
                "active_users": active_users,
                "total_messages": total_messages,
                "mod_actions": mod_actions
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/guild/<int:guild_id>/top_users")
@login_required
def api_top_users(guild_id):
    """Top utilisateurs actifs"""
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, message_count 
            FROM message_stats 
            WHERE guild_id = ? 
            ORDER BY message_count DESC 
            LIMIT 10
        """, (guild_id,))
        
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({"success": True, "users": users})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/guild/<int:guild_id>/mod_logs")
@login_required
def api_mod_logs(guild_id):
    """Logs de modération d'un serveur"""
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT action_type, moderator_id, target_id, reason, timestamp
            FROM mod_logs 
            WHERE guild_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 20
        """, (guild_id,))
        
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({"success": True, "logs": logs})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/guild/<int:guild_id>/activity")
@login_required
def api_guild_activity(guild_id):
    """Activité des 7 derniers jours"""
    try:
        from datetime import datetime, timedelta
        
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Calculer les 7 derniers jours
        today = datetime.now().date()
        days = []
        labels = []
        
        for i in range(6, -1, -1):  # 6 jours en arrière + aujourd'hui
            day = today - timedelta(days=i)
            days.append(day)
            # Format français: Lun, Mar, etc.
            day_names = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
            labels.append(day_names[day.weekday()])
        
        # Compter les messages par jour
        message_counts = []
        for day in days:
            start = datetime.combine(day, datetime.min.time())
            end = datetime.combine(day, datetime.max.time())
            
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM message_logs
                WHERE guild_id = ? 
                AND timestamp >= ? 
                AND timestamp <= ?
            """, (guild_id, start, end))
            
            result = cursor.fetchone()
            message_counts.append(result['count'] if result else 0)
        
        conn.close()
        
        return jsonify({
            "success": True,
            "labels": labels,
            "data": message_counts
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ===== DÉMARRAGE =====

if __name__ == "__main__":
    print("=" * 50)
    print("🌐 Dashboard Web du Bot Discord")
    print(f"📍 URL: http://{Config.HOST}:{Config.PORT}")
    print("=" * 50)
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
