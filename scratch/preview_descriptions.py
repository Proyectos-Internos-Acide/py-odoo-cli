#!/usr/bin/env python3
"""
Preview HTML output from descriptions.json without touching Odoo.
Generates: /home/acide/py-odoo-cli/scratch/preview_descriptions.html
"""
import json, sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from convert_all_descriptions_to_html import text_to_html

DATA_FILE = Path(__file__).parent / "descriptions.json"
OUT_FILE  = Path(__file__).parent / "preview_descriptions.html"

data: dict = json.loads(DATA_FILE.read_text(encoding="utf-8"))

cards = []
for name, plain in data.items():
    if not plain or not plain.strip():
        continue
    html_body = text_to_html(plain)
    card = f"""
    <div class="card">
      <div class="card-header">{name}</div>
      <div class="card-body">{html_body}</div>
    </div>
    """
    cards.append(card)

page = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Preview – Wayki Trek Product Descriptions</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    background: #f3f4f6;
    margin: 0;
    padding: 24px;
    color: #1f2937;
  }}
  h1 {{
    font-size: 22px;
    font-weight: 800;
    color: #20603D;
    margin-bottom: 24px;
    border-bottom: 3px solid #E5B745;
    padding-bottom: 8px;
  }}
  .card {{
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    margin-bottom: 28px;
    overflow: hidden;
    max-width: 820px;
  }}
  .card-header {{
    background: #20603D;
    color: #fff;
    font-size: 13px;
    font-weight: 700;
    padding: 10px 16px;
    letter-spacing: 0.03em;
  }}
  .card-body {{
    padding: 14px 16px;
  }}
</style>
</head>
<body>
<h1>🌿 Wayki Trek – Product Description Preview</h1>
{''.join(cards)}
</body>
</html>
"""

OUT_FILE.write_text(page, encoding="utf-8")
print(f"✅ Preview written to: {OUT_FILE}")
