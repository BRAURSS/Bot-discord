# 🤖 Bot Discord Polyvalent

Bot Discord professionnel avec système de modération, auto-modération, utilitaires, leveling, et tickets.

## ✨ Fonctionnalités

### 🔨 Modération
- `/ban` - Bannir un membre du serveur
- `/unban` - Débannir un utilisateur (requiert l'ID Discord)
- `/tempban` - Bannir temporairement avec auto-unban
- `/kick` - Expulser un membre
- `/mute` - Mettre en sourdine (timeout)
- `/unmute` - Retirer la sourdine
- `/tempmute` - Mute temporaire avec auto-unmute
- `/warn` - Avertir un membre
- `/ban` - Bannir un utilisateur du serveur
- `/kick` - Expulser un utilisateur
- `/mute` - Rendre muet un membre
- `/unmute` - Retirer le mute d'un membre
- `/warn` - Avertir un utilisateur
- `/warnings` - Afficher les avertissements d'un utilisateur
- `/clear` - Supprimer des messages en masse

### 🤖 Auto-Modération
- **Anti-spam** - Détection automatique de spam
- **Anti-lien** - Bloquer les liens Discord/autres
- **Anti-mention** - Protection contre les mentions de masse
- **Filtre de mots** - Bloquer les mots interdits
- Configuration personnalisable par serveur

### 🛠️ Utilitaires
- `/ping` - Vérifier la latence du bot
- `/serverinfo` - Informations détaillées sur le serveur
- `/userinfo` - Informations sur un utilisateur
- `/avatar` - Afficher l'avatar en haute résolution
- `/poll` - Créer des sondages interactifs
- `/embed` - Créer des messages embed personnalisés

### 📊 Système de Leveling
- **XP automatique** - Gagnez de l'XP en chattant
- `/rank` - Voir votre niveau et progression
- `/leaderboard` - Classement du serveur
- `/setlevel` - Modifier le niveau d'un utilisateur (admin)
- `/leveling` - Activer/désactiver le système
- Messages de level-up personnalisables

### 🎫 Système de Tickets
- `/ticketsetup` - Configuration initiale
- **Création automatique** via bouton
- `/close` - Fermer un ticket avec transcription
- `/add` / `/remove` - Gérer les accès au ticket
- Logs complets des tickets

### ⚙️ Setup et Configuration
- `/createrole` - Créer des rôles personnalisés
- `/createchannel` - Créer des salons (texte/vocal/catégorie)
- `/pack` - Pack complet de salons et rôles
- `/deletechannel` - Supprimer un salon
- `/deleterole` - Supprimer un rôle

---

## 🚀 Installation

### Prérequis

- **Python 3.11+**
- **Git**
- **Compte Discord Developer**

### Installation Locale

#### 1. Cloner le repository

```bash
git clone https://github.com/VOTRE-USERNAME/Bot-discord.git
cd Bot-discord
```

#### 2. Créer un environnement virtuel

**Linux/Mac/WSL :**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows :**
```bash
python -m venv venv
venv\Scripts\activate
```

#### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

#### 4. Configuration

Créez un fichier `.env` à la racine :

```bash
cp .env.example .env
nano .env  # ou utilisez votre éditeur préféré
```

Ajoutez votre token Discord :

```env
DISCORD_TOKEN=votre_token_discord_ici
```

#### 5. Lancer le bot

```bash
python3 bot.py
```

Vous devriez voir :
```
✅ Base de données initialisée
✅ Cog chargé: moderation
✅ Cog chargé: automod
...
🤖 Bot connecté en tant que VotreBot#1234
```

---

## 🔐 Configuration Discord

### Obtenir votre Token

1. Allez sur [Discord Developer Portal](https://discord.com/developers/applications)
2. Cliquez sur **"New Application"**
3. Donnez un nom à votre bot
4. Allez dans l'onglet **"Bot"**
5. Cliquez sur **"Reset Token"** et **copiez le token**
6. ⚠️ **NE PARTAGEZ JAMAIS CE TOKEN !**

### Activer les Intents

Dans l'onglet **"Bot"**, activez :
- ✅ **PRESENCE INTENT**
- ✅ **SERVER MEMBERS INTENT**
- ✅ **MESSAGE CONTENT INTENT**

Cliquez sur **"Save Changes"**

### Inviter le Bot

1. Allez dans **"OAuth2"** → **"URL Generator"**
2. **Scopes** : Cochez `bot` et `applications.commands`
3. **Bot Permissions** : Cochez `Administrator` (ou permissions spécifiques)
4. Copiez l'URL générée et ouvrez-la dans votre navigateur
5. Sélectionnez votre serveur et autorisez

---

## 🌐 Déploiement

### ☁️ Railway.app (Recommandé - Gratuit)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

**Étapes simples :**

1. Créez un compte sur [Railway.app](https://railway.app)
2. Cliquez sur **"New Project"** → **"Deploy from GitHub repo"**
3. Sélectionnez ce repository
4. Ajoutez la variable d'environnement :
   - `DISCORD_TOKEN` = votre token
5. Railway déploie automatiquement ! 🚀

**Avantages :**
- ✅ Gratuit (500h/mois)
- ✅ Déploiement automatique depuis GitHub
- ✅ Logs en temps réel
- ✅ Redémarrage automatique

### 🐳 Docker

```bash
# Build l'image
docker build -t discord-bot .

# Lancer le conteneur
docker run -d --name bot \
  -e DISCORD_TOKEN=votre_token \
  discord-bot
```

### 🖥️ VPS

Pour un déploiement sur VPS avec systemd, consultez le [guide complet](https://github.com/VOTRE-USERNAME/Bot-discord/wiki/VPS-Deployment).

---

## 📁 Structure du Projet

```
Bot-discord/
├── 📄 bot.py                    # Point d'entrée principal
├── ⚙️ config.py                 # Configuration (couleurs, emojis, etc.)
├── 💾 database.py               # Gestion base de données SQLite
├── 📋 requirements.txt          # Dépendances Python
├── 🐳 Dockerfile                # Configuration Docker
├── 📁 cogs/                     # Modules/Extensions
│   ├── moderation.py           # Commandes de modération
│   ├── automod.py              # Auto-modération
│   ├── utils.py                # Utilitaires
│   ├── leveling.py             # Système de niveaux
│   ├── tickets.py              # Système de tickets
│   └── setup.py                # Setup serveur
├── 📁 data/                     # Données
│   └── bot.db                  # Base de données SQLite
├── 📁 backups/                  # Sauvegardes auto
└── 📁 dashboard/                # Dashboard web (optionnel)
    ├── app.py                  # Application Flask
    └── templates/              # Templates HTML
```

## 🔧 Configuration Avancée

### Modifier les paramètres XP
Dans `config.py` :
```python
XP_MIN = 5              # XP minimum par message
XP_MAX = 15             # XP maximum par message
XP_COOLDOWN = 60        # Cooldown en secondes
```

### Modifier les seuils d'auto-modération
Dans `config.py` :
```python
SPAM_THRESHOLD = 5      # Messages identiques avant action
SPAM_TIME_WINDOW = 10   # Fenêtre temporelle (secondes)
MENTION_THRESHOLD = 5   # Mentions max par message
```

## 📊 Base de Données

Le bot utilise SQLite avec les tables suivantes :
- `warns` - Avertissements
- `mod_logs` - Logs de modération
- `levels` - Niveaux et XP
- `tickets` - Tickets de support
- `guild_config` - Configuration par serveur

La base de données est créée automatiquement au premier lancement.

## 🚀 Commandes Utiles

### Configuration initiale du serveur
1. `/automod True` - Activer l'auto-modération
2. `/leveling True` - Activer le système de niveaux
3. `/ticketsetup` - Configurer les tickets

### Pour les modérateurs
- `/warn @membre raison` - Avertir
- `/mute @membre durée raison` - Mute temporaire
- `/clear 10` - Supprimer 10 messages

### Pour les admins
- `/pack 📌・règlement | 💬・chat | 🎮・gaming` - Créer plusieurs salons
- `/createrole Membre color=5865F2` - Créer un rôle bleu
- `/setlevel @membre 10` - Définir niveau 10

## 🛡️ Permissions Requises

Le bot a besoin des permissions suivantes :
- Gérer les rôles
- Gérer les salons
- Bannir des membres
- Expulser des membres
- Gérer les messages
- Lire l'historique des messages
- Envoyer des messages
- Intégrer des liens
- Ajouter des réactions

## 📝 Logs

Les logs sont enregistrés dans `bot.log` avec les informations suivantes :
- Démarrage/arrêt du bot
- Commandes utilisées
- Actions de modération
- Erreurs et avertissements

## ⚠️ Notes Importantes

> **IMPORTANT** : N'oubliez pas d'activer les **Privileged Gateway Intents** dans le Discord Developer Portal !

> **WARNING** : Le fichier `.env` contient des informations sensibles. Ne le partagez jamais et ne le commitez pas sur Git.

> **TIP** : Pour une meilleure performance, hébergez le bot sur un VPS ou utilisez un service comme Heroku.

## 🤝 Support

Si vous rencontrez des problèmes :
1. Vérifiez que tous les intents sont activés
2. Vérifiez que le bot a les permissions nécessaires
3. Consultez les logs dans `bot.log`
4. Vérifiez que toutes les dépendances sont installées

## 📄 Licence

Ce projet est libre d'utilisation. Modifiez-le selon vos besoins !

---

**Créé avec ❤️ en Python et discord.py**
