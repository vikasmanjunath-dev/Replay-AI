"""Guard the finalized pitch deck against claims that diverge from the build."""

from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[2]
DECK = ROOT / "deliverables" / "RELAY_AI_Hackathon_Pitch_Deck_Aligned_v3.pptx"


def _presentation_text():
    with ZipFile(DECK) as archive:
        parts = (
            name
            for name in archive.namelist()
            if name.startswith(("ppt/slides/slide", "ppt/notesSlides/notesSlide"))
            and name.endswith(".xml")
        )
        return "\n".join(
            " ".join(
                element.text or ""
                for element in ElementTree.fromstring(archive.read(name)).iter()
                if element.tag.endswith("}t")
            )
            for name in parts
        )


def test_pitch_deck_describes_the_real_three_stage_pipeline():
    text = _presentation_text()
    assert "Three model stages" in text
    assert "Stage A · model" in text
    assert "Stage B · model" in text
    assert "Stage C · model" in text
    assert "Deterministic runner" in text
    assert "Human approval" in text
    assert "GitHub" in text


def test_pitch_deck_uses_real_lifecycle_and_protected_action_claims():
    text = _presentation_text()
    assert "AWAITING_HUMAN_APPROVAL" in text
    assert "COMMITTED" in text
    assert "REJECTED" in text and "FAILED" in text and "CANCELLED" in text
    assert "PR_CREATED and RESOLVED are not pipeline statuses" in text
    assert "published branch" in text
    assert "Relay does not push, merge, or deploy" in text
    assert "APPROVED > PR_CREATED > RESOLVED" not in text
    assert "Five specialists" not in text
    assert "pull request after approval" not in text.lower()


def test_closing_slide_headline_fits_without_wrapping_into_subtitle():
    text = _presentation_text()
    assert "One tested change out." in text
    assert "Agents do the work. Humans hold the decision." in text
