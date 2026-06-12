#!/usr/bin/env python3
"""
convert_all_descriptions_to_html.py

Migrates the plain-text `description_sale` field of every product.template in Odoo
to a rich HTML version stored in the custom `x_description_sale_html` field.

Design system:
  Primary (dark green)  #20603D  – inclusion / general section headers
  Danger  (crimson)     #c0392b  – exclusion section headers
  Gold    (mustard)     #E5B745  – rate / tarifa section headers
  Neutral (charcoal)    #1f2937  – body text
  Muted   (slate)       #6b7280  – secondary text / notes
"""

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve project root so the script can be run from any working directory
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from odoo_cli import OdooClient


# ===========================================================================
# ─── DESIGN CONSTANTS ───────────────────────────────────────────────────────
# ===========================================================================

COLOR_PRIMARY  = "#20603D"   # dark green  – inclusions / general
COLOR_DANGER   = "#c0392b"   # crimson red – exclusions
COLOR_GOLD     = "#E5B745"   # mustard     – rates / tariffs
COLOR_BODY     = "#1f2937"   # near-black  – body copy
COLOR_MUTED    = "#6b7280"   # slate grey  – notes / sub-text
COLOR_BG_GREEN = "#f0fdf4"   # pale green  – intro card background
COLOR_BG_GRAY  = "#f9fafb"   # off-white   – section card background
COLOR_BORDER   = "#d1fae5"   # light green – card border

FONT_BASE = "font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;"

# ---------------------------------------------------------------------------
# Section classification dictionaries
# ---------------------------------------------------------------------------

INCLUSION_PATTERNS = [
    "INCLUDED SERVICES", "SERVICES INCLUDED", "INCLUDES", "INCLUYE",
    "SERVICIOS INCLUIDOS", "SERVIÇOS INCLUSOS", "SERVIÇOS INCLUÍDOS",
    "INCLUI", "INBEGRIFFENE LEISTUNGEN", "INKLUSIVE",
    "INCLUDED SERVICES ACCORDING TO TRAIN TYPE",
    # Numbered variants handled separately
]

EXCLUSION_PATTERNS = [
    "NOT INCLUDED", "NO INCLUYE", "SERVICES NOT INCLUDED",
    "SERVICIOS NO INCLUIDOS", "NO INCLUIDO",
    "NÃO INCLUSO", "SERVIÇOS NÃO INCLUSOS",
    "NICHT INBEGRIFFEN", "EXKLUSIVE",
    "NOT INCLUDED SERVICES",
]

RATES_PATTERNS = [
    "TARIFAS POR TIPO DE GRUPO", "TARIFAS", "RATES", "GROUP RATES",
    "TARIFAS POR GRUPO",
]

# Keywords that classify an all-caps / title-case line as a *general* section
GENERAL_SECTION_PATTERNS = [
    "TRANSPORTATION", "TRANSFERS", "TRANSPORTATION & TRANSFERS",
    "EXCURSIONS", "EXPERIENCES", "EXCURSIONS & EXPERIENCES",
    "ENTRANCE TICKETS", "PERMITS", "ENTRANCE TICKETS & PERMITS",
    "OFFICIAL ENTRANCE TICKETS & PERMITS",
    "PROFESSIONAL GUIDES", "SPECIALIZED STAFF", "STAFF",
    "TREKKING STAFF",
    "ACCOMMODATION", "CAMPSITES",
    "MEALS", "FULL MEAL PLAN", "MEAL PLAN",
    "CAMPING EQUIPMENT", "PREMIUM CAMPING EQUIPMENT",
    "EMERGENCY EQUIPMENT", "SAFETY", "PERMANENT ASSISTANCE",
    "SAFETY & PERMANENT ASSISTANCE",
    "GENERAL SERVICES",
    "MEALS INCLUDED",
    "INCLUDED TRAIN", "INCLUDED TRAIN – CHOOSE YOUR EXPERIENCE",
    "OPTION", "OPTION 1", "OPTION 2",
    "AIR TRANSPORTATION", "PERSONAL EQUIPMENT",
    "MEALS & DRINKS", "MEALS & BEVERAGES",
    "OPTIONAL ENTRANCE TICKETS & ACTIVITIES",
    "ADDITIONAL ACCOMMODATION & SERVICES",
    "TRAVEL INSURANCE",
    "TIPS & PERSONAL EXPENSES", "TIPS",
    "SLEEPING MATS", "SLEEPING BAGS", "TENTS", "PILLOWS", "BLANKETS",
    "DINING TENT", "KITCHEN TENT", "BATHROOM TENTS",
    "SATELLITE PHONES", "RADIOS", "FIRST AID KIT",
    "PROFESSIONAL GUIDE", "CHEFS", "WATER",
    "BREAKFASTS", "LUNCHES", "DINNERS", "TEA TIME", "SNACKS",
    "NOTE",
]


def _is_header_cased(text: str) -> bool:
    """
    True if the text looks like a section header rather than a descriptive sentence.
    Criteria: short line (<=70 chars) OR mostly upper-case (>=60% uppercase alpha chars).
    """
    stripped = text.strip().rstrip(":")
    if len(stripped) <= 70:
        return True
    alpha = [c for c in stripped if c.isalpha()]
    if not alpha:
        return True
    upper_ratio = sum(1 for c in alpha if c.isupper()) / len(alpha)
    return upper_ratio >= 0.55


def _classify_line(raw: str):
    """
    Returns one of: 'inclusion', 'exclusion', 'rates', 'general',
                    'sub_header', 'bullet', 'note', 'blank', 'paragraph'
    along with the cleaned display text.
    """
    stripped = raw.strip()
    if not stripped:
        return "blank", ""

    upper = stripped.upper().replace(":", "").strip()
    # Remove leading numbering  "1. TRANSPORTATION" → "TRANSPORTATION"
    upper_no_num = re.sub(r"^\d+\.\s*", "", upper).strip()

    # ---- Parenthetical-only lines → notes ---------------------------------
    if stripped.startswith("(") and stripped.endswith(")"):
        return "note", stripped

    # ---- Classify by keyword match ----------------------------------------
    def _matches(patterns, text):
        return any(p in text for p in patterns)

    if _matches(INCLUSION_PATTERNS, upper) or _matches(INCLUSION_PATTERNS, upper_no_num):
        if _is_header_cased(stripped):
            return "inclusion", stripped
    if _matches(EXCLUSION_PATTERNS, upper) or _matches(EXCLUSION_PATTERNS, upper_no_num):
        if _is_header_cased(stripped):
            return "exclusion", stripped
    if _matches(RATES_PATTERNS, upper) or _matches(RATES_PATTERNS, upper_no_num):
        if _is_header_cased(stripped):
            return "rates", stripped
    if _matches(GENERAL_SECTION_PATTERNS, upper) or _matches(GENERAL_SECTION_PATTERNS, upper_no_num):
        if _is_header_cased(stripped):
            return "general", stripped

    # ---- Sub-header: line ending with ":" that is short and not a sentence -
    if stripped.endswith(":") and len(stripped) < 80 and stripped.count(".") == 0:
        return "sub_header", stripped

    # ---- Numbered section: "1. Something" or "2. Something" at line start
    #      only if the text after the number is a short header-like phrase     --
    m = re.match(r"^\d+\.\s+(.+)$", stripped)
    if m and _is_header_cased(m.group(1)):
        return "general", stripped

    # ---- Bullet items -------------------------------------------------------
    if stripped.startswith(("-", "*", "•", "–")):
        return "bullet", stripped[1:].strip()

    return "paragraph", stripped


def _section_header_html(text: str, color: str, border_left_color: str = None,
                          bg: str = None, margin_top: str = "18px") -> str:
    bcolor = border_left_color or color
    background = f"background: {bg};" if bg else ""
    return (
        f'<div style="{FONT_BASE} color: {color}; font-size: 10.5px; '
        f'font-weight: 800; text-transform: uppercase; '
        f'letter-spacing: 0.06em; margin-top: {margin_top}; margin-bottom: 6px; '
        f'padding: 5px 10px 5px 10px; border-left: 3px solid {bcolor}; '
        f'{background} border-radius: 2px;">'
        f'{text.upper()}'
        f'</div>'
    )


def _sub_header_html(text: str) -> str:
    label = text.rstrip(":").strip()
    return (
        f'<div style="{FONT_BASE} color: {COLOR_BODY}; font-size: 10px; '
        f'font-weight: 700; margin-top: 8px; margin-bottom: 3px;">'
        f'{label}:'
        f'</div>'
    )


def _bullet_html(text: str) -> str:
    return (
        f'<li style="{FONT_BASE} color: {COLOR_BODY}; font-size: 10px; '
        f'line-height: 1.55; margin-bottom: 2px;">'
        f'{text}'
        f'</li>'
    )


def _paragraph_html(text: str) -> str:
    return (
        f'<p style="{FONT_BASE} color: {COLOR_BODY}; font-size: 10.5px; '
        f'line-height: 1.6; margin: 0 0 8px 0;">'
        f'{text}'
        f'</p>'
    )


def _note_html(text: str) -> str:
    # Remove outer parens for display
    inner = text.strip("(").rstrip(")")
    return (
        f'<p style="{FONT_BASE} color: {COLOR_MUTED}; font-size: 9.5px; '
        f'font-style: italic; line-height: 1.5; margin: 3px 0 4px 12px;">'
        f'{inner}'
        f'</p>'
    )


def _intro_box_html(paragraphs: list) -> str:
    """Wrap the intro paragraph(s) in a styled card."""
    content = "\n".join(_paragraph_html(p) for p in paragraphs)
    return (
        f'<div style="background: {COLOR_BG_GREEN}; border: 1px solid {COLOR_BORDER}; '
        f'border-radius: 4px; padding: 10px 12px; margin-bottom: 14px;">'
        f'{content}'
        f'</div>'
    )


def _ul_open() -> str:
    return (
        f'<ul style="margin: 0 0 6px 0; padding-left: 16px; '
        f'list-style-type: disc; color: {COLOR_BODY};">'
    )


UL_CLOSE = "</ul>"


# ===========================================================================
# ─── MAIN PARSER ────────────────────────────────────────────────────────────
# ===========================================================================

def text_to_html(text: str) -> str:
    """Convert a plain-text product description to premium branded HTML."""
    if not text or not text.strip():
        return ""

    lines = text.split("\n")

    # ----- Phase 1: classify every line ------------------------------------
    classified = []  # list of (kind, display_text)
    for line in lines:
        kind, display = _classify_line(line)
        classified.append((kind, display))

    # ----- Phase 2: separate leading intro paragraphs ----------------------
    # Collect all paragraph/blank lines that appear BEFORE the first section header.
    # A "section header" is any kind in {inclusion, exclusion, rates, general, sub_header}.
    SECTION_KINDS_DETECT = {"inclusion", "exclusion", "rates", "general", "sub_header"}

    # Find the index of the first real section header
    first_section_idx = None
    for i, (kind, _) in enumerate(classified):
        if kind in SECTION_KINDS_DETECT:
            first_section_idx = i
            break

    intro_paragraphs = []
    body_start = 0

    if first_section_idx is not None and first_section_idx > 0:
        # Everything before the first section header is intro material
        for i in range(first_section_idx):
            kind, display = classified[i]
            if kind == "paragraph":
                intro_paragraphs.append(display)
            # blanks between intro paragraphs are simply skipped
        body_start = first_section_idx
    elif first_section_idx is None:
        # No section headers at all → everything is a body paragraph
        body_start = 0
    else:
        # Section header is the very first line → no intro
        body_start = 0

    # ----- Phase 3: render -------------------------------------------------
    html_parts = []

    if intro_paragraphs:
        html_parts.append(_intro_box_html(intro_paragraphs))

    in_list = False
    last_kind = None

    def close_list():
        nonlocal in_list
        if in_list:
            html_parts.append(UL_CLOSE)
            in_list = False

    SECTION_KINDS = {"inclusion", "exclusion", "rates", "general"}

    # Track whether we are "inside" a section block (so paragraphs → bullets)
    after_section = False

    for kind, display in classified[body_start:]:
        if kind == "blank":
            close_list()
            after_section = False
            continue

        if kind in SECTION_KINDS:
            close_list()
            after_section = True
            if kind == "inclusion":
                html_parts.append(_section_header_html(display, COLOR_PRIMARY, bg="#f0fdf4"))
            elif kind == "exclusion":
                html_parts.append(_section_header_html(display, COLOR_DANGER, bg="#fff5f5"))
            elif kind == "rates":
                html_parts.append(_section_header_html(display, COLOR_GOLD, bg="#fffbeb"))
            else:  # general
                html_parts.append(_section_header_html(display, COLOR_PRIMARY,
                                                        border_left_color="#86efac",
                                                        margin_top="14px"))

        elif kind == "sub_header":
            close_list()
            after_section = True
            html_parts.append(_sub_header_html(display))

        elif kind == "bullet":
            if not in_list:
                html_parts.append(_ul_open())
                in_list = True
            html_parts.append(_bullet_html(display))
            after_section = True  # stay in section context

        elif kind == "note":
            close_list()
            html_parts.append(_note_html(display))
            after_section = False

        elif kind == "paragraph":
            # Inside a section block → render as bullet
            if after_section:
                if not in_list:
                    html_parts.append(_ul_open())
                    in_list = True
                html_parts.append(_bullet_html(display))
            else:
                close_list()
                html_parts.append(_paragraph_html(display))

        last_kind = kind

    close_list()

    return "\n".join(html_parts)


# ===========================================================================
# ─── ODOO MIGRATION ─────────────────────────────────────────────────────────
# ===========================================================================

def main():
    client = OdooClient()
    client.connect()
    print("✅ Connected to Odoo.")

    # Fetch all active languages
    print("\n📋 Fetching active languages...")
    langs = client.execute("res.lang", "search_read",
                            [["active", "=", True]], fields=["code"])
    lang_codes = [l["code"] for l in langs]
    print(f"   Languages: {lang_codes}")

    total_updated = 0

    for lang in lang_codes:
        print(f"\n{'─'*55}")
        print(f"🌐 Language: {lang}")
        print(f"{'─'*55}")

        # Fetch all templates with a non-empty description_sale
        templates = client.execute(
            "product.template",
            "search_read",
            [
                ["description_sale", "!=", False],
                ["description_sale", "!=", ""],
            ],
            fields=["id", "name", "description_sale"],
            context={"lang": lang},
        )

        print(f"   Found {len(templates)} products with descriptions.")

        for tmpl in templates:
            tid   = tmpl["id"]
            name  = tmpl["name"]
            plain = tmpl.get("description_sale") or ""

            if not plain.strip():
                continue

            html = text_to_html(plain)

            print(f"   ↳ [{tid:>4}] {name[:60]}")

            client.execute(
                "product.template",
                "write",
                [tid],
                {"x_description_sale_html": html},
                context={"lang": lang},
            )
            total_updated += 1

    print(f"\n{'═'*55}")
    print(f"🎉 Migration complete! {total_updated} records updated.")
    print(f"{'═'*55}\n")


if __name__ == "__main__":
    main()
