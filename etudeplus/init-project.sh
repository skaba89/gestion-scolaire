#!/bin/bash

# ============================================
# EtudePlus - Initialisation Complète
# Script de démarrage pour commercialisation
# ============================================

set -e

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       EtudePlus / SchoolFlow Pro - Initialisation          ║${NC}"
echo -e "${BLUE}║            Solution de Gestion Scolaire SaaS                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Vérifier les prérequis
echo -e "${YELLOW}📋 Vérification des prérequis...${NC}"

command -v docker &> /dev/null || { echo -e "${RED}❌ Docker n'est pas installé${NC}"; exit 1; }
command -v docker-compose &> /dev/null || { echo -e "${RED}❌ Docker Compose n'est pas installé${NC}"; exit 1; }
command -v node &> /dev/null || { echo -e "${RED}❌ Node.js n'est pas installé${NC}"; exit 1; }
command -v python3 &> /dev/null || { echo -e "${RED}❌ Python 3 n'est pas installé${NC}"; exit 1; }

echo -e "${GREEN}✅ Tous les prérequis sont installés${NC}"
echo ""

# Créer le fichier .env s'il n'existe pas
if [ ! -f .env ]; then
    echo -e "${YELLOW}📝 Création du fichier .env...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ Fichier .env créé${NC}"
fi

# Demander le mode de démarrage
echo ""
echo "Choisissez le mode de démarrage:"
echo "  1) 🚀 Démarrage rapide (infrastructure + frontend local)"
echo "  2) 🐳 Docker complet (tous les services en containers)"
echo "  3) 🔧 Développement (infrastructure seulement, code local)"
echo "  4) 🏭 Production (build et déploiement)"
echo ""
read -p "Votre choix [1-4]: " choice

case $choice in
    1)
        echo -e "${GREEN}🚀 Démarrage rapide...${NC}"
        
        # Démarrer l'infrastructure
        echo -e "${YELLOW}🐳 Démarrage de l'infrastructure (PostgreSQL, Redis, Keycloak)...${NC}"
        docker-compose up -d postgres redis keycloak-db keycloak minio
        
        echo -e "${YELLOW}⏳ Attente du démarrage des services (30s)...${NC}"
        sleep 30
        
        # Initialiser la base de données
        echo -e "${YELLOW}📊 Initialisation de la base de données...${NC}"
        cd backend
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        source venv/bin/activate
        pip install -q -r requirements.txt
        alembic upgrade head || echo "Migrations déjà appliquées"
        cd ..
        
        # Démarrer le backend
        echo -e "${YELLOW}🔧 Démarrage du backend...${NC}"
        cd backend
        source venv/bin/activate
        uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
        BACKEND_PID=$!
        cd ..
        
        # Installer les dépendances frontend
        echo -e "${YELLOW}📦 Installation des dépendances frontend...${NC}"
        npm install --legacy-peer-deps
        
        # Démarrer le frontend
        echo -e "${YELLOW}🎨 Démarrage du frontend...${NC}"
        npm run dev &
        FRONTEND_PID=$!
        
        echo ""
        echo -e "${GREEN}✅ Démarrage rapide terminé!${NC}"
        echo ""
        echo -e "${BLUE}🔗 URLs d'accès:${NC}"
        echo "   Frontend:     http://localhost:5173"
        echo "   Backend API:  http://localhost:8000"
        echo "   API Docs:     http://localhost:8000/docs"
        echo "   Keycloak:     http://localhost:8080 (admin/admin123)"
        echo ""
        echo -e "${YELLOW}💡 Identifiants de test:${NC}"
        echo "   Super Admin:  admin@schoolflow.pro / admin123"
        echo "   Demo User:    demo@schoolflow.pro / demo123"
        echo ""
        echo "Appuyez sur Ctrl+C pour arrêter les services..."
        wait $BACKEND_PID $FRONTEND_PID
        ;;
        
    2)
        echo -e "${GREEN}🐳 Démarrage Docker complet...${NC}"
        docker-compose up -d
        
        echo -e "${YELLOW}⏳ Attente du démarrage des services (45s)...${NC}"
        sleep 45
        
        # Exécuter les migrations
        echo -e "${YELLOW}📊 Exécution des migrations...${NC}"
        docker-compose exec api alembic upgrade head || echo "Migrations déjà appliquées"
        
        echo ""
        echo -e "${GREEN}✅ Tous les services sont démarrés!${NC}"
        echo ""
        docker-compose ps
        ;;
        
    3)
        echo -e "${GREEN}🔧 Mode développement...${NC}"
        
        # Démarrer l'infrastructure seulement
        echo -e "${YELLOW}🐳 Démarrage de l'infrastructure...${NC}"
        docker-compose up -d postgres redis keycloak-db keycloak minio
        
        echo -e "${YELLOW}⏳ Attente du démarrage (30s)...${NC}"
        sleep 30
        
        echo ""
        echo -e "${GREEN}✅ Infrastructure prête!${NC}"
        echo ""
        echo -e "${BLUE}Pour démarrer le backend:${NC}"
        echo "  cd backend && source venv/bin/activate"
        echo "  pip install -r requirements.txt"
        echo "  alembic upgrade head"
        echo "  uvicorn app.main:app --reload --port 8000"
        echo ""
        echo -e "${BLUE}Pour démarrer le frontend:${NC}"
        echo "  npm install --legacy-peer-deps"
        echo "  npm run dev"
        ;;
        
    4)
        echo -e "${GREEN}🏭 Mode production...${NC}"
        
        # Build frontend
        echo -e "${YELLOW}📦 Build du frontend...${NC}"
        npm install --legacy-peer-deps
        npm run build
        
        # Build Docker images
        echo -e "${YELLOW}🐳 Build des images Docker...${NC}"
        docker-compose build
        
        echo -e "${GREEN}✅ Build terminé!${NC}"
        echo ""
        echo "Pour déployer sur Render:"
        echo "  1. Connectez votre repo GitHub à Render"
        echo "  2. Sélectionnez 'Blueprint' dans Render"
        echo "  3. Configurez les variables d'environnement"
        echo ""
        echo "Variables d'environnement requises pour la production:"
        echo "  - SECRET_KEY (générez avec: openssl rand -hex 32)"
        echo "  - DATABASE_URL"
        echo "  - REDIS_URL"
        echo "  - KEYCLOAK_*"
        ;;
        
    *)
        echo -e "${RED}Choix invalide${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}           EtudePlus est prêt à être utilisé!              ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
