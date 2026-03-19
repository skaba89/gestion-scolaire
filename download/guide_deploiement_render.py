#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guide de Déploiement EtudePlus sur Render et Alternatives Gratuites
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image, ListFlowable, ListItem
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
import os

# Register fonts
pdfmetrics.registerFont(TTFont('SimHei', '/usr/share/fonts/truetype/chinese/SimHei.ttf'))
pdfmetrics.registerFont(TTFont('Microsoft YaHei', '/usr/share/fonts/truetype/chinese/msyh.ttf'))
pdfmetrics.registerFont(TTFont('Times New Roman', '/usr/share/fonts/truetype/english/Times-New-Roman.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'))

# Register font families
registerFontFamily('Microsoft YaHei', normal='Microsoft YaHei', bold='Microsoft YaHei')
registerFontFamily('SimHei', normal='SimHei', bold='SimHei')
registerFontFamily('Times New Roman', normal='Times New Roman', bold='Times New Roman')

def create_deployment_guide():
    # Document setup
    doc = SimpleDocTemplate(
        "/home/z/my-project/download/EtudePlus_Guide_Deploiement_Render.pdf",
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
        title="EtudePlus_Guide_Deploiement_Render",
        author='Z.ai',
        creator='Z.ai',
        subject='Guide de déploiement EtudePlus sur Render et alternatives gratuites'
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Title styles
    title_style = ParagraphStyle(
        'CoverTitle',
        fontName='Microsoft YaHei',
        fontSize=36,
        leading=44,
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        fontName='SimHei',
        fontSize=18,
        leading=26,
        alignment=TA_CENTER,
        spaceAfter=40
    )
    
    # Heading styles
    h1_style = ParagraphStyle(
        'H1',
        fontName='Microsoft YaHei',
        fontSize=20,
        leading=28,
        alignment=TA_LEFT,
        spaceBefore=24,
        spaceAfter=12,
        textColor=colors.HexColor('#1F4E79')
    )
    
    h2_style = ParagraphStyle(
        'H2',
        fontName='Microsoft YaHei',
        fontSize=16,
        leading=22,
        alignment=TA_LEFT,
        spaceBefore=18,
        spaceAfter=8,
        textColor=colors.HexColor('#2E75B6')
    )
    
    h3_style = ParagraphStyle(
        'H3',
        fontName='SimHei',
        fontSize=13,
        leading=18,
        alignment=TA_LEFT,
        spaceBefore=12,
        spaceAfter=6,
        textColor=colors.HexColor('#404040')
    )
    
    # Body styles
    body_style = ParagraphStyle(
        'Body',
        fontName='SimHei',
        fontSize=11,
        leading=18,
        alignment=TA_LEFT,
        spaceAfter=8,
        wordWrap='CJK'
    )
    
    body_en_style = ParagraphStyle(
        'BodyEN',
        fontName='Times New Roman',
        fontSize=11,
        leading=18,
        alignment=TA_LEFT,
        spaceAfter=8
    )
    
    code_style = ParagraphStyle(
        'Code',
        fontName='DejaVuSans',
        fontSize=9,
        leading=12,
        alignment=TA_LEFT,
        backColor=colors.HexColor('#F5F5F5'),
        leftIndent=10,
        rightIndent=10,
        spaceBefore=6,
        spaceAfter=6
    )
    
    # Table styles
    header_style = ParagraphStyle(
        'TableHeader',
        fontName='Microsoft YaHei',
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.white
    )
    
    cell_style = ParagraphStyle(
        'TableCell',
        fontName='SimHei',
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        wordWrap='CJK'
    )
    
    cell_left_style = ParagraphStyle(
        'TableCellLeft',
        fontName='SimHei',
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        wordWrap='CJK'
    )
    
    story = []
    
    # === COVER PAGE ===
    story.append(Spacer(1, 120))
    story.append(Paragraph("<b>EtudePlus</b>", title_style))
    story.append(Paragraph("Guide de Déploiement", subtitle_style))
    story.append(Spacer(1, 40))
    story.append(Paragraph("Render & Alternatives Gratuites", subtitle_style))
    story.append(Spacer(1, 80))
    story.append(Paragraph("Version 1.0", ParagraphStyle('Date', fontName='SimHei', fontSize=14, alignment=TA_CENTER)))
    story.append(PageBreak())
    
    # === TABLE OF CONTENTS ===
    story.append(Paragraph("<b>Table des Matières</b>", h1_style))
    story.append(Spacer(1, 12))
    
    toc_items = [
        ("1. Introduction", "Architecture de déploiement dynamique"),
        ("2. Déploiement sur Render", "Guide complet pour le plan gratuit"),
        ("3. Configuration des Services", "Base de données, Redis, Keycloak"),
        ("4. Alternatives Gratuites", "Railway, Fly.io, et autres options"),
        ("5. Checklist de Déploiement", "Liste de vérification complète"),
        ("6. Dépannage", "Solutions aux problèmes courants")
    ]
    
    for title, desc in toc_items:
        story.append(Paragraph(f"<b>{title}</b> - {desc}", body_style))
    
    story.append(PageBreak())
    
    # === SECTION 1: INTRODUCTION ===
    story.append(Paragraph("<b>1. Introduction</b>", h1_style))
    story.append(Spacer(1, 12))
    
    intro_text = """Ce guide vous accompagne dans le déploiement de l'application EtudePlus sur des plateformes d'hébergement gratuites. Contrairement à un déploiement statique, cette architecture <b>dynamique</b> permet de servir l'application React et l'API FastAPI depuis un seul service web, offrant ainsi une meilleure flexibilité et une gestion simplifiée."""
    story.append(Paragraph(intro_text, body_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>1.1 Architecture de Déploiement</b>", h2_style))
    
    arch_text = """L'architecture de déploiement repose sur un conteneur Docker unifié qui intègre à la fois le frontend React (compilé en fichiers statiques) et le backend FastAPI. Le backend FastAPI sert les fichiers statiques du frontend pour toutes les routes non-API, tandis que les requêtes vers <font name='DejaVuSans'>/api/v1/*</font> sont traitées par l'API. Cette approche permet d'avoir une application monolithique déployable sur un seul service web gratuit, tout en conservant la séparation des préoccupations entre le frontend et le backend."""
    story.append(Paragraph(arch_text, body_style))
    story.append(Spacer(1, 12))
    
    # Architecture table
    arch_data = [
        [Paragraph('<b>Composant</b>', header_style), Paragraph('<b>Technologie</b>', header_style), Paragraph('<b>Rôle</b>', header_style)],
        [Paragraph('Frontend', cell_style), Paragraph('React + Vite', cell_style), Paragraph('Interface utilisateur servie par FastAPI', cell_left_style)],
        [Paragraph('Backend', cell_style), Paragraph('FastAPI + Uvicorn', cell_style), Paragraph('API REST et serveur de fichiers statiques', cell_left_style)],
        [Paragraph('Base de données', cell_style), Paragraph('PostgreSQL 15', cell_style), Paragraph('Stockage persistant des données', cell_left_style)],
        [Paragraph('Cache', cell_style), Paragraph('Redis', cell_style), Paragraph('Cache et limitation de débit', cell_left_style)],
        [Paragraph('Authentification', cell_style), Paragraph('Keycloak', cell_style), Paragraph('Gestion des identités (externe)', cell_left_style)],
        [Paragraph('Stockage fichiers', cell_style), Paragraph('MinIO / S3', cell_style), Paragraph('Stockage des documents et images', cell_left_style)]
    ]
    
    arch_table = Table(arch_data, colWidths=[3.5*cm, 4*cm, 8*cm])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E79')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 18))
    
    # === SECTION 2: RENDER DEPLOYMENT ===
    story.append(Paragraph("<b>2. Déploiement sur Render</b>", h1_style))
    story.append(Spacer(1, 12))
    
    render_intro = """Render est une plateforme cloud moderne qui offre un plan gratuit généreux pour les applications web. Le plan gratuit inclut 750 heures par mois pour les services web, une base de données PostgreSQL de 1 Go (expire après 90 jours), et un cache Redis de 25 Mo. Cette section vous guide pas à pas dans le déploiement de votre application."""
    story.append(Paragraph(render_intro, body_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>2.1 Prérequis</b>", h2_style))
    
    prereq_text = """Avant de commencer le déploiement, assurez-vous de disposer des éléments suivants. Un compte GitHub avec votre dépôt EtudePlus configuré est essentiel, car Render se connecte directement à votre dépôt pour le déploiement continu. Vous aurez également besoin d'un compte Render créé sur render.com, ainsi que des clés et configurations pour vos services externes comme Keycloak (que vous pouvez héberger séparément ou utiliser via un fournisseur d'identité comme Auth0)."""
    story.append(Paragraph(prereq_text, body_style))
    story.append(Spacer(1, 8))
    
    prereq_list = [
        "Un compte GitHub avec le code source d'EtudePlus",
        "Un compte Render (render.com)",
        "Une instance Keycloak fonctionnelle (ou Auth0)",
        "Un bucket S3 ou MinIO pour le stockage de fichiers"
    ]
    for item in prereq_list:
        story.append(Paragraph(f"• {item}", body_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>2.2 Étapes de Déploiement</b>", h2_style))
    
    step1_text = """<b>Étape 1 : Créer le compte Render</b> - Rendez-vous sur render.com et créez un compte gratuit. Vous pouvez vous inscrire avec votre compte GitHub pour faciliter la connexion avec votre dépôt. Une fois connecté, vous accéderez au tableau de bord Render où vous pourrez créer de nouveaux services."""
    story.append(Paragraph(step1_text, body_style))
    story.append(Spacer(1, 8))
    
    step2_text = """<b>Étape 2 : Créer la base de données PostgreSQL</b> - Depuis le tableau de bord, cliquez sur 'New' puis 'PostgreSQL'. Choisissez le nom 'etudeplus-db', sélectionnez la région 'Frankfurt' (ou la plus proche de vos utilisateurs), et choisissez le plan 'Free'. Render créera automatiquement la base de données et générera les variables de connexion que vous utiliserez plus tard."""
    story.append(Paragraph(step2_text, body_style))
    story.append(Spacer(1, 8))
    
    step3_text = """<b>Étape 3 : Créer le service Redis</b> - De même, créez un service Redis en cliquant sur 'New' puis 'Redis'. Nommez-le 'etudeplus-redis', choisissez la même région que votre base de données, et sélectionnez le plan 'Free'. Ce service sera utilisé pour le cache et la limitation de débit de l'application."""
    story.append(Paragraph(step3_text, body_style))
    story.append(Spacer(1, 8))
    
    step4_text = """<b>Étape 4 : Créer le service Web principal</b> - Cliquez sur 'New' puis 'Web Service'. Connectez votre dépôt GitHub et sélectionnez le dépôt EtudePlus. Configurez le service avec le nom 'etudeplus', l'environnement 'Docker', et le fichier Dockerfile 'Dockerfile.render'. Sélectionnez le plan 'Free' et la même région que vos autres services."""
    story.append(Paragraph(step4_text, body_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>2.3 Configuration des Variables d'Environnement</b>", h2_style))
    
    env_text = """Les variables d'environnement suivantes doivent être configurées dans le service Web Render. Certaines sont automatiquement liées aux services créés (DATABASE_URL, REDIS_URL), tandis que d'autres doivent être définies manuellement. Voici la liste complète des variables nécessaires avec leurs descriptions et valeurs recommandées."""
    story.append(Paragraph(env_text, body_style))
    story.append(Spacer(1, 12))
    
    # Environment variables table
    env_data = [
        [Paragraph('<b>Variable</b>', header_style), Paragraph('<b>Description</b>', header_style), Paragraph('<b>Valeur</b>', header_style)],
        [Paragraph('DATABASE_URL', cell_style), Paragraph('URL de connexion PostgreSQL', cell_left_style), Paragraph('Auto-généré', cell_style)],
        [Paragraph('REDIS_URL', cell_style), Paragraph('URL de connexion Redis', cell_left_style), Paragraph('Auto-généré', cell_style)],
        [Paragraph('SECRET_KEY', cell_style), Paragraph('Clé secrète pour JWT', cell_left_style), Paragraph('openssl rand -hex 32', cell_style)],
        [Paragraph('DEBUG', cell_style), Paragraph('Mode débogage', cell_left_style), Paragraph('False', cell_style)],
        [Paragraph('SERVE_FRONTEND', cell_style), Paragraph('Servir le frontend React', cell_left_style), Paragraph('true', cell_style)],
        [Paragraph('KEYCLOAK_URL', cell_style), Paragraph('URL du serveur Keycloak', cell_left_style), Paragraph('https://votre-keycloak.com', cell_style)],
        [Paragraph('KEYCLOAK_REALM', cell_style), Paragraph('Realm Keycloak', cell_left_style), Paragraph('schoolflow', cell_style)],
        [Paragraph('KEYCLOAK_CLIENT_ID', cell_style), Paragraph('ID client backend', cell_left_style), Paragraph('schoolflow-backend', cell_style)],
        [Paragraph('KEYCLOAK_CLIENT_SECRET', cell_style), Paragraph('Secret client Keycloak', cell_left_style), Paragraph('(définir manuellement)', cell_style)],
        [Paragraph('MINIO_ENDPOINT', cell_style), Paragraph('Endpoint S3/MinIO', cell_left_style), Paragraph('s3.region.amazonaws.com', cell_style)],
        [Paragraph('MINIO_ACCESS_KEY', cell_style), Paragraph('Clé d\'accès S3', cell_left_style), Paragraph('(définir manuellement)', cell_style)],
        [Paragraph('MINIO_SECRET_KEY', cell_style), Paragraph('Clé secrète S3', cell_left_style), Paragraph('(définir manuellement)', cell_style)]
    ]
    
    env_table = Table(env_data, colWidths=[4*cm, 6*cm, 5.5*cm])
    env_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E79')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
    ]))
    story.append(env_table)
    story.append(Spacer(1, 18))
    
    # === SECTION 3: SERVICES CONFIGURATION ===
    story.append(Paragraph("<b>3. Configuration des Services Externes</b>", h1_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>3.1 Keycloak (Authentification)</b>", h2_style))
    
    keycloak_text = """Keycloak est le serveur d'identité utilisé par EtudePlus pour l'authentification et l'autorisation. Pour un déploiement gratuit, vous avez plusieurs options. La première consiste à utiliser un fournisseur d'identité géré comme Auth0 qui offre un plan gratuit jusqu'à 7000 utilisateurs actifs. La deuxième option est de déployer Keycloak sur une autre plateforme comme Railway ou Fly.io qui offrent des crédits gratuits. La troisième option est d'utiliser Keycloak Cloud qui propose un essai gratuit. Quelle que soit l'option choisie, vous devez créer un realm 'schoolflow' et configurer deux clients : 'schoolflow-frontend' pour l'application React et 'schoolflow-backend' pour l'API."""
    story.append(Paragraph(keycloak_text, body_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>3.2 Stockage de Fichiers (MinIO / S3)</b>", h2_style))
    
    storage_text = """Pour le stockage des fichiers (documents, images, etc.), EtudePlus utilise un backend compatible S3. AWS S3 offre un plan gratuit de 5 Go de stockage pendant 12 mois pour les nouveaux comptes. Alternativement, vous pouvez utiliser Cloudflare R2 qui offre 10 Go gratuits sans frais de sortie, ou Render Object Storage qui s'intègre directement avec vos services Render mais nécessite un plan payant. Pour les besoins de test en production, AWS S3 ou Cloudflare R2 sont les options les plus économiques."""
    story.append(Paragraph(storage_text, body_style))
    story.append(Spacer(1, 18))
    
    # === SECTION 4: ALTERNATIVES ===
    story.append(Paragraph("<b>4. Alternatives Gratuites</b>", h1_style))
    story.append(Spacer(1, 12))
    
    alt_intro = """Outre Render, plusieurs autres plateformes offrent des plans gratuits ou des crédits d'essai pour le déploiement d'applications web. Cette section présente les alternatives les plus intéressantes avec leurs avantages et limites respectifs."""
    story.append(Paragraph(alt_intro, body_style))
    story.append(Spacer(1, 12))
    
    # Alternatives comparison table
    alt_data = [
        [Paragraph('<b>Plateforme</b>', header_style), Paragraph('<b>Offre Gratuite</b>', header_style), Paragraph('<b>Avantages</b>', header_style), Paragraph('<b>Limites</b>', header_style)],
        [Paragraph('Render', cell_style), Paragraph('750h/mois, 1Go DB', cell_left_style), Paragraph('Simple, intégré, SSL auto', cell_left_style), Paragraph('DB expire 90 jours, cold start', cell_left_style)],
        [Paragraph('Railway', cell_style), Paragraph('$5 crédit/mois', cell_left_style), Paragraph('Pas de cold start, flexible', cell_left_style), Paragraph('Crédit limité, CC requise', cell_left_style)],
        [Paragraph('Fly.io', cell_style), Paragraph('3 VMs, 3Go volume', cell_left_style), Paragraph('Global, performant', cell_left_style), Paragraph('CC requise, complexe', cell_left_style)],
        [Paragraph('Koyeb', cell_style), Paragraph('$5.50/mois', cell_left_style), Paragraph('Edge network, simple', cell_left_style), Paragraph('Pas de DB gratuite', cell_left_style)],
        [Paragraph('Northflank', cell_style), Paragraph('1 service gratuit', cell_left_style), Paragraph('CI/CD intégré', cell_left_style), Paragraph('Limites restrictives', cell_left_style)]
    ]
    
    alt_table = Table(alt_data, colWidths=[2.8*cm, 3.5*cm, 4.5*cm, 4.7*cm])
    alt_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E79')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
    ]))
    story.append(alt_table)
    story.append(Spacer(1, 18))
    
    story.append(Paragraph("<b>4.1 Railway</b>", h2_style))
    
    railway_text = """Railway offre 5$ de crédit mensuel gratuit pour les nouveaux utilisateurs, ce qui est suffisant pour héberger une petite application comme EtudePlus. La plateforme ne souffre pas de cold starts comme Render, ce qui signifie que votre application répond immédiatement aux requêtes même après une période d'inactivité. Railway propose également des plugins intégrés pour PostgreSQL et Redis, simplifiant considérablement la configuration. Pour déployer sur Railway, installez la CLI avec 'npm install -g @railway/cli', connectez-vous avec 'railway login', puis utilisez 'railway init' et 'railway up' pour déployer votre application."""
    story.append(Paragraph(railway_text, body_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>4.2 Fly.io</b>", h2_style))
    
    fly_text = """Fly.io est particulièrement intéressant pour sa capacité à déployer des applications sur plusieurs régions du monde, offrant ainsi une faible latence pour les utilisateurs internationaux. L'offre gratuite inclut jusqu'à 3 machines virtuelles shared-cpu-1x avec 256 Mo de RAM chacune, 3 Go de stockage persistant, et 160 Go de transfert de données sortantes par mois. Contrairement à Render, les applications sur Fly.io ne subissent pas de cold starts, mais une carte de crédit est requise pour la vérification du compte. La plateforme utilise un fichier 'fly.toml' pour la configuration et supporte nativement Docker."""
    story.append(Paragraph(fly_text, body_style))
    story.append(Spacer(1, 18))
    
    # === SECTION 5: CHECKLIST ===
    story.append(Paragraph("<b>5. Checklist de Déploiement</b>", h1_style))
    story.append(Spacer(1, 12))
    
    checklist_intro = """Utilisez cette liste de vérification pour vous assurer que tous les éléments nécessaires au déploiement sont correctement configurés avant de lancer votre application en production."""
    story.append(Paragraph(checklist_intro, body_style))
    story.append(Spacer(1, 12))
    
    checklist_items = [
        ("Pré-déploiement", [
            "Code source poussé sur GitHub",
            "Fichier Dockerfile.render présent à la racine",
            "Fichier render.yaml configuré",
            "Tests unitaires passent localement",
            "Variables d'environnement documentées"
        ]),
        ("Services Render", [
            "Base de données PostgreSQL créée",
            "Service Redis créé",
            "Service Web créé avec le bon Dockerfile",
            "Région cohérente pour tous les services"
        ]),
        ("Configuration", [
            "DATABASE_URL liée au service Web",
            "REDIS_URL liée au service Web",
            "SECRET_KEY générée et définie",
            "KEYCLOAK_URL et secrets configurés",
            "MINIO/S3 credentials configurés",
            "SERVE_FRONTEND=true activé"
        ]),
        ("Post-déploiement", [
            "Health check /health/ répond 200",
            "Migration de base de données exécutée",
            "Frontend accessible à la racine",
            "API accessible sur /api/v1",
            "Authentification Keycloak fonctionnelle"
        ])
    ]
    
    for section_title, items in checklist_items:
        story.append(Paragraph(f"<b>{section_title}</b>", h3_style))
        for item in items:
            story.append(Paragraph(f"☐ {item}", body_style))
        story.append(Spacer(1, 8))
    
    story.append(Spacer(1, 12))
    
    # === SECTION 6: TROUBLESHOOTING ===
    story.append(Paragraph("<b>6. Dépannage</b>", h1_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>6.1 Problèmes Courants</b>", h2_style))
    story.append(Spacer(1, 8))
    
    problems = [
        ("Erreur de build Docker", "Vérifiez que le fichier Dockerfile.render est présent à la racine du projet. Assurez-vous que toutes les dépendances npm sont correctement listées dans package.json et que les chemins des fichiers COPY sont corrects."),
        ("Cold start lent", "Le plan gratuit de Render met en veille l'application après 15 minutes d'inactivité. Le premier accès peut prendre 30-60 secondes. Pour un accès plus rapide, envisagez Railway ou Fly.io."),
        ("Erreur de connexion DB", "Vérifiez que la variable DATABASE_URL est correctement liée. Assurez-vous que la base de données est dans la même région que le service Web. Vérifiez les logs pour les erreurs de connexion."),
        ("Frontend non servi", "Vérifiez que SERVE_FRONTEND=true. Assurez-vous que le build React a réussi et que les fichiers sont dans /app/static. Vérifiez les logs de démarrage pour les erreurs."),
        ("Erreur d'authentification", "Vérifiez que KEYCLOAK_URL est accessible publiquement. Assurez-vous que KEYCLOAK_CLIENT_SECRET correspond à la configuration dans Keycloak. Vérifiez que le realm et les clients sont correctement configurés.")
    ]
    
    for title, solution in problems:
        story.append(Paragraph(f"<b>{title}</b>", h3_style))
        story.append(Paragraph(solution, body_style))
        story.append(Spacer(1, 6))
    
    story.append(Spacer(1, 18))
    
    # === FINAL NOTES ===
    story.append(Paragraph("<b>Notes Finales</b>", h2_style))
    
    final_text = """Ce guide couvre les aspects essentiels du déploiement d'EtudePlus sur des plateformes gratuites. Pour un usage en production à long terme, envisagez de passer à un plan payant pour bénéficier de ressources supplémentaires, d'un support technique, et de fonctionnalités avancées comme les sauvegardes automatiques et les déploiements multi-régions. Les fichiers de configuration créés pour ce déploiement incluent Dockerfile.render pour l'image Docker unifiée, render.yaml pour le blueprint Render, railway.toml pour Railway, et fly.toml pour Fly.io. Ces fichiers sont situés à la racine du projet et peuvent être adaptés selon vos besoins spécifiques."""
    story.append(Paragraph(final_text, body_style))
    
    # Build the PDF
    doc.build(story)
    print("PDF créé avec succès!")

if __name__ == "__main__":
    create_deployment_guide()
