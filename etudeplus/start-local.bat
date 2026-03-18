@echo off
REM ============================================
REM EtudePlus - Script de démarrage local Windows
REM ============================================

echo.
echo 🚀 Démarrage d'EtudePlus en local...
echo.

REM Vérifier Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker n'est pas installé
    echo Installez Docker Desktop: https://docs.docker.com/desktop/install/windows-install/
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose n'est pas installé
    exit /b 1
)

REM Créer le fichier .env s'il n'existe pas
if not exist .env (
    echo 📝 Création du fichier .env...
    (
        echo # Database
        echo POSTGRES_DB=schoolflow
        echo POSTGRES_USER=schoolflow
        echo POSTGRES_PASSWORD=schoolflow123
        echo.
        echo # Keycloak
        echo KEYCLOAK_DB=keycloak
        echo KEYCLOAK_DB_USER=keycloak
        echo KEYCLOAK_DB_PASSWORD=keycloak123
        echo KEYCLOAK_ADMIN_USER=admin
        echo KEYCLOAK_ADMIN_PASSWORD=admin123
        echo KEYCLOAK_REALM=schoolflow
        echo KEYCLOAK_CLIENT_ID=schoolflow-frontend
        echo.
        echo # MinIO
        echo MINIO_ROOT_USER=minioadmin
        echo MINIO_ROOT_PASSWORD=minioadmin123
        echo MINIO_BUCKET=schoolflow
        echo.
        echo # pgAdmin
        echo PGADMIN_EMAIL=admin@schoolflow.com
        echo PGADMIN_PASSWORD=admin123
        echo.
        echo # App
        echo SECRET_KEY=dev-secret-key-change-in-production-12345678
        echo DEBUG=True
        echo LOG_LEVEL=INFO
        echo.
        echo # Frontend
        echo VITE_API_URL=http://localhost:8000
        echo VITE_KEYCLOAK_URL=http://localhost:8080
    ) > .env
    echo ✅ Fichier .env créé
)

echo.
echo Choisissez le mode de démarrage:
echo 1) Services essentiels (Postgres, Redis, Backend, Frontend)
echo 2) Services complets (avec Keycloak, MinIO, pgAdmin)
echo 3) Infrastructure seulement (Postgres, Redis)
echo.
set /p choice="Votre choix [1-3]: "

if "%choice%"=="1" (
    echo 🐳 Démarrage des services essentiels...
    docker-compose up -d postgres redis api frontend
) else if "%choice%"=="2" (
    echo 🐳 Démarrage de tous les services...
    docker-compose up -d
) else if "%choice%"=="3" (
    echo 🐳 Démarrage de l'infrastructure...
    docker-compose up -d postgres redis
    echo.
    echo Pour démarrer le backend manuellement:
    echo   cd backend ^&^& pip install -r requirements.txt
    echo   uvicorn app.main:app --reload --port 8000
    echo.
    echo Pour démarrer le frontend manuellement:
    echo   npm install ^&^& npm run dev
) else (
    echo Choix invalide
    exit /b 1
)

echo.
echo ⏳ Attente du démarrage des services...
timeout /t 10 /nobreak >nul

echo.
echo 📊 État des services:
docker-compose ps

echo.
echo ✅ Démarrage terminé!
echo.
echo 🔗 URLs d'accès:
echo    Frontend:     http://localhost:3000
echo    Backend API:  http://localhost:8000
echo    API Docs:     http://localhost:8000/docs
echo    Keycloak:     http://localhost:8080 (admin/admin123)
echo    MinIO:        http://localhost:9001 (minioadmin/minioadmin123)
echo    pgAdmin:      http://localhost:5050 (admin@schoolflow.com/admin123)
echo.
echo 💡 Pour arrêter les services: docker-compose down
echo.

pause
