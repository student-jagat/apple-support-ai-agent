"""
Script to generate a beautifully styled PDF from REPORT.md using Microsoft Edge headless print.
"""
import os
import subprocess
import markdown

WORKSPACE = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
REPORT_MD = os.path.join(WORKSPACE, "REPORT.md")
REPORT_HTML = os.path.join(WORKSPACE, "REPORT.html")
REPORT_PDF = os.path.join(WORKSPACE, "REPORT.pdf")

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(EDGE_PATH):
    EDGE_PATH = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

def build_html():
    with open(REPORT_MD, "r", encoding="utf-8") as f:
        md_content = f.read()

    html_body = markdown.markdown(
        md_content,
        extensions=["tables", "fenced_code", "toc"]
    )

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Technical Evaluation & System Architecture Report: @AppleSupport AI Agent</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 18mm 16mm 18mm 16mm;
  }}

  * {{
    box-sizing: border-box;
  }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #1f2328;
    background: #ffffff;
    line-height: 1.55;
    font-size: 10.5pt;
    margin: 0;
    padding: 20px 30px;
  }}

  h1 {{
    font-size: 20pt;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 2px solid #0284c7;
    padding-bottom: 8px;
    margin-top: 0;
    margin-bottom: 12px;
  }}

  h2 {{
    font-size: 14pt;
    font-weight: 600;
    color: #0f172a;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 5px;
    margin-top: 24px;
    margin-bottom: 10px;
    page-break-after: avoid;
  }}

  h3 {{
    font-size: 11.5pt;
    font-weight: 600;
    color: #1e293b;
    margin-top: 16px;
    margin-bottom: 6px;
    page-break-after: avoid;
  }}

  p, li {{
    color: #334155;
    margin-top: 4px;
    margin-bottom: 8px;
  }}

  ul, ol {{
    padding-left: 22px;
    margin-top: 4px;
    margin-bottom: 8px;
  }}

  li {{
    margin-bottom: 4px;
  }}

  strong {{
    color: #0f172a;
    font-weight: 600;
  }}

  hr {{
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 18px 0;
  }}

  /* Tables */
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0;
    font-size: 9pt;
    page-break-inside: avoid;
  }}

  th, td {{
    padding: 7px 10px;
    text-align: left;
    border: 1px solid #cbd5e1;
    vertical-align: top;
  }}

  th {{
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: 600;
  }}

  tr:nth-child(even) td {{
    background-color: #f8fafc;
  }}

  /* Code and Pre */
  code {{
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
    font-size: 8.8pt;
    background-color: #f1f5f9;
    color: #0f172a;
    padding: 2px 5px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
  }}

  pre {{
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 3px solid #0284c7;
    border-radius: 4px;
    padding: 10px 14px;
    font-size: 8.5pt;
    line-height: 1.4;
    overflow-x: auto;
    page-break-inside: avoid;
    margin: 12px 0;
  }}

  pre code {{
    background: transparent;
    border: none;
    padding: 0;
    color: #1e293b;
  }}

  a {{
    color: #0284c7;
    text-decoration: none;
  }}

  /* Blockquotes */
  blockquote {{
    margin: 12px 0;
    padding: 6px 14px;
    border-left: 4px solid #0284c7;
    background: #f8fafc;
    color: #475569;
  }}

  /* Print specific */
  @media print {{
    body {{
      padding: 0;
      font-size: 9.8pt;
    }}
    h2, h3 {{
      page-break-after: avoid;
    }}
    table, pre, blockquote {{
      page-break-inside: avoid;
    }}
  }}
</style>
</head>
<body>
{html_body}
</body>
</html>
"""
    with open(REPORT_HTML, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"Generated HTML at: {REPORT_HTML}")

def convert_to_pdf():
    file_url = f"file:///{REPORT_HTML.replace(os.sep, '/')}"
    cmd = [
        EDGE_PATH,
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={REPORT_PDF}",
        "--no-pdf-header-footer",
        file_url
    ]
    print("Running Edge PDF converter...")
    subprocess.run(cmd, check=True)
    if os.path.exists(REPORT_PDF):
        size_kb = os.path.getsize(REPORT_PDF) / 1024
        print(f"SUCCESS: Generated PDF at {REPORT_PDF} ({size_kb:.1f} KB)")
    else:
        print("Error: PDF was not generated.")

if __name__ == "__main__":
    build_html()
    convert_to_pdf()
