"""D-123 — /about two-track extract is a substring of the owner Doc; no second About route.

Failure-reds: a missing `### D-123` heading, a missing aboutPaper import, a
paraphrased excerpt, a rewritten PAPER_QUESTIONS lead, or a second /about
route. An import error is not the assertion this file exists to fire.

⚠ `/adcs` is D-122 on `main` (`86f8a10` / #232). This file must not pin its
absence — that was true when D-123 was first written and is now a lie.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "docs" / "README.md"
PAPER = ROOT / "docs" / "pharmfold-adc-nectin4-paper.md"
ABOUT_PAPER = ROOT / "ui" / "src" / "aboutPaper.js"
ADC = ROOT / "ui" / "src" / "components" / "AdcContext.jsx"
APP = ROOT / "ui" / "src" / "App.jsx"

# Owner-supplied D-094 leads — pinned from AdcContext.jsx at 04023a8. A rewrite
# of PAPER_QUESTIONS fails here even if the rendered page still "sounds similar".
PAPER_QUESTION_LEADS = (
    "Does the shape of a protein tell you something about its suitability as an ADC target that its abundance does not?",
    "What can an expression-threshold screen actually support?",
)
PAPER_QUESTION_ASKS = (
    "This project asks whether a second, independent axis — derived from predicted structure — reorders that list."
)


def test_d123_heading_exists_in_the_log():
    log = LOG.read_text(encoding="utf-8")
    assert "### D-123 —" in log, "D-123 must be a real ### entry, not a citation of one"


def test_owner_doc_is_the_cited_file_on_disk():
    text = PAPER.read_text(encoding="utf-8")
    assert "## Part 2" in text
    assert "Track A — Reuse EV antibody" in text
    assert "not a universal V-domain key" in text


def test_aboutpaper_excerpts_are_substrings_of_the_doc():
    paper = PAPER.read_text(encoding="utf-8")
    src = ABOUT_PAPER.read_text(encoding="utf-8")
    assert "VERBATIM_EXCERPTS" in src
    # Load the JS string literals that aboutPaper.test.js also pins. A paraphrase
    # that keeps the export name but changes the words still fails the substring.
    assert "Wet binding assays — required" in src
    assert "Wet binding assays — required" in paper
    assert "No bind → stop" in src and "No bind → stop" in paper
    assert "rank by (cancer × membrane × internalization × density) / normal risk" in src
    assert "rank by (cancer × membrane × internalization × density) / normal risk" in paper
    assert "That same antibody is not a universal V-domain key." in src
    assert "That same antibody is not a universal V-domain key." in paper


def test_adccontext_imports_aboutpaper_and_does_not_rewrite_paper_questions():
    src = ADC.read_text(encoding="utf-8")
    assert "from '../aboutPaper.js'" in src
    assert "const PAPER_QUESTIONS = [" in src
    for lead in PAPER_QUESTION_LEADS:
        assert lead in src
    assert PAPER_QUESTION_ASKS in src
    # The new section is additive, not a replacement of the questions heading.
    assert "The questions this project is trying to answer" in src
    assert "Two tracks (Nectin-4 / ADC framing)" in src or "TWO_TRACKS_TITLE" in src


def test_app_still_has_exactly_one_about_route():
    app = APP.read_text(encoding="utf-8")
    assert app.count('path="/about"') == 1
    assert 'path="/about/' not in app
    assert 'element={<AdcContext />}' in app
    # D-122 shipped /adcs on main. This GO does not edit those routes.
    assert 'path="/adcs"' in app
    assert 'path="/adcs/:id"' in app
