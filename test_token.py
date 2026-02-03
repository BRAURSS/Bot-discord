"""
Script pour tester et diagnostiquer le token Discord
"""

import os
from dotenv import load_dotenv

print("=" * 70)
print("🔍 DIAGNOSTIC DU TOKEN DISCORD")
print("=" * 70)
print()

# Charger le fichier .env
load_dotenv()

# Récupérer le token
token = os.getenv("DISCORD_TOKEN")

print("📄 Contenu du fichier .env :")
print("-" * 70)

# Lire et afficher le fichier .env (masquer le vrai token s'il existe)
try:
    with open(".env", "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if line.strip().startswith("DISCORD_TOKEN="):
                # Afficher partiellement le token pour diagnostic
                if "=" in line:
                    key, value = line.split("=", 1)
                    value = value.strip()
                    if value and value != "votre_token_discord_ici":
                        # Token configuré, masquer en partie
                        display_token = value[:10] + "..." + value[-10:] if len(value) > 20 else "***"
                        print(f"Ligne {i}: DISCORD_TOKEN={display_token}")
                    else:
                        print(f"Ligne {i}: {line.rstrip()} ❌ VALEUR D'EXEMPLE")
            else:
                print(f"Ligne {i}: {line.rstrip()}")
except Exception as e:
    print(f"❌ Erreur lors de la lecture du fichier .env: {e}")

print("-" * 70)
print()

# Analyser le token
print("🔍 Analyse du Token :")
print("-" * 70)

if not token:
    print("❌ ERREUR : Aucun token trouvé !")
    print("   → Variable DISCORD_TOKEN vide ou absente")
    print()
    print("💡 Solution :")
    print("   1. Ouvrez le fichier .env")
    print("   2. Remplacez 'votre_token_discord_ici' par votre vrai token")
    print("   3. Sauvegardez le fichier (Ctrl+S)")
    
elif token == "votre_token_discord_ici" or token == "VOTRE_TOKEN_ICI":
    print("❌ ERREUR : Token non configuré (valeur d'exemple détectée)")
    print(f"   → Valeur actuelle : '{token}'")
    print()
    print("💡 Solution :")
    print("   1. Allez sur https://discord.com/developers/applications")
    print("   2. Sélectionnez votre application → Onglet 'Bot'")
    print("   3. Cliquez sur 'Reset Token' et copiez le token")
    print("   4. Collez-le dans le fichier .env à la place de 'votre_token_discord_ici'")
    
elif len(token) < 50:
    print(f"❌ ERREUR : Token trop court ({len(token)} caractères)")
    print(f"   → Token actuel : '{token}'")
    print()
    print("💡 Un vrai token Discord fait environ 70-90 caractères")
    print("   Vérifiez que vous avez copié le token en entier")
    
elif not "." in token:
    print(f"❌ ERREUR : Format de token invalide")
    print(f"   → Le token doit contenir des points (.)")
    print()
    print("💡 Format attendu : MTIzNDU2Nzg5.GaBcDe.FgHiJkLmNoPqRsTuVw")
    
else:
    print(f"✅ Token détecté ({len(token)} caractères)")
    
    # Vérifier le format
    parts = token.split(".")
    if len(parts) == 3:
        print(f"✅ Format correct (3 parties séparées par des points)")
        print(f"   → Partie 1 : {len(parts[0])} caractères")
        print(f"   → Partie 2 : {len(parts[1])} caractères")
        print(f"   → Partie 3 : {len(parts[2])} caractères")
        print()
        print("✅ Le token semble valide !")
        print()
        print("⚠️ Si vous avez toujours l'erreur 'Improper token', vérifiez :")
        print("   1. Que le token n'a pas expiré (régénérez-le sur Discord)")
        print("   2. Qu'il n'y a pas d'espaces avant/après le token dans .env")
        print("   3. Que vous avez sauvegardé le fichier .env après modification")
    else:
        print(f"⚠️ Format inhabituel ({len(parts)} parties au lieu de 3)")
        print("   Un token Discord standard a 3 parties séparées par des points")

print("-" * 70)
print()

# Vérifications supplémentaires
print("🔍 Vérifications Supplémentaires :")
print("-" * 70)

# Vérifier les espaces
if token and (token.startswith(" ") or token.endswith(" ")):
    print("⚠️ ATTENTION : Espaces détectés au début/fin du token")
    print("   → Supprimez les espaces dans le fichier .env")
else:
    print("✅ Pas d'espaces parasites détectés")

# Vérifier les guillemets
if token and (token.startswith('"') or token.startswith("'")):
    print("⚠️ ATTENTION : Guillemets détectés dans le token")
    print("   → Ne mettez PAS de guillemets autour du token dans .env")
else:
    print("✅ Pas de guillemets détectés")

print("-" * 70)
print()

print("=" * 70)
print("📋 RÉSUMÉ")
print("=" * 70)

if not token or token == "votre_token_discord_ici" or token == "VOTRE_TOKEN_ICI":
    print()
    print("❌ VOUS DEVEZ CONFIGURER VOTRE TOKEN !")
    print()
    print("Étapes à suivre :")
    print("1. Ouvrez : https://discord.com/developers/applications")
    print("2. Créez une application ou sélectionnez-en une")
    print("3. Allez dans l'onglet 'Bot'")
    print("4. Cliquez sur 'Reset Token' et copiez le token")
    print("5. Dans le fichier .env (ligne 4), remplacez :")
    print("   DISCORD_TOKEN=votre_token_discord_ici")
    print("   par :")
    print("   DISCORD_TOKEN=VOTRE_VRAI_TOKEN_COPIE")
    print("6. Sauvegardez le fichier .env (Ctrl+S)")
    print("7. Relancez le bot avec : python3 bot.py")
    print()
elif len(token) >= 50 and "." in token:
    print()
    print("✅ Votre token semble correctement configuré !")
    print()
    print("Si vous avez toujours une erreur :")
    print("→ Le token a peut-être expiré, régénérez-le sur Discord")
    print("→ Vérifiez les 'Privileged Gateway Intents' dans l'onglet Bot")
    print()
else:
    print()
    print("⚠️ Le token semble incorrect")
    print("→ Vérifiez que vous avez copié le token en entier")
    print()

print("=" * 70)
