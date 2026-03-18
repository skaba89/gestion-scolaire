# Guide de Déploiement Gratuit - EtudePlus

Ce guide vous explique comment déployer EtudePlus sur différentes plateformes gratuites pour effectuer des tests en production.

## 📊 Comparatif des Plateformes Gratuites

| Plateforme | RAM | CPU | Base de données | Storage | Avantages |
|------------|-----|-----|-----------------|---------|-----------|
| **Render** | 512MB | 0.1 CPU | PostgreSQL 90 jours | - | Le plus simple, 750h/mois |
| **Railway** | 512MB | 0.5 CPU | PostgreSQL + Redis | 1GB | $5 crédit/mois |
| **Fly.io** | 256MB | 1 vCPU | PostgreSQL 3GB | 3GB | Multi-région |
| **Vercel + Supabase** | - | - | PostgreSQL 500MB | 1GB | Frontend optimisé |
| **Oracle Cloud** | 24GB ARM | 4 OCPU | Autonome | 200GB | Plus puissant, setup complexe |

---

## 🚀 Option 1: Render.com (Recommandé)

### Pourquoi Render ?
- **Gratuit 750 heures/mois** (assez pour 1 service continu)
- Configuration la plus simple
- PostgreSQL gratuit pendant 90 jours
- SSL automatique

### Étapes de déploiement

#### 1. Préparer le repository

```bash
# Assurez-vous que votre code est sur GitHub
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

#### 2. Créer un compte Render
Allez sur [render.com](https://render.com) et créez un compte (connexion GitHub recommandée).

#### 3. Créer la base de données PostgreSQL

1. Dashboard → **New +** → **PostgreSQL**
2. Configuration:
   - Name: `etudeplus-db`
   - Region: Frankfurt (ou le plus proche)
   - PostgreSQL Version: 15
   - Plan: **Free**
3. Cliquez **Create Database**
4. Notez l'URL de connexion (DATABASE_URL)

#### 4. Créer Redis (optionnel mais recommandé)

1. **New +** → **Redis**
2. Configuration:
   - Name: `etudeplus-redis`
   - Plan: **Free**
3. Cliquez **Create Redis Instance**

#### 5. Déployer le Backend

1. **New +** → **Web Service**
2. Connectez votre repo GitHub
3. Configuration:
   - Name: `etudeplus-api`
   - Region: Même que la DB
   - Branch: `main`
   - Root Directory: `backend`
   - Runtime: **Docker**
   - Dockerfile Path: `./Dockerfile.backend`
   - Plan: **Free**

4. Variables d'environnement (cliquez **Advanced** → **Add Environment Variable**):

```
DATABASE_URL=${etudeplus-db.DATABASE_URL}
REDIS_URL=${etudeplus-redis.DATABASE_URL}
SECRET_KEY=<générez avec: openssl rand -hex 32>
DEBUG=False
LOG_LEVEL=INFO
KEYCLOAK_URL=https://votre-keycloak.com
KEYCLOAK_REALM=schoolflow
KEYCLOAK_CLIENT_ID=schoolflow-backend
KEYCLOAK_CLIENT_SECRET=<votre-secret>
CORS_ORIGINS=https://votre-frontend.onrender.com
```

#### 6. Déployer le Frontend

1. **New +** → **Static Site**
2. Configuration:
   - Name: `etudeplus-frontend`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`
   
3. Variables d'environnement:
```
VITE_API_URL=https://etudeplus-api.onrender.com/api/v1
VITE_KEYCLOAK_URL=https://votre-keycloak.com
VITE_KEYCLOAK_REALM=schoolflow
VITE_KEYCLOAK_CLIENT_ID=schoolflow-frontend
```

### URLs finales
- Frontend: `https://etudeplus-frontend.onrender.com`
- Backend: `https://etudeplus-api.onrender.com`

---

## 🚂 Option 2: Railway.app

### Pourquoi Railway ?
- $5 de crédit gratuit chaque mois
- Interface CLI pratique
- Logs en temps réel
- Déploiement très rapide

### Installation

```bash
# Installer CLI
npm install -g @railway/cli

# Se connecter
railway login

# Initialiser le projet
railway init

# Ajouter PostgreSQL
railway add --database postgres

# Ajouter Redis
railway add --database redis

# Déployer
railway up

# Configurer les variables
railway variables set SECRET_KEY=$(openssl rand -hex 32)
railway variables set DEBUG=False

# Obtenir l'URL
railway domain
```

---

## ✈️ Option 3: Fly.io

### Pourquoi Fly.io ?
- Multi-région
- Edge caching
- Très bonnes performances
- 3 VMs gratuites

### Installation

```bash
# Installer flyctl
curl -L https://fly.io/install.sh | sh

# Se connecter
fly auth login

# Lancer la configuration
fly launch

# Configurer PostgreSQL
fly postgres create
fly postgres attach

# Déployer
fly deploy

# Voir les logs
fly logs
```

### Configuration fly.toml

Le fichier `fly.toml` est déjà configuré dans le projet.

---

## 🟢 Option 4: Vercel + Supabase

### Pourquoi cette option ?
- Frontend Vercel optimisé pour React
- Supabase offre une base de données PostgreSQL gérée
- Authentification intégrée avec Supabase Auth

### Setup Supabase

1. Allez sur [supabase.com](https://supabase.com)
2. Créez un nouveau projet
3. Notez les credentials:
   - Project URL
   - Anon Key
   - Service Role Key

4. Exécutez les migrations SQL dans l'éditeur SQL

### Déployer sur Vercel

```bash
# Installer CLI
npm i -g vercel

# Déployer
vercel --prod

# Ou connectez votre repo GitHub via vercel.com
```

### Variables d'environnement Vercel

```
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_API_URL=https://your-backend-url.com/api/v1
```

---

## ☁️ Option 5: Oracle Cloud (Always Free)

### Pourquoi Oracle Cloud ?
- Ressources les plus généreuses (24GB RAM ARM)
- 10TB de transfert/mois
- Vraiment gratuit "toujours"

### Setup

1. Créez un compte sur [cloud.oracle.com](https://cloud.oracle.com)
2. Créez une VM:
   - Shape: `VM.Standard.E2.1.Micro` ou `VM.Standard.A1.Flex` (ARM)
   - OS: Ubuntu 22.04
   - Ajoutez votre clé SSH

3. Connectez-vous:
```bash
ssh ubuntu@<votre-ip-publique>
```

4. Installation:
```bash
# Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu

# Docker Compose
sudo apt install docker-compose-plugin -y

# Cloner le projet
git clone https://github.com/votre-repo/etudeplus.git
cd etudeplus

# Configuration
cp .env.example .env
nano .env  # Éditez les variables

# Lancer
docker compose up -d
```

5. Ouvrir les ports dans Oracle:
   - Compute → Instance → VNIC → Security Lists
   - Ajoutez des règles ingress pour ports 80, 443, 8000

---

## ⚠️ Limites du Tier Gratuit

| Problème | Solution |
|----------|----------|
| **Cold starts** (Render/Railway) | Utilisez un service Uptime (UptimeRobot) |
| **Base de données limitée** | Optimisez les requêtes, nettoyez les logs |
| **Pas de Keycloak gratuit** | Utilisez Supabase Auth, Auth0 gratuit, ou Keycloak sur Oracle Cloud |
| **CORS errors** | Configurez correctement les origines autorisées |

---

## 🔧 Configuration Post-Déploiement

### 1. Vérifier la santé

```bash
# Backend
curl https://votre-api.onrender.com/health/

# Database connection
curl https://votre-api.onrender.com/api/v1/health/database
```

### 2. Configurer Keycloak

Option A - Utiliser une instance gérée:
- [Keycloak Cloud](https://www.keycloak.org/downloads) 
- [Auth0](https://auth0.com) (gratuit 7000 utilisateurs)
- [Supabase Auth](https://supabase.com/auth)

Option B - Déployer Keycloak:

```yaml
# Ajouter à docker-compose.yml
keycloak:
  image: quay.io/keycloak/keycloak:latest
  environment:
    KEYCLOAK_ADMIN: admin
    KEYCLOAK_ADMIN_PASSWORD: admin
  command: start-dev
  ports:
    - "8080:8080"
```

### 3. Configurer les Webhooks

```bash
# Stripe webhooks
stripe listen --forward-to https://votre-api.onrender.com/api/v1/webhooks/stripe
```

### 4. Monitoring

Utilisez les dashboards intégrés ou configurez:
- [Sentry](https://sentry.io) (gratuit pour les petits projets)
- [Grafana Cloud](https://grafana.com) (free tier disponible)

---

## 📱 Optimisations pour la Production

### Backend

```python
# Activer la compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Optimiser les requêtes DB
QUERY_TIMEOUT = 30  # secondes
POOL_SIZE = 5  # Réduire pour le free tier

# Activer le cache
CACHE_TTL = 300  # 5 minutes
```

### Frontend

```javascript
// vite.config.ts - Optimisations
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        vendor: ['react', 'react-dom'],
        ui: ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu']
      }
    }
  }
}
```

---

## 🆘 Dépannage

### Erreur: "Database connection failed"
```bash
# Vérifier l'URL de connexion
echo $DATABASE_URL

# Tester la connexion
psql $DATABASE_URL -c "SELECT 1"
```

### Erreur: "Memory limit exceeded"
```bash
# Réduire la consommation
# Dans gunicorn.conf.py
workers = 1
threads = 2
worker_class = "sync"
max_requests = 1000
```

### Erreur: "CORS blocked"
```bash
# Vérifier CORS_ORIGINS dans .env
CORS_ORIGINS=https://votre-frontend.vercel.app,https://votre-frontend.onrender.com
```

---

## 📚 Ressources

- [Render Documentation](https://render.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [Fly.io Documentation](https://fly.io/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)

---

## 💰 Coûts estimés (si vous dépassez le gratuit)

| Service | Plan Payant | Prix/mois |
|---------|-------------|-----------|
| Render Starter | 512MB RAM | $7 |
| Railway | 1GB RAM | $5-10 |
| Fly.io | 1GB RAM | $3-5 |
| Supabase Pro | 8GB DB | $25 |
| Keycloak Cloud | Standard | $50+ |

**Recommandation**: Commencez avec Render gratuit, puis migrez vers Railway ou Fly.io si vous avez besoin de plus de ressources.
