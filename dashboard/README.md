# Dashboard Web - Bot Discord 🌐

Interface web moderne pour administrer votre bot Discord.

## 🚀 Démarrage Rapide

### 1. Installation

```bash
cd dashboard
pip install -r requirements.txt
```

### 2. Configuration

Ajoutez ces variables à votre fichier `.env` (à la racine du projet):

```env
# Discord OAuth2
DISCORD_CLIENT_ID=votre_client_id
DISCORD_CLIENT_SECRET=votre_client_secret  
DISCORD_REDIRECT_URI=http://localhost:5000/callback

# Flask
FLASK_SECRET_KEY=votre_secret_key_random
FLASK_DEBUG=True
```

**📝 Comment obtenir Client ID et Secret ?**
1. Allez sur https://discord.com/developers/applications
2. Sélectionnez votre application
3. Onglet "OAuth2"
4. Copiez Client ID et Client Secret
5. Ajoutez `http://localhost:5000/callback` dans les redirects

### 3. Lancer le Dashboard

```bash
python app.py
```

Ouvrez votre navigateur sur : **http://localhost:5000**

---

## ✨ Fonctionnalités

### 🔐 Authentification
- Login via Discord OAuth2
- Session sécurisée
- Vérification des permissions serveur

### 📊 Dashboard
- Stats en temps réel
- Graphiques d'activité
- Top utilisateurs actifs
- Rafraîchissement auto (30s)

### 🛡️ Modération
- Actions rapides (ban, kick, mute, warn)
- Historique des sanctions
- Interface intuitive

### ⚙️ Paramètres
- Activation/désactivation modules
- Configuration des canaux
- Paramètres de sécurité

---

## 🎨 Design

- **Dark Mode** par défaut
- **Glassmorphism** moderne
- **Responsive** (mobile-friendly)
- **Animations** fluides
- **Chart.js** pour graphiques

---

## 📁 Structure

```
dashboard/
├── app.py              # Application Flask
├── config.py           # Configuration
├── requirements.txt    # Dépendances
├── templates/          # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── guild.html
│   ├── moderation.html
│   └── settings.html
└── static/             # Assets statiques
    ├── css/
    │   └── style.css
    └── js/
        └── dashboard.js
```

---

## 🔧 API Endpoints

### Publics
- `GET /` - Page d'accueil
- `GET /login` - Connexion Discord
- `GET /callback` - Callback OAuth2
- `GET /logout` - Déconnexion

### Protégés (authentification requise)
- `GET /dashboard` - Liste des serveurs
- `GET /guild/<id>` - Dashboard serveur
- `GET /guild/<id>/moderation` - Panel modération
- `GET /guild/<id>/settings` - Paramètres

### API
- `GET /api/guild/<id>/stats` - Stats serveur
- `GET /api/guild/<id>/top_users` - Top utilisateurs

---

## ⚠️ Notes Importantes

> **DATABASE**: Le dashboard partage la même base de données (`data/bot.db`) que le bot. Assurez-vous que le bot a créé la base avant de lancer le dashboard.

> **PRODUCTION**: Pour déployer en production, utilisez un serveur WSGI (Gunicorn) et activez HTTPS.

> **SÉCURITÉ**: Changez `FLASK_SECRET_KEY` en production avec une valeur aléatoire forte.

---

## 🐛 Dépannage

**Erreur "Table not found"**
→ Lancez le bot une fois pour créer les tables

**OAuth2 ne fonctionne pas**
→ Vérifiez Client ID/Secret et Redirect URI

**Stats vides**
→ Le bot doit avoir tracké des messages

---

## 📈 Améliorations Futures

- [ ] WebSockets pour updates temps réel
- [ ] Gestion avancée des rôles
- [ ] Système de notifications in-app
- [ ] Export de rapports PDF
- [ ] Dark/Light mode toggle
- [ ] Traductions multilingues

---

## 📞 Support

En cas de problème, vérifiez :
1. Variables `.env` correctement configurées
2. Bot lancé au moins une fois
3. Dépendances installées
4. Port 5000 libre

---

**Fait avec ❤️ pour gérer votre serveur Discord**
