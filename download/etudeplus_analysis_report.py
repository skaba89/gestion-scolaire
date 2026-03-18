#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SchoolFlow Pro (EtudePlus) - Project Analysis Report
Comprehensive analysis of the school management system
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, ListFlowable, ListItem
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
import os
from datetime import datetime

# Register fonts
pdfmetrics.registerFont(TTFont('SimHei', '/usr/share/fonts/truetype/chinese/SimHei.ttf'))
pdfmetrics.registerFont(TTFont('Microsoft YaHei', '/usr/share/fonts/truetype/chinese/msyh.ttf'))
pdfmetrics.registerFont(TTFont('Times New Roman', '/usr/share/fonts/truetype/english/Times-New-Roman.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'))

# Register font families for bold support
registerFontFamily('SimHei', normal='SimHei', bold='SimHei')
registerFontFamily('Times New Roman', normal='Times New Roman', bold='Times New Roman')

# Color scheme
TABLE_HEADER_COLOR = colors.HexColor('#1F4E79')
TABLE_HEADER_TEXT = colors.white
TABLE_ROW_EVEN = colors.white
TABLE_ROW_ODD = colors.HexColor('#F5F5F5')
ACCENT_COLOR = colors.HexColor('#2E86AB')
SUCCESS_COLOR = colors.HexColor('#28A745')
WARNING_COLOR = colors.HexColor('#FFC107')
DANGER_COLOR = colors.HexColor('#DC3545')

def create_styles():
    styles = getSampleStyleSheet()
    
    # Cover styles
    styles.add(ParagraphStyle(
        name='CoverTitle',
        fontName='Microsoft YaHei',
        fontSize=36,
        leading=44,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor('#1F4E79')
    ))
    
    styles.add(ParagraphStyle(
        name='CoverSubtitle',
        fontName='SimHei',
        fontSize=18,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=30,
        textColor=colors.HexColor('#666666')
    ))
    
    styles.add(ParagraphStyle(
        name='CoverAuthor',
        fontName='SimHei',
        fontSize=14,
        leading=20,
        alignment=TA_CENTER,
        spaceAfter=10
    ))
    
    # Section headers
    styles.add(ParagraphStyle(
        name='SectionH1',
        fontName='Microsoft YaHei',
        fontSize=20,
        leading=28,
        alignment=TA_LEFT,
        spaceBefore=20,
        spaceAfter=12,
        textColor=colors.HexColor('#1F4E79')
    ))
    
    styles.add(ParagraphStyle(
        name='SectionH2',
        fontName='Microsoft YaHei',
        fontSize=16,
        leading=22,
        alignment=TA_LEFT,
        spaceBefore=16,
        spaceAfter=10,
        textColor=colors.HexColor('#2E86AB')
    ))
    
    styles.add(ParagraphStyle(
        name='SectionH3',
        fontName='SimHei',
        fontSize=13,
        leading=18,
        alignment=TA_LEFT,
        spaceBefore=12,
        spaceAfter=8,
        textColor=colors.HexColor('#333333')
    ))
    
    # Body text
    styles.add(ParagraphStyle(
        name='BodyTextCustom',
        fontName='SimHei',
        fontSize=10.5,
        leading=18,
        alignment=TA_LEFT,
        spaceBefore=0,
        spaceAfter=8,
        wordWrap='CJK'
    ))
    
    styles.add(ParagraphStyle(
        name='BodyTextJustify',
        fontName='SimHei',
        fontSize=10.5,
        leading=18,
        alignment=TA_JUSTIFY,
        spaceBefore=0,
        spaceAfter=8,
        wordWrap='CJK'
    ))
    
    # Table styles
    styles.add(ParagraphStyle(
        name='TableHeader',
        fontName='SimHei',
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.white
    ))
    
    styles.add(ParagraphStyle(
        name='TableCell',
        fontName='SimHei',
        fontSize=9,
        leading=13,
        alignment=TA_LEFT,
        wordWrap='CJK'
    ))
    
    styles.add(ParagraphStyle(
        name='TableCellCenter',
        fontName='SimHei',
        fontSize=9,
        leading=13,
        alignment=TA_CENTER,
        wordWrap='CJK'
    ))
    
    # Special styles
    styles.add(ParagraphStyle(
        name='BulletText',
        fontName='SimHei',
        fontSize=10.5,
        leading=16,
        alignment=TA_LEFT,
        leftIndent=20,
        spaceBefore=4,
        spaceAfter=4,
        wordWrap='CJK'
    ))
    
    styles.add(ParagraphStyle(
        name='CodeBlock',
        fontName='DejaVuSans',
        fontSize=9,
        leading=12,
        alignment=TA_LEFT,
        leftIndent=10,
        rightIndent=10,
        spaceBefore=8,
        spaceAfter=8,
        backColor=colors.HexColor('#F5F5F5')
    ))
    
    styles.add(ParagraphStyle(
        name='Caption',
        fontName='SimHei',
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        spaceBefore=6,
        spaceAfter=12,
        textColor=colors.HexColor('#666666')
    ))
    
    return styles

def create_table(data, col_widths, styles):
    """Create a styled table with consistent formatting"""
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), TABLE_HEADER_TEXT),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'SimHei'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), TABLE_ROW_EVEN),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [TABLE_ROW_EVEN, TABLE_ROW_ODD]),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'SimHei'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    return table

def build_report():
    # Setup
    output_path = '/home/z/my-project/download/EtudePlus_Analyse_Complete.pdf'
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
        title='EtudePlus_Analyse_Complete',
        author='Z.ai',
        creator='Z.ai',
        subject='Analyse complete du projet SchoolFlow Pro (EtudePlus)'
    )
    
    styles = create_styles()
    story = []
    
    # ============================================
    # COVER PAGE
    # ============================================
    story.append(Spacer(1, 80))
    story.append(Paragraph('<b>SchoolFlow Pro (EtudePlus)</b>', styles['CoverTitle']))
    story.append(Spacer(1, 20))
    story.append(Paragraph('Analyse Complete du Projet de Gestion Scolaire', styles['CoverSubtitle']))
    story.append(Spacer(1, 10))
    story.append(Paragraph('Etat Actuel, Architecture, Recommandations et Evolutions', styles['CoverSubtitle']))
    story.append(Spacer(1, 60))
    
    # Info box
    info_data = [
        [Paragraph('<b>Repository</b>', styles['TableCellCenter']), 
         Paragraph('github.com/skaba89/etudeplus', styles['TableCell'])],
        [Paragraph('<b>Version Analysee</b>', styles['TableCellCenter']), 
         Paragraph('1.0 Production-Ready', styles['TableCell'])],
        [Paragraph('<b>Date d\'Analyse</b>', styles['TableCellCenter']), 
         Paragraph(datetime.now().strftime('%d/%m/%Y'), styles['TableCell'])],
        [Paragraph('<b>Lignes de Code</b>', styles['TableCellCenter']), 
         Paragraph('~155,000 lignes (TypeScript + Python + SQL)', styles['TableCell'])],
        [Paragraph('<b>Technologies</b>', styles['TableCellCenter']), 
         Paragraph('React, FastAPI, PostgreSQL, Keycloak, Docker', styles['TableCell'])],
    ]
    info_table = Table(info_data, colWidths=[5*cm, 10*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F0F0')),
        ('FONTNAME', (0, 0), (-1, -1), 'SimHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    
    story.append(Spacer(1, 60))
    story.append(Paragraph('Rapport genere automatiquement par Z.ai', styles['CoverAuthor']))
    story.append(PageBreak())
    
    # ============================================
    # TABLE OF CONTENTS (Manual)
    # ============================================
    story.append(Paragraph('<b>Table des Matieres</b>', styles['SectionH1']))
    story.append(Spacer(1, 20))
    
    toc_items = [
        ('1. Etat Actuel du Projet', '3'),
        ('   1.1 Resume Executif', '3'),
        ('   1.2 Fonctionnalites Implementees', '3'),
        ('   1.3 Statut de Developpement', '4'),
        ('2. Architecture et Technologies', '5'),
        ('   2.1 Stack Technique', '5'),
        ('   2.2 Architecture Multi-Tenant', '6'),
        ('   2.3 Modele de Donnees', '7'),
        ('3. Points Forts et Points Faibles', '8'),
        ('   3.1 Points Forts', '8'),
        ('   3.2 Points Faibles', '9'),
        ('   3.3 Analyse Comparative', '10'),
        ('4. Recommandations Detaillees', '11'),
        ('   4.1 Securite', '11'),
        ('   4.2 Performance', '12'),
        ('   4.3 Code Quality', '13'),
        ('5. Ameliorations Prioritaires', '14'),
        ('   5.1 Priorite Critique', '14'),
        ('   5.2 Priorite Haute', '15'),
        ('   5.3 Priorite Moyenne', '16'),
        ('6. Evolutions pour la Production', '17'),
        ('   6.1 Infrastructure', '17'),
        ('   6.2 Fonctionnalites', '18'),
        ('   6.3 Roadmap', '19'),
    ]
    
    for item, page in toc_items:
        toc_text = f'{item}{"." * (60 - len(item))} {page}'
        story.append(Paragraph(toc_text, styles['BodyTextCustom']))
    
    story.append(PageBreak())
    
    # ============================================
    # SECTION 1: ETAT ACTUEL DU PROJET
    # ============================================
    story.append(Paragraph('<b>1. Etat Actuel du Projet</b>', styles['SectionH1']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph('<b>1.1 Resume Executif</b>', styles['SectionH2']))
    story.append(Paragraph(
        'SchoolFlow Pro (EtudePlus) est une plateforme de gestion scolaire multi-tenant de nouvelle generation, '
        'concue pour repondre aux exigences de souverainete et de conformite. Le projet presente une architecture '
        'moderne avec un frontend React/Vite et un backend FastAPI, supporte par PostgreSQL avec isolation des donnees '
        'par Row-Level Security (RLS). Le systeme integre Keycloak comme fournisseur d\'identite souverain, '
        'permettant une gestion unifiee des identites et une authentification OIDC robuste.',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        'Le projet a atteint un niveau de maturite avance avec 4 phases de developpement completees, '
        'incluant les fondations architectureales, les fonctionnalites academiques, les optimisations de performance '
        'et la documentation complete. Avec environ 155 000 lignes de code et plus de 45 composants React, '
        'le systeme offre une couverture fonctionnelle etendue couvrant la gestion administrative, academique, '
        'financiere et communicative des etablissements scolaires.',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 12))
    
    # Key metrics table
    story.append(Paragraph('<b>1.2 Metriques Cles du Projet</b>', styles['SectionH2']))
    metrics_data = [
        [Paragraph('<b>Metric</b>', styles['TableHeader']), 
         Paragraph('<b>Valeur</b>', styles['TableHeader']),
         Paragraph('<b>Commentaire</b>', styles['TableHeader'])],
        [Paragraph('Lignes de Code', styles['TableCell']), 
         Paragraph('~155,000', styles['TableCellCenter']),
         Paragraph('TypeScript, Python, SQL combines', styles['TableCell'])],
        [Paragraph('Composants React', styles['TableCell']), 
         Paragraph('45+', styles['TableCellCenter']),
         Paragraph('Composants modulaires et reutilisables', styles['TableCell'])],
        [Paragraph('Pages/Interfaces', styles['TableCell']), 
         Paragraph('25+', styles['TableCellCenter']),
         Paragraph('Dashboard, portails par role', styles['TableCell'])],
        [Paragraph('Tables PostgreSQL', styles['TableCell']), 
         Paragraph('22+', styles['TableCellCenter']),
         Paragraph('Modele relationnel complet', styles['TableCell'])],
        [Paragraph('Endpoints API', styles['TableCell']), 
         Paragraph('50+', styles['TableCellCenter']),
         Paragraph('RESTful avec documentation OpenAPI', styles['TableCell'])],
        [Paragraph('Tests E2E', styles['TableCell']), 
         Paragraph('10+', styles['TableCellCenter']),
         Paragraph('Playwright, couverture auth/RBAC', styles['TableCell'])],
        [Paragraph('Tests Backend', styles['TableCell']), 
         Paragraph('6+', styles['TableCellCenter']),
         Paragraph('Pytest avec couverture code', styles['TableCell'])],
        [Paragraph('Documentation', styles['TableCell']), 
         Paragraph('50+ pages', styles['TableCellCenter']),
         Paragraph('Guides techniques et utilisateurs', styles['TableCell'])],
        [Paragraph('Taille Bundle', styles['TableCell']), 
         Paragraph('956 KB', styles['TableCellCenter']),
         Paragraph('Gzip, optimisation Vite', styles['TableCell'])],
    ]
    story.append(Spacer(1, 8))
    story.append(create_table(metrics_data, [4*cm, 3*cm, 8*cm], styles))
    story.append(Paragraph('Tableau 1: Metriques cles du projet EtudePlus', styles['Caption']))
    story.append(Spacer(1, 12))
    
    # Implemented features
    story.append(Paragraph('<b>1.3 Fonctionnalites Implementees</b>', styles['SectionH2']))
    story.append(Paragraph(
        'Le systeme offre une couverture fonctionnelle complete organisee en modules coherents. '
        'Chaque module a ete concu pour repondre aux besoins specifiques des differents acteurs '
        'du systeme educatif (administrateurs, enseignants, eleves, parents, personnels).',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 8))
    
    features_data = [
        [Paragraph('<b>Module</b>', styles['TableHeader']), 
         Paragraph('<b>Fonctionnalites</b>', styles['TableHeader']),
         Paragraph('<b>Statut</b>', styles['TableHeader'])],
        [Paragraph('Administration', styles['TableCell']), 
         Paragraph('Gestion etablissements, utilisateurs, roles, parametrage dynamique', styles['TableCell']),
         Paragraph('Complete', styles['TableCellCenter'])],
        [Paragraph('Academique', styles['TableCell']), 
         Paragraph('Annees, niveaux, classes, matieres, emploi du temps, inscriptions', styles['TableCell']),
         Paragraph('Complete', styles['TableCellCenter'])],
        [Paragraph('Notes/Evaluations', styles['TableCell']), 
         Paragraph('Saisie notes, calcul moyennes, bulletins PDF, historique', styles['TableCell']),
         Paragraph('Complete', styles['TableCellCenter'])],
        [Paragraph('Presence', styles['TableCell']), 
         Paragraph('Marquage quotidien, statistiques, alertes, notifications parents', styles['TableCell']),
         Paragraph('Complete', styles['TableCellCenter'])],
        [Paragraph('Finance', styles['TableCell']), 
         Paragraph('Factures, paiements, rappels automatiques, rapports financiers', styles['TableCell']),
         Paragraph('Complete', styles['TableCellCenter'])],
        [Paragraph('Communication', styles['TableCell']), 
         Paragraph('Messages, annonces, notifications push, portail parents', styles['TableCell']),
         Paragraph('Complete', styles['TableCellCenter'])],
        [Paragraph('RH', styles['TableCell']), 
         Paragraph('Employes, contrats, conges, bulletins de paie', styles['TableCell']),
         Paragraph('Partiel', styles['TableCellCenter'])],
        [Paragraph('Bibliotheque', styles['TableCell']), 
         Paragraph('Gestion livres, prets, inventaire', styles['TableCell']),
         Paragraph('Partiel', styles['TableCellCenter'])],
        [Paragraph('E-Learning', styles['TableCell']), 
         Paragraph('Cours en ligne, devoirs, ressources', styles['TableCell']),
         Paragraph('Partiel', styles['TableCellCenter'])],
    ]
    story.append(Spacer(1, 8))
    story.append(create_table(features_data, [3.5*cm, 8*cm, 3*cm], styles))
    story.append(Paragraph('Tableau 2: Fonctionnalites implementees par module', styles['Caption']))
    story.append(Spacer(1, 12))
    
    # Development status
    story.append(Paragraph('<b>1.4 Statut de Developpement par Phase</b>', styles['SectionH2']))
    story.append(Paragraph(
        'Le projet a ete developpe selon une approche iterative en 4 phases majeures, chacune apportant '
        'des fonctionnalites et ameliorations specifiques. Cette approche a permis une validation progressive '
        'des choix techniques et une adaptation aux besoins utilisateurs tout au long du developpement.',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 8))
    
    phases_data = [
        [Paragraph('<b>Phase</b>', styles['TableHeader']), 
         Paragraph('<b>Objectifs</b>', styles['TableHeader']),
         Paragraph('<b>Livrables</b>', styles['TableHeader']),
         Paragraph('<b>Statut</b>', styles['TableHeader'])],
        [Paragraph('Phase 1', styles['TableCell']), 
         Paragraph('Fondations & Architecture', styles['TableCell']),
         Paragraph('Modele donnees, Auth JWT, RLS, UI base', styles['TableCell']),
         Paragraph('Complete', styles['TableCellCenter'])],
        [Paragraph('Phase 2', styles['TableCell']), 
         Paragraph('Fonctionnalites Academiques', styles['TableCell']),
         Paragraph('Annees, classes, inscriptions, notes', styles['TableCell']),
         Paragraph('Complete', styles['TableCellCenter'])],
        [Paragraph('Phase 3', styles['TableCell']), 
         Paragraph('Optimisations & Securite', styles['TableCell']),
         Paragraph('Lazy loading, PWA, caching, audit', styles['TableCell']),
         Paragraph('Complete', styles['TableCellCenter'])],
        [Paragraph('Phase 4', styles['TableCell']), 
         Paragraph('Documentation & Hardening', styles['TableCell']),
         Paragraph('Guides, FAQ, API docs, checklist', styles['TableCell']),
         Paragraph('Complete', styles['TableCellCenter'])],
        [Paragraph('Bonus', styles['TableCell']), 
         Paragraph('Parametres Dynamiques', styles['TableCell']),
         Paragraph('Logo, couleurs, customisation sans code', styles['TableCell']),
         Paragraph('Complete', styles['TableCellCenter'])],
    ]
    story.append(Spacer(1, 8))
    story.append(create_table(phases_data, [2.5*cm, 4*cm, 5.5*cm, 3*cm], styles))
    story.append(Paragraph('Tableau 3: Statut de developpement par phase', styles['Caption']))
    
    story.append(PageBreak())
    
    # ============================================
    # SECTION 2: ARCHITECTURE ET TECHNOLOGIES
    # ============================================
    story.append(Paragraph('<b>2. Architecture et Technologies</b>', styles['SectionH1']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph('<b>2.1 Stack Technique</b>', styles['SectionH2']))
    story.append(Paragraph(
        'L\'architecture technique du projet repose sur une separation claire entre le frontend et le backend, '
        'communicant via des API REST. Le choix des technologies privilegie la modernite, la performance et '
        'la maintenabilite, avec un accent particulier sur l\'ecosysteme JavaScript/TypeScript pour le frontend '
        'et Python pour le backend.',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 12))
    
    # Frontend stack
    story.append(Paragraph('<b>2.1.1 Frontend</b>', styles['SectionH3']))
    frontend_data = [
        [Paragraph('<b>Technologie</b>', styles['TableHeader']), 
         Paragraph('<b>Version</b>', styles['TableHeader']),
         Paragraph('<b>Role</b>', styles['TableHeader'])],
        [Paragraph('React', styles['TableCell']), 
         Paragraph('18.3.1', styles['TableCellCenter']),
         Paragraph('Framework UI principal', styles['TableCell'])],
        [Paragraph('TypeScript', styles['TableCell']), 
         Paragraph('5.8.3', styles['TableCellCenter']),
         Paragraph('Typage statique, securite code', styles['TableCell'])],
        [Paragraph('Vite', styles['TableCell']), 
         Paragraph('5.4.19', styles['TableCellCenter']),
         Paragraph('Bundler rapide avec SWC', styles['TableCell'])],
        [Paragraph('TanStack Query', styles['TableCell']), 
         Paragraph('5.83.0', styles['TableCellCenter']),
         Paragraph('Data fetching et caching', styles['TableCell'])],
        [Paragraph('Zustand', styles['TableCell']), 
         Paragraph('5.0.10', styles['TableCellCenter']),
         Paragraph('State management leger', styles['TableCell'])],
        [Paragraph('shadcn/ui', styles['TableCell']), 
         Paragraph('Latest', styles['TableCellCenter']),
         Paragraph('Composants UI accessibles', styles['TableCell'])],
        [Paragraph('Tailwind CSS', styles['TableCell']), 
         Paragraph('3.4.17', styles['TableCellCenter']),
         Paragraph('Styling utility-first', styles['TableCell'])],
        [Paragraph('React Router', styles['TableCell']), 
         Paragraph('6.30.1', styles['TableCellCenter']),
         Paragraph('Routing avec lazy loading', styles['TableCell'])],
        [Paragraph('Capacitor', styles['TableCell']), 
         Paragraph('8.0.1', styles['TableCellCenter']),
         Paragraph('Build mobile natif iOS/Android', styles['TableCell'])],
        [Paragraph('PWA Plugin', styles['TableCell']), 
         Paragraph('1.2.0', styles['TableCellCenter']),
         Paragraph('Support offline et caching', styles['TableCell'])],
        [Paragraph('i18next', styles['TableCell']), 
         Paragraph('25.8.0', styles['TableCellCenter']),
         Paragraph('Internationalisation (FR, EN, ES, AR, ZH)', styles['TableCell'])],
    ]
    story.append(Spacer(1, 8))
    story.append(create_table(frontend_data, [4*cm, 3*cm, 7*cm], styles))
    story.append(Paragraph('Tableau 4: Stack technique frontend', styles['Caption']))
    story.append(Spacer(1, 12))
    
    # Backend stack
    story.append(Paragraph('<b>2.1.2 Backend</b>', styles['SectionH3']))
    backend_data = [
        [Paragraph('<b>Technologie</b>', styles['TableHeader']), 
         Paragraph('<b>Version</b>', styles['TableHeader']),
         Paragraph('<b>Role</b>', styles['TableHeader'])],
        [Paragraph('FastAPI', styles['TableCell']), 
         Paragraph('Latest', styles['TableCellCenter']),
         Paragraph('Framework API asynchrone', styles['TableCell'])],
        [Paragraph('SQLAlchemy', styles['TableCell']), 
         Paragraph('Latest', styles['TableCellCenter']),
         Paragraph('ORM pour PostgreSQL', styles['TableCell'])],
        [Paragraph('Alembic', styles['TableCell']), 
         Paragraph('Latest', styles['TableCellCenter']),
         Paragraph('Migrations base de donnees', styles['TableCell'])],
        [Paragraph('Pydantic', styles['TableCell']), 
         Paragraph('v2', styles['TableCellCenter']),
         Paragraph('Validation des donnees', styles['TableCell'])],
        [Paragraph('python-keycloak', styles['TableCell']), 
         Paragraph('Latest', styles['TableCellCenter']),
         Paragraph('Integration Keycloak OIDC', styles['TableCell'])],
        [Paragraph('SlowAPI', styles['TableCell']), 
         Paragraph('Latest', styles['TableCellCenter']),
         Paragraph('Rate limiting', styles['TableCell'])],
        [Paragraph('MinIO', styles['TableCell']), 
         Paragraph('Latest', styles['TableCellCenter']),
         Paragraph('Stockage objet S3-compatible', styles['TableCell'])],
        [Paragraph('Redis', styles['TableCell']), 
         Paragraph('7-alpine', styles['TableCellCenter']),
         Paragraph('Cache et sessions', styles['TableCell'])],
    ]
    story.append(Spacer(1, 8))
    story.append(create_table(backend_data, [4*cm, 3*cm, 7*cm], styles))
    story.append(Paragraph('Tableau 5: Stack technique backend', styles['Caption']))
    story.append(Spacer(1, 12))
    
    # Infrastructure
    story.append(Paragraph('<b>2.1.3 Infrastructure</b>', styles['SectionH3']))
    infra_data = [
        [Paragraph('<b>Composant</b>', styles['TableHeader']), 
         Paragraph('<b>Technologie</b>', styles['TableHeader']),
         Paragraph('<b>Role</b>', styles['TableHeader'])],
        [Paragraph('Base de donnees', styles['TableCell']), 
         Paragraph('PostgreSQL 16', styles['TableCellCenter']),
         Paragraph('Stockage principal avec RLS', styles['TableCell'])],
        [Paragraph('Identity Provider', styles['TableCell']), 
         Paragraph('Keycloak 26.0', styles['TableCellCenter']),
         Paragraph('Authentification OIDC/SAML', styles['TableCell'])],
        [Paragraph('Containerisation', styles['TableCell']), 
         Paragraph('Docker Compose', styles['TableCellCenter']),
         Paragraph('Orchestration services', styles['TableCell'])],
        [Paragraph('CI/CD', styles['TableCell']), 
         Paragraph('GitHub Actions', styles['TableCellCenter']),
         Paragraph('Automatisation builds/deploy', styles['TableCell'])],
        [Paragraph('Monitoring', styles['TableCell']), 
         Paragraph('Prometheus + Sentry', styles['TableCellCenter']),
         Paragraph('Metriques et error tracking', styles['TableCell'])],
    ]
    story.append(Spacer(1, 8))
    story.append(create_table(infra_data, [4*cm, 4*cm, 6*cm], styles))
    story.append(Paragraph('Tableau 6: Infrastructure et services', styles['Caption']))
    story.append(Spacer(1, 12))
    
    # Multi-tenant architecture
    story.append(Paragraph('<b>2.2 Architecture Multi-Tenant</b>', styles['SectionH2']))
    story.append(Paragraph(
        'L\'architecture multi-tenant constitue le coeur de la conception systeme. Chaque etablissement (tenant) '
        'dispose d\'une isolation complete de ses donnees, garantie a la fois au niveau applicatif et base de donnees. '
        'Cette approche permet d\'heberger plusieurs etablissements sur une meme infrastructure tout en garantissant '
        'une separation stricte des donnees.',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        'Le systeme implemente un modele hybride combinant Row-Level Security (RLS) au niveau PostgreSQL '
        'et un middleware tenant au niveau applicatif. Cette double couche de protection garantit que meme '
        'en cas de defaillance d\'un niveau, l\'isolation des donnees reste assuree. Le JWT emis par Keycloak '
        'inclut systematiquement le tenant_id, permettant une verification a chaque requete.',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 12))
    
    # Tenant isolation mechanism
    story.append(Paragraph('<b>2.2.1 Mecanisme d\'Isolation</b>', styles['SectionH3']))
    isolation_data = [
        [Paragraph('<b>Niveau</b>', styles['TableHeader']), 
         Paragraph('<b>Mecanisme</b>', styles['TableHeader']),
         Paragraph('<b>Description</b>', styles['TableHeader'])],
        [Paragraph('Base de donnees', styles['TableCell']), 
         Paragraph('Row-Level Security', styles['TableCellCenter']),
         Paragraph('Chaque table comporte tenant_id, les policies RLS filtrent automatiquement', styles['TableCell'])],
        [Paragraph('Application', styles['TableCell']), 
         Paragraph('TenantMiddleware', styles['TableCellCenter']),
         Paragraph('Extraction tenant_id depuis JWT ou header X-Tenant-ID', styles['TableCell'])],
        [Paragraph('Authentification', styles['TableCell']), 
         Paragraph('JWT Claims', styles['TableCellCenter']),
         Paragraph('Keycloak injecte tenant_id dans le token', styles['TableCell'])],
        [Paragraph('Frontend', styles['TableCell']), 
         Paragraph('TenantContext', styles['TableCellCenter']),
         Paragraph('Filtrage client-side et routing par slug tenant', styles['TableCell'])],
    ]
    story.append(Spacer(1, 8))
    story.append(create_table(isolation_data, [3.5*cm, 4*cm, 6.5*cm], styles))
    story.append(Paragraph('Tableau 7: Mecanismes d\'isolation multi-tenant', styles['Caption']))
    story.append(Spacer(1, 12))
    
    # Data model
    story.append(Paragraph('<b>2.3 Modele de Donnees</b>', styles['SectionH2']))
    story.append(Paragraph(
        'Le modele de donnees comprend plus de 22 tables organisees en domaines fonctionnels coherents. '
        'La conception suit les principes de normalisation tout en optimisant pour les performances de lecture '
        'frequentes dans un contexte applicatif. Chaque table integre le tenant_id et les colonnes d\'audit '
        '(created_at, updated_at, deleted_at pour le soft-delete).',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 8))
    
    model_data = [
        [Paragraph('<b>Domaine</b>', styles['TableHeader']), 
         Paragraph('<b>Tables</b>', styles['TableHeader']),
         Paragraph('<b>Entites Principales</b>', styles['TableHeader'])],
        [Paragraph('Auth & Users', styles['TableCell']), 
         Paragraph('5', styles['TableCellCenter']),
         Paragraph('users, profiles, user_roles, permissions, tenant_security', styles['TableCell'])],
        [Paragraph('Tenants', styles['TableCell']), 
         Paragraph('3', styles['TableCellCenter']),
         Paragraph('tenants, tenant_settings, campuses', styles['TableCell'])],
        [Paragraph('Academique', styles['TableCell']), 
         Paragraph('6', styles['TableCellCenter']),
         Paragraph('academic_years, levels, classrooms, subjects, terms, departments', styles['TableCell'])],
        [Paragraph('Etudiants', styles['TableCell']), 
         Paragraph('3', styles['TableCellCenter']),
         Paragraph('students, enrollments, parent_student', styles['TableCell'])],
        [Paragraph('Evaluation', styles['TableCell']), 
         Paragraph('3', styles['TableCellCenter']),
         Paragraph('grades, assessments, attendance', styles['TableCell'])],
        [Paragraph('Finance', styles['TableCell']), 
         Paragraph('3', styles['TableCellCenter']),
         Paragraph('invoices, payments, payment_methods', styles['TableCell'])],
        [Paragraph('RH', styles['TableCell']), 
         Paragraph('4', styles['TableCellCenter']),
         Paragraph('employees, contracts, leave_requests, payslips', styles['TableCell'])],
        [Paragraph('Communication', styles['TableCell']), 
         Paragraph('3', styles['TableCellCenter']),
         Paragraph('notifications, messages, push_subscriptions', styles['TableCell'])],
        [Paragraph('Audit & RGPD', styles['TableCell']), 
         Paragraph('3', styles['TableCellCenter']),
         Paragraph('audit_logs, account_deletion_requests, rgpd_logs', styles['TableCell'])],
    ]
    story.append(Spacer(1, 8))
    story.append(create_table(model_data, [3.5*cm, 2*cm, 8.5*cm], styles))
    story.append(Paragraph('Tableau 8: Modele de donnees par domaine fonctionnel', styles['Caption']))
    
    story.append(PageBreak())
    
    # ============================================
    # SECTION 3: POINTS FORTS ET POINTS FAIBLES
    # ============================================
    story.append(Paragraph('<b>3. Points Forts et Points Faibles</b>', styles['SectionH1']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph('<b>3.1 Points Forts</b>', styles['SectionH2']))
    story.append(Paragraph(
        'Le projet presente de nombreux atouts qui le positionnent favorablement pour une mise en production. '
        'Les choix architecturaux et techniques temoignent d\'une reflexion approfondie sur les besoins '
        'd\'un systeme de gestion scolaire moderne et scalable.',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 12))
    
    strengths = [
        ('Architecture Multi-Tenant Robuste', 
         'L\'isolation des donnees par RLS au niveau PostgreSQL, combinee au middleware applicatif, '
         'offre une garantie de securite forte. Chaque tenant est completement isole, permettant '
         'd\'heberger des centaines d\'etablissements sur une meme infrastructure sans risque de fuite de donnees.'),
        ('Authentification Souveraine avec Keycloak',
         'L\'integration de Keycloak comme fournisseur d\'identite OIDC permet une gestion unifiee des identites, '
         'supportant SSO, MFA, et federation avec des annuaires externes (LDAP, AD). Cette approche repond '
         'aux exigences de souverainete des donnees pour les etablissements publics.'),
        ('Couverture Fonctionnelle Complete',
         'Le systeme couvre l\'ensemble des processus metier d\'un etablissement scolaire: inscriptions, '
         'notes, absences, facturation, communication, RH. Les 45+ composants React offrent une UX riche '
         'et coherente pour tous les profils utilisateurs.'),
        ('Stack Moderne et Performante',
         'L\'utilisation de React 18 avec Vite, TypeScript strict mode, et TanStack Query garantit '
         'une experience developpeur optimale et des performances frontend excellentes (bundle 956KB gzip).'),
        ('PWA et Support Mobile',
         'L\'application est configurable en PWA avec support offline et push notifications. '
         'Capacitor permet la generation d\'applications natives iOS/Android sans reecriture du code.'),
        ('Documentation Complete',
         'Plus de 50 pages de documentation technique et utilisateur, guides en francais et anglais, '
         'facilitant l\'onboarding des nouvelles equipes et la maintenance.'),
        ('CI/CD et DevOps Ready',
         'Pipeline GitHub Actions complet avec tests automatises, security scanning, deploiement staging/production. '
         'Configuration Docker Compose pour le developpement local et le deploiement.'),
        ('Internationalisation Native',
         'Support de 5 langues (FR, EN, ES, AR, ZH) avec i18next, permettant un deploiement international.'),
    ]
    
    for title, desc in strengths:
        story.append(Paragraph(f'<b>{title}</b>', styles['SectionH3']))
        story.append(Paragraph(desc, styles['BodyTextJustify']))
        story.append(Spacer(1, 8))
    
    story.append(Spacer(1, 12))
    
    # Weaknesses
    story.append(Paragraph('<b>3.2 Points Faibles et Risques</b>', styles['SectionH2']))
    story.append(Paragraph(
        'Malgre ses qualites, le projet presente des points d\'attention qui devront etre adresses '
        'avant une mise en production a grande echelle. Ces elements representent des risques potentiels '
        'qu\'il convient de mitiguer.',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 12))
    
    weaknesses_data = [
        [Paragraph('<b>Point Faible</b>', styles['TableHeader']), 
         Paragraph('<b>Impact</b>', styles['TableHeader']),
         Paragraph('<b>Risque</b>', styles['TableHeader']),
         Paragraph('<b>Recommandation</b>', styles['TableHeader'])],
        [Paragraph('Couverture de tests insuffisante', styles['TableCell']), 
         Paragraph('Moyen', styles['TableCellCenter']),
         Paragraph('Eleve', styles['TableCellCenter']),
         Paragraph('Augmenter couverture a 80%+', styles['TableCell'])],
        [Paragraph('Absence de tests de charge', styles['TableCell']), 
         Paragraph('Eleve', styles['TableCellCenter']),
         Paragraph('Moyen', styles['TableCellCenter']),
         Paragraph('Implementer k6/Locust tests', styles['TableCell'])],
        [Paragraph('Documentation API incomplete', styles['TableCell']), 
         Paragraph('Moyen', styles['TableCellCenter']),
         Paragraph('Moyen', styles['TableCellCenter']),
         Paragraph('Completer OpenAPI specs', styles['TableCell'])],
        [Paragraph('Gestion des erreurs frontend', styles['TableCell']), 
         Paragraph('Moyen', styles['TableCellCenter']),
         Paragraph('Moyen', styles['TableCellCenter']),
         Paragraph('Error boundaries + logging', styles['TableCell'])],
        [Paragraph('Secrets management', styles['TableCell']), 
         Paragraph('Eleve', styles['TableCellCenter']),
         Paragraph('Eleve', styles['TableCellCenter']),
         Paragraph('HashiCorp Vault / AWS Secrets', styles['TableCell'])],
        [Paragraph('Monitoring productif absent', styles['TableCell']), 
         Paragraph('Eleve', styles['TableCellCenter']),
         Paragraph('Eleve', styles['TableCellCenter']),
         Paragraph('Grafana + alerting', styles['TableCell'])],
        [Paragraph('Rate limiting basique', styles['TableCell']), 
         Paragraph('Moyen', styles['TableCellCenter']),
         Paragraph('Moyen', styles['TableCellCenter']),
         Paragraph('Rate limiting par utilisateur', styles['TableCell'])],
        [Paragraph('Backup/DR non teste', styles['TableCell']), 
         Paragraph('Critique', styles['TableCellCenter']),
         Paragraph('Eleve', styles['TableCellCenter']),
         Paragraph('Tests de restauration reguliers', styles['TableCell'])],
    ]
    story.append(Spacer(1, 8))
    story.append(create_table(weaknesses_data, [4.5*cm, 2*cm, 2*cm, 5.5*cm], styles))
    story.append(Paragraph('Tableau 9: Analyse des points faibles et recommandations', styles['Caption']))
    story.append(Spacer(1, 12))
    
    # Comparative analysis
    story.append(Paragraph('<b>3.3 Analyse Comparative des Points Cles</b>', styles['SectionH2']))
    story.append(Paragraph(
        'L\'evaluation suivante positionne le projet sur les dimensions critiques pour une mise en production. '
        'Chaque dimension est notee sur une echelle de 1 a 5, avec identification des actions correctives prioritaires.',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 8))
    
    comparative_data = [
        [Paragraph('<b>Dimension</b>', styles['TableHeader']), 
         Paragraph('<b>Note</b>', styles['TableHeader']),
         Paragraph('<b>Statut</b>', styles['TableHeader']),
         Paragraph('<b>Commentaire</b>', styles['TableHeader'])],
        [Paragraph('Securite', styles['TableCell']), 
         Paragraph('4/5', styles['TableCellCenter']),
         Paragraph('Bon', styles['TableCellCenter']),
         Paragraph('RLS + Keycloak solides, secrets management a ameliorer', styles['TableCell'])],
        [Paragraph('Performance', styles['TableCell']), 
         Paragraph('4/5', styles['TableCellCenter']),
         Paragraph('Bon', styles['TableCellCenter']),
         Paragraph('Frontend optimise, tests de charge manquants', styles['TableCell'])],
        [Paragraph('Scalabilite', styles['TableCell']), 
         Paragraph('3/5', styles['TableCellCenter']),
         Paragraph('Moyen', styles['TableCellCenter']),
         Paragraph('Architecture mono-service, passage microservices envisageable', styles['TableCell'])],
        [Paragraph('Maintenabilite', styles['TableCell']), 
         Paragraph('4/5', styles['TableCellCenter']),
         Paragraph('Bon', styles['TableCellCenter']),
         Paragraph('Code bien structure, documentation presente', styles['TableCell'])],
        [Paragraph('Testabilite', styles['TableCell']), 
         Paragraph('2/5', styles['TableCellCenter']),
         Paragraph('Insuffisant', styles['TableCellCenter']),
         Paragraph('Couverture tests faible, tests d\'integration a completer', styles['TableCell'])],
        [Paragraph('Observabilite', styles['TableCell']), 
         Paragraph('3/5', styles['TableCellCenter']),
         Paragraph('Moyen', styles['TableCellCenter']),
         Paragraph('Sentry integre, dashboards monitoring a creer', styles['TableCell'])],
        [Paragraph('Documentation', styles['TableCell']), 
         Paragraph('5/5', styles['TableCellCenter']),
         Paragraph('Excellent', styles['TableCellCenter']),
         Paragraph('Documentation complete et bien organisee', styles['TableCell'])],
        [Paragraph('DevOps/CI-CD', styles['TableCell']), 
         Paragraph('4/5', styles['TableCellCenter']),
         Paragraph('Bon', styles['TableCellCenter']),
         Paragraph('Pipeline complet, deploiement automatisable', styles['TableCell'])],
    ]
    story.append(Spacer(1, 8))
    story.append(create_table(comparative_data, [3.5*cm, 2*cm, 2.5*cm, 6*cm], styles))
    story.append(Paragraph('Tableau 10: Evaluation comparative des dimensions critiques', styles['Caption']))
    
    story.append(PageBreak())
    
    # ============================================
    # SECTION 4: RECOMMANDATIONS DETAILLEES
    # ============================================
    story.append(Paragraph('<b>4. Recommandations Detaillees</b>', styles['SectionH1']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph('<b>4.1 Recommandations Securite</b>', styles['SectionH2']))
    story.append(Paragraph(
        'La securite constitue un pilier fondamental pour un systeme de gestion scolaire manipulant '
        'des donnees sensibles (notes, informations personnelles, donnees financieres). Les recommandations '
        'suivantes visent a renforcer la posture de securite du systeme.',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 12))
    
    security_recs = [
        ('Gestion des Secrets',
         'Implementer une solution de gestion des secrets (HashiCorp Vault, AWS Secrets Manager, ou Azure KeyVault). '
         'Les secrets ne doivent jamais etre stockes en clair dans le code ou les fichiers de configuration. '
         'Utiliser les Docker Secrets pour le deploiement en conteneurs.'),
        ('Chiffrement des Donnees Sensibles',
         'Mettre en place le chiffrement au repos pour les donnees sensibles (PII, donnees financieres). '
         'PostgreSQL offre le chiffrement transparent des donnees (TDE) et les colonnes chiffrees via pgcrypto. '
         'Les sauvegardes doivent egalement etre chiffrees.'),
        ('Audit Logging Renforce',
         'Etendre le systeme d\'audit existant pour capturer tous les acces aux donnees sensibles. '
         'Implementer des alertes automatiques sur les patterns suspects (acces massifs, modifications hors heures). '
         'Conserver les logs d\'audit pendant la duree legale (5 ans selon RGPD).'),
        ('Penetration Testing',
         'Realiser un audit de securite externe (pentest) avant la mise en production. '
         'Corriger les vulnerabilites identifiees selon leur severite. '
         'Planifier des tests reguliers (annuels minimum).'),
        ('MFA Obligatoire',
         'Rendre le MFA obligatoire pour les roles privilegies (SUPER_ADMIN, TENANT_ADMIN, ACCOUNTANT). '
         'Supporter plusieurs methodes (TOTP, SMS, cles materiels). '
         'Implementer des codes de recuperation securises.'),
        ('Headers de Securite HTTP',
         'Configurer les headers de securite: Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, '
         'Strict-Transport-Security. Utiliser helmet-like middleware pour FastAPI.'),
    ]
    
    for title, desc in security_recs:
        story.append(Paragraph(f'<b>{title}</b>', styles['SectionH3']))
        story.append(Paragraph(desc, styles['BodyTextJustify']))
        story.append(Spacer(1, 6))
    
    story.append(Spacer(1, 12))
    
    # Performance recommendations
    story.append(Paragraph('<b>4.2 Recommandations Performance</b>', styles['SectionH2']))
    story.append(Paragraph(
        'Les performances utilisateurs et systeme impactent directement l\'experience et les couts d\'infrastructure. '
        'Les optimisations suivantes permettront de garantir des temps de reponse optimaux meme sous charge.',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 12))
    
    perf_recs = [
        ('Indexation Base de Donnees',
         'Analyser les requetes lentes avec pg_stat_statements et ajouter les index manquants. '
         'Les colonnes frequently filtered (tenant_id, user_id, created_at) doivent etre indexees. '
         'Considerer les index composites pour les requetes frequentes.'),
        ('Cache Redis Multi-Niveau',
         'Etendre l\'utilisation de Redis pour le caching des donnees de reference (niveaux, matieres, parametres). '
         'Implementer le cache-aside pattern avec invalidation intelligente. '
         'Utiliser Redis pour les sessions utilisateurs et la rate limiting distribuee.'),
        ('Connection Pooling',
         'Configurer PgBouncer pour le pooling de connexions PostgreSQL. '
         'Limiter le nombre de connexions par service pour eviter la saturation. '
         'Monitorer l\'utilisation du pool et ajuster les parametres.'),
        ('CDN et Assets Optimization',
         'Servir les assets statiques (images, CSS, JS) via un CDN (CloudFront, Cloudflare). '
         'Implementer le cache-busting pour les mises a jour. '
         'Optimiser les images avec conversion WebP/AVIF automatique.'),
        ('Database Read Replicas',
         'Configurer des read replicas pour distribuer la charge de lecture. '
         'Router les requetes de lecture vers les replicas via le middleware. '
         'Utiliser les replicas pour les rapports et analyses lourds.'),
        ('Lazy Loading et Code Splitting',
         'Etendre le lazy loading a tous les modules non-critiques. '
         'Prefetcher les ressources probables lors des temps morts. '
         'Monitorer le bundle size dans le CI pour eviter les regressions.'),
    ]
    
    for title, desc in perf_recs:
        story.append(Paragraph(f'<b>{title}</b>', styles['SectionH3']))
        story.append(Paragraph(desc, styles['BodyTextJustify']))
        story.append(Spacer(1, 6))
    
    story.append(Spacer(1, 12))
    
    # Code quality recommendations
    story.append(Paragraph('<b>4.3 Recommandations Qualite Code</b>', styles['SectionH2']))
    story.append(Paragraph(
        'La qualite du code impacte la maintenabilite, la fiabilite et la velocite de l\'equipe. '
        'Les pratiques suivantes permettront d\'ameliorer progressivement la base de code.',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 12))
    
    quality_recs = [
        ('Augmentation de la Couverture de Tests',
         'Objectif: 80% de couverture minimum sur le code metier critique. '
         'Prioriser les tests sur: authentification, isolation tenant, calculs financiers, workflows academiques. '
         'Implementer des tests de mutation pour verifier l\'efficacite des tests.'),
        ('Tests d\'Integration End-to-End',
         'Etendre les tests Playwright pour couvrir les workflows critiques complets. '
         'Inclure des tests de non-regression pour chaque bug corrige. '
         'Automatiser l\'execution des tests dans le pipeline CI/CD.'),
        ('Linting et Formatting Strict',
         'Configurer ESLint et Prettier avec des regles strictes. '
         'Interdire les warnings dans le CI (fail_on_warning: true). '
         'Ajouter des regles specifiques: no-any TypeScript, imports absolus.'),
        ('Code Review Process',
         'Etablir un processus de code review obligatoire avec checklist. '
         'Utiliser les Pull Request templates. '
         'Requerir l\'approbation d\'au moins un reviewer senior.'),
        ('Technical Debt Tracking',
         'Documenter la dette technique avec des TODO commentes et des issues GitHub. '
         'Allouer 20% du temps sprint a la reduction de la dette. '
         'Mesurer et monitorer les metriques de qualite (complexite cyclomatique, duplication).'),
    ]
    
    for title, desc in quality_recs:
        story.append(Paragraph(f'<b>{title}</b>', styles['SectionH3']))
        story.append(Paragraph(desc, styles['BodyTextJustify']))
        story.append(Spacer(1, 6))
    
    story.append(PageBreak())
    
    # ============================================
    # SECTION 5: AMELIORATIONS PRIORITAIRES
    # ============================================
    story.append(Paragraph('<b>5. Ameliorations Prioritaires</b>', styles['SectionH1']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        'Les ameliorations suivantes sont classees par priorite en fonction de leur impact sur la stabilite, '
        'la securite et l\'experience utilisateur. Chaque priorite est accompagnee d\'une estimation '
        'de l\'effort et des dependances.',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 12))
    
    # Priority Critical
    story.append(Paragraph('<b>5.1 Priorite Critique (Avant Production)</b>', styles['SectionH2']))
    story.append(Paragraph(
        'Ces elements doivent etre adresses imperativement avant toute mise en production. '
        'Leur absence represente un risque majeur pour la securite ou la stabilite du systeme.',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 8))
    
    critical_data = [
        [Paragraph('<b>Ameleoration</b>', styles['TableHeader']), 
         Paragraph('<b>Description</b>', styles['TableHeader']),
         Paragraph('<b>Effort</b>', styles['TableHeader']),
         Paragraph('<b>Dependances</b>', styles['TableHeader'])],
        [Paragraph('Secrets Management', styles['TableCell']), 
         Paragraph('Migrer vers Vault ou equivalent pour tous les secrets', styles['TableCell']),
         Paragraph('3-5 jours', styles['TableCellCenter']),
         Paragraph('Infrastructure', styles['TableCell'])],
        [Paragraph('Backup & Restore', styles['TableCell']), 
         Paragraph('Tester et documenter le processus de restauration', styles['TableCell']),
         Paragraph('2-3 jours', styles['TableCellCenter']),
         Paragraph('Ops', styles['TableCell'])],
        [Paragraph('Tests Critiques', styles['TableCell']), 
         Paragraph('Ajouter tests pour auth, RLS, finance', styles['TableCell']),
         Paragraph('5-7 jours', styles['TableCellCenter']),
         Paragraph('QA', styles['TableCell'])],
        [Paragraph('Monitoring Alerting', styles['TableCell']), 
         Paragraph('Configurer Grafana dashboards et alertes', styles['TableCell']),
         Paragraph('3-4 jours', styles['TableCellCenter']),
         Paragraph('Infrastructure', styles['TableCell'])],
        [Paragraph('Security Headers', styles['TableCell']), 
         Paragraph('Implementer CSP, HSTS, X-Frame-Options', styles['TableCell']),
         Paragraph('1-2 jours', styles['TableCellCenter']),
         Paragraph('Backend', styles['TableCell'])],
        [Paragraph('Rate Limiting Avance', styles['TableCell']), 
         Paragraph('Limite par utilisateur + endpoint sensible', styles['TableCell']),
         Paragraph('2-3 jours', styles['TableCellCenter']),
         Paragraph('Backend', styles['TableCell'])],
    ]
    story.append(Spacer(1, 8))
    story.append(create_table(critical_data, [3.5*cm, 5.5*cm, 2.5*cm, 3.5*cm], styles))
    story.append(Paragraph('Tableau 11: Ameliorations prioritaires critiques', styles['Caption']))
    story.append(Spacer(1, 12))
    
    # Priority High
    story.append(Paragraph('<b>5.2 Priorite Haute (Premier Mois)</b>', styles['SectionH2']))
    story.append(Paragraph(
        'Ces ameliorations devraient etre implementees dans le premier mois suivant la mise en production '
        'pour garantir une experience utilisateur optimale et une operationnalite complete.',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 8))
    
    high_data = [
        [Paragraph('<b>Ameleoration</b>', styles['TableHeader']), 
         Paragraph('<b>Description</b>', styles['TableHeader']),
         Paragraph('<b>Effort</b>', styles['TableHeader']),
         Paragraph('<b>Dependances</b>', styles['TableHeader'])],
        [Paragraph('Tests de Charge', styles['TableCell']), 
         Paragraph('Implementer tests k6 pour valider 1000 users concurrent', styles['TableCell']),
         Paragraph('5-7 jours', styles['TableCellCenter']),
         Paragraph('Dev + Ops', styles['TableCell'])],
        [Paragraph('Error Tracking Frontend', styles['TableCell']), 
         Paragraph('Etendre Sentry avec context utilisateur et breadcrumbs', styles['TableCell']),
         Paragraph('2-3 jours', styles['TableCellCenter']),
         Paragraph('Frontend', styles['TableCell'])],
        [Paragraph('API Documentation', styles['TableCell']), 
         Paragraph('Completer specs OpenAPI pour tous endpoints', styles['TableCell']),
         Paragraph('3-4 jours', styles['TableCellCenter']),
         Paragraph('Backend', styles['TableCell'])],
        [Paragraph('Index Database', styles['TableCell']), 
         Paragraph('Analyser et ajouter index manquants', styles['TableCell']),
         Paragraph('2-3 jours', styles['TableCellCenter']),
         Paragraph('DBA', styles['TableCell'])],
        [Paragraph('Cache Strategy', styles['TableCell']), 
         Paragraph('Implementer caching Redis pour donnees de reference', styles['TableCell']),
         Paragraph('3-4 jours', styles['TableCellCenter']),
         Paragraph('Backend', styles['TableCell'])],
        [Paragraph('MFA Obligatoire Admin', styles['TableCell']), 
         Paragraph('Rendre MFA obligatoire pour roles admin', styles['TableCell']),
         Paragraph('2-3 jours', styles['TableCellCenter']),
         Paragraph('Keycloak', styles['TableCell'])],
        [Paragraph('Audit Trail Complet', styles['TableCell']), 
         Paragraph('Logger tous acces donnees sensibles', styles['TableCell']),
         Paragraph('3-4 jours', styles['TableCellCenter']),
         Paragraph('Backend', styles['TableCell'])],
    ]
    story.append(Spacer(1, 8))
    story.append(create_table(high_data, [3.5*cm, 5.5*cm, 2.5*cm, 3.5*cm], styles))
    story.append(Paragraph('Tableau 12: Ameliorations prioritaires hautes', styles['Caption']))
    story.append(Spacer(1, 12))
    
    # Priority Medium
    story.append(Paragraph('<b>5.3 Priorite Moyenne (Premier Trimestre)</b>', styles['SectionH2']))
    story.append(Paragraph(
        'Ces ameliorations contribuent a la qualite globale du systeme et a l\'amelioration '
        'continue de l\'experience utilisateur.',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 8))
    
    medium_data = [
        [Paragraph('<b>Ameleoration</b>', styles['TableHeader']), 
         Paragraph('<b>Description</b>', styles['TableHeader']),
         Paragraph('<b>Effort</b>', styles['TableHeader']),
         Paragraph('<b>Dependances</b>', styles['TableHeader'])],
        [Paragraph('Coverage Tests 80%', styles['TableCell']), 
         Paragraph('Atteindre 80% couverture sur code metier', styles['TableCell']),
         Paragraph('10-15 jours', styles['TableCellCenter']),
         Paragraph('Dev Team', styles['TableCell'])],
        [Paragraph('CDN Integration', styles['TableCell']), 
         Paragraph('Servir assets via CloudFront/Cloudflare', styles['TableCell']),
         Paragraph('2-3 jours', styles['TableCellCenter']),
         Paragraph('Infrastructure', styles['TableCell'])],
        [Paragraph('Read Replicas', styles['TableCell']), 
         Paragraph('Configurer replicas pour distribuer charge lecture', styles['TableCell']),
         Paragraph('3-5 jours', styles['TableCellCenter']),
         Paragraph('DBA + Backend', styles['TableCell'])],
        [Paragraph('i18n Completion', styles['TableCell']), 
         Paragraph('Completer traductions et ajouter langues', styles['TableCell']),
         Paragraph('5-7 jours', styles['TableCellCenter']),
         Paragraph('Frontend', styles['TableCell'])],
        [Paragraph('Performance Budget', styles['TableCell']), 
         Paragraph('Definir et monitorer budgets performance', styles['TableCell']),
         Paragraph('2-3 jours', styles['TableCellCenter']),
         Paragraph('Dev Team', styles['TableCell'])],
        [Paragraph('Accessibility Audit', styles['TableCell']), 
         Paragraph('Audit WCAG 2.1 et corrections', styles['TableCell']),
         Paragraph('5-7 jours', styles['TableCellCenter']),
         Paragraph('Frontend + UX', styles['TableCell'])],
    ]
    story.append(Spacer(1, 8))
    story.append(create_table(medium_data, [3.5*cm, 5.5*cm, 2.5*cm, 3.5*cm], styles))
    story.append(Paragraph('Tableau 13: Ameliorations prioritaires moyennes', styles['Caption']))
    
    story.append(PageBreak())
    
    # ============================================
    # SECTION 6: EVOLUTIONS POUR LA PRODUCTION
    # ============================================
    story.append(Paragraph('<b>6. Evolutions pour un Deploiement 100% Product-Ready</b>', styles['SectionH1']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph('<b>6.1 Evolutions Infrastructure</b>', styles['SectionH2']))
    story.append(Paragraph(
        'L\'evolution vers une infrastructure production-ready necessite des investissements '
        'dans la resilience, la scalabilite et l\'observabilite. L\'architecture cible devrait '
        'supporter une montee en charge progressive tout en garantissant un SLA de 99.9%.',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph('<b>6.1.1 Architecture Cible</b>', styles['SectionH3']))
    story.append(Paragraph(
        'L\'architecture de production recommandee s\'articule autour des composants suivants: '
        'un load balancer (AWS ALB ou equivalent) distribuant le trafic vers plusieurs instances '
        'de l\'application, une base de donnees PostgreSQL en mode Primary-Replica avec failover automatique, '
        'un cluster Redis pour le caching distribue, et un cluster Kubernetes pour l\'orchestration des services.',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 8))
    
    infra_evo_data = [
        [Paragraph('<b>Composant</b>', styles['TableHeader']), 
         Paragraph('<b>Actuel</b>', styles['TableHeader']),
         Paragraph('<b>Cible</b>', styles['TableHeader']),
         Paragraph('<b>Benefice</b>', styles['TableHeader'])],
        [Paragraph('Orchestration', styles['TableCell']), 
         Paragraph('Docker Compose', styles['TableCellCenter']),
         Paragraph('Kubernetes (EKS/GKE)', styles['TableCellCenter']),
         Paragraph('Scalabilite, auto-healing', styles['TableCell'])],
        [Paragraph('Base de Donnees', styles['TableCell']), 
         Paragraph('PostgreSQL single', styles['TableCellCenter']),
         Paragraph('RDS Multi-AZ', styles['TableCellCenter']),
         Paragraph('HA, automated failover', styles['TableCell'])],
        [Paragraph('Cache', styles['TableCell']), 
         Paragraph('Redis single', styles['TableCellCenter']),
         Paragraph('ElastiCache Cluster', styles['TableCellCenter']),
         Paragraph('HA, distributed cache', styles['TableCell'])],
        [Paragraph('Storage', styles['TableCell']), 
         Paragraph('MinIO local', styles['TableCellCenter']),
         Paragraph('S3 compatible', styles['TableCellCenter']),
         Paragraph('Durability, CDN integration', styles['TableCell'])],
        [Paragraph('Monitoring', styles['TableCell']), 
         Paragraph('Sentry only', styles['TableCellCenter']),
         Paragraph('Prometheus + Grafana', styles['TableCellCenter']),
         Paragraph('Full observability', styles['TableCell'])],
        [Paragraph('CDN', styles['TableCell']), 
         Paragraph('None', styles['TableCellCenter']),
         Paragraph('CloudFront/Cloudflare', styles['TableCellCenter']),
         Paragraph('Latency, DDoS protection', styles['TableCell'])],
        [Paragraph('Secrets', styles['TableCell']), 
         Paragraph('Env variables', styles['TableCellCenter']),
         Paragraph('HashiCorp Vault', styles['TableCellCenter']),
         Paragraph('Security, rotation', styles['TableCell'])],
    ]
    story.append(Spacer(1, 8))
    story.append(create_table(infra_evo_data, [3*cm, 3*cm, 4*cm, 5*cm], styles))
    story.append(Paragraph('Tableau 14: Evolutions infrastructure cibles', styles['Caption']))
    story.append(Spacer(1, 12))
    
    # Functional evolutions
    story.append(Paragraph('<b>6.2 Evolutions Fonctionnelles</b>', styles['SectionH2']))
    story.append(Paragraph(
        'Au-dela des aspects techniques, le systeme peut etre enrichi de fonctionnalites '
        'apportant une valeur ajoutee significative aux utilisateurs et permettant de se '
        'differencier sur le marche.',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 12))
    
    func_evo_data = [
        [Paragraph('<b>Fonctionnalite</b>', styles['TableHeader']), 
         Paragraph('<b>Description</b>', styles['TableHeader']),
         Paragraph('<b>Effort</b>', styles['TableHeader']),
         Paragraph('<b>Priorite</b>', styles['TableHeader'])],
        [Paragraph('Tableau de Bord Analytics', styles['TableCell']), 
         Paragraph('Dashboards personnalises avec KPIs et visualisations', styles['TableCell']),
         Paragraph('15-20 jours', styles['TableCellCenter']),
         Paragraph('Haute', styles['TableCellCenter'])],
        [Paragraph('Module E-Learning', styles['TableCell']), 
         Paragraph('Cours en ligne, videos, quizzes interactifs', styles['TableCell']),
         Paragraph('30-40 jours', styles['TableCellCenter']),
         Paragraph('Moyenne', styles['TableCellCenter'])],
        [Paragraph('Application Mobile Native', styles['TableCell']), 
         Paragraph('Apps iOS/Android avec Capacitor ou React Native', styles['TableCell']),
         Paragraph('20-30 jours', styles['TableCellCenter']),
         Paragraph('Haute', styles['TableCellCenter'])],
        [Paragraph('Intelligence Artificielle', styles['TableCell']), 
         Paragraph('Predictions reussite, recommandations personnalisees', styles['TableCell']),
         Paragraph('25-35 jours', styles['TableCellCenter']),
         Paragraph('Moyenne', styles['TableCellCenter'])],
        [Paragraph('Integration Paiement', styles['TableCell']), 
         Paragraph('Stripe/PayPal pour paiements en ligne', styles['TableCell']),
         Paragraph('10-15 jours', styles['TableCellCenter']),
         Paragraph('Haute', styles['TableCellCenter'])],
        [Paragraph('Portail Parents Avance', styles['TableCell']), 
         Paragraph('Suivi temps reel, messagerie, rendez-vous', styles['TableCell']),
         Paragraph('15-20 jours', styles['TableCellCenter']),
         Paragraph('Haute', styles['TableCellCenter'])],
        [Paragraph('Module Bibliotheque', styles['TableCell']), 
         Paragraph('Gestion complete prets, reservations, inventaire', styles['TableCell']),
         Paragraph('15-20 jours', styles['TableCellCenter']),
         Paragraph('Basse', styles['TableCellCenter'])],
        [Paragraph('Integration Calendrier', styles['TableCell']), 
         Paragraph('Sync Google Calendar, Outlook, iCal', styles['TableCell']),
         Paragraph('5-10 jours', styles['TableCellCenter']),
         Paragraph('Moyenne', styles['TableCellCenter'])],
        [Paragraph('API Publique', styles['TableCell']), 
         Paragraph('API REST publique pour integrations tierces', styles['TableCell']),
         Paragraph('10-15 jours', styles['TableCellCenter']),
         Paragraph('Moyenne', styles['TableCellCenter'])],
        [Paragraph('Marketplace Plugins', styles['TableCell']), 
         Paragraph('Systeme de plugins pour extensions tierces', styles['TableCell']),
         Paragraph('40-50 jours', styles['TableCellCenter']),
         Paragraph('Basse', styles['TableCellCenter'])],
    ]
    story.append(Spacer(1, 8))
    story.append(create_table(func_evo_data, [4*cm, 6*cm, 2.5*cm, 2.5*cm], styles))
    story.append(Paragraph('Tableau 15: Evolutions fonctionnelles proposees', styles['Caption']))
    story.append(Spacer(1, 12))
    
    # Roadmap
    story.append(Paragraph('<b>6.3 Roadmap Recommandee</b>', styles['SectionH2']))
    story.append(Paragraph(
        'La feuille de route suivante propose une progression realiste vers un systeme '
        '100% product-ready, en alignant les priorites techniques et fonctionnelles.',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 8))
    
    roadmap_data = [
        [Paragraph('<b>Periode</b>', styles['TableHeader']), 
         Paragraph('<b>Objectifs</b>', styles['TableHeader']),
         Paragraph('<b>Livrables</b>', styles['TableHeader'])],
        [Paragraph('Semaine 1-2', styles['TableCell']), 
         Paragraph('Hardening Securite', styles['TableCell']),
         Paragraph('Secrets management, security headers, MFA admin', styles['TableCell'])],
        [Paragraph('Semaine 3-4', styles['TableCell']), 
         Paragraph('Infrastructure Product-Ready', styles['TableCell']),
         Paragraph('Kubernetes, RDS Multi-AZ, monitoring complet', styles['TableCell'])],
        [Paragraph('Mois 2', styles['TableCell']), 
         Paragraph('Tests & Qualite', styles['TableCell']),
         Paragraph('Couverture 80%, tests charge, pentest', styles['TableCell'])],
        [Paragraph('Mois 3', styles['TableCell']), 
         Paragraph('Fonctionnalites Cle', styles['TableCell']),
         Paragraph('Paiement en ligne, mobile app MVP', styles['TableCell'])],
        [Paragraph('Mois 4-6', styles['TableCell']), 
         Paragraph('Enrichissement', styles['TableCell']),
         Paragraph('Analytics, e-learning, API publique', styles['TableCell'])],
        [Paragraph('Mois 6-12', styles['TableCell']), 
         Paragraph('Innovation', styles['TableCell']),
         Paragraph('AI/ML features, marketplace, integrations', styles['TableCell'])],
    ]
    story.append(Spacer(1, 8))
    story.append(create_table(roadmap_data, [3*cm, 4*cm, 8*cm], styles))
    story.append(Paragraph('Tableau 16: Roadmap de mise en production', styles['Caption']))
    story.append(Spacer(1, 20))
    
    # Conclusion
    story.append(Paragraph('<b>Conclusion</b>', styles['SectionH1']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        'SchoolFlow Pro (EtudePlus) represente une base solide pour un systeme de gestion scolaire moderne. '
        'L\'architecture multi-tenant bien concue, l\'integration de Keycloak pour l\'identite souveraine, '
        'et la couverture fonctionnelle etendue constituent des atouts majeurs. Cependant, plusieurs aspects '
        'necessitent des ameliorations avant une mise en production a grande echelle: la couverture de tests, '
        'la gestion des secrets, le monitoring operationnel et les tests de charge.',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        'En suivant la roadmap proposee et en adressant les points critiques identifies, le projet peut '
        'atteindre un niveau de maturite product-ready en 2 a 3 mois. L\'investissement dans la qualite '
        'et la securite en amont permettra de garantir une exploitation sereine et une experience utilisateur '
        'optimale pour les etablissements scolaires utilisateurs de la plateforme.',
        styles['BodyTextJustify']
    ))
    story.append(Spacer(1, 20))
    
    # Build PDF
    doc.build(story)
    print(f"PDF generated: {output_path}")
    return output_path

if __name__ == "__main__":
    build_report()
