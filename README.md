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
- `/warnings` - Voir les avertissements
- `/clear` - Supprimer des messages en masse
- `/bans` - Liste des utilisateurs bannis
- `/massban` - Bannir plusieurs utilisateurs
- `/masskick` - Expulser plusieurs membres

> **Note :** Le propriétaire du serveur (couronne 👑) peut utiliser toutes les commandes de modération même si son rôle est égal ou inférieur à celui du membre ciblé.

### 🤖 Auto-Modération
- Détection de spam automatique
- Filtrage de liens (optionnel)
- Protection contre les mentions massives
- Actions progressives (warn → mute → kick)
- `/automod` - Activer/désactiver l'auto-mod
- `/antilink` - Activer/désactiver le filtre anti-liens

### 🛠️ Utilitaires
- `/ping` - Vérifier la latence
- `/serverinfo` - Informations sur le serveur
- `/userinfo` - Informations sur un utilisateur
- `/avatar` - Afficher l'avatar
- `/poll` - Créer un sondage
- `/embed` - Créer un embed personnalisé

### 📊 Leveling & Analytics
- Gain d'XP automatique sur les messages
- `/rank` - Voir son niveau et XP
- `/leaderboard` - Classement par niveau
- `/setlevel` - Définir le niveau d'un membre (admin)
- `/leveling` - Activer/désactiver le leveling (admin)
- `/stats` - Statistiques d'un membre
- `/activityboard` - Classement d'activité par messages

### 🎫 Système de Tickets
- `/ticketsetup` - Configurer le système
- Création via bouton interactif
- Salons privés automatiques
- `/close` - Fermer un ticket
- `/add` / `/remove` - Gérer les membres

### ⚙️ Configuration
- `/createrole` - Créer un rôle avec couleur
- `/createchannel` - Créer un salon
- `/pack` - Créer plusieurs salons en une fois
- `/deletechannel` - Supprimer un salon
- `/deleterole` - Supprimer un rôle
- `/setlogchannel` - Définir le canal des logs de modération
- `/antiraid` - Activer/désactiver la protection anti-raid
- `/unlock` - Réactiver les invitations après un raid

### 💬 Communauté
- `/suggest` - Proposer une suggestion
- `/suggestions` - Voir toutes les suggestions (modérateurs)

## 📦 Installation

### 1. Prérequis
- Python 3.8 ou supérieur
- Un token Discord Bot ([Discord Developer Portal](https://discord.com/developers/applications))

### 2. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 3. Configuration
Créez un fichier `.env` à la racine du projet :
```env
DISCORD_TOKEN=votre_token_ici
```

### 4. Permissions et Intents
Dans le Discord Developer Portal, activez les **Privileged Gateway Intents** :
- ✅ **MESSAGE CONTENT INTENT** (pour auto-mod et leveling)
- ✅ **SERVER MEMBERS INTENT** (pour les infos membres)

### 5. Lancement
```bash
python bot.py
```

## 📁 Structure du Projet

```
bot discord/
├── bot.py                 # Point d'entrée principal
├── config.py             # Configuration (couleurs, emojis, etc.)
├── database.py           # Gestion de la base de données
├── requirements.txt      # Dépendances Python
├── .env                  # Variables d'environnement (à créer)
├── .env.example          # Exemple de fichier .env
├── bot.log              # Logs du bot
├── cogs/                # Modules (cogs)
│   ├── moderation.py    # Commandes de modération
│   ├── automod.py       # Auto-modération
│   ├── utility.py       # Commandes utilitaires
│   ├── leveling.py      # Système XP/niveaux
│   ├── tickets.py       # Système de tickets
│   └── setup.py         # Commandes de setup
└── data/
    └── bot.db           # Base de données SQLite (créée auto)
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
