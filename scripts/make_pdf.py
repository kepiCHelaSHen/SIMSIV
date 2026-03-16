"""Convert SIMSIV paper Markdown to styled HTML for PDF printing."""
import markdown
import pathlib

md_path = pathlib.Path("docs/simsiv_calibrated_abm_gene_culture_coevolution.md")
html_path = pathlib.Path("docs/simsiv_paper1.html")

md_text = md_path.read_text(encoding="utf-8")

style = """
<html>
<head>
<meta charset="utf-8">
<style>
  body {
    font-family: Georgia, serif;
    max-width: 900px;
    margin: 40px auto;
    padding: 0 20px;
    line-height: 1.65;
    color: #111;
    font-size: 12pt;
  }
  h1 { font-size: 18pt; margin-bottom: 6px; }
  h2 { font-size: 14pt; margin-top: 28px; border-bottom: 1px solid #ccc; padding-bottom: 4px; }
  h3 { font-size: 12pt; margin-top: 20px; }
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;
    font-size: 11pt;
  }
  td, th {
    border: 1px solid #bbb;
    padding: 6px 10px;
    text-align: left;
  }
  th { background: #f0f0f0; font-weight: bold; }
  tr:nth-child(even) { background: #fafafa; }
  code {
    background: #f5f5f5;
    padding: 2px 5px;
    font-family: monospace;
    font-size: 10pt;
  }
  blockquote {
    border-left: 3px solid #ccc;
    margin-left: 0;
    padding-left: 16px;
    color: #444;
    font-style: italic;
  }
  strong { font-weight: bold; }
  em { font-style: italic; }
  hr { border: none; border-top: 1px solid #ddd; margin: 24px 0; }
  p { margin: 10px 0; }
</style>
</head>
<body>
"""

html_body = markdown.markdown(
    md_text,
    extensions=["tables", "fenced_code", "nl2br"]
)

full_html = style + html_body + "\n</body>\n</html>"
html_path.write_text(full_html, encoding="utf-8")
print(f"Done — open this file in Chrome and print to PDF:")
print(f"  {html_path.resolve()}")
