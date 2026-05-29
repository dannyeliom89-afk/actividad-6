"""
Utilidades del sistema — Generación de reportes PDF.
"""
from io import BytesIO
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image as RLImage, PageBreak
)
from reportlab.platypus.flowables import KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os


# Paleta de colores institucional
COLOR_PRIMARIO = colors.HexColor('#1a237e')    # Azul marino
COLOR_SECUNDARIO = colors.HexColor('#283593')  # Azul
COLOR_ACENTO = colors.HexColor('#e53935')      # Rojo
COLOR_GRIS = colors.HexColor('#546e7a')
COLOR_CLARO = colors.HexColor('#e8eaf6')
COLOR_BLANCO = colors.white


def get_styles():
    """Retorna estilos personalizados para el PDF."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='TituloDoc',
        parent=styles['Title'],
        fontSize=20,
        textColor=COLOR_PRIMARIO,
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        name='SubtituloDoc',
        parent=styles['Normal'],
        fontSize=12,
        textColor=COLOR_GRIS,
        spaceAfter=12,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name='SeccionHeader',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=COLOR_PRIMARIO,
        spaceBefore=14,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        name='CuerpoTexto',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=4,
        leading=14
    ))
    styles.add(ParagraphStyle(
        name='Etiqueta',
        parent=styles['Normal'],
        fontSize=9,
        textColor=COLOR_GRIS,
        fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        name='Pie',
        parent=styles['Normal'],
        fontSize=8,
        textColor=COLOR_GRIS,
        alignment=TA_CENTER,
    ))
    return styles


def generar_pdf_actividad(actividad):
    """Genera un PDF detallado de una actividad institucional con evidencias."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2.5*cm,
        bottomMargin=2*cm,
        title=f'Reporte - {actividad.titulo}',
        author='I.E. 1122 María Auxiliadora',
    )

    styles = get_styles()
    story = []

    # ---- ENCABEZADO ----
    story.append(Paragraph('I.E. 1122 MARÍA AUXILIADORA', styles['TituloDoc']))
    story.append(Paragraph('Puno, Perú — Sistema de Gestión de Actividades', styles['SubtituloDoc']))
    story.append(HRFlowable(width='100%', thickness=2, color=COLOR_PRIMARIO, spaceAfter=10))

    story.append(Paragraph('REPORTE DE ACTIVIDAD INSTITUCIONAL', styles['SeccionHeader']))
    story.append(Spacer(1, 6))

    # Datos principales de la actividad
    estado_labels = {
        'pendiente': 'Pendiente',
        'en_proceso': 'En Proceso',
        'finalizada': 'Finalizada',
        'cancelada': 'Cancelada',
    }
    data_actividad = [
        ['Campo', 'Información'],
        ['Título', actividad.titulo],
        ['Fecha', actividad.fecha.strftime('%d de %B de %Y') if actividad.fecha else '—'],
        ['Lugar', actividad.lugar or '—'],
        ['Estado', estado_labels.get(actividad.estado, actividad.estado)],
        ['Creado por', actividad.created_by.get_full_name() or actividad.created_by.username],
        ['Fecha de registro', actividad.fecha_creacion.strftime('%d/%m/%Y %H:%M')],
    ]

    tabla_actividad = Table(data_actividad, colWidths=[5*cm, 12*cm])
    tabla_actividad.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARIO),
        ('TEXTCOLOR', (0, 0), (-1, 0), COLOR_BLANCO),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BACKGROUND', (0, 1), (0, -1), COLOR_CLARO),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [COLOR_BLANCO, colors.HexColor('#f5f5f5')]),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(tabla_actividad)
    story.append(Spacer(1, 12))

    # Descripción
    story.append(Paragraph('Descripción:', styles['SeccionHeader']))
    story.append(Paragraph(actividad.descripcion, styles['CuerpoTexto']))
    story.append(Spacer(1, 12))

    # Evidencias
    evidencias = actividad.evidencias.all()
    if evidencias.exists():
        story.append(HRFlowable(width='100%', thickness=1, color=COLOR_SECUNDARIO, spaceAfter=6))
        story.append(Paragraph(f'EVIDENCIAS FOTOGRÁFICAS ({evidencias.count()})', styles['SeccionHeader']))
        story.append(Spacer(1, 6))

        for i, evidencia in enumerate(evidencias, 1):
            items = []
            items.append(Paragraph(
                f'Evidencia {i}: {evidencia.descripcion or "Sin descripción"}',
                styles['Etiqueta']
            ))
            items.append(Paragraph(
                f'Subido por: {evidencia.subido_por.get_full_name() or evidencia.subido_por.username} — '
                f'{evidencia.fecha_subida.strftime("%d/%m/%Y %H:%M")}',
                styles['CuerpoTexto']
            ))
            if evidencia.imagen and os.path.exists(evidencia.imagen.path):
                try:
                    img = RLImage(evidencia.imagen.path, width=8*cm, height=6*cm)
                    img.hAlign = 'LEFT'
                    items.append(img)
                except Exception:
                    items.append(Paragraph('[Imagen no disponible]', styles['CuerpoTexto']))
            items.append(Spacer(1, 8))
            story.append(KeepTogether(items))

    # Pie de página del documento
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width='100%', thickness=1, color=COLOR_GRIS))
    story.append(Paragraph(
        f'Documento generado el {timezone.now().strftime("%d/%m/%Y a las %H:%M")} — '
        'I.E. 1122 María Auxiliadora — Sistema de Gestión Escolar',
        styles['Pie']
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


def generar_pdf_reporte_general(actividades, filtro_estado='todos'):
    """Genera un reporte general de todas las actividades en PDF."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
        title='Reporte General de Actividades',
    )

    styles = get_styles()
    story = []

    story.append(Paragraph('I.E. 1122 MARÍA AUXILIADORA', styles['TituloDoc']))
    story.append(Paragraph('REPORTE GENERAL DE ACTIVIDADES INSTITUCIONALES', styles['SubtituloDoc']))
    story.append(Paragraph(
        f'Generado: {timezone.now().strftime("%d/%m/%Y %H:%M")} — Total: {actividades.count()} actividades',
        styles['SubtituloDoc']
    ))
    story.append(HRFlowable(width='100%', thickness=2, color=COLOR_PRIMARIO, spaceAfter=12))

    # Tabla de actividades
    headers = ['N°', 'Título', 'Fecha', 'Estado', 'Lugar', 'Evidencias']
    data = [headers]

    for i, act in enumerate(actividades, 1):

        estado_labels = {
            'pendiente': 'Pendiente',
            'en_proceso': 'En Proceso',
            'finalizada': 'Finalizada',
            'cancelada': 'Cancelada',
        }

        data.append([
            str(i),
            act.titulo[:45] + ('...' if len(act.titulo) > 45 else ''),
            act.fecha.strftime('%d/%m/%Y') if act.fecha else '—',
            estado_labels.get(act.estado, act.estado),
            (act.lugar or '—')[:25],
            str(act.evidencias.count()),
        ])

    tabla = Table(data, colWidths=[1*cm, 8*cm, 3*cm, 3*cm, 6*cm, 2.5*cm])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARIO),
        ('TEXTCOLOR', (0, 0), (-1, 0), COLOR_BLANCO),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [COLOR_BLANCO, colors.HexColor('#f5f5f5')]),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (6, 0), (6, -1), 'CENTER'),
    ]))
    story.append(tabla)

    story.append(Spacer(1, 15))
    story.append(HRFlowable(width='100%', thickness=1, color=COLOR_GRIS))
    story.append(Paragraph(
        'I.E. 1122 María Auxiliadora — Sistema de Gestión de Actividades Escolares',
        styles['Pie']
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer
