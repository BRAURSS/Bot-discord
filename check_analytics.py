"""
Script de vérification de la base de données analytics
"""

import sqlite3
import os

db_path = "data/bot.db"

if not os.path.exists(db_path):
    print("❌ La base de données n'existe pas encore !")
    print("▶️  Lancez le bot une première fois pour la créer.")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 50)
print("📊 VÉRIFICATION BASE DE DONNÉES ANALYTICS")
print("=" * 50)

# Vérifier si la table existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='message_stats'")
table_exists = cursor.fetchone()

if table_exists:
    print("✅ Table 'message_stats' existe")
    
    # Compter les entrées
    cursor.execute("SELECT COUNT(*) FROM message_stats")
    count = cursor.fetchone()[0]
    
    print(f"📈 Nombre d'utilisateurs trackés: {count}")
    
    if count > 0:
        # Afficher les stats
        cursor.execute("SELECT guild_id, user_id, message_count FROM message_stats ORDER BY message_count DESC LIMIT 5")
        stats = cursor.fetchall()
        
        print("\n🏆 Top 5 utilisateurs:")
        for guild_id, user_id, msg_count in stats:
            print(f"   - User {user_id}: {msg_count} messages")
    else:
        print("\n⚠️  Aucune donnée encore !")
        print("\n📝 Solution:")
        print("   1. Démarrez le bot: python bot.py")
        print("   2. Envoyez quelques messages dans Discord")
        print("   3. Réessayez /stats")
else:
    print("❌ Table 'message_stats' n'existe PAS")
    print("\n📝 Solution:")
    print("   Le bot doit être lancé au moins une fois pour créer les tables.")
    print("   Lancez: python bot.py")

conn.close()
print("=" * 50)
