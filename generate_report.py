"""generate_report.py — produces snowflower_strategy_report.docx (~15 pages).

Demonstrates advanced python-docx use: custom styles, cover page, TOC field,
header/footer with PAGE / NUMPAGES field codes, shaded cells, table borders,
embedded matplotlib charts, callout boxes, multi-section layout.

Usage:
    python generate_report.py
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

# Force UTF-8 stdout for Windows codepage compatibility (Korean strings).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx import Document
from docx.enum.section import WD_SECTION_START
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPORT_PATH = Path("snowflower_strategy_report.docx")
ASSETS_DIR = Path("_report_assets")
ASSETS_DIR.mkdir(exist_ok=True)

DOC_TITLE = "snowflower"
DOC_SUBTITLE = "An independent accessibility-input-tech editorial channel"
DOC_VERSION = "Strategic Report v1.0"
DOC_DATE = datetime.now().strftime("%Y-%m-%d")
DOC_AUTHOR = "snowflower editorial"

# Color palette
PRIMARY_HEX = "1A3A52"   # midnight blue
ACCENT_HEX = "E8F2F9"    # ice
MUTED_HEX = "6B7380"
CALLOUT_HEX = "FFF8E7"   # warm beige for callouts
DANGER_HEX = "FCE7E7"    # for risk boxes
SUCCESS_HEX = "E7F5E7"   # for win boxes

PRIMARY_RGB = RGBColor(0x1A, 0x3A, 0x52)
MUTED_RGB = RGBColor(0x6B, 0x73, 0x80)
TEXT_RGB = RGBColor(0x22, 0x22, 0x22)


# ---------------------------------------------------------------------------
# Low-level XML helpers
# ---------------------------------------------------------------------------


def _set_cell_shading(cell, hex_color: str) -> None:
    """Apply background shading to a table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tc_pr.append(shd)


def _set_table_borders(table, color: str = "CCCCCC", size: str = "4") -> None:
    """Apply uniform borders to a table."""
    tbl = table._tbl
    tbl_pr = tbl.find(qn("w:tblPr"))
    if tbl_pr is None:
        tbl_pr = OxmlElement("w:tblPr")
        tbl.insert(0, tbl_pr)
    tbl_borders = OxmlElement("w:tblBorders")
    for border_name in ("top", "left", "bottom", "right", "insideH", "insideV"):
        border = OxmlElement(f"w:{border_name}")
        border.set(qn("w:val"), "single")
        border.set(qn("w:sz"), size)
        border.set(qn("w:color"), color)
        tbl_borders.append(border)
    # Replace any existing tblBorders block
    existing = tbl_pr.find(qn("w:tblBorders"))
    if existing is not None:
        tbl_pr.remove(existing)
    tbl_pr.append(tbl_borders)


def _add_page_number_field(paragraph) -> None:
    """Insert PAGE field code into a paragraph (renders as page number in Word)."""
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = "PAGE"
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char1)
    run._r.append(instr_text)
    run._r.append(fld_char2)


def _add_total_pages_field(paragraph) -> None:
    """Insert NUMPAGES field for 'page X of Y' footer."""
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = "NUMPAGES"
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char1)
    run._r.append(instr_text)
    run._r.append(fld_char2)


def _add_toc_field(paragraph) -> None:
    """Insert a TOC field that auto-populates when opened in Word."""
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = r'TOC \o "1-3" \h \z \u'
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "separate")
    placeholder = OxmlElement("w:t")
    placeholder.text = (
        "Right-click and select 'Update Field' in Word to populate this table of contents."
    )
    fld_char3 = OxmlElement("w:fldChar")
    fld_char3.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char1)
    run._r.append(instr_text)
    run._r.append(fld_char2)
    run._r.append(placeholder)
    run._r.append(fld_char3)


# ---------------------------------------------------------------------------
# Style setup
# ---------------------------------------------------------------------------


def configure_styles(doc: Document) -> None:
    """Tune default styles for a clean editorial look."""
    styles = doc.styles

    # Default Normal
    normal = styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = TEXT_RGB
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.2

    # Headings — H1 as section opener
    h1 = styles["Heading 1"]
    h1.font.name = "Calibri"
    h1.font.size = Pt(20)
    h1.font.bold = True
    h1.font.color.rgb = PRIMARY_RGB
    h1.paragraph_format.space_before = Pt(18)
    h1.paragraph_format.space_after = Pt(12)
    h1.paragraph_format.keep_with_next = True

    h2 = styles["Heading 2"]
    h2.font.name = "Calibri"
    h2.font.size = Pt(14)
    h2.font.bold = True
    h2.font.color.rgb = PRIMARY_RGB
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)
    h2.paragraph_format.keep_with_next = True

    h3 = styles["Heading 3"]
    h3.font.name = "Calibri"
    h3.font.size = Pt(11.5)
    h3.font.bold = True
    h3.font.color.rgb = TEXT_RGB
    h3.paragraph_format.space_before = Pt(8)
    h3.paragraph_format.space_after = Pt(2)
    h3.paragraph_format.keep_with_next = True

    # Page margins
    for section in doc.sections:
        section.top_margin = Inches(0.85)
        section.bottom_margin = Inches(0.85)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)


def set_core_properties(doc: Document) -> None:
    cp = doc.core_properties
    cp.title = f"{DOC_TITLE} — {DOC_VERSION}"
    cp.author = DOC_AUTHOR
    cp.subject = "Independent accessibility-input-tech editorial channel"
    cp.keywords = "accessibility, assistive technology, MouthPad, augmental, snowflower, editorial, content engine"
    cp.comments = "Generated by generate_report.py"


# ---------------------------------------------------------------------------
# Document-building helpers
# ---------------------------------------------------------------------------


def add_page_break(doc: Document) -> None:
    p = doc.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)


def add_heading(doc: Document, text: str, level: int = 1) -> None:
    if level == 1:
        add_page_break(doc) if doc.paragraphs and doc.paragraphs[-1].text.strip() else None
    doc.add_heading(text, level=level)


def add_paragraph(doc: Document, text: str, *, bold: bool = False, italic: bool = False,
                  align=None, size_pt: float | None = None, color: RGBColor | None = None) -> None:
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    run = p.add_run(text)
    if bold:
        run.bold = True
    if italic:
        run.italic = True
    if size_pt is not None:
        run.font.size = Pt(size_pt)
    if color is not None:
        run.font.color.rgb = color


def add_bullets(doc: Document, items: list[str]) -> None:
    for item in items:
        doc.add_paragraph(item, style="List Bullet")


def add_numbered(doc: Document, items: list[str]) -> None:
    for item in items:
        doc.add_paragraph(item, style="List Number")


def add_table(doc: Document, headers: list[str], rows: list[list[str]],
              header_fill: str = PRIMARY_HEX, alt_fill: str = "F7F9FC",
              col_widths: list[float] | None = None) -> None:
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    _set_table_borders(table)

    # Header row
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        para = cell.paragraphs[0]
        run = para.add_run(h)
        run.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        run.font.size = Pt(10)
        _set_cell_shading(cell, header_fill)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    # Body rows
    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            cell = table.rows[r].cells[c]
            cell.text = ""
            run = cell.paragraphs[0].add_run(str(val))
            run.font.size = Pt(9.5)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
            if r % 2 == 0:
                _set_cell_shading(cell, alt_fill)

    if col_widths:
        for r in table.rows:
            for c, w in enumerate(col_widths):
                if c < len(r.cells):
                    r.cells[c].width = Inches(w)

    # Spacing after table
    doc.add_paragraph()


def add_callout(doc: Document, title: str, body: str, fill_hex: str = CALLOUT_HEX) -> None:
    """Single-cell shaded box — used for key insights / risks / wins."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.rows[0].cells[0]
    _set_cell_shading(cell, fill_hex)
    _set_table_borders(table, color="DDDDDD")

    cell.text = ""
    p1 = cell.paragraphs[0]
    r1 = p1.add_run(title)
    r1.bold = True
    r1.font.size = Pt(10.5)
    r1.font.color.rgb = PRIMARY_RGB

    p2 = cell.add_paragraph()
    r2 = p2.add_run(body)
    r2.font.size = Pt(9.5)

    doc.add_paragraph()


def add_figure(doc: Document, image_path: Path, caption: str, width_inches: float = 6.0) -> None:
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run()
    run.add_picture(str(image_path), width=Inches(width_inches))

    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap_run = cap.add_run(caption)
    cap_run.italic = True
    cap_run.font.size = Pt(9)
    cap_run.font.color.rgb = MUTED_RGB
    doc.add_paragraph()


# ---------------------------------------------------------------------------
# Cover + headers/footers
# ---------------------------------------------------------------------------


def build_cover(doc: Document) -> None:
    # Spacer to push content down
    for _ in range(6):
        doc.add_paragraph()

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_title.add_run(DOC_TITLE)
    r.bold = True
    r.font.size = Pt(56)
    r.font.color.rgb = PRIMARY_RGB

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p_sub.add_run(DOC_SUBTITLE)
    r2.italic = True
    r2.font.size = Pt(14)
    r2.font.color.rgb = MUTED_RGB

    doc.add_paragraph()
    doc.add_paragraph()

    p_ver = doc.add_paragraph()
    p_ver.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r3 = p_ver.add_run(DOC_VERSION)
    r3.font.size = Pt(13)
    r3.bold = True
    r3.font.color.rgb = PRIMARY_RGB

    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r4 = p_date.add_run(DOC_DATE)
    r4.font.size = Pt(11)
    r4.font.color.rgb = MUTED_RGB

    # Spacer to footer area
    for _ in range(12):
        doc.add_paragraph()

    p_author = doc.add_paragraph()
    p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r5 = p_author.add_run(f"Prepared by {DOC_AUTHOR}\nrepository: github.com/ksk5429/snowflower")
    r5.font.size = Pt(10)
    r5.font.color.rgb = MUTED_RGB


def configure_header_footer(doc: Document) -> None:
    """Apply header (title) + footer (page X of Y) to all sections after cover."""
    for section in doc.sections[1:]:
        # Header
        header = section.header
        h_para = header.paragraphs[0]
        h_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        h_run = h_para.add_run(f"{DOC_TITLE} · {DOC_VERSION}")
        h_run.font.size = Pt(9)
        h_run.font.color.rgb = MUTED_RGB
        h_run.italic = True

        # Footer
        footer = section.footer
        f_para = footer.paragraphs[0]
        f_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_pre = f_para.add_run("Page ")
        run_pre.font.size = Pt(9)
        run_pre.font.color.rgb = MUTED_RGB
        _add_page_number_field(f_para)
        run_mid = f_para.add_run(" of ")
        run_mid.font.size = Pt(9)
        run_mid.font.color.rgb = MUTED_RGB
        _add_total_pages_field(f_para)
        run_post = f_para.add_run(f"   ·   {DOC_DATE}")
        run_post.font.size = Pt(9)
        run_post.font.color.rgb = MUTED_RGB


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------


def chart_platform_matrix() -> Path:
    """Scatter: automation friction (x) × audience fit (y), colored by tier."""
    platforms = [
        # (name, automation_friction_inverted [10=easy], audience_fit, tier)
        ("YouTube", 8, 9, 1),
        ("LinkedIn", 8, 10, 1),
        ("Bluesky", 9, 8, 1),
        ("Beehiiv", 9, 9, 1),
        ("Threads", 7, 5, 2),
        ("Instagram", 6, 7, 2),
        ("TikTok", 5, 7, 2),
        ("X", 6, 4, 2),
        ("Reddit", 3, 6, 3),
        ("Naver Blog", 3, 8, 3),
        ("Stibee", 9, 8, 3),
    ]
    tier_colors = {1: "#1A3A52", 2: "#5B7FA8", 3: "#B0B8C0"}

    fig, ax = plt.subplots(figsize=(8, 5), dpi=140)
    for name, x, y, tier in platforms:
        ax.scatter(x, y, s=220, c=tier_colors[tier], alpha=0.85, edgecolor="white", linewidth=1.5)
        ax.annotate(
            name, (x, y), xytext=(8, 4), textcoords="offset points",
            fontsize=9, color="#222"
        )

    ax.set_xlabel("Automation friendliness (10 = trivial cron)", fontsize=10)
    ax.set_ylabel("Audience fit for accessibility/assistive-input niche", fontsize=10)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 11)
    ax.set_xticks(range(0, 12, 2))
    ax.set_yticks(range(0, 12, 2))
    ax.grid(True, linestyle=":", alpha=0.4)
    ax.set_title("Platform priority matrix (size = invest priority)", fontsize=11, pad=12)

    legend_handles = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=tier_colors[1],
                   markersize=12, label="Tier 1 — primary"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=tier_colors[2],
                   markersize=12, label="Tier 2 — secondary / post-audit"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=tier_colors[3],
                   markersize=12, label="Tier 3 — manual / KR"),
    ]
    ax.legend(handles=legend_handles, loc="lower right", fontsize=9, framealpha=0.95)

    plt.tight_layout()
    out = ASSETS_DIR / "platform_matrix.png"
    plt.savefig(out, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return out


def chart_budget_breakdown() -> Path:
    """Horizontal bar: monthly budget allocation."""
    items = [
        ("Cloud / GitHub Actions", 6),
        ("Beehiiv (≥2,500 subs)", 39),
        ("ElevenLabs (Korean voice)", 22),
        ("fal.ai (image gen)", 18),
        ("X API Basic", 17),
        ("Captioning / misc", 8),
    ]
    items_sorted = sorted(items, key=lambda x: x[1])
    labels = [i[0] for i in items_sorted]
    vals = [i[1] for i in items_sorted]

    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=140)
    bars = ax.barh(labels, vals, color="#1A3A52", alpha=0.85, edgecolor="white")
    ax.set_xlabel("USD per month", fontsize=10)
    ax.set_xlim(0, max(vals) * 1.25)
    for bar, val in zip(bars, vals):
        ax.text(val + 1, bar.get_y() + bar.get_height() / 2,
                f"${val}", va="center", fontsize=9, color="#222")

    total = sum(vals)
    ax.set_title(f"Monthly budget allocation — total ~${total}/mo (within $50–100 cap)",
                 fontsize=11, pad=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, axis="x", linestyle=":", alpha=0.4)

    plt.tight_layout()
    out = ASSETS_DIR / "budget_breakdown.png"
    plt.savefig(out, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return out


def chart_90_day_timeline() -> Path:
    """Gantt-style horizontal timeline of 90-day plan."""
    workstreams = [
        ("Pre-flight (domain, gmail, voice)", 0, 1, "#5B7FA8"),
        ("Account creation (Tier 1)", 1, 3, "#5B7FA8"),
        ("Episode pre-batch (4 pieces)", 1, 3, "#1A3A52"),
        ("Methodology page + first publish", 3, 5, "#1A3A52"),
        ("Weekly cadence engaged", 4, 13, "#1A3A52"),
        ("Newsletter weekly", 4, 13, "#7A9FBC"),
        ("LinkedIn 2x/week + daily Bluesky", 4, 13, "#7A9FBC"),
        ("CSUN 2026 conference", 9, 10, "#C8451A"),
        ("CSUN footage → 6-episode series", 10, 12, "#1A3A52"),
        ("augmental.tech pitch", 12, 13, "#C8451A"),
    ]

    fig, ax = plt.subplots(figsize=(8.6, 4.6), dpi=140)
    for i, (name, start, end, color) in enumerate(workstreams):
        ax.barh(i, end - start, left=start, color=color, alpha=0.88,
                edgecolor="white", height=0.65)
        ax.text(start + 0.1, i, name, va="center", fontsize=8.5, color="white"
                if (end - start) > 2 else "#222")

    ax.set_yticks(range(len(workstreams)))
    ax.set_yticklabels([f"W{ws[1]}-{ws[2]}" for ws in workstreams], fontsize=8.5, color="#555")
    ax.invert_yaxis()
    ax.set_xlabel("Week", fontsize=10)
    ax.set_xlim(0, 14)
    ax.set_xticks(range(0, 14, 2))
    ax.set_title("90-day execution timeline — anchored to CSUN 2026 (W9) and pitch (W12)",
                 fontsize=11, pad=12)
    ax.grid(True, axis="x", linestyle=":", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    out = ASSETS_DIR / "timeline_90day.png"
    plt.savefig(out, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------


def section_executive_summary(doc: Document) -> None:
    add_heading(doc, "1 · Executive Summary", level=1)
    doc.add_paragraph(
        "snowflower is an independent editorial channel covering hands-free and assistive "
        "input technology — MouthPad (augmental.tech), Tobii eye trackers, Quha head mice, "
        "Glassouse, Apple AssistiveTouch, and the broader category. It is built as a real "
        "publishing brand and as a reusable Python content engine, with the explicit goal "
        "of becoming the category-king editorial voice and using that audience to pitch "
        "sponsorship or employment to augmental.tech at the 90-day mark."
    )

    add_callout(
        doc,
        "Strategic premise — corrected from initial framing",
        "The original idea was 'company brand promotion via AI content automation, dark "
        "psychology, secret ads, every platform.' Three premises were rejected as illegal "
        "(undisclosed advertising violates FTC + KFTC + EU DSA), economically obsolete "
        "(the 2024-25 AI-slop flood closed automation arbitrage), and mismatched (augmental "
        "is accessibility hardware, not AI/digital twin). The corrected strategy: "
        "transparent independent editorial covering the hands-free input category, with "
        "augmental as one flagship subject — pitched at day 90 as data-backed evidence.",
    )

    add_paragraph(doc, "Key strategic decisions", bold=True)
    add_bullets(
        doc,
        [
            "Identity: brand-only across all platforms; LinkedIn personal profile excluded per LinkedIn ToS Art. 8.2.",
            "Niche: motor-disability + hands-free input only — direct overlap with augmental's MouthPad audience.",
            "Editorial rule: cover competitors fairly (Tobii, Quha, Glassouse, AssistiveTouch).",
            "Disclosure-first under FTC 16 CFR § 255 + Korea 표시·광고법 — templates published in DISCLOSURE.md.",
            "Korean market: build-awareness mode (Naver Blog manual + LinkedIn KR + Korean YouTube subtitles).",
            "Budget: $50–100/mo, single editor, $200/episode floor for paid disabled co-host.",
        ],
    )

    add_paragraph(doc, "Pitch arc", bold=True)
    doc.add_paragraph(
        "Run snowflower for 90 days → reach 5–15k followers across YouTube, LinkedIn, "
        "Bluesky, Beehiiv → pitch augmental with data: audience composition (% verified "
        "OT/SLP/AT-specialist/VA prosthetist), MouthPad-coverage views and click-throughs, "
        "conference attendee overlap from CSUN 2026. The pitch metric is audience density, "
        "not subscriber count. Same engine + same pitch is portable to Tobii / Quha / "
        "Glassouse if augmental passes."
    )


def section_background(doc: Document) -> None:
    add_heading(doc, "2 · Background — Company, Product, Market", level=1)

    add_heading(doc, "2.1 augmental.tech and MouthPad^", level=2)
    doc.add_paragraph(
        "augmental.tech is an MIT Media Lab spinoff developing the MouthPad^ — the world's "
        "first hands-free intra-oral touchpad. Worn on the roof of the mouth (~1 mm thick, "
        "~7.5 g, dental resin with stainless steel enclosure), it tracks tongue and head "
        "gestures, supports sip-clicks, and pairs over Bluetooth with macOS, Windows, "
        "Linux, iOS, and Android. Battery life is 5+ hours per session. The flagship "
        "user-impact case study (Keely Horch, University of Maryland) has anchored "
        "coverage in The Verge, MIT News, BBC, NBC News, Forbes, TechCrunch, and Wired."
    )

    add_heading(doc, "2.2 The hands-free input category", level=2)
    doc.add_paragraph(
        "MouthPad sits in a wider category of hands-free input devices used by people "
        "with mobility limitations. The competitive set:"
    )
    add_table(
        doc,
        ["Category", "Devices", "Typical user"],
        [
            ["Intra-oral", "MouthPad^", "C2-C4 SCI, ALS, advanced MS, locked-in"],
            ["Head-mouse / IMU", "Quha Zono 2, SmartNav 4, headband-IMU arrays", "C5+ SCI, MS, advanced CP"],
            ["Cheek-button", "Glassouse V2", "Spinal cord injury, CP, stroke survivors"],
            ["Eye-gaze", "Tobii Eye Tracker 5, Tobii PCEye, Eyegaze Edge", "ALS, locked-in, severe motor disability"],
            ["Software (built-in)", "Apple AssistiveTouch, Voice Control, Switch Control; Windows Eye Control; Android Switch Access", "Anyone with a smartphone, free"],
            ["Voice / dictation", "Apple Voice Control, Google Voice Access, Talon Voice", "Variable; works for many but not all"],
            ["Sip-and-puff", "Origin Instruments Jouse, AbleNet QuadJoy", "Long history; declining vs newer modalities"],
        ],
        col_widths=[1.2, 3.4, 2.4],
    )

    add_heading(doc, "2.3 Buyer landscape", level=2)
    doc.add_paragraph(
        "Direct cash sale is the smallest slice. The bulk of unit volume flows through "
        "five reimbursed paths in the US: private insurance, Medicare/Medicaid (DME), VA, "
        "K-12 IEP, and state Vocational Rehabilitation. In Korea: KEAD 보조공학기기 "
        "지원사업 (up to 15M KRW per worker, 20M for severe disability), KNAT 장애인보조"
        "기기 교부사업, 산재보험, 보훈. Every reimbursed path requires a credentialed "
        "clinician (OT, SLP, ATP) to sign — they are the real marketing target, not the "
        "end-user."
    )


def section_strategic_premise(doc: Document) -> None:
    add_heading(doc, "3 · Strategic Premise", level=1)
    doc.add_paragraph(
        "Three premises from the initial idea were tested and rejected:"
    )

    add_table(
        doc,
        ["Original premise", "Why it broke", "Replacement"],
        [
            [
                "Dark psychology + secret ads",
                "Undisclosed advertising violates FTC 16 CFR § 255 (US), 표시·광고법 (KR), DSA Art. 26 (EU). AI-content forensics in 2026 surfaces it routinely. Discovery destroys company value asymmetrically.",
                "Transparent disclosed editorial — DISCLOSURE.md templates for neutral / sample / sponsored / attribution / AI-generated.",
            ],
            [
                "Automate everything across every platform",
                "2024–25 AI-slop flood closed the arbitrage. YouTube demonetized mass-produced channels. Instagram throttles unoriginal content. X requires paid API ($200+/mo). TikTok forbids 'apps that copy arbitrary content from other platforms'.",
                "Pick ONE channel, prove it, expand. Tier 1 = YouTube + LinkedIn + Bluesky + Beehiiv.",
            ],
            [
                "Niche = AI and digital twin (for augmental.tech)",
                "augmental sells MouthPad^ — accessibility hardware, not AI/digital-twin. Audiences differ entirely. AI-niche pipelines reach the wrong buyers.",
                "Niche corrected to motor-disability + hands-free input. Editorial covers the category; augmental is one subject.",
            ],
            [
                "Direct brand promo for augmental",
                "No augmental account credentials available; running official accounts without authorization = trademark + impersonation risk. Medical/efficacy claims without clinical data = FDA exposure.",
                "b+c hybrid: build an independent third-party editorial channel (snowflower); use 90 days of measurable reach as proof for the augmental pitch.",
            ],
        ],
        col_widths=[1.7, 3.0, 2.3],
    )


def section_brand(doc: Document) -> None:
    add_heading(doc, "4 · Brand Architecture & Pitch Arc", level=1)

    add_heading(doc, "4.1 Two outputs from one effort", level=2)
    add_table(
        doc,
        ["Output", "What it is", "Why it exists"],
        [
            [
                "The engine",
                "Flat-folder Python content pipeline (snowflower repo) covering source-asset → multi-platform fan-out → measurement loop.",
                "Sellable IP. Eventually licensable to accessibility-tech vendors. Augmental can take in-house if they prefer.",
            ],
            [
                "The channel",
                "snowflower (snowflower.tech) — a real publishing brand running on the engine, covering hands-free input devices fairly across vendors.",
                "Proof. Demonstrates the engine works in market before any pitch lands.",
            ],
        ],
        col_widths=[1.4, 3.1, 2.5],
    )

    add_heading(doc, "4.2 Editorial constraints (non-negotiable)", level=2)
    add_bullets(
        doc,
        [
            "Paid disabled co-host of record before episode 1 — 'nothing about us without us' operationalized; non-disabled-led accessibility channels hit a credibility ceiling without lived-experience editorial.",
            "Cover competitors fairly: Tobii, Quha, Glassouse, AssistiveTouch all in editorial scope.",
            "Identity-first vs person-first: ask the individual. Defaults vary by community (Deaf/Autistic/Blind = identity-first; SMA/CP/MS = often person-first).",
            "Trigger-pattern auto-reject: inspiration porn, cure framing, 'overcoming,' before/after as transformation, ableist metaphors, 'wheelchair-bound,' 'high/low-functioning'.",
            "Reference frame: Apple's 'The Greatest' (Dec 2022) + 'I'm Not Remarkable' (May 2025). Show ordinary use. No pity score, no slow piano.",
        ],
    )

    add_heading(doc, "4.3 Pitch arc", level=2)
    doc.add_paragraph(
        "Run snowflower for 90 days. Reach 5–15k followers. Pitch augmental with three "
        "engagement options: anchor sponsor (fixed monthly retainer + premium placement), "
        "content partnership (augmental produces footage, snowflower handles fan-out), or "
        "hire (snowflower joins augmental as content lead, engine becomes augmental IP). "
        "If augmental passes, the same pitch is portable to Tobii / Quha / Glassouse — "
        "snowflower's category-king position is the durable asset."
    )


def section_platform(doc: Document, matrix_path: Path) -> None:
    add_heading(doc, "5 · Platform Feasibility Analysis", level=1)
    doc.add_paragraph(
        "Eleven platforms scoped for snowflower. Tier 1 = cron-publishable with free or "
        "low-friction APIs. Tier 2 = high-friction (audit / app review / paid tier). "
        "Tier 3 = manual-only or Korean-market specific."
    )

    add_figure(doc, matrix_path,
               "Figure 5.1 — Platform priority matrix. Tier 1 cluster (top right) is the "
               "cron-publishable primary stack. Tier 3 lower-left platforms are deferred or manual-only.",
               width_inches=6.5)

    add_heading(doc, "5.1 Tier 1 — primary (cron-publishable)", level=2)
    add_table(
        doc,
        ["Platform", "API", "Cost", "Notes"],
        [
            ["YouTube", "Data API v3 / videos.insert", "Free", "Default 10k units/day quota → ~6 uploads/day. Hero pieces."],
            ["LinkedIn", "Posts API REST versioned", "Free", "Company Page only (brand-only ToS). w_organization_social scope after MDP approval."],
            ["Bluesky", "AT Protocol / app password", "Free", "Easiest API in stack. Tech / accessibility-research audience migrated from X."],
            ["Beehiiv", "v2 REST", "0% take + $39/mo at 2,500 subs", "Owned audience — the asset augmental will pay against."],
        ],
        col_widths=[1.2, 2.0, 1.4, 2.4],
    )

    add_heading(doc, "5.2 Tier 2 — secondary (post-audit / paid)", level=2)
    add_table(
        doc,
        ["Platform", "Gate", "Time to clear"],
        [
            ["Threads", "Meta API; Instagram-linked", "Comes free with IG"],
            ["Instagram Reels", "Graph API + App Review", "1–4 weeks"],
            ["TikTok", "Content Posting API + audit", "5–10 business days; private until approved"],
            ["X (Twitter)", "Paid tier ($200+/mo Basic)", "Instant once paid"],
        ],
        col_widths=[1.5, 3.5, 2.0],
    )

    add_heading(doc, "5.3 Tier 3 — manual or KR-specific", level=2)
    add_table(
        doc,
        ["Platform", "Status"],
        [
            ["Reddit (r/disability, r/als, r/SCI, ...)", "Manual posting only — CQS shadowban risk on cron + $12k/yr commercial API tier"],
            ["Hacker News", "Manual quarterly when an OSS artifact ships — AI prose flagged hard since late 2025"],
            ["Naver Blog (KR)", "Manual editing only — cron triggers 영구정지 per 2025 저품대란 sweep"],
            ["Stibee (KR newsletter)", "REST API works; defer to Tier 1 once Korean list exists"],
            ["KakaoStory, Tistory, Brunch, Disquiet, ResearchGate", "Skipped — APIs dead, gated, or no value for niche"],
        ],
        col_widths=[2.5, 4.5],
    )


def section_engine(doc: Document) -> None:
    add_heading(doc, "6 · Content Engine Architecture", level=1)
    doc.add_paragraph(
        "The engine is a flat-folder Python codebase (no package install — files run "
        "directly via `python snowflower.py ...`). Repository: github.com/ksk5429/snowflower. "
        "34+ files at root, 11 platform connectors, 5 transformers, 3 OAuth helpers, "
        "33 smoke tests."
    )

    add_heading(doc, "6.1 Module layout", level=2)
    add_table(
        doc,
        ["Group", "Files", "Role"],
        [
            ["Core", "snowflower.py, models.py, base_connector.py, connectors_registry.py, measure.py", "CLI + data models + ABC + registry + metrics aggregator"],
            ["Connectors (11)", "connector_youtube.py, connector_linkedin.py, connector_bluesky.py, connector_beehiiv.py, connector_threads.py, connector_x.py, connector_tiktok.py, connector_instagram.py, connector_reddit.py, connector_naver_blog.py, connector_stibee.py", "Per-platform adapt() + publish() pairs"],
            ["Transformers (5)", "transformer_captions.py (Whisper), transformer_thumbnails.py (fal.ai), transformer_shorts_cut.py (ffmpeg), transformer_carousel.py, transformer_voiceover_kr.py (ElevenLabs)", "Source-asset transformations"],
            ["Auth (3)", "auth_youtube.py, auth_linkedin.py, auth_bluesky.py", "Browser-based OAuth helpers"],
            ["Content / docs", "ep001_episode.yaml, methodology.md, template_titles.md, template_disclosure.md, pitch_deck.md, accounts_setup.md, research_findings.md, DISCLOSURE.md, README.md", "First episode + reusable templates + strategic docs"],
            ["Reporting", "generate_report.py + this report", "Comprehensive strategy artifact (you are reading the output)"],
        ],
        col_widths=[1.3, 3.3, 2.4],
    )

    add_heading(doc, "6.2 Verified end-to-end", level=2)
    add_callout(
        doc,
        "Sprint 0 verification (2026-04-26)",
        "33/33 pytest assertions pass. health-check renders all 11 connectors. dry-run on "
        "ep001_episode.yaml processes 11 platforms end-to-end and writes ep001_results.json. "
        "Korean characters render via stdout UTF-8 reconfigure at snowflower.py entry "
        "(Windows cp949 fix). No live API calls made — every connector gated by --dry-run "
        "or missing credentials.",
        SUCCESS_HEX,
    )


def section_research(doc: Document) -> None:
    add_heading(doc, "7 · Research Findings — Professional Marketing Insights", level=1)
    doc.add_paragraph(
        "Synthesized from four parallel deep-research streams: (1) disability/accessibility "
        "creator + brand marketing; (2) independent tech-editorial channel growth playbooks; "
        "(3) B2B medical-grade assistive-tech sales channels; (4) content marketing tactics + "
        "sponsorship economics."
    )

    add_heading(doc, "7.1 Seven highest-leverage findings", level=2)
    add_table(
        doc,
        ["#", "Finding", "Source convergence"],
        [
            ["1", "Lock paid disabled co-host before ep1. Non-disabled-led accessibility channels hit credibility ceiling.", "All agents"],
            ["2", "Niche down to motor-disability + hands-free input only. Direct overlap with augmental's audience.", "All agents"],
            ["3", "Publish methodology page before first review (RTINGS playbook).", "Editorial + B2B"],
            ["4", "Pain Point SEO over thought leadership. BoFu queries convert 5–7% vs <0.5% for ToFu.", "Tactics agent"],
            ["5", "Newsletter is the asset; YouTube/LinkedIn/Bluesky are acquisition. Beehiiv (0% take) > Substack (10%).", "Editorial + Tactics"],
            ["6", "B2B audience density > raw size. 2,500 verified OT/SLP/AT-buyers = $200–400/placement.", "B2B + Tactics"],
            ["7", "Anchor 90-day arc to a conference moment — CSUN, ATIA, RESNA, Closing The Gap.", "All agents"],
        ],
        col_widths=[0.3, 4.4, 1.8],
    )

    add_heading(doc, "7.2 Cultural rules — non-negotiable", level=2)
    add_bullets(
        doc,
        [
            "'Nothing about us without us' — operationalized with paid disabled co-host, on-camera with editorial control.",
            "Identity-first vs person-first: ask the individual. Defaults vary by community.",
            "Cover augmental and its competitors fairly. Editorial credibility = sponsor leverage.",
            "Trigger pattern auto-reject (script-review checklist): inspiration porn, cure framing, 'overcoming,' before/after as transformation, ableist metaphors, 'wheelchair-bound,' 'high/low-functioning'.",
        ],
    )

    add_heading(doc, "7.3 Trade publications that accept sponsored editorial", level=2)
    add_table(
        doc,
        ["Publication", "Region", "Sponsored content product"],
        [
            ["The ASHA Leader", "US", "Yes — formal program"],
            ["OT Practice / AOTA", "US", "Yes — 2025 Media Planner publishes rate card"],
            ["AT Today", "UK", "Display + advertorial"],
            ["Closing The Gap newsletter + webinars", "US (education-AT)", "Formal advertising program"],
            ["Mobility Management", "US", "Wheelchair / seating / CRT trade press"],
            ["에이블뉴스 (ablenews.co.kr)", "KR", "광고/후원 form"],
            ["함께걸음 (hamkkewalk.co.kr)", "KR", "Inquiry-based"],
            ["더인디고 (theindigo.co.kr)", "KR", "Inquiry-based"],
        ],
        col_widths=[2.2, 1.6, 3.2],
    )

    add_heading(doc, "7.4 Conference circuit (2026 dates)", level=2)
    add_table(
        doc,
        ["Conference", "Dates", "Location", "Why"],
        [
            ["ATIA 2026", "Jan 29–31", "Orlando", "Industry anchor — Tobii Dynavox / PRC-Saltillo / AbleNet / Smartbox"],
            ["CSUN AT 2026", "Mar 9–13", "Anaheim", "Cross-disability — Microsoft / Apple / Google accessibility"],
            ["RESNA 2026", "Mar 26–27", "Long Beach", "Engineer / researcher — ATP credentialing"],
            ["Closing The Gap", "Oct 20–22", "Minneapolis", "AT Maker Fair — education-AT crowd"],
            ["RehaCare", "Sep (annual)", "Düsseldorf", "European procurement"],
        ],
        col_widths=[1.5, 1.2, 1.4, 2.9],
    )


def section_methodology(doc: Document) -> None:
    add_heading(doc, "8 · Test Methodology Framework", level=1)
    doc.add_paragraph(
        "snowflower's reviews are only as trustworthy as the methodology underneath them. "
        "Most accessibility-tech reviews stop at 'I tried it, here's how it felt' — that "
        "fails clinicians, who need repeatable numbers to justify procurement to insurance, "
        "schools, VA, or KEAD. The published methodology page (methodology.md, version 0.1, "
        "open for community review) is the credibility anchor."
    )

    add_heading(doc, "8.1 Six test categories", level=2)
    add_table(
        doc,
        ["#", "Category", "Primary metric"],
        [
            ["1", "Performance", "Fitts's law throughput (bits/sec, ISO 9241-411) + WPM (Soukoreff & MacKenzie)"],
            ["2", "Setup", "Minutes from unboxing to verified click"],
            ["3", "Sustainability", "Throughput retention % at 30 min + NASA-TLX + Borg CR10"],
            ["4", "Compatibility", "Verified OS × app matrix (macOS 26, iOS 26, Win 11/12, Android 16, ChromeOS)"],
            ["5", "Funding & access", "Out-of-pocket $ by funding path (insurance / Medicaid / VA / IEP / KEAD / KNAT / NHS)"],
            ["6", "Practical", "Hours of continuous use, charging time, weight, public-comfort"],
        ],
        col_widths=[0.3, 1.7, 4.5],
    )

    add_heading(doc, "8.2 The most important section: user-driven testing", level=2)
    doc.add_paragraph(
        "A non-disabled tester driving a MouthPad scores a particular throughput; a person "
        "with C2 SCI scores something different. Both numbers are real, but only the second "
        "matters to the buying decision. Every published snowflower review includes at least "
        "one disabled co-host as the primary tester for headline performance numbers. Their "
        "performance, not the non-disabled benchmark, is what we lead with. Non-disabled "
        "numbers are reported as a device-performance ceiling in an appendix."
    )

    add_callout(
        doc,
        "Open data commitment",
        "Every published review includes raw Fitts's law trial logs (CSV), NASA-TLX and "
        "Borg responses, the exact apparatus + software versions, and the vendor firmware "
        "version under test — hosted at github.com/ksk5429/snowflower/tree/main/data/<episode_id>. "
        "Methodology is versioned. Disputes via GitHub Issues with tag 'methodology' are "
        "addressed publicly.",
    )


def section_audience_density(doc: Document) -> None:
    add_heading(doc, "9 · Audience-Density Strategy", level=1)
    doc.add_paragraph(
        "The most important reframe from the research: augmental's pitch metric is not "
        "subscriber count — it is audience density. A snowflower with 2,500 verified "
        "OT/SLP/AT-buyer subscribers is worth more to augmental than 200,000 generic "
        "tech viewers. Augmental's bottleneck is not consumer awareness (MIT News, BBC, "
        "Verge, Forbes already covered them); it is clinical legitimacy with US OTs "
        "serving high-cervical SCI and ALS populations, plus a press surface for FDA "
        "clearance moments. snowflower exists to be that surface."
    )

    add_heading(doc, "9.1 Decision-makers by job title", level=2)
    add_bullets(
        doc,
        [
            "Speech-Language Pathologist (SLP) — gatekeeper for AAC / SGDs.",
            "Occupational Therapist (OT) — gatekeeper for access devices, switches, mounting (MouthPad falls here).",
            "RESNA-certified Assistive Technology Professional (ATP).",
            "AT Specialist at school district / BOCES — K-12 IEP procurement.",
            "VA prosthetist / OT / Polytrauma case manager — VA path; largest single institutional buyer in US.",
            "Rehab engineer / clinical educator at SCI rehab centers (Shepherd, Craig, Kessler, Magee, Spaulding).",
            "Korea: 작업치료사, 언어재활사, 보조공학사, 재활의학과 전문의, KEAD 보조공학센터 평가팀.",
        ],
    )

    add_heading(doc, "9.2 Revenue pyramid", level=2)
    add_table(
        doc,
        ["Tier", "Revenue source", "Plan"],
        [
            ["Floor", "YouTube AdSense + Amazon AT affiliate", "$50–200/mo at 1k–10k subs (FLOOR — never the strategy)"],
            ["Mid", "Beehiiv ad-network auto-fill + selective brand placements", "$40–80/mo at 1,200 subs · $200–400/placement at 2,500+"],
            ["High", "Patreon / membership for clinics + schools at $15–25/mo", "~50 subscribers = $1K/mo (the SBSK structural play)"],
            ["Anchor", "augmental (or Tobii / Quha) anchor sponsor at month 6+", "$3K–10K/mo · 6-month commitment with measured attribution"],
        ],
        col_widths=[0.8, 2.6, 3.1],
    )


def section_90day(doc: Document, timeline_path: Path) -> None:
    add_heading(doc, "10 · 90-Day Execution Plan", level=1)

    add_figure(
        doc, timeline_path,
        "Figure 10.1 — 90-day timeline. CSUN 2026 (W9, Anaheim) is the conference anchor; "
        "the augmental pitch lands at W12 with 90 days of measurable audience-density data.",
        width_inches=6.8,
    )

    add_table(
        doc,
        ["Week", "Deliverables"],
        [
            ["W1", "snowflower.tech registered · Bluesky live · YouTube Brand Account + Cloud OAuth · disabled co-host candidate identified · methodology page drafted"],
            ["W2", "Beehiiv newsletter live · 4 hero-piece outlines drafted · CSUN 2026 press credentials applied · ASHA Leader / OT Practice editorial pitch drafted"],
            ["W3", "Ep001 recorded (Apple AssistiveTouch primer) · methodology page published · first Bluesky 5-post intro thread"],
            ["W4", "Ep001 publishes · newsletter #1 · LinkedIn Company Page launch + first 3 posts"],
            ["W5–8", "Eps 2–5: MouthPad explainer · Quha Zono review · Tobii PCEye review · 'Funding paths for SGDs in 2026' · weekly newsletter · 2 LinkedIn/wk · daily Bluesky"],
            ["W9", "CSUN 2026 (Mar 9–13) — film 8–10 vendor booths, 5 clinician interviews, augmental on-camera if attending"],
            ["W10–11", "CSUN footage → 6-episode series · newsletter feature: 'What I learned at CSUN 2026'"],
            ["W12", "Pitch to augmental: data deck (audience composition, OT/SLP %, MouthPad-coverage views), 90-day metrics, three engagement options"],
        ],
        col_widths=[0.6, 6.2],
    )


def section_budget(doc: Document, budget_path: Path) -> None:
    add_heading(doc, "11 · Budget & Financial Model", level=1)
    doc.add_paragraph(
        "Target: $30 floor / $90 ceiling per month. Budget below assumes the channel "
        "passes 2,500 newsletter subscribers (Beehiiv paid tier kicks in) and includes "
        "headroom for paid X API and Korean voice generation."
    )

    add_figure(
        doc, budget_path,
        "Figure 11.1 — Monthly operating budget by category, within the $50–100/mo cap.",
        width_inches=6.5,
    )

    add_heading(doc, "11.1 Pricing posture (when revenue starts)", level=2)
    add_bullets(
        doc,
        [
            "Newsletter (B2B clinician density): $200–400 per placement at 1k–2.5k subs.",
            "LinkedIn post: $500–1,500 at 5k followers.",
            "YouTube anchor sponsor: $500–2,000/video at 5k–25k subs.",
            "Anchor placement package (target month 6+): $3K–10K/mo for 6-month commitment, scaling with measured attribution to augmental.tech traffic.",
            "Price by audience density (% verified OT/SLP/AT-buyer), not raw CPM.",
        ],
    )


def section_risk(doc: Document) -> None:
    add_heading(doc, "12 · Risk Register & Mitigation", level=1)
    add_table(
        doc,
        ["Risk", "Likelihood", "Mitigation"],
        [
            ["Disability community calls out non-disabled-led channel as parasitic", "Medium-high", "Paid disabled co-host of record before ep1. Standing escalation channel in DISCLOSURE.md. Editorial veto for subjects."],
            ["augmental rejects the pitch at day 90", "Medium", "Engine + audience are durable assets. Same pitch portable to Tobii / Quha / Glassouse. Channel monetizes via Patreon + anchor sponsor regardless."],
            ["YouTube demonetizes for 'sensitive content' (false flag)", "Medium", "Plan AdSense as ≤30% of revenue. Patreon + earned-media partnerships are primary."],
            ["Naver Blog suspension due to algorithmic detection", "Medium-high if cron-published", "Manual editing only — connector returns blocked_manual_only by design."],
            ["LinkedIn Marketing Developer Platform approval delayed", "Medium", "w_member_social fallback works on personal profile (admin-of-Page); migrate to w_organization_social once approved."],
            ["TikTok Content Posting API audit fails or stalls", "Medium", "Manual posting works without API; defer until first Bluesky / YouTube cycle is profitable."],
            ["Unauthorized use of augmental trademark surfaces complaint", "Low", "Nominative fair use only — never as account name / handle / logo. Disclosure in every post body. DISCLOSURE.md hard rules."],
            ["Single-editor burnout at month 4–6", "High if cadence too aggressive", "Pre-batch 4 episodes. Outsource editing once revenue covers $50–150/video. Defer Tier 2/3 platforms until Tier 1 is steady."],
            ["Korean market entry blocked by lack of MFDS clearance for MouthPad", "External (augmental dependency)", "Build awareness only — no KakaoTalk Channel / press outreach until augmental has KR distributor + 식약처 clearance."],
        ],
        col_widths=[2.5, 1.4, 3.0],
    )


def section_compliance(doc: Document) -> None:
    add_heading(doc, "13 · Legal & Compliance Framework", level=1)

    add_heading(doc, "13.1 Disclosure regimes", level=2)
    add_bullets(
        doc,
        [
            "US: FTC 16 CFR § 255 (Endorsement Guides), 16 CFR § 465 (Native Advertising).",
            "Korea: 표시·광고의 공정화에 관한 법률 (표시광고법) + KFTC 추천·보증 등에 관한 광고 심사지침.",
            "EU: Digital Services Act (DSA) Art. 26 — transparent advertising.",
            "Platform overlays: YouTube 'altered or synthetic' toggle; Instagram 'Paid partnership'; TikTok 'Promotional content'; Meta 'AI Info' label.",
        ],
    )

    add_heading(doc, "13.2 FDA / medical-claim rules", level=2)
    doc.add_paragraph(
        "MouthPad is a body-contacting electronic device. Claims about efficacy, "
        "regulatory status, or clinical outcomes are FDA-regulated under 21 CFR 801. "
        "snowflower's hard rule: no medical / efficacy claims about MouthPad (or any "
        "covered device) without direct attribution to the brand's published source. "
        "All claims are quoted with citation; snowflower does not present third-party "
        "claims as our own findings."
    )

    add_heading(doc, "13.3 Identity stance per platform", level=2)
    add_table(
        doc,
        ["Platform", "Brand-only OK?", "Why"],
        [
            ["YouTube (Brand Account), TikTok (Business), Instagram (Creator), Threads, Bluesky, X, Reddit, Substack/Beehiiv", "Yes", "Standard for editorial channels"],
            ["LinkedIn personal profile", "No", "ToS Art. 8.2 — fake-name personal accounts terminated"],
            ["LinkedIn Company Page", "Yes", "Brand-only is the entire point of a Company Page"],
        ],
        col_widths=[3.0, 1.4, 2.5],
    )


def section_conclusion(doc: Document) -> None:
    add_heading(doc, "14 · Conclusion & Next Actions", level=1)
    doc.add_paragraph(
        "snowflower exists at the intersection of three under-served categories: "
        "(1) high-quality independent editorial in accessibility-input technology; "
        "(2) clinician-readable B2B content for assistive-tech procurement decisions; "
        "(3) Korean-language coverage of accessibility-tech funding pathways. The "
        "engine + brand are designed to compound across all three, with augmental.tech "
        "as the anchor pitch at day 90 and Tobii / Quha / Glassouse as backup pitches "
        "if augmental passes."
    )

    add_callout(
        doc,
        "Smallest move that turns this into something real",
        "Register snowflower.tech (5 min, $15). Create snowflower.editorial@gmail.com. "
        "Mint Bluesky app password. Run python auth_bluesky.py to verify. Then python "
        "snowflower.py publish --episode ep001_episode.yaml --live --platforms bluesky "
        "for the first real published artifact. Total wall time: ~30 min.",
        SUCCESS_HEX,
    )

    add_heading(doc, "Immediate next actions (in order)", level=2)
    add_numbered(
        doc,
        [
            "Buy snowflower.tech via Porkbun or Namecheap (~$15/yr).",
            "Create snowflower.editorial@gmail.com + Google Voice number.",
            "Create Bluesky account, mint app password, populate .env, run python auth_bluesky.py.",
            "Publish ep001 to Bluesky (live) — proves the pipeline against a real API.",
            "Create YouTube Brand Account + Google Cloud project + OAuth (10 min). Run python auth_youtube.py.",
            "Create LinkedIn Company Page (skip personal profile per ToS).",
            "Identify and contract paid disabled co-host before episode 2.",
            "Apply for CSUN 2026 press credentials (deadline TBD; apply early).",
            "Pitch ASHA Leader + OT Practice editorial slots in week 2.",
            "Pre-batch 4 episodes before public launch — survives the early-burnout window where most niche channels die.",
        ],
    )


def section_appendix(doc: Document) -> None:
    add_heading(doc, "Appendix A · Repository structure", level=1)
    doc.add_paragraph(
        "Repository: github.com/ksk5429/snowflower (public, MIT license to be added). "
        "Branch: main. Layout is intentionally flat — all .py files at root, no package "
        "install. Run scripts directly via python <file>.py."
    )
    add_table(
        doc,
        ["Document", "Purpose"],
        [
            ["README.md", "Project overview, stack table, quick-start commands"],
            ["DISCLOSURE.md", "FTC + KFTC + EU DSA disclosure templates (4 kinds × EN/KR)"],
            ["methodology.md", "Test methodology framework (RTINGS-style); the credibility anchor"],
            ["accounts_setup.md", "Per-platform account-creation work-along checklist"],
            ["pitch_deck.md", "augmental.tech pitch (audience-density-first structure)"],
            ["research_findings.md", "Synthesized 4-stream marketing research playbook"],
            ["template_titles.md", "Pain Point SEO patterns + LinkedIn hook templates + ban list"],
            ["template_disclosure.md", "Copy-paste disclosure footers for post bodies"],
            ["ep001_episode.yaml", "First episode source — Apple AssistiveTouch primer"],
            ["snowflower_strategy_report.docx", "This document (auto-generated by generate_report.py)"],
        ],
        col_widths=[2.4, 4.4],
    )

    add_heading(doc, "Appendix B · References", level=1)
    add_bullets(
        doc,
        [
            "Augmental — augmental.tech; MIT News (June 2024) coverage of MouthPad",
            "FTC 16 CFR § 255 — Endorsement Guides",
            "Korea Fair Trade Commission 추천·보증 등에 관한 광고 심사지침",
            "ISO 9241-411:2012 — Evaluation methods for the design of physical input devices",
            "NASA-TLX (Hart & Staveland 1988) — subjective workload assessment",
            "Borg CR10 scale — perceived exertion",
            "ATIA 2026, CSUN AT 2026, RESNA 2026, Closing The Gap 2026",
            "ASHA Leader, AOTA OT Practice, AT Today UK, 에이블뉴스, 함께걸음, 더인디고",
            "RTINGS methodology pages (rtings.com/labs)",
            "Wirecutter founding-era review structure (Brian Lam, 2011–2016)",
            "Stratechery (Ben Thompson) — paid newsletter analytical-lens model",
            "Justin Welsh / Lara Acosta / Sahil Bloom — 2026 LinkedIn B2B playbooks",
            "Grow & Convert — Pain Point SEO methodology",
            "HubSpot — topic-cluster architecture",
            "MrBeast leaked memo (2023) — first-15-seconds + thumbnail rules",
        ],
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    print("Generating charts...")
    matrix_path = chart_platform_matrix()
    timeline_path = chart_90_day_timeline()
    budget_path = chart_budget_breakdown()
    print(f"  - {matrix_path}")
    print(f"  - {timeline_path}")
    print(f"  - {budget_path}")

    print("Building document...")
    doc = Document()
    set_core_properties(doc)
    configure_styles(doc)

    # Cover (in section 0)
    build_cover(doc)

    # New section break for the body — gets its own header/footer
    new_section = doc.add_section(WD_SECTION_START.NEW_PAGE)
    new_section.top_margin = Inches(0.85)
    new_section.bottom_margin = Inches(0.85)
    new_section.left_margin = Inches(0.85)
    new_section.right_margin = Inches(0.85)
    # Disable inheritance from previous section so cover stays clean
    new_section.header.is_linked_to_previous = False
    new_section.footer.is_linked_to_previous = False

    # TOC page
    toc_para = doc.add_paragraph()
    toc_run = toc_para.add_run("Table of Contents")
    toc_run.bold = True
    toc_run.font.size = Pt(20)
    toc_run.font.color.rgb = PRIMARY_RGB
    doc.add_paragraph()
    toc_field_para = doc.add_paragraph()
    _add_toc_field(toc_field_para)
    doc.add_paragraph(
        "(In Microsoft Word, right-click anywhere in the table above and select "
        "'Update Field' to populate the table of contents with current page numbers.)"
    ).runs[0].italic = True
    doc.paragraphs[-1].runs[0].font.size = Pt(9)
    doc.paragraphs[-1].runs[0].font.color.rgb = MUTED_RGB

    # Body sections
    section_executive_summary(doc)
    section_background(doc)
    section_strategic_premise(doc)
    section_brand(doc)
    section_platform(doc, matrix_path)
    section_engine(doc)
    section_research(doc)
    section_methodology(doc)
    section_audience_density(doc)
    section_90day(doc, timeline_path)
    section_budget(doc, budget_path)
    section_risk(doc)
    section_compliance(doc)
    section_conclusion(doc)
    section_appendix(doc)

    # Configure header/footer for body sections (skip cover at index 0)
    configure_header_footer(doc)

    print(f"Saving {REPORT_PATH}...")
    doc.save(REPORT_PATH)

    size_kb = REPORT_PATH.stat().st_size / 1024
    print(f"OK wrote {REPORT_PATH} ({size_kb:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
