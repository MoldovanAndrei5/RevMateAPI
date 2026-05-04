from io import BytesIO
from datetime import datetime, timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

PRIMARY = colors.HexColor("#1A1A2E")
ACCENT = colors.HexColor("#E94560")
LIGHT_BG = colors.HexColor("#F5F5F5")
WHITE = colors.white
MUTED = colors.HexColor("#888888")


def format_timestamp(ts: int | None) -> str:
    if ts is None:
        return "—"
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%d %b %Y")


def format_cost(cost) -> str:
    if cost is None:
        return "—"
    return f"${float(cost):,.2f}"


def format_mileage(mileage: int | None) -> str:
    if mileage is None:
        return "—"
    return f"{mileage:,} km"


def format_file_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    else:
        return f"{size / (1024 * 1024):.1f} MB"


def generate_car_report(car, tasks: list) -> bytes:
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )

    elements = []

    title_style = ParagraphStyle(
        "Title", fontSize=26, fontName="Helvetica-Bold",
        textColor=WHITE, alignment=TA_LEFT, spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", fontSize=12, fontName="Helvetica",
        textColor=colors.HexColor("#CCCCCC"), alignment=TA_LEFT,
    )
    section_header_style = ParagraphStyle(
        "SectionHeader", fontSize=13, fontName="Helvetica-Bold",
        textColor=PRIMARY, spaceBefore=16, spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "Body", fontSize=10, fontName="Helvetica",
        textColor=PRIMARY, leading=14,
    )
    muted_style = ParagraphStyle(
        "Muted", fontSize=9, fontName="Helvetica",
        textColor=MUTED, alignment=TA_RIGHT,
    )
    footer_style = ParagraphStyle(
        "Footer", fontSize=8, textColor=MUTED, alignment=TA_CENTER
    )

    # Header 
    car_label = f"{car.year} {car.make} {car.model}"
    header_data = [[
        Paragraph("<b>RevMate</b>", title_style),
        Paragraph(f"Service History Report<br/><font size=10>{car_label}</font>", subtitle_style),
    ]]
    header_table = Table(header_data, colWidths=[8 * cm, 9 * cm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
        ("LEFTPADDING", (0, 0), (0, -1), 16),
        ("RIGHTPADDING", (-1, 0), (-1, -1), 16),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.4 * cm))

    generated = datetime.now(timezone.utc).strftime("%d %B %Y, %H:%M UTC")
    elements.append(Paragraph(f"Generated on {generated}", muted_style))
    elements.append(Spacer(1, 0.4 * cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=LIGHT_BG))
    elements.append(Spacer(1, 0.3 * cm))

    # Car Details
    elements.append(Paragraph("Vehicle Details", section_header_style))
    car_details = [
        ["Name", car.name or "—", "VIN", car.vin or "—"],
        ["Make", car.make or "—", "License Plate", car.license_plate or "—"],
        ["Model", car.model or "—", "Current Mileage", format_mileage(car.mileage)],
        ["Year", str(car.year) if car.year else "—", "", ""],
    ]
    car_table = Table(car_details, colWidths=[3.5 * cm, 6 * cm, 3.5 * cm, 4 * cm])
    car_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), MUTED),
        ("TEXTCOLOR", (2, 0), (2, -1), MUTED),
        ("TEXTCOLOR", (1, 0), (1, -1), PRIMARY),
        ("TEXTCOLOR", (3, 0), (3, -1), PRIMARY),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, LIGHT_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
    ]))
    elements.append(car_table)
    elements.append(Spacer(1, 0.5 * cm))

    # Summary
    elements.append(Paragraph("Summary", section_header_style))
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.completed_date is not None)
    total_cost = sum(float(t.cost) for t in tasks if t.cost is not None)
    total_invoices = sum(len(t.invoices) for t in tasks)

    summary_data = [
        ["Total Tasks", "Completed", "Total Cost", "Invoices"],
        [str(total_tasks), str(completed_tasks), format_cost(total_cost), str(total_invoices)],
    ]
    summary_table = Table(summary_data, colWidths=[4.25 * cm, 4.25 * cm, 4.25 * cm, 4.25 * cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, 1), LIGHT_BG),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 1), (-1, 1), 16),
        ("TEXTCOLOR", (0, 1), (-1, 1), ACCENT),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.5 * cm))

    # Service History
    elements.append(Paragraph("Service History", section_header_style))
    if not tasks:
        elements.append(Paragraph("No maintenance tasks recorded.", body_style))
    else:
        task_header = ["Title", "Category", "Mileage", "Cost", "Scheduled", "Completed", "Invoices"]
        task_rows = [task_header]
        for t in sorted(tasks, key=lambda x: x.scheduled_date or 0, reverse=True):
            task_rows.append([
                t.title or "—",
                t.category or "—",
                format_mileage(t.mileage),
                format_cost(t.cost),
                format_timestamp(t.scheduled_date),
                format_timestamp(t.completed_date),
                str(len(t.invoices)) if t.invoices else "0",
            ])

        col_widths = [3.8 * cm, 2.5 * cm, 2.3 * cm, 1.8 * cm, 2.2 * cm, 2.2 * cm, 1.7 * cm]
        task_table = Table(task_rows, colWidths=col_widths, repeatRows=1)
        task_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("TEXTCOLOR", (0, 1), (-1, -1), PRIMARY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
            ("ALIGN", (2, 1), (-1, -1), "CENTER"),
            ("ALIGN", (0, 1), (1, -1), "LEFT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(task_table)

        # Notes
        tasks_with_notes = [t for t in tasks if t.notes]
        if tasks_with_notes:
            elements.append(Spacer(1, 0.5 * cm))
            elements.append(Paragraph("Notes", section_header_style))
            for t in tasks_with_notes:
                elements.append(Paragraph(f"<b>{t.title}</b>: {t.notes}", body_style))
                elements.append(Spacer(1, 0.15 * cm))

        # Invoices
        tasks_with_invoices = [t for t in tasks if t.invoices]
        if tasks_with_invoices:
            elements.append(Spacer(1, 0.5 * cm))
            elements.append(Paragraph("Invoices & Attachments", section_header_style))
            invoice_header = ["Task", "File Name", "Type", "Size", "Uploaded"]
            invoice_rows = [invoice_header]
            for t in tasks_with_invoices:
                for inv in t.invoices:
                    invoice_rows.append([
                        t.title or "—",
                        inv.file_name,
                        inv.file_type.split("/")[-1].upper(),
                        format_file_size(inv.file_size),
                        inv.uploaded_at.strftime("%d %b %Y"),
                    ])
            inv_col_widths = [4 * cm, 5.5 * cm, 2 * cm, 2 * cm, 3.5 * cm]
            invoice_table = Table(invoice_rows, colWidths=inv_col_widths, repeatRows=1)
            invoice_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("TEXTCOLOR", (0, 1), (-1, -1), PRIMARY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
                ("ALIGN", (2, 1), (-1, -1), "CENTER"),
                ("ALIGN", (0, 1), (1, -1), "LEFT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]))
            elements.append(invoice_table)

    # Footer 
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=LIGHT_BG))
    elements.append(Spacer(1, 0.2 * cm))
    elements.append(Paragraph(
        "This report was generated by RevMate. All records are provided by the vehicle owner.",
        footer_style
    ))

    doc.build(elements)
    return buffer.getvalue()