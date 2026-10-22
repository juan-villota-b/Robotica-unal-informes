#!/usr/bin/env python3
"""Convierte INFORME_CAP5.md a HTML y luego a PDF con Chrome headless.

Uso:
    ~/venvs/robotica/bin/python Informe/md_a_pdf.py

Requiere mistune (ya está en el venv del curso) y Google Chrome.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import mistune

BASE_DIR = Path(__file__).resolve().parent
MD = BASE_DIR / "INFORME_CAP5.md"
HTML = BASE_DIR / "INFORME_CAP5.html"
PDF = BASE_DIR / "INFORME_CAP5.pdf"

CSS = """
@page { size: A4; margin: 18mm 16mm 18mm 16mm; }
* { box-sizing: border-box; }
body {
  font-family: "DejaVu Sans", Arial, sans-serif;
  font-size: 10.5pt;
  line-height: 1.45;
  color: #222;
  max-width: 100%;
}
h1 {
  font-size: 21pt;
  line-height: 1.2;
  margin: 0 0 6pt 0;
  color: #111;
  border-bottom: 2px solid #333;
  padding-bottom: 6pt;
}
h2 {
  font-size: 15pt;
  margin: 18pt 0 6pt 0;
  color: #111;
  border-bottom: 1px solid #bbb;
  padding-bottom: 3pt;
  page-break-after: avoid;
}
h3 {
  font-size: 12pt;
  margin: 14pt 0 4pt 0;
  color: #222;
  page-break-after: avoid;
}
h4 { font-size: 11pt; margin: 10pt 0 3pt 0; }
p { margin: 5pt 0; text-align: justify; }
ul, ol { margin: 4pt 0 6pt 18pt; padding: 0; }
li { margin: 2pt 0; }
code {
  font-family: "DejaVu Sans Mono", monospace;
  font-size: 9pt;
  background: #f2f2f2;
  padding: 1px 3px;
  border-radius: 2px;
}
pre {
  background: #f7f7f7;
  border: 1px solid #ddd;
  border-radius: 3px;
  padding: 7pt 9pt;
  font-size: 8.4pt;
  line-height: 1.35;
  white-space: pre-wrap;
  word-break: break-word;
  page-break-inside: avoid;
}
pre code { background: none; padding: 0; font-size: 8.4pt; }
table {
  border-collapse: collapse;
  width: 100%;
  margin: 8pt 0;
  font-size: 9pt;
  page-break-inside: avoid;
}
th, td {
  border: 1px solid #aaa;
  padding: 4pt 5pt;
  vertical-align: top;
  text-align: left;
}
th { background: #eee; font-weight: bold; }
img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 8pt auto 4pt auto;
  page-break-inside: avoid;
}
blockquote {
  border-left: 3px solid #999;
  margin: 6pt 0;
  padding-left: 10pt;
  color: #555;
}
hr { border: none; border-top: 1px solid #ccc; margin: 12pt 0; }
strong { color: #111; }
"""


def main() -> int:
    if not MD.exists():
        print(f"No existe {MD}", file=sys.stderr)
        return 1

    markdown = MD.read_text(encoding="utf-8")
    renderer = mistune.create_markdown(
        escape=False,
        plugins=["table", "strikethrough", "task_lists"],
    )
    body = renderer(markdown)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Informe Capítulo 5 — Navegación</title>
<style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>
"""
    HTML.write_text(html, encoding="utf-8")

    chrome = "google-chrome"
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        "--virtual-time-budget=8000",
        f"--print-to-pdf={PDF}",
        HTML.resolve().as_uri(),
    ]

    print("Generando PDF con Chrome…")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stdout, file=sys.stderr)
        print(proc.stderr, file=sys.stderr)
        return proc.returncode

    if not PDF.exists() or PDF.stat().st_size == 0:
        print("Chrome no generó el PDF.", file=sys.stderr)
        return 1

    print(f"HTML: {HTML}")
    print(f"PDF:  {PDF} ({PDF.stat().st_size / 1024:.0f} kB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
