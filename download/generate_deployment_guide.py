#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Deployment Guide PDF for EtudePlus
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import TableStyle

# Register fonts
pdfmetrics.registerFont(TTFont('SimHei', '/usr/share/fonts/truetype/chinese/SimHei.ttf'))
pdfmetrics.registerFont(TTFont('Microsoft YaHei', '/usr/share/fonts/truetype/chinese/msyh.ttf'))
pdfmetrics.registerFont(TTFont('Times New Roman', '/usr/share/fonts/truetype/english/Times-New-Roman.ttf'))

registerFontFamily('Microsoft YaHei', normal='Microsoft YaHei', bold='Microsoft YaHei')
registerFontFamily('SimHei', normal='SimHei', bold='SimHei')
registerFontFamily('Times New Roman', normal='Times New Roman', bold='Times New Roman')

# Create document
output_path = '/home/z/my-project/download/EtudePlus_Guide_Deploiement.pdf'
doc = SimpleDocTemplate(
    output_path,
    pagesize=A4,
    title='EtudePlus_Guide_Deploiement',
    author='Z.ai',
    creator='Z.ai',
    subject='Guide complet de deploiement gratuit'
)

# Define styles
cover_title_style = ParagraphStyle(
    name='CoverTitle',
    fontName='Microsoft YaHei',
    fontSize=32,
    leading=40,
    alignment=TA_CENTER,
    spaceAfter=36
)

cover_subtitle_style = ParagraphStyle(
    name='CoverSubtitle',
    fontName='SimHei',
    fontSize=18,
    leading=26,
    alignment=TA_CENTER,
    spaceAfter=48
)

cover_author_style = ParagraphStyle(
    name='CoverAuthor',
    fontName='SimHei',
    fontSize=12,
    leading=18,
    alignment=TA_CENTER
)

h1_style = ParagraphStyle(
    name='Heading1Custom',
    fontName='Microsoft YaHei',
    fontSize=16,
    leading=22,
    spaceBefore=24,
    spaceAfter=12,
    alignment=TA_LEFT
)

h3_style = ParagraphStyle(
    name='Heading3Custom',
    fontName='Microsoft YaHei',
    fontSize=11,
    leading=16,
    spaceBefore=12,
    spaceAfter=6,
    alignment=TA_LEFT
)

body_style = ParagraphStyle(
    name='BodyStyle',
    fontName='SimHei',
    fontSize=10,
    leading=16,
    spaceBefore=4,
    spaceAfter=4,
    alignment=TA_LEFT,
    wordWrap='CJK'
)

code_style = ParagraphStyle(
    name='CodeStyle',
    fontName='Times New Roman',
    fontSize=9,
    leading=12,
    spaceBefore=4,
    spaceAfter=4,
    alignment=TA_LEFT,
    backColor=colors.HexColor('#F5F5F5')
)

header_style = ParagraphStyle(
    name='TableHeader',
    fontName='SimHei',
    fontSize=9,
    textColor=colors.white,
    alignment=TA_CENTER
)

cell_style = ParagraphStyle(
    name='TableCell',
    fontName='SimHei',
    fontSize=8,
    textColor=colors.black,
    alignment=TA_CENTER
)

cell_left_style = ParagraphStyle(
    name='TableCellLeft',
    fontName='SimHei',
    fontSize=8,
    textColor=colors.black,
    alignment=TA_LEFT
)

# Build story
story = []

# Cover page
story.append(Spacer(1, 80))
story.append(Paragraph('<b>EtudePlus</b>', cover_title_style))
story.append(Spacer(1, 36))
story.append(Paragraph('Guide de Deploiement Gratuit', cover_subtitle_style))
story.append(Spacer(1, 48))
story.append(Paragraph('Options de deploiement pour tests en production', cover_subtitle_style))
story.append(Spacer(1, 60))
story.append(Paragraph('Version 1.0 - Janvier 2025', cover_author_style))
story.append(Paragraph('Genere par Z.ai', cover_author_style))
story.append(PageBreak())

# Section 1: Comparatif
story.append(Paragraph('<b>1. Comparatif des Plateformes</b>', h1_style))
story.append(Spacer(1, 12))

story.append(Paragraph(
    'Ce tableau compare les differentes plateformes gratuites disponibles pour deployer EtudePlus.',
    body_style
))
story.append(Spacer(1, 12))

# Comparison table
compare_data = [
    [Paragraph('<b>Plateforme</b>', header_style), 
     Paragraph('<b>RAM</b>', header_style), 
     Paragraph('<b>DB</b>', header_style), 
     Paragraph('<b>Credit</b>', header_style)],
    [Paragraph('Render.com', cell_left_style), Paragraph('512MB', cell_style), Paragraph('PostgreSQL 90j', cell_style), Paragraph('750h/mois', cell_style)],
    [Paragraph('Railway.app', cell_left_style), Paragraph('512MB', cell_style), Paragraph('PostgreSQL', cell_style), Paragraph('$5/mois', cell_style)],
    [Paragraph('Fly.io', cell_left_style), Paragraph('256MB', cell_style), Paragraph('3GB', cell_style), Paragraph('3 VMs free', cell_style)],
    [Paragraph('Vercel+Supabase', cell_left_style), Paragraph('-', cell_style), Paragraph('500MB', cell_style), Paragraph('Generous', cell_style)],
    [Paragraph('Oracle Cloud', cell_left_style), Paragraph('24GB', cell_style), Paragraph('Autonome', cell_style), Paragraph('Always Free', cell_style)],
]

compare_table = Table(compare_data, colWidths=[4*cm, 3*cm, 3.5*cm, 3.5*cm])
compare_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E79')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('BACKGROUND', (0, 1), (-1, 1), colors.white),
    ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#F5F5F5')),
    ('BACKGROUND', (0, 3), (-1, 3), colors.white),
    ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#F5F5F5')),
    ('BACKGROUND', (0, 5), (-1, 5), colors.white),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))

story.append(compare_table)
story.append(Spacer(1, 18))

# Section 2: Render
story.append(Paragraph('<b>2. Render.com (Recommande)</b>', h1_style))
story.append(Spacer(1, 12))

story.append(Paragraph(
    'Render offre le meilleur rapport simplicite/configuration pour les projets gratuits.',
    body_style
))

story.append(Paragraph('<b>Etapes de deploiement :</b>', h3_style))

steps = [
    '1. Pousser le code sur GitHub',
    '2. Creer un compte sur render.com',
    '3. Creer une base PostgreSQL (New + > PostgreSQL)',
    '4. Creer un Redis (New + > Redis)',
    '5. Creer le Backend (New + > Web Service > Docker)',
    '6. Creer le Frontend (New + > Static Site)',
]

for step in steps:
    story.append(Paragraph(step, body_style))

story.append(Spacer(1, 12))

story.append(Paragraph('<b>Variables environnement Backend :</b>', h3_style))

env_vars = [
    'DATABASE_URL = ${etudeplus-db.DATABASE_URL}',
    'REDIS_URL = ${etudeplus-redis.DATABASE_URL}',
    'SECRET_KEY = (openssl rand -hex 32)',
    'DEBUG = False',
    'KEYCLOAK_URL = https://your-keycloak.com',
]

for var in env_vars:
    story.append(Paragraph(var, code_style))

story.append(Spacer(1, 12))

# Section 3: Tips
story.append(Paragraph('<b>3. Conseils Importants</b>', h1_style))
story.append(Spacer(1, 12))

tips = [
    'Le plan gratuit "spin down" apres 15 min d\'inactivite',
    'Le "cold start" prend 30-60 secondes',
    'Utilisez UptimeRobot pour garder l\'app active',
    'La base PostgreSQL gratuite expire apres 90 jours',
    'Pour Keycloak, utilisez un service externe',
]

for tip in tips:
    story.append(Paragraph(f'• {tip}', body_style))

story.append(Spacer(1, 18))

# Section 4: Fichiers
story.append(Paragraph('<b>4. Fichiers de Configuration</b>', h1_style))
story.append(Spacer(1, 12))

story.append(Paragraph(
    'Les fichiers suivants ont ete crees :',
    body_style
))

files = [
    'render.yaml - Configuration Render Blueprint',
    'railway.toml - Configuration Railway',
    'fly.toml - Configuration Fly.io',
    'Dockerfile.backend - Docker optimise',
    '.env.production - Variables exemple',
    'scripts/deploy.sh - Script interactif',
]

for file in files:
    story.append(Paragraph(f'• {file}', body_style))

# Build PDF
doc.build(story)
print(f"PDF generated: {output_path}")
