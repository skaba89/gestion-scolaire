#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EtudePlus Deployment Guide PDF Generator
Generates a comprehensive deployment guide for Render, Railway, and Fly.io
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, ListFlowable, ListItem
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.units import cm, inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
import os

# Output path
OUTPUT_PATH = "/home/z/my-project/download/EtudePlus_Guide_Deploiement.pdf"

# Register fonts
pdfmetrics.registerFont(TTFont('Microsoft YaHei', '/usr/share/fonts/truetype/chinese/msyh.ttf'))
pdfmetrics.registerFont(TTFont('SimHei', '/usr/share/fonts/truetype/chinese/SimHei.ttf'))
pdfmetrics.registerFont(TTFont('Times New Roman', '/usr/share/fonts/truetype/english/Times-New-Roman.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'))

registerFontFamily('Microsoft YaHei', normal='Microsoft YaHei', bold='Microsoft YaHei')
registerFontFamily('SimHei', normal='SimHei', bold='SimHei')
registerFontFamily('Times New Roman', normal='Times New Roman', bold='Times New Roman')

def create_styles():
    """Create paragraph styles for the document."""
    styles = getSampleStyleSheet()
    
    # Cover title
    styles.add(ParagraphStyle(
        name='CoverTitle',
        fontName='Microsoft YaHei',
        fontSize=36,
        leading=44,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor('#1F4E79')
    ))
    
    # Cover subtitle
    styles.add(ParagraphStyle(
        name='CoverSubtitle',
        fontName='SimHei',
        fontSize=18,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=40,
        textColor=colors.HexColor('#666666')
    ))
    
    # Chapter heading
    styles.add(ParagraphStyle(
        name='ChapterHeading',
        fontName='Microsoft YaHei',
        fontSize=22,
        leading=28,
        alignment=TA_LEFT,
        spaceBefore=20,
        spaceAfter=15,
        textColor=colors.HexColor('#1F4E79')
    ))
    
    # Section heading
    styles.add(ParagraphStyle(
        name='SectionHeading',
        fontName='Microsoft YaHei',
        fontSize=16,
        leading=22,
        alignment=TA_LEFT,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.HexColor('#2E75B6')
    ))
    
    # Subsection heading
    styles.add(ParagraphStyle(
        name='SubsectionHeading',
        fontName='SimHei',
        fontSize=13,
        leading=18,
        alignment=TA_LEFT,
        spaceBefore=10,
        spaceAfter=8,
        textColor=colors.HexColor('#333333')
    ))
    
    # Body text
    styles.add(ParagraphStyle(
        name='BodyTextCN',
        fontName='SimHei',
        fontSize=11,
        leading=18,
        alignment=TA_LEFT,
        spaceAfter=8,
        wordWrap='CJK'
    ))
    
    # Code style
    styles.add(ParagraphStyle(
        name='CodeStyle',
        fontName='DejaVuSans',
        fontSize=9,
        leading=14,
        alignment=TA_LEFT,
        spaceAfter=6,
        backColor=colors.HexColor('#F5F5F5'),
        leftIndent=10,
        rightIndent=10
    ))
    
    # Table header
    styles.add(ParagraphStyle(
        name='TableHeader',
        fontName='SimHei',
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.white
    ))
    
    # Table cell
    styles.add(ParagraphStyle(
        name='TableCell',
        fontName='SimHei',
        fontSize=9,
        leading=13,
        alignment=TA_CENTER,
        wordWrap='CJK'
    ))
    
    # Table cell left
    styles.add(ParagraphStyle(
        name='TableCellLeft',
        fontName='SimHei',
        fontSize=9,
        leading=13,
        alignment=TA_LEFT,
        wordWrap='CJK'
    ))
    
    return styles

def create_table(data, col_widths, styles):
    """Create a styled table."""
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E79')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'SimHei'),
        ('FONTNAME', (0, 1), (-1, -1), 'SimHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    return table

def build_document():
    """Build the deployment guide PDF."""
    styles = create_styles()
    story = []
    
    # ========== COVER PAGE ==========
    story.append(Spacer(1, 120))
    story.append(Paragraph("EtudePlus", styles['CoverTitle']))
    story.append(Paragraph("Guide de Deploiement", styles['CoverTitle']))
    story.append(Spacer(1, 30))
    story.append(Paragraph("Deployment Guide for Free Tier Hosting", styles['CoverSubtitle']))
    story.append(Spacer(1, 60))
    story.append(Paragraph("Render | Railway | Fly.io", styles['CoverSubtitle']))
    story.append(Spacer(1, 80))
    story.append(Paragraph("Version 1.0 - 2025", styles['CoverSubtitle']))
    story.append(PageBreak())
    
    # ========== TABLE OF CONTENTS ==========
    story.append(Paragraph("<b>Table des Matieres</b>", styles['ChapterHeading']))
    story.append(Spacer(1, 15))
    
    toc_items = [
        "1. Introduction et Pre-requis",
        "2. Option A: Deploiement sur Render (Recommande)",
        "3. Option B: Deploiement sur Railway",
        "4. Option C: Deploiement sur Fly.io",
        "5. Configuration des Services Externes",
        "6. Variables d'Environnement",
        "7. Limitations des Offres Gratuites",
        "8. Checklist de Deploiement",
        "9. Resolution des Problemes"
    ]
    
    for item in toc_items:
        story.append(Paragraph(item, styles['BodyTextCN']))
    
    story.append(PageBreak())
    
    # ========== CHAPTER 1: INTRODUCTION ==========
    story.append(Paragraph("1. Introduction et Pre-requis", styles['ChapterHeading']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(
        "Ce guide vous accompagne dans le deploiement de l'application EtudePlus sur des plateformes d'hebergement "
        "gratuites. EtudePlus est un systeme complet de gestion scolaire comprenant un backend FastAPI (Python) "
        "et un frontend React (Vite + TypeScript). L'architecture multi-tenant permet de gerer plusieurs etablissements "
        "sur une seule instance.",
        styles['BodyTextCN']
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("1.1 Pre-requis", styles['SectionHeading']))
    
    prereqs = [
        "Compte GitHub avec le code source pousse",
        "Compte sur la plateforme choisie (Render, Railway, ou Fly.io)",
        "Instance Keycloak ou service d'authentification (Auth0, Supabase)",
        "Stockage S3-compatible (AWS S3, Cloudflare R2, ou Supabase Storage)",
        "CLI installee pour Fly.io (flyctl) si cette option est choisie"
    ]
    
    for prereq in prereqs:
        story.append(Paragraph(f"- {prereq}", styles['BodyTextCN']))
    
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("1.2 Architecture de l'Application", styles['SectionHeading']))
    
    story.append(Paragraph(
        "L'application utilise une architecture moderne avec separation des responsabilites. Le backend FastAPI "
        "sert l'API REST et peut egalement servir le frontend React compile en mode production. Cette approche "
        "mono-conteneur simplifie le deploiement sur les plateformes gratuites qui limitent le nombre de services.",
        styles['BodyTextCN']
    ))
    story.append(Spacer(1, 10))
    
    arch_data = [
        [Paragraph('<b>Composant</b>', styles['TableHeader']), 
         Paragraph('<b>Technologie</b>', styles['TableHeader']), 
         Paragraph('<b>Description</b>', styles['TableHeader'])],
        [Paragraph('Backend', styles['TableCell']), 
         Paragraph('FastAPI + Python 3.11', styles['TableCell']), 
         Paragraph('API REST avec SQLAlchemy', styles['TableCellLeft'])],
        [Paragraph('Frontend', styles['TableCell']), 
         Paragraph('React 18 + Vite', styles['TableCell']), 
         Paragraph('Interface utilisateur moderne', styles['TableCellLeft'])],
        [Paragraph('Database', styles['TableCell']), 
         Paragraph('PostgreSQL 15', styles['TableCell']), 
         Paragraph('Base de donnees relationnelle', styles['TableCellLeft'])],
        [Paragraph('Cache', styles['TableCell']), 
         Paragraph('Redis', styles['TableCell']), 
         Paragraph('Cache et sessions', styles['TableCellLeft'])],
        [Paragraph('Auth', styles['TableCell']), 
         Paragraph('Keycloak/OIDC', styles['TableCell']), 
         Paragraph('Authentification OAuth2', styles['TableCellLeft'])],
        [Paragraph('Storage', styles['TableCell']), 
         Paragraph('S3-compatible', styles['TableCell']), 
         Paragraph('Stockage de fichiers', styles['TableCellLeft'])],
    ]
    
    story.append(create_table(arch_data, [3*cm, 4*cm, 8*cm], styles))
    story.append(Spacer(1, 18))
    
    # ========== CHAPTER 2: RENDER ==========
    story.append(Paragraph("2. Option A: Deploiement sur Render (Recommande)", styles['ChapterHeading']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(
        "Render offre le meilleur plan gratuit pour les applications web avec 750 heures mensuelles, "
        "une base de donnees PostgreSQL gratuite (1GB) et un cache Redis (25MB). L'inconvenient principal "
        "est le temps de demarrage a froid (30-60 secondes) apres une periode d'inactivite.",
        styles['BodyTextCN']
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("2.1 Etapes de Deploiement", styles['SectionHeading']))
    
    render_steps = [
        ("Etape 1", "Creer un compte sur render.com et connecter votre repository GitHub"),
        ("Etape 2", "Cliquer sur 'New' puis 'Blueprint' pour utiliser le fichier render.yaml"),
        ("Etape 3", "Selectionner le repository GitHub contenant le code source"),
        ("Etape 4", "Render detectera automatiquement les services a creer (Web, Redis, PostgreSQL)"),
        ("Etape 5", "Configurer les variables d'environnement dans le dashboard Render"),
        ("Etape 6", "Deployer et verifier l'application sur l'URL fournie"),
    ]
    
    for step_name, step_desc in render_steps:
        story.append(Paragraph(f"<b>{step_name}:</b> {step_desc}", styles['BodyTextCN']))
    
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("2.2 Fichiers de Configuration", styles['SectionHeading']))
    
    story.append(Paragraph(
        "Le projet inclut deux fichiers essentiels pour Render: Dockerfile.render (multi-stage build "
        "compilant le frontend et servant le tout via FastAPI) et render.yaml (blueprint declaratif "
        "pour la creation automatique des ressources). Ces fichiers sont pre-configures et ne necessitent "
        "generalement pas de modifications.",
        styles['BodyTextCN']
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("2.3 Variables d'Environnement Render", styles['SectionHeading']))
    
    env_data = [
        [Paragraph('<b>Variable</b>', styles['TableHeader']), 
         Paragraph('<b>Valeur/Source</b>', styles['TableHeader']), 
         Paragraph('<b>Description</b>', styles['TableHeader'])],
        [Paragraph('DATABASE_URL', styles['TableCell']), 
         Paragraph('Auto (PostgreSQL)', styles['TableCell']), 
         Paragraph('URL de connexion DB', styles['TableCellLeft'])],
        [Paragraph('REDIS_URL', styles['TableCell']), 
         Paragraph('Auto (Redis)', styles['TableCell']), 
         Paragraph('URL de connexion Redis', styles['TableCellLeft'])],
        [Paragraph('SECRET_KEY', styles['TableCell']), 
         Paragraph('generateValue: true', styles['TableCell']), 
         Paragraph('Cle secrete auto-generee', styles['TableCellLeft'])],
        [Paragraph('DEBUG', styles['TableCell']), 
         Paragraph('False', styles['TableCell']), 
         Paragraph('Mode production', styles['TableCellLeft'])],
        [Paragraph('SERVE_FRONTEND', styles['TableCell']), 
         Paragraph('true', styles['TableCell']), 
         Paragraph('Servir le frontend', styles['TableCellLeft'])],
        [Paragraph('KEYCLOAK_URL', styles['TableCell']), 
         Paragraph('Manual', styles['TableCell']), 
         Paragraph('URL Keycloak', styles['TableCellLeft'])],
        [Paragraph('KEYCLOAK_CLIENT_SECRET', styles['TableCell']), 
         Paragraph('Manual', styles['TableCell']), 
         Paragraph('Secret client OIDC', styles['TableCellLeft'])],
    ]
    
    story.append(create_table(env_data, [4*cm, 4*cm, 7*cm], styles))
    story.append(Spacer(1, 18))
    
    # ========== CHAPTER 3: RAILWAY ==========
    story.append(Paragraph("3. Option B: Deploiement sur Railway", styles['ChapterHeading']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(
        "Railway offre 5 USD de credits gratuits mensuels, ce qui est suffisant pour une petite application. "
        "L'avantage principal est l'absence de temps de demarrage a froid. Cependant, les bases de donnees "
        "et Redis sont des services payants qui consomment rapidement les credits gratuits.",
        styles['BodyTextCN']
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("3.1 Etapes de Deploiement Railway", styles['SectionHeading']))
    
    railway_steps = [
        ("Etape 1", "Creer un compte sur railway.app et connecter votre GitHub"),
        ("Etape 2", "Creer un nouveau projet depuis le repository GitHub"),
        ("Etape 3", "Ajouter un addon PostgreSQL (environ 1 USD)"),
        ("Etape 4", "Ajouter un addon Redis ou utiliser Upstash (gratuit)"),
        ("Etape 5", "Configurer les variables d'environnement"),
        ("Etape 6", "Deployer et verifier l'application"),
    ]
    
    for step_name, step_desc in railway_steps:
        story.append(Paragraph(f"<b>{step_name}:</b> {step_desc}", styles['BodyTextCN']))
    
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("3.2 Configuration railway.toml", styles['SectionHeading']))
    
    story.append(Paragraph(
        "Le fichier railway.toml specifie la configuration du build et du deploiement. Railway detecte "
        "automatiquement le Dockerfile et utilise les parametres definis. Les variables d'environnement "
        "doivent etre configurees manuellement dans le dashboard Railway.",
        styles['BodyTextCN']
    ))
    story.append(Spacer(1, 10))
    
    # ========== CHAPTER 4: FLY.IO ==========
    story.append(Paragraph("4. Option C: Deploiement sur Fly.io", styles['ChapterHeading']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(
        "Fly.io offre une allocation gratuite de 3 VMs, 3GB de stockage persistant et 160GB de transfert "
        "sortant mensuel. La plateforme permet un deploiement mondial avec des serveurs en Europe, Amerique "
        "et Asie. Le demarrage est rapide (pas de cold start) mais une carte de credit est requise.",
        styles['BodyTextCN']
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("4.1 Installation de flyctl", styles['SectionHeading']))
    
    story.append(Paragraph("Installer l'outil CLI flyctl selon votre systeme d'exploitation:", styles['BodyTextCN']))
    story.append(Spacer(1, 5))
    
    fly_install = [
        ("macOS", "brew install flyctl"),
        ("Linux", "curl -L https://fly.io/install.sh | sh"),
        ("Windows", 'powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"'),
    ]
    
    for system, command in fly_install:
        story.append(Paragraph(f"<b>{system}:</b> <font name='DejaVuSans'>{command}</font>", styles['BodyTextCN']))
    
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("4.2 Commandes de Deploiement", styles['SectionHeading']))
    
    fly_commands = [
        ("Authentification", "fly auth login"),
        ("Creation app", "fly apps create etudeplus"),
        ("Creation DB", "fly postgres create"),
        ("Attachement DB", "fly postgres attach <db-name>"),
        ("Configuration secrets", "fly secrets set SECRET_KEY=$(openssl rand -hex 32)"),
        ("Deploiement", "fly deploy"),
        ("Ouverture", "fly open"),
    ]
    
    cmd_data = [
        [Paragraph('<b>Action</b>', styles['TableHeader']), 
         Paragraph('<b>Commande</b>', styles['TableHeader'])],
    ]
    for action, cmd in fly_commands:
        cmd_data.append([
            Paragraph(action, styles['TableCell']),
            Paragraph(f"<font name='DejaVuSans'>{cmd}</font>", styles['TableCellLeft'])
        ])
    
    story.append(create_table(cmd_data, [4*cm, 10*cm], styles))
    story.append(Spacer(1, 18))
    
    # ========== CHAPTER 5: EXTERNAL SERVICES ==========
    story.append(Paragraph("5. Configuration des Services Externes", styles['ChapterHeading']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("5.1 Authentification (Keycloak Alternatives)", styles['SectionHeading']))
    
    auth_options = [
        ("Auth0", "Gratuit jusqu'a 7,000 utilisateurs actifs. Configuration simple, documentation excellente, SDK pour tous les frameworks."),
        ("Supabase Auth", "Gratuit jusqu'a 50,000 utilisateurs. Inclut aussi une base de donnees et du stockage."),
        ("Keycloak Self-hosted", "Solution gratuite et open-source. A deployer sur une autre plateforme (Railway ou Fly.io)."),
        ("Clerk", "Gratuit jusqu'a 5,000 utilisateurs. Interface moderne et fonctionnalites avancees."),
    ]
    
    for name, desc in auth_options:
        story.append(Paragraph(f"<b>{name}:</b> {desc}", styles['BodyTextCN']))
    
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("5.2 Stockage de Fichiers (S3-compatible)", styles['SectionHeading']))
    
    storage_options = [
        ("AWS S3", "12 mois gratuits: 5GB stockage, 20,000 requetes GET, 2,000 requetes PUT."),
        ("Cloudflare R2", "Gratuit: 10GB stockage, pas de frais d'egress (sortie de donnees)."),
        ("Supabase Storage", "Gratuit: 1GB stockage, inclus avec l'authentification."),
        ("Backblaze B2", "Gratuit: 10GB stockage, compatible S3."),
    ]
    
    for name, desc in storage_options:
        story.append(Paragraph(f"<b>{name}:</b> {desc}", styles['BodyTextCN']))
    
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("5.3 Redis (Cache)", styles['SectionHeading']))
    
    story.append(Paragraph(
        "Pour les utilisateurs de Fly.io ou Railway, Upstash offre un Redis gratuit (10,000 commandes/jour) "
        "qui s'integre parfaitement. Creer un compte sur upstash.com, creer une base Redis, puis copier "
        "l'URL de connexion dans la variable d'environnement REDIS_URL.",
        styles['BodyTextCN']
    ))
    story.append(Spacer(1, 18))
    
    # ========== CHAPTER 6: ENVIRONMENT VARIABLES ==========
    story.append(Paragraph("6. Variables d'Environnement Completes", styles['ChapterHeading']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(
        "Voici la liste complete des variables d'environnement necessaires pour faire fonctionner "
        "l'application en production. Celles marquees 'Auto' sont configurees automatiquement par "
        "la plateforme, les autres doivent etre definies manuellement.",
        styles['BodyTextCN']
    ))
    story.append(Spacer(1, 10))
    
    all_env_data = [
        [Paragraph('<b>Variable</b>', styles['TableHeader']), 
         Paragraph('<b>Requis</b>', styles['TableHeader']), 
         Paragraph('<b>Valeur par defaut</b>', styles['TableHeader'])],
        [Paragraph('DATABASE_URL', styles['TableCell']), 
         Paragraph('Oui', styles['TableCell']), 
         Paragraph('Auto (plateforme)', styles['TableCell'])],
        [Paragraph('REDIS_URL', styles['TableCell']), 
         Paragraph('Oui', styles['TableCell']), 
         Paragraph('Auto (plateforme)', styles['TableCell'])],
        [Paragraph('SECRET_KEY', styles['TableCell']), 
         Paragraph('Oui', styles['TableCell']), 
         Paragraph('Generer: openssl rand -hex 32', styles['TableCell'])],
        [Paragraph('DEBUG', styles['TableCell']), 
         Paragraph('Oui', styles['TableCell']), 
         Paragraph('False', styles['TableCell'])],
        [Paragraph('LOG_LEVEL', styles['TableCell']), 
         Paragraph('Non', styles['TableCell']), 
         Paragraph('INFO', styles['TableCell'])],
        [Paragraph('SERVE_FRONTEND', styles['TableCell']), 
         Paragraph('Oui', styles['TableCell']), 
         Paragraph('true', styles['TableCell'])],
        [Paragraph('KEYCLOAK_URL', styles['TableCell']), 
         Paragraph('Oui', styles['TableCell']), 
         Paragraph('URL de votre instance', styles['TableCell'])],
        [Paragraph('KEYCLOAK_REALM', styles['TableCell']), 
         Paragraph('Non', styles['TableCell']), 
         Paragraph('schoolflow', styles['TableCell'])],
        [Paragraph('KEYCLOAK_CLIENT_ID', styles['TableCell']), 
         Paragraph('Non', styles['TableCell']), 
         Paragraph('schoolflow-backend', styles['TableCell'])],
        [Paragraph('KEYCLOAK_CLIENT_SECRET', styles['TableCell']), 
         Paragraph('Oui', styles['TableCell']), 
         Paragraph('Depuis Keycloak', styles['TableCell'])],
        [Paragraph('MINIO_ENDPOINT', styles['TableCell']), 
         Paragraph('Oui', styles['TableCell']), 
         Paragraph('Endpoint S3', styles['TableCell'])],
        [Paragraph('MINIO_ACCESS_KEY', styles['TableCell']), 
         Paragraph('Oui', styles['TableCell']), 
         Paragraph("Cle d'acces", styles['TableCell'])],
        [Paragraph('MINIO_SECRET_KEY', styles['TableCell']), 
         Paragraph('Oui', styles['TableCell']), 
         Paragraph('Cle secrete', styles['TableCell'])],
        [Paragraph('MINIO_BUCKET', styles['TableCell']), 
         Paragraph('Non', styles['TableCell']), 
         Paragraph('schoolflow', styles['TableCell'])],
    ]
    
    story.append(create_table(all_env_data, [4.5*cm, 2.5*cm, 7*cm], styles))
    story.append(Spacer(1, 18))
    
    # ========== CHAPTER 7: LIMITATIONS ==========
    story.append(Paragraph("7. Limitations des Offres Gratuites", styles['ChapterHeading']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("7.1 Comparatif des Plateformes", styles['SectionHeading']))
    
    limit_data = [
        [Paragraph('<b>Ressource</b>', styles['TableHeader']), 
         Paragraph('<b>Render</b>', styles['TableHeader']), 
         Paragraph('<b>Railway</b>', styles['TableHeader']), 
         Paragraph('<b>Fly.io</b>', styles['TableHeader'])],
        [Paragraph('RAM', styles['TableCell']), 
         Paragraph('512MB', styles['TableCell']), 
         Paragraph('Variable', styles['TableCell']), 
         Paragraph('256MB-512MB', styles['TableCell'])],
        [Paragraph('CPU', styles['TableCell']), 
         Paragraph('0.1 vCPU', styles['TableCell']), 
         Paragraph('Variable', styles['TableCell']), 
         Paragraph('Shared', styles['TableCell'])],
        [Paragraph('Stockage DB', styles['TableCell']), 
         Paragraph('1GB', styles['TableCell']), 
         Paragraph('Payant', styles['TableCell']), 
         Paragraph('3GB', styles['TableCell'])],
        [Paragraph('Redis', styles['TableCell']), 
         Paragraph('25MB', styles['TableCell']), 
         Paragraph('Payant', styles['TableCell']), 
         Paragraph('Via Upstash', styles['TableCell'])],
        [Paragraph('Cold Start', styles['TableCell']), 
         Paragraph('30-60s', styles['TableCell']), 
         Paragraph('Non', styles['TableCell']), 
         Paragraph('Non', styles['TableCell'])],
        [Paragraph('Heures/mois', styles['TableCell']), 
         Paragraph('750h', styles['TableCell']), 
         Paragraph('$5 credits', styles['TableCell']), 
         Paragraph('3 VMs', styles['TableCell'])],
        [Paragraph('Expire', styles['TableCell']), 
         Paragraph('DB 90 jours', styles['TableCell']), 
         Paragraph('Non', styles['TableCell']), 
         Paragraph('Non', styles['TableCell'])],
    ]
    
    story.append(create_table(limit_data, [3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm], styles))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("7.2 Recommandations", styles['SectionHeading']))
    
    recommendations = [
        "Render est recommande pour un test gratuit complet avec base de donnees incluse",
        "Railway convient si vous avez besoin d'absence de cold start et acceptez de payer ~$5/mois",
        "Fly.io est ideal pour un deploiement mondial avec controle total via CLI",
        "Pour une production reelle, envisagez de passer a un plan payant pour la fiabilite",
        "Sauvegardez regulierement vos donnees car les offres gratuites n'incluent pas toujours les backups",
    ]
    
    for rec in recommendations:
        story.append(Paragraph(f"- {rec}", styles['BodyTextCN']))
    
    story.append(Spacer(1, 18))
    
    # ========== CHAPTER 8: CHECKLIST ==========
    story.append(Paragraph("8. Checklist de Deploiement", styles['ChapterHeading']))
    story.append(Spacer(1, 10))
    
    checklist = [
        ("Pre-deploiement", [
            "Code source pousse sur GitHub (branche main)",
            "Fichiers Dockerfile.render et render.yaml presents",
            "Fichier railway.toml ou fly.toml configure",
            "Variables d'environnement preparees",
        ]),
        ("Services externes", [
            "Instance Keycloak ou Auth0 creee et configuree",
            "Client OIDC configure avec redirect URIs",
            "Bucket S3 cree avec credentials",
            "Redis Upstash configure (si applicable)",
        ]),
        ("Post-deploiement", [
            "Migrations de base de donnees executees",
            "Utilisateur admin cree",
            "Test de connexion authentification",
            "Test d'upload de fichiers",
            "Verification des logs d'erreur",
        ]),
    ]
    
    for section, items in checklist:
        story.append(Paragraph(f"<b>{section}:</b>", styles['SubsectionHeading']))
        for item in items:
            story.append(Paragraph(f"[ ] {item}", styles['BodyTextCN']))
        story.append(Spacer(1, 10))
    
    # ========== CHAPTER 9: TROUBLESHOOTING ==========
    story.append(Paragraph("9. Resolution des Problemes", styles['ChapterHeading']))
    story.append(Spacer(1, 10))
    
    issues = [
        ("Erreur de connexion a la base de donnees", 
         "Verifiez que DATABASE_URL est correct. Sur Render, la variable est auto-configuree. "
         "Sur Fly.io, utilisez 'fly postgres attach' pour connecter la DB."),
        ("Erreur 502 Bad Gateway", 
         "L'application n'a pas demarre correctement. Verifiez les logs pour identifier l'erreur. "
         "Les causes frequentes incluent: migrations echouees, variables manquantes, memoire insuffisante."),
        ("Cold start trop lent sur Render", 
         "Normal pour le plan gratuit. Pour reduire l'impact, utilisez un service de monitoring "
         "qui ping regulierement l'application ou passez a un plan payant."),
        ("Erreurs CORS", 
         "Verifiez BACKEND_CORS_ORIGINS. En production avec frontend servi par le backend, "
         "cette variable peut etre vide (meme origine)."),
        ("Upload de fichiers echoue", 
         "Verifiez les variables MINIO_* et que le bucket existe. Testez avec un outil comme "
         "MinIO Client ou AWS CLI pour confirmer les credentials."),
    ]
    
    for issue, solution in issues:
        story.append(Paragraph(f"<b>{issue}</b>", styles['SubsectionHeading']))
        story.append(Paragraph(solution, styles['BodyTextCN']))
        story.append(Spacer(1, 8))
    
    # Build PDF
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
        title='EtudePlus_Guide_Deploiement',
        author='Z.ai',
        creator='Z.ai',
        subject='Guide de deploiement pour EtudePlus sur Render, Railway et Fly.io'
    )
    
    doc.build(story)
    print(f"PDF genere: {OUTPUT_PATH}")
    return OUTPUT_PATH

if __name__ == '__main__':
    build_document()
