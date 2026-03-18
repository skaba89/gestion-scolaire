#!/bin/bash

# ============================================
# EtudePlus - Script de démarrage local
# ============================================

set -e

echo "🚀 Démarrage d'EtudePlus en local..."
echo ""

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas installé${NC}"
    echo "Installez Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose n'est pas installé${NC}"
    echo "Installez Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Créer le fichier .env s'il n'existe pas
if [ ! -f .env ]; then
    echo -e "${YELLOW}📝 Création du fichier .env...${NC}"
    cat > .env << 'EOF'
# Database
POSTGRES_DB=schoolflow
POSTGRES_USER=schoolflow
POSTGRES_PASSWORD=schoolflow123

# Keycloak
KEYCLOAK_DB=keycloak
KEYCLOAK_DB_USER=keycloak
KEYCLOAK_DB_PASSWORD=keycloak123
KEYCLOAK_ADMIN_USER=admin
KEYCLOAK_ADMIN_PASSWORD=admin123
KEYCLOAK_REALM=schoolflow
KEYCLOAK_CLIENT_ID=schoolflow-frontend

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123
MINIO_BUCKET=schoolflow

# pgAdmin
PGADMIN_EMAIL=admin@schoolflow.com
PGADMIN_PASSWORD=admin123

# App
SECRET_KEY=dev-secret-key-change-in-production-12345678
DEBUG=True
LOG_LEVEL=INFO

# Frontend
VITE_API_URL=http://localhost:8000
VITE_KEYCLOAK_URL=http://localhost:8080
EOF
    echo -e "${GREEN}✅ Fichier .env créé${NC}"
fi

# Vérifier si les conteneurs sont déjà en cours
if docker-compose ps | grep -q "Up"; then
    echo -e "${YELLOW}⚠️  Des conteneurs sont déjà en cours d'exécution${NC}"
    echo "Voulez-vous les redémarrer? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo -e "${YELLOW}🛑 Arrêt des conteneurs...${NC}"
        docker-compose down
    else
        echo "Utilisation des conteneurs existants..."
    fi
fi

# Démarrer les services
echo -e "${GREEN}🐳 Démarrage des services Docker...${NC}"
echo ""

# Option 1: Tous les services (recommandé pour première fois)
echo "Choisissez le mode de démarrage:"
echo "1) Services essentiels (Postgres, Redis, Backend, Frontend)"
echo "2) Services complets (avec Keycloak, MinIO, pgAdmin)"
echo "3) Infrastructure seulement (Postgres, Redis)"
read -p "Votre choix [1-3]: " choice

case $choice in
    1)
        echo -e "${GREEN}Démarrage des services essentiels...${NC}"
        docker-compose up -d postgres redis api frontend
        ;;
    2)
        echo -e "${GREEN}Démarrage de tous les services...${NC}"
        docker-compose up -d
        ;;
    3)
        echo -e "${GREEN}Démarrage de l'infrastructure...${NC}"
        docker-compose up -d postgres redis
        echo ""
        echo -e "${YELLOW}Pour démarrer le backend manuellement:${NC}"
        echo "  cd backend && pip install -r requirements.txt"
        echo "  uvicorn app.main:app --reload --port 8000"
        echo ""
        echo -e "${YELLOW}Pour démarrer le frontend manuellement:${NC}"
        echo "  npm install && npm run dev"
        ;;
    *)
        echo -e "${RED}Choix invalide${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}⏳ Attente du démarrage des services...${NC}"
sleep 10

# Vérifier l'état des services
echo ""
echo -e "${GREEN}📊 État des services:${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}✅ Démarrage terminé!${NC}"
echo ""
echo "🔗 URLs d'accès:"
echo "   Frontend:     http://localhost:3000"
echo "   Backend API:  http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   Keycloak:     http://localhost:8080 (admin/admin123)"
echo "   MinIO:        http://localhost:9001 (minioadmin/minioadmin123)"
echo "   pgAdmin:      http://localhost:5050 (admin@schoolflow.com/admin123)"
echo ""
echo -e "${YELLOW}💡 Pour arrêter les services: docker-compose down${NC}"
echo ""
