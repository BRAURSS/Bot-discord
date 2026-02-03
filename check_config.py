"""
Script de vérification de la configuration du bot
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def check_config():
    """Vérifie que le bot est correctement configuré"""
    
    print("=" * 60)
    print("🔍 VÉRIFICATION DE LA CONFIGURATION DU BOT")
    print("=" * 60)
    print()
    
    errors = []
    warnings = []
    
    # 1. Vérifier le fichier .env
    print("1️⃣ Vérification du fichier .env...")
    env_path = Path(".env")
    
    if not env_path.exists():
        errors.append("❌ Fichier .env introuvable")
        print("   ❌ Fichier .env introuvable")
    else:
        print("   ✅ Fichier .env trouvé")
        
        # Charger les variables
        load_dotenv()
        token = os.getenv("DISCORD_TOKEN")
        
        if not token:
            errors.append("❌ Variable DISCORD_TOKEN non définie dans .env")
            print("   ❌ Variable DISCORD_TOKEN non définie")
        elif token == "votre_token_discord_ici" or token == "VOTRE_TOKEN_ICI":
            errors.append("❌ Token Discord non configuré (valeur par défaut détectée)")
            print("   ❌ Token non configuré (encore la valeur d'exemple)")
        elif len(token) < 50:
            errors.append("❌ Token trop court (probablement invalide)")
            print(f"   ❌ Token trop court ({len(token)} caractères)")
        else:
            print(f"   ✅ Token configuré ({len(token)} caractères)")
    
    print()
    
    # 2. Vérifier les dépendances
    print("2️⃣ Vérification des dépendances...")
    
    try:
        import discord
        print(f"   ✅ discord.py installé (version {discord.__version__})")
    except ImportError:
        errors.append("❌ discord.py non installé")
        print("   ❌ discord.py non installé")
    
    try:
        import dotenv
        print("   ✅ python-dotenv installé")
    except ImportError:
        errors.append("❌ python-dotenv non installé")
        print("   ❌ python-dotenv non installé")
    
    try:
        import aiosqlite
        print("   ✅ aiosqlite installé")
    except ImportError:
        errors.append("❌ aiosqlite non installé")
        print("   ❌ aiosqlite non installé")
    
    print()
    
    # 3. Vérifier la structure du projet
    print("3️⃣ Vérification de la structure du projet...")
    
    required_files = {
        "bot.py": "Fichier principal du bot",
        "database.py": "Gestion de la base de données",
        "config.py": "Configuration",
        "cogs": "Dossier des extensions"
    }
    
    for file_name, description in required_files.items():
        path = Path(file_name)
        if path.exists():
            print(f"   ✅ {file_name} ({description})")
        else:
            warnings.append(f"⚠️ {file_name} introuvable")
            print(f"   ⚠️ {file_name} introuvable")
    
    print()
    
    # 4. Vérifier le dossier cogs
    print("4️⃣ Vérification des cogs...")
    cogs_dir = Path("cogs")
    
    if cogs_dir.exists():
        cog_files = list(cogs_dir.glob("*.py"))
        cog_files = [f for f in cog_files if not f.name.startswith("_")]
        print(f"   ✅ {len(cog_files)} cog(s) détecté(s)")
        for cog in cog_files:
            print(f"      • {cog.stem}")
    else:
        warnings.append("⚠️ Dossier cogs introuvable")
        print("   ⚠️ Dossier cogs introuvable")
    
    print()
    print("=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    
    if errors:
        print("\n❌ ERREURS À CORRIGER :")
        for error in errors:
            print(f"   {error}")
    
    if warnings:
        print("\n⚠️ AVERTISSEMENTS :")
        for warning in warnings:
            print(f"   {warning}")
    
    if not errors and not warnings:
        print("\n✅ TOUT EST CONFIGURÉ CORRECTEMENT !")
        print("   Vous pouvez lancer le bot avec : python bot.py")
    elif not errors:
        print("\n⚠️ Configuration OK avec quelques avertissements")
        print("   Vous pouvez tenter de lancer le bot avec : python bot.py")
    else:
        print("\n❌ Configuration incomplète")
        print("   Corrigez les erreurs avant de lancer le bot")
    
    print()
    print("=" * 60)
    
    return len(errors) == 0

if __name__ == "__main__":
    check_config()
