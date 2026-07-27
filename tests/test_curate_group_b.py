"""Tests for scripts/curate_group_b.py — pure functions only, no network.

The calibration test is the one that matters: the six near-misses from D-040 that each look like a
Group B positive and are not. If the flags do not separate them from a real ADC, the script is
routing the owner's attention wrongly and is worse than no script.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from curate_group_b import classify_evidence, parse_uniprot_aliases  # noqa: E402


# --------------------------------------------------------------------------------------
# The invariant that keeps a registry miss from becoming a false label
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "", "some unrelated cardiology trial", "enfortumab vedotin in urothelial carcinoma",
    "radiolabeled antibody", "a peptide-drug conjugate", "tarextumab phase II",
])
def test_classify_never_asserts_a_label(text):
    """No input may produce a true/false determination. The script flags; the owner decides."""
    result = classify_evidence(text)
    assert result["suggested_status"].startswith("review_")
    assert result["suggested_status"] not in {"true", "false"}
    assert isinstance(result["flags"], list)


# --------------------------------------------------------------------------------------
# Positive controls
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("agent", [
    "enfortumab vedotin", "trastuzumab deruxtecan", "ado-trastuzumab emtansine",
    "anetumab ravtansine", "depatuxizumab mafodotin", "gemtuzumab ozogamicin",
    "sacituzumab govitecan", "ladiratuzumab vedotin",
])
def test_known_adcs_flag_as_probable_group_b(agent):
    result = classify_evidence(f"A study of {agent} in advanced solid tumors")
    assert "adc_payload_stem" in result["flags"]
    assert result["suggested_status"] == "review_as_probable_group_b"


def test_generic_adc_phrase_is_enough_without_a_stem():
    result = classify_evidence("XYZ-123, an antibody-drug conjugate targeting CDH17")
    assert "adc_phrase" in result["flags"]
    assert result["suggested_status"] == "review_as_probable_group_b"


# --------------------------------------------------------------------------------------
# The calibration set — six cohort targets that look like yes and are not (D-040)
# --------------------------------------------------------------------------------------

CALIBRATION = [
    ("NOTCH2", "Tarextumab (OMP-59R5), an anti-Notch2/3 monoclonal antibody, phase II",
     "naked_antibody_suspected"),
    ("CSF1R", "Emactuzumab, a monoclonal antibody against CSF1R, in solid tumors",
     "naked_antibody_suspected"),
    ("OSMR", "Vixarelimab, a human monoclonal antibody to oncostatin M receptor beta",
     "naked_antibody_suspected"),
    ("IGF2R", "Radiolabeled monoclonal antibody to IGF2R in osteosarcoma",
     "radioimmunoconjugate_suspected"),
    ("SORT1", "TH1902, a sortilin-targeting peptide-drug conjugate",
     "peptide_drug_conjugate_suspected"),
]


@pytest.mark.parametrize("symbol,text,expected_flag", CALIBRATION)
def test_calibration_cases_are_not_routed_as_probable_group_b(symbol, text, expected_flag):
    result = classify_evidence(text)
    assert expected_flag in result["flags"], f"{symbol}: expected {expected_flag}, got {result}"
    assert result["suggested_status"] == "review_as_probable_exclusion", (
        f"{symbol} would have been routed as a probable positive — the flags do not separate it"
    )
    assert "adc_payload_stem" not in result["flags"]


def test_radio_conjugate_of_an_antibody_is_not_read_as_an_adc():
    """A radioimmunoconjugate names an antibody and a payload-ish word. It is still not an ADC."""
    result = classify_evidence("177Lu-labeled anti-PSMA antibody radioimmunoconjugate")
    assert "radioimmunoconjugate_suspected" in result["flags"]
    assert result["suggested_status"] == "review_as_probable_exclusion"


# --------------------------------------------------------------------------------------
# Alias parsing — degrade, never empty
# --------------------------------------------------------------------------------------

def test_symbol_survives_an_empty_uniprot_payload():
    assert parse_uniprot_aliases("SLC39A6", {}) == ["SLC39A6"]


def test_aliases_include_synonyms_and_alternative_names():
    payload = {
        "genes": [{"geneName": {"value": "SLC39A6"},
                   "synonyms": [{"value": "LIV1"}, {"value": "ZIP6"}]}],
        "proteinDescription": {
            "alternativeNames": [
                {"fullName": {"value": "Estrogen-regulated protein LIV-1"},
                 "shortNames": [{"value": "LIV-1"}]}
            ]
        },
    }
    aliases = parse_uniprot_aliases("SLC39A6", payload)
    assert "LIV1" in aliases and "ZIP6" in aliases and "LIV-1" in aliases
    assert "SLC39A6" in aliases


def test_useless_alias_tokens_are_dropped():
    payload = {"genes": [{"geneName": {"value": "X"},
                          "synonyms": [{"value": "6"}, {"value": "ZIP6"}]}]}
    aliases = parse_uniprot_aliases("SLC39A6", payload)
    assert "X" not in aliases and "6" not in aliases
    assert "ZIP6" in aliases
