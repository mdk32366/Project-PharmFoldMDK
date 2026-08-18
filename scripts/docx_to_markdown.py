"""Convert a `.docx` to Markdown with the standard library only, for landing authored documents.

⚠⚠ **THIS EXISTS SO THE REPO COPY IS CHECKABLE BY REPRODUCTION, NOT BY LABEL** (KEEL-2 V9 Step 21).
A `.md` pasted into the tree is a claim that it matches the owner's `.docx`. A `.md` **derived by a
committed script from a `.docx` whose `sha256` is recorded in the `.md`'s own header** is a claim
anyone can check: re-run this, compare.

⚠ **Only the `.md` is committed.** Committing both formats would be two paths to one artifact —
KEEL-2 V9 Step 20's own subject, in the doctrine's own filing.

⚠ No third-party dependency. `python-docx`, `lxml` and `pandoc` are all absent here, and adding one
to land a doctrine document would put a dependency in the lock file for a one-way conversion.
A `.docx` is a zip of XML; that is all this needs to know.

**What it does NOT preserve, stated so a reader does not assume fidelity it lacks:** comments,
tracked changes, images, footnotes, exact numbering (ordered lists become `1.`), and styling beyond
bold/italic. ⚠ **Text, headings, list structure and tables are preserved; everything else is
dropped.** For doctrine documents that is the whole content, but the limitation is named rather
than discovered.

Usage:
    python scripts/docx_to_markdown.py IN.docx OUT.md [--title "..."]
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import zipfile
from xml.etree import ElementTree

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _text_of_run(run) -> str:
    """A run's text, with bold/italic mapped to Markdown. ⚠ Tabs and breaks are preserved as
    whitespace rather than dropped — a checklist that loses its indentation loses its structure."""
    parts = []
    for node in run:
        if node.tag == f"{W}t":
            parts.append(node.text or "")
        elif node.tag == f"{W}tab":
            parts.append("    ")
        elif node.tag in (f"{W}br", f"{W}cr"):
            parts.append("\n")
    text = "".join(parts)
    if not text.strip():
        return text
    props = run.find(f"{W}rPr")
    if props is not None:
        bold = props.find(f"{W}b") is not None
        italic = props.find(f"{W}i") is not None
        lead = len(text) - len(text.lstrip())
        trail = len(text) - len(text.rstrip())
        core = text.strip()
        if bold:
            core = f"**{core}**"
        if italic:
            core = f"*{core}*"
        text = text[:lead] + core + text[len(text) - trail:] if trail else text[:lead] + core
    return text


def _paragraph(par) -> str:
    style = ""
    numbered = False
    props = par.find(f"{W}pPr")
    if props is not None:
        st = props.find(f"{W}pStyle")
        if st is not None:
            style = st.get(f"{W}val", "")
        numbered = props.find(f"{W}numPr") is not None

    body = "".join(_text_of_run(r) for r in par.iter(f"{W}r")).strip()
    if not body:
        return ""

    m = re.fullmatch(r"(?:Heading|heading)\s*(\d)", style)
    if m:
        return "#" * min(int(m.group(1)) + 1, 6) + " " + body
    if style in ("Title",):
        return "# " + body
    if style in ("Subtitle",):
        return "*" + body + "*"
    if numbered or style.startswith("List"):
        return "- " + body
    if style in ("Quote", "IntenseQuote"):
        return "> " + body
    return body


def _table(tbl) -> str:
    rows = []
    for tr in tbl.findall(f"{W}tr"):
        cells = []
        for tc in tr.findall(f"{W}tc"):
            cell = " ".join(
                "".join(_text_of_run(r) for r in p.iter(f"{W}r")).strip()
                for p in tc.findall(f"{W}p"))
            cells.append(cell.replace("|", "\\|").strip())
        if cells:
            rows.append(cells)
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    out = ["| " + " | ".join(rows[0]) + " |",
           "|" + "---|" * width]
    out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(out)


def convert(src: pathlib.Path) -> str:
    with zipfile.ZipFile(src) as zf:
        xml = zf.read("word/document.xml")
    root = ElementTree.fromstring(xml)
    body = root.find(f"{W}body")
    blocks: list[str] = []
    for child in body:
        if child.tag == f"{W}p":
            blocks.append(_paragraph(child))
        elif child.tag == f"{W}tbl":
            blocks.append(_table(child))
    out: list[str] = []
    for b in blocks:
        if not b:
            if out and out[-1] != "":
                out.append("")
            continue
        # ⚠ consecutive list items stay adjacent; everything else gets a blank line
        if out and out[-1].startswith("- ") and b.startswith("- "):
            out.append(b)
        else:
            if out and out[-1] != "":
                out.append("")
            out.append(b)
    return "\n".join(out).strip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("dst")
    args = ap.parse_args()

    src = pathlib.Path(args.src)
    digest = hashlib.sha256(src.read_bytes()).hexdigest()
    body = convert(src)

    header = (
        f"<!-- DERIVED FILE — do not hand-edit. -->\n"
        f"<!-- source: {src.name} -->\n"
        f"<!-- source sha256: {digest} -->\n"
        f"<!-- derived by: scripts/docx_to_markdown.py -->\n\n"
        f"> ⚠ **Derived from `{src.name}`**, sha256 `{digest}`.\n"
        f"> **The `.docx` is the owner's authored master; this Markdown is the repository record.**\n"
        f"> ⚠⚠ Only the Markdown is committed — two formats of one document is two paths to one\n"
        f"> artifact (KEEL-2 V9 Step 20). Re-derive with\n"
        f"> `python scripts/docx_to_markdown.py <source>.docx <this file>` and compare.\n\n"
        f"---\n\n")
    pathlib.Path(args.dst).write_text(header + body, encoding="utf-8")
    print(f"{src.name}\n  sha256 {digest}\n  -> {args.dst}  ({len(body):,} chars of body)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
