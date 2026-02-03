#!/bin/bash

# Script pour lancer le bot Discord avec auto-redémarrage en cas de crash
# Usage: ./start_bot.sh

# Configuration
BOT_DIR="$HOME/OneDrive - Epitech/Documents/Bot-discord"
LOG_FILE="$BOT_DIR/auto_restart.log"

# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Bot Discord - Auto-Restart Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Vérifier que le dossier existe
if [ ! -d "$BOT_DIR" ]; then
    echo -e "${RED}❌ Erreur: Dossier du bot introuvable${NC}"
    echo -e "${RED}   Chemin: $BOT_DIR${NC}"
    exit 1
fi

# Aller dans le dossier du bot
cd "$BOT_DIR" || exit 1

# Vérifier que l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Environnement virtuel introuvable${NC}"
    echo -e "${YELLOW}   Création de l'environnement virtuel...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${YELLOW}   Installation des dépendances...${NC}"
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Vérifier que le fichier .env existe
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Erreur: Fichier .env introuvable${NC}"
    echo -e "${RED}   Créez le fichier .env avec votre DISCORD_TOKEN${NC}"
    exit 1
fi

# Fonction pour nettoyer à la sortie
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Arrêt du script demandé${NC}"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Script arrêté par l'utilisateur" >> "$LOG_FILE"
    exit 0
}

# Capturer Ctrl+C
trap cleanup SIGINT SIGTERM

# Initialiser le compteur de redémarrages
RESTART_COUNT=0
START_TIME=$(date +%s)

echo -e "${GREEN}✅ Configuration OK${NC}"
echo -e "${GREEN}📁 Dossier: $BOT_DIR${NC}"
echo -e "${GREEN}📝 Logs: $LOG_FILE${NC}"
echo ""
echo -e "${YELLOW}Appuyez sur Ctrl+C pour arrêter le bot${NC}"
echo ""

# Boucle infinie pour redémarrer le bot
while true; do
    echo "========================================"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Démarrage du bot (redémarrage #$RESTART_COUNT)"
    echo "========================================"
    
    # Logger le démarrage
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Démarrage du bot (redémarrage #$RESTART_COUNT)" >> "$LOG_FILE"
    
    # Lancer le bot
    python3 bot.py
    
    # Capturer le code de sortie
    EXIT_CODE=$?
    
    # Logger l'arrêt
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Bot arrêté (code: $EXIT_CODE)" >> "$LOG_FILE"
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✅ Bot arrêté normalement${NC}"
    else
        echo -e "${RED}❌ Bot arrêté avec une erreur (code: $EXIT_CODE)${NC}"
    fi
    
    # Incrémenter le compteur
    RESTART_COUNT=$((RESTART_COUNT + 1))
    
    # Vérifier si trop de redémarrages rapides (protection anti-crash loop)
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    
    if [ $RESTART_COUNT -ge 5 ] && [ $ELAPSED -lt 60 ]; then
        echo -e "${RED}⚠️  ATTENTION: Trop de redémarrages en peu de temps !${NC}"
        echo -e "${RED}   Le bot crash probablement. Vérifiez les logs.${NC}"
        echo -e "${YELLOW}   Pause de 60 secondes...${NC}"
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Trop de redémarrages, pause de 60s" >> "$LOG_FILE"
        sleep 60
        RESTART_COUNT=0
        START_TIME=$(date +%s)
    else
        echo -e "${YELLOW}⏳ Redémarrage dans 5 secondes...${NC}"
        sleep 5
    fi
    
    echo ""
done
