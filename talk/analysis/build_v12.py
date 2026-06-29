"""Deck v11 -> v12: thread the point-agreement result into the evidence arc.

Adds a small footnote to slide 8 ("converged agreement", measured) and slide 17 ("per-decision,
not per-person") with the new number: calibrated annotators match the expert grader (Pat) on ~99%
of individual point decisions, while the unpromoted group is bimodal with a low tail. Companion
figure: ../fig_point_agreement.png (make_point_agreement_figure.py). Scripted/reversible; each
edit only ADDS a textbox, so nothing existing is disturbed. Run with BERLIN_TALK pointing at talk/.
"""
import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

HERE = Path(__file__).resolve().parent
TALK = Path(os.environ.get("BERLIN_TALK", HERE.parent))
prs = Presentation(str(TALK / "berlin_deck_v11.pptx")); S = prs.slides

def add_footnote(slide, text):
    tb = slide.shapes.add_textbox(Inches(0.6), Inches(6.62), Inches(11.4), Inches(0.36))
    tf = tb.text_frame; tf.word_wrap = True
    r = tf.paragraphs[0].add_run(); r.text = text
    f = r.font; f.size = Pt(11); f.italic = True; f.color.rgb = RGBColor(0x2A, 0x4D, 0x7A)
    return tb

log = []
add_footnote(S[7], "Converged agreement, measured: calibrated annotators match the expert grader on "
                   "~99% of individual point decisions (promoted median 100%, expert 98%).  → fig_point_agreement")
log.append("S8 footnote: ~99% point-agreement (converged agreement)")
add_footnote(S[16], "Per-decision convergence: promoted ≈ expert — both ~99% point-agreement with the grader; "
                    "the unpromoted group is bimodal with a low tail.  → fig_point_agreement")
log.append("S17 footnote: promoted ≈ expert ~99%, unpromoted bimodal")

prs.save(str(TALK / "berlin_deck_v12.pptx"))
print("saved berlin_deck_v12.pptx |", len(prs.slides), "slides | edits:", log)
