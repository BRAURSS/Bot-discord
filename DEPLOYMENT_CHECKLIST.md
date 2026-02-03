# ✅ Checklist de Déploiement Railway

## 📋 Avant de Déployer

### Fichiers Projet
- [x] `bot.py` - Fichier principal du bot
- [x] `requirements.txt` - Dépendances Python
- [x] `Dockerfile` - Configuration Docker
- [x] `.dockerignore` - Optimisation build
- [x] `.gitignore` - Protection fichiers sensibles
- [x] `README.md` - Documentation

### Configuration Locale
- [ ] `.env` créé avec `DISCORD_TOKEN`
- [ ] Bot testé localement (`python3 bot.py`)
- [ ] Bot fonctionne correctement
- [ ] Commande `/ping` testée

### Git & GitHub
- [ ] Projet initialisé avec `git init`
- [ ] Repository créé sur GitHub
- [ ] `.env` bien ignoré (vérifier avec `git status`)
- [ ] Code poussé sur GitHub :
  ```bash
  git add .
  git commit -m "Initial commit"
  git push origin main
  ```

---

## 🚂 Déploiement sur Railway

### 1. Compte Railway
- [ ] Compte créé sur https://railway.app
- [ ] GitHub connecté à Railway
- [ ] Email vérifié

### 2. Créer le Projet
- [ ] Clic sur "New Project"
- [ ] Sélectionné "Deploy from GitHub repo"
- [ ] Repository `Bot-discord` sélectionné
- [ ] Railway détecte le Dockerfile

### 3. Configuration
- [ ] Variable `DISCORD_TOKEN` ajoutée :
  - Aller dans Variables
  - New Variable
  - Nom: `DISCORD_TOKEN`
  - Valeur: Votre token complet
  - Save

### 4. Premier Déploiement
- [ ] Build lancé automatiquement
- [ ] Build réussi (✅ dans Deployments)
- [ ] Logs vérifiés :
  ```
  ✅ Base de données initialisée
  ✅ Cog chargé: moderation
  🤖 Bot connecté
  ```

### 5. Vérification Discord
- [ ] Bot en ligne (🟢) sur Discord
- [ ] Commande `/ping` fonctionne
- [ ] Commande `/help` fonctionne

---

## ⚙️ Configuration Post-Déploiement

### Limites et Budget
- [ ] Limite de dépenses configurée ($5)
  - Settings → Usage Limits
- [ ] Notifications email activées
  - Settings → Notifications

### Déploiement Automatique
- [ ] Auto-deploy activé (par défaut)
  - Settings → Auto Deploy → ON
- [ ] Test: Modifier code → Push → Vérifier redéploiement

---

## 🔍 Tests Finaux

### Commandes de Base
- [ ] `/ping` - Latence
- [ ] `/serverinfo` - Info serveur
- [ ] `/help` - Liste commandes

### Modération (avec permissions)
- [ ] `/clear 5` - Supprimer messages
- [ ] `/warn @user raison` - Avertir

### Système
- [ ] Bot reste en ligne
- [ ] Logs accessibles sur Railway
- [ ] Métriques visibles (CPU, RAM)

---

## 🐛 Dépannage

### Si le bot ne démarre pas :

1. **Vérifier les Logs Railway**
   - Deployments → Dernier déploiement → Logs
   - Chercher les erreurs

2. **Erreurs courantes :**

   **"Improper token has been passed"**
   - [ ] Token correct dans Variables
   - [ ] Pas d'espaces avant/après
   - [ ] Intents activés sur Discord

   **"Module not found"**
   - [ ] `requirements.txt` complet
   - [ ] Redéployer

   **"Database error"**
   - [ ] `aiosqlite` dans requirements
   - [ ] Permissions d'écriture OK

---

## 📊 Surveillance

### Quotidien
- [ ] Vérifier uptime sur Railway
- [ ] Bot toujours en ligne sur Discord

### Hebdomadaire
- [ ] Vérifier les logs pour erreurs
- [ ] Vérifier utilisation (Railway → Usage)

### Mensuel
- [ ] Vérifier le budget
- [ ] Mettre à jour dépendances si besoin

---

## 🎉 Succès !

Si toutes les cases sont cochées :
✅ Votre bot est déployé avec succès sur Railway !
✅ Il tourne 24/7 automatiquement
✅ Les mises à jour sont automatiques (git push)

---

## 📚 Ressources

- [Guide Détaillé Railway](./brain/guide_railway_deployment.md)
- [Documentation Railway](https://docs.railway.app)
- [Support Railway Discord](https://discord.gg/railway)
- [discord.py Docs](https://discordpy.readthedocs.io/)

---

## 💡 Prochaines Étapes

Maintenant que votre bot est en ligne :

1. **Ajoutez des fonctionnalités**
   - Modifiez le code localement
   - `git push` → Déploiement automatique

2. **Surveillez les performances**
   - Railway Dashboard → Metrics

3. **Invitez sur plus de serveurs**
   - Partagez le lien d'invitation

4. **Collectez des feedbacks**
   - Améliorez basé sur les retours

Bon développement ! 🚀
