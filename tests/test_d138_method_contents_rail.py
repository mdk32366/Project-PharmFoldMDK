"""D-138 — the `/method` contents rail, checked at the FILE level.

⚠ The behaviour half lives in ``ui/src/components/MethodNote.toc.test.jsx``, which mounts
the page and walks the rendered rail. This file is the other half, and it exists because
the rail is **derived**: ``MethodToc`` reads the headings out of the mounted body, so a
heading with no ``id`` does not produce a broken link — it produces **no link at all**, and
a rendered-DOM test that compares the rail to the ids it can see agrees with itself.

So the invariant that actually needs pinning is upstream of the render: **every ``h2``/``h3``
on the Method page carries an ``id``**, read off the source the way ``test_image_contents.py``
reads a non-Python artefact as its subject. And its mirror: **no section name is typed into
the rail component**, because a typed list is the ghost-entry failure the GO forbids.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = ROOT / "ui" / "src" / "components"
METHOD_NOTE = (COMPONENTS / "MethodNote.jsx").read_text(encoding="utf-8")
METHOD_TOC = (COMPONENTS / "MethodToc.jsx").read_text(encoding="utf-8")
GLOSSARY = (COMPONENTS / "Glossary.jsx").read_text(encoding="utf-8")
SPAN_GLOSSARY = (COMPONENTS / "SpanGlossary.jsx").read_text(encoding="utf-8")
LOG = (chr(10) * 2).join((ROOT / "docs" / n).read_text(encoding="utf-8")
                      for n in ("decisions.md", "findings.md", "assumptions.md", "README.md"))
ARCHITECTURE = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")

# The Method page's sections come from three components; the rail spans all three.
METHOD_SURFACES = {
    "MethodNote.jsx": METHOD_NOTE,
    "Glossary.jsx": GLOSSARY,
    "SpanGlossary.jsx": SPAN_GLOSSARY,
}

HEADING = re.compile(r"<(h[23])\b([^>]*)>")
ID_ATTR = re.compile(r'\bid="([^"]+)"')


def _code(text: str) -> str:
    """The component minus its comments.

    ⚠ The rail's own comments explain WHY it derives its entries, and naming D-121 there
    is the explanation, not a typed section name. The fence below is about what the
    component can render, so it reads the code.
    """
    return "\n".join(
        line for line in text.split("\n") if not line.lstrip().startswith("//")
    )


def _headings(text: str) -> list[tuple[str, str | None]]:
    out: list[tuple[str, str | None]] = []
    for match in HEADING.finditer(text):
        attrs = match.group(2)
        found = ID_ATTR.search(attrs)
        out.append((match.group(1), found.group(1) if found else None))
    return out


def test_every_method_heading_carries_an_anchor_id():
    """⚠ The direction a derived rail CANNOT catch: a heading that silently drops out.

    A section with no ``id`` is a section the contents rail does not list and no link
    can reach. There is no error anywhere — the rail simply gets shorter, which is why
    this is asserted on the source rather than on the render.
    """
    missing: list[str] = []
    total = 0
    for name, text in METHOD_SURFACES.items():
        for tag, anchor in _headings(text):
            total += 1
            if not anchor:
                missing.append(f"{name}: <{tag}> with no id")
    assert missing == [], (
        "every h2/h3 on /method must carry an id or it drops out of the D-138 "
        f"contents rail: {missing}"
    )
    # Fourteen at D-138, measured. Not an upper bound: a section added without an id
    # reddens above, and one added WITH an id is welcome and moves this number.
    assert total >= 14, f"expected at least the 14 D-138 sections, found {total}"


def test_anchor_ids_are_unique_across_the_page():
    """Two headings with one id makes one of them unreachable and the rail a liar."""
    seen: list[str] = []
    for text in METHOD_SURFACES.values():
        seen.extend(a for _, a in _headings(text) if a)
    duplicates = sorted({a for a in seen if seen.count(a) > 1})
    assert duplicates == [], f"duplicate heading ids on /method: {duplicates}"


def test_the_sections_a_reader_comes_for_are_addressable_by_a_stable_name():
    """The ids a Spec, a PR or the log may cite as `/method#…`.

    ⚠ Named here, not generated: these are the addresses D-138's log entry hands out,
    so renaming one silently breaks a citation rather than a render.
    """
    for anchor in (
        "where-the-deep-learning-runs",  # D-051
        "hold-48-tiles-and-assembler",  # D-121
        "kabsch-path-restitch",  # D-125-B
        "overlap-confidence-kabsch",  # D-126-B
        "piecewise-domain-kabsch",  # D-127-B
        "linker-seam-honesty",  # D-128-B
        "phase-5-named-refuse",  # D-129-B
        "phase-4-named-refuse",  # D-130-B / D-131
        "non-goals",  # D-028
    ):
        assert f'id="{anchor}"' in METHOD_NOTE, anchor


def test_the_rail_types_no_section_name_of_its_own():
    """⚠ The ghost-entry fence, and the reason the rail is derived at all.

    A contents list written in the component is a second copy of the section names, free
    to name a section the page dropped. ``MethodToc`` must therefore query the DOM and
    must not contain the headings it renders.
    """
    code = _code(METHOD_TOC)
    assert "querySelectorAll" in code
    assert "h2[id], h3[id]" in code
    for name in (
        "Kabsch",
        "hold-48",
        "D-051",
        "D-121",
        "D-127",
        "Glossary",
        "commitments",
    ):
        assert name not in code, (
            f"MethodToc.jsx must not spell the section name {name!r} — the entries are "
            "read off the rendered headings, and a typed copy is the ghost entry D-138 "
            "decision 1 forbids"
        )


def test_the_rail_is_not_javascript_only():
    """Every entry is a real fragment link; the smooth scroll is an enhancement.

    ⚠ ``scrollIntoView`` is feature-detected and the handler returns WITHOUT calling
    ``preventDefault`` when it is absent, so the ``href`` still navigates.
    """
    assert 'href={`#${entry.id}`}' in METHOD_TOC
    handler = _code(METHOD_TOC)
    handler = handler[handler.index("const jump ="):]
    guard = handler.index("scrollIntoView !== 'function'")
    assert guard < handler.index("preventDefault"), (
        "the scrollIntoView feature-detect must return before preventDefault, or a "
        "browser without it gets a dead link"
    )


def test_the_rail_carries_navigation_and_no_claims():
    """A contents list is the most tempting place here to put a rollup. It has none."""
    code = _code(METHOD_TOC)
    for forbidden in ("PASS", "REFUSE", "Å", "F-004", "accept-refuse", "0 of 7"):
        assert forbidden not in code, forbidden


def test_d138_is_recorded_in_the_log_and_the_architecture():
    """CLAUDE.md rule 1: the entry itself, not a commit message naming it (method note 7)."""
    assert re.search(r"^### D-138 — `/method` gets a contents rail", LOG, re.M), (
        "D-138 must have its own ### entry in docs/README.md"
    )
    entry = LOG[LOG.index("### D-138 —"):]
    entry = entry[: entry.index("\n### ")]
    # The claims the GO fenced, restated where the decision is recorded.
    for phrase in ("CLOSED", "no F-004", "Deep-learning justification"):
        assert phrase in entry, phrase
    # ⚠ 137 is spent on a branch, not free. The entry must say so rather than look like
    # an off-by-one.
    assert "D-137" in entry and "#261" in entry
    assert "D-138" in ARCHITECTURE, "ARCHITECTURE.md must carry the /method rail"
