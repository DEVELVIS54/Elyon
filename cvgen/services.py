import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer,
                                 Table, TableStyle)

FONT_MAP = {
    'modern': ('Helvetica', 'Helvetica-Bold'),
    'classic': ('Times-Roman', 'Times-Bold'),
    'technical': ('Courier', 'Courier-Bold'),
    'bold': ('Helvetica', 'Helvetica-Bold'),
}

SPACING_MULTIPLIER = {
    'compact': 0.7,
    'comfortable': 1.0,
    'spacious': 1.3,
}

DEFAULT_SPEC = {
    'palette': None,
    'typography_mood': 'modern',
    'layout_archetype': 'single-column',
    'spacing': 'comfortable',
}


def _resolve_spec(profile):
    spec = dict(DEFAULT_SPEC)
    theme = getattr(profile, 'cv_theme', None)
    if theme and theme.design_spec:
        spec.update(theme.design_spec)

    palette = spec.get('palette') or []
    accent = colors.HexColor(palette[0]) if palette else colors.HexColor(profile.primary_color or '#E8231A')
    secondary = colors.HexColor(palette[1]) if len(palette) > 1 else colors.HexColor('#444444')

    body_font, bold_font = FONT_MAP.get(spec['typography_mood'], FONT_MAP['modern'])
    mult = SPACING_MULTIPLIER.get(spec['spacing'], 1.0)

    return {
        'archetype': spec['layout_archetype'],
        'accent': accent,
        'secondary': secondary,
        'body_font': body_font,
        'bold_font': bold_font,
        'spacing_mult': mult,
    }


def _build_styles(r):
    styles = getSampleStyleSheet()
    return {
        'name': ParagraphStyle('Name', parent=styles['Title'], fontName=r['bold_font'],
                                fontSize=22, textColor=r['accent'], spaceAfter=2 * r['spacing_mult']),
        'name_inverse': ParagraphStyle('NameInverse', parent=styles['Title'], fontName=r['bold_font'],
                                        fontSize=22, textColor=colors.white, spaceAfter=2),
        'role': ParagraphStyle('Role', parent=styles['Normal'], fontName=r['body_font'],
                                fontSize=13, textColor=colors.HexColor('#444444'), spaceAfter=10 * r['spacing_mult']),
        'role_inverse': ParagraphStyle('RoleInverse', parent=styles['Normal'], fontName=r['body_font'],
                                        fontSize=13, textColor=colors.whitesmoke, spaceAfter=4),
        'section': ParagraphStyle('Section', parent=styles['Heading2'], fontName=r['bold_font'],
                                   fontSize=13, textColor=r['accent'],
                                   spaceBefore=14 * r['spacing_mult'], spaceAfter=6 * r['spacing_mult']),
        'section_sidebar': ParagraphStyle('SectionSidebar', parent=styles['Heading2'], fontName=r['bold_font'],
                                           fontSize=11, textColor=colors.white,
                                           spaceBefore=12 * r['spacing_mult'], spaceAfter=4 * r['spacing_mult']),
        'body': ParagraphStyle('Body', parent=styles['Normal'], fontName=r['body_font'], fontSize=10, leading=14),
        'body_sidebar': ParagraphStyle('BodySidebar', parent=styles['Normal'], fontName=r['body_font'],
                                        fontSize=9, leading=13, textColor=colors.white),
        'small': ParagraphStyle('Small', parent=styles['Normal'], fontName=r['body_font'],
                                 fontSize=9, textColor=colors.grey),
        'small_sidebar': ParagraphStyle('SmallSidebar', parent=styles['Normal'], fontName=r['body_font'],
                                         fontSize=9, textColor=colors.whitesmoke),
    }


def _experience_flowables(profile, s, style_key='body', small_key='small'):
    flow = []
    for exp in profile.experiences.all():
        end = "Présent" if exp.is_current else (exp.end_date.strftime('%m/%Y') if exp.end_date else '')
        header = f"<b>{exp.title}</b> — {exp.company} ({exp.start_date.strftime('%m/%Y')} - {end})"
        flow.append(Paragraph(header, s[style_key]))
        if exp.description:
            flow.append(Paragraph(exp.description, s[small_key]))
        flow.append(Spacer(1, 4))
    return flow


def _education_flowables(profile, s, style_key='body'):
    flow = []
    for edu in profile.educations.all():
        end = edu.end_date.strftime('%m/%Y') if edu.end_date else 'en cours'
        header = f"<b>{edu.degree}</b> — {edu.school} ({edu.start_date.strftime('%m/%Y')} - {end})"
        flow.append(Paragraph(header, s[style_key]))
        flow.append(Spacer(1, 4))
    return flow


def _build_single_column(profile, r):
    s = _build_styles(r)
    elements = [
        Paragraph(profile.full_name or profile.user.username, s['name']),
        Paragraph(profile.profession or '', s['role']),
    ]

    contact_bits = [b for b in [profile.email_public, profile.phone, profile.location] if b]
    if contact_bits:
        elements.append(Paragraph(" · ".join(contact_bits), s['small']))
    elements.append(Spacer(1, 8))

    if profile.bio:
        elements.append(Paragraph("PROFIL", s['section']))
        elements.append(Paragraph(profile.bio, s['body']))

    if profile.experiences.exists():
        elements.append(Paragraph("EXPÉRIENCES", s['section']))
        elements += _experience_flowables(profile, s)

    if profile.educations.exists():
        elements.append(Paragraph("FORMATIONS", s['section']))
        elements += _education_flowables(profile, s)

    skills = profile.skills.all()
    if skills:
        elements.append(Paragraph("COMPÉTENCES", s['section']))
        elements.append(Paragraph(", ".join(sk.name for sk in skills), s['body']))

    social_links = profile.social_links.all()
    if social_links:
        elements.append(Paragraph("LIENS", s['section']))
        links_text = " · ".join(f"{l.get_platform_display()}: {l.url}" for l in social_links)
        elements.append(Paragraph(links_text, s['small']))

    return elements


def _build_sidebar(profile, r):
    s = _build_styles(r)

    sidebar = [Paragraph(profile.full_name or profile.user.username, s['name_inverse']),
               Paragraph(profile.profession or '', s['role_inverse']), Spacer(1, 10)]

    contact_bits = [b for b in [profile.email_public, profile.phone, profile.location] if b]
    if contact_bits:
        sidebar.append(Paragraph("CONTACT", s['section_sidebar']))
        for bit in contact_bits:
            sidebar.append(Paragraph(bit, s['small_sidebar']))

    skills = profile.skills.all()
    if skills:
        sidebar.append(Paragraph("COMPÉTENCES", s['section_sidebar']))
        for sk in skills:
            sidebar.append(Paragraph(sk.name, s['body_sidebar']))

    social_links = profile.social_links.all()
    if social_links:
        sidebar.append(Paragraph("LIENS", s['section_sidebar']))
        for l in social_links:
            sidebar.append(Paragraph(f"{l.get_platform_display()}: {l.url}", s['small_sidebar']))

    main = []
    if profile.bio:
        main.append(Paragraph("PROFIL", s['section']))
        main.append(Paragraph(profile.bio, s['body']))
    if profile.experiences.exists():
        main.append(Paragraph("EXPÉRIENCES", s['section']))
        main += _experience_flowables(profile, s)
    if profile.educations.exists():
        main.append(Paragraph("FORMATIONS", s['section']))
        main += _education_flowables(profile, s)

    table = Table([[sidebar, main]], colWidths=[55 * mm, 115 * mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), r['accent']),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (0, 0), 10),
        ('RIGHTPADDING', (0, 0), (0, 0), 10),
        ('TOPPADDING', (0, 0), (0, 0), 14),
        ('LEFTPADDING', (1, 0), (1, 0), 14),
        ('TOPPADDING', (1, 0), (1, 0), 0),
    ]))
    return [table]


def _build_header_band(profile, r):
    s = _build_styles(r)

    header_content = [
        Paragraph(profile.full_name or profile.user.username, s['name_inverse']),
        Paragraph(profile.profession or '', s['role_inverse']),
    ]
    contact_bits = [b for b in [profile.email_public, profile.phone, profile.location] if b]
    if contact_bits:
        header_content.append(Paragraph(" · ".join(contact_bits), s['small_sidebar']))

    band = Table([[header_content]], colWidths=[170 * mm])
    band.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), r['accent']),
        ('LEFTPADDING', (0, 0), (0, 0), 16),
        ('TOPPADDING', (0, 0), (0, 0), 16),
        ('BOTTOMPADDING', (0, 0), (0, 0), 16),
    ]))

    elements = [band, Spacer(1, 14)]

    if profile.bio:
        elements.append(Paragraph("PROFIL", s['section']))
        elements.append(Paragraph(profile.bio, s['body']))
    if profile.experiences.exists():
        elements.append(Paragraph("EXPÉRIENCES", s['section']))
        elements += _experience_flowables(profile, s)
    if profile.educations.exists():
        elements.append(Paragraph("FORMATIONS", s['section']))
        elements += _education_flowables(profile, s)
    skills = profile.skills.all()
    if skills:
        elements.append(Paragraph("COMPÉTENCES", s['section']))
        elements.append(Paragraph(", ".join(sk.name for sk in skills), s['body']))
    social_links = profile.social_links.all()
    if social_links:
        elements.append(Paragraph("LIENS", s['section']))
        links_text = " · ".join(f"{l.get_platform_display()}: {l.url}" for l in social_links)
        elements.append(Paragraph(links_text, s['small']))

    return elements


ARCHETYPE_BUILDERS = {
    'single-column': _build_single_column,
    'sidebar': _build_sidebar,
    'header-band': _build_header_band,
}


def build_cv_pdf(profile):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=18 * mm, bottomMargin=18 * mm,
        leftMargin=18 * mm, rightMargin=18 * mm,
    )

    r = _resolve_spec(profile)
    builder = ARCHETYPE_BUILDERS.get(r['archetype'], _build_single_column)
    elements = builder(profile, r)

    doc.build(elements)
    buffer.seek(0)
    return buffer