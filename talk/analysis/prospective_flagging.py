"""Prospective deployment view: rank fullyProofread tasks by a GROUND-TRUTH-FREE behavioral
anomaly score (slow-for-this-person), show error-catch (recall) vs fraction flagged for
re-review. The value proposition for the prospective test: flag risky decisions without GT."""
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score
import os
from pathlib import Path
HERE=Path(__file__).resolve().parent
OUT=Path(os.environ.get("BERLIN_DATA", HERE/"live_out"))   # CSVs (override with BERLIN_DATA)
TALK=Path(os.environ.get("BERLIN_TALK", HERE.parent))      # repo talk/ for figure output
CAV="Preliminary analysis — MICrONS proofreading annotators"
def _cav():
    plt.figtext(0.995,0.004,CAV,ha="right",va="bottom",fontsize=6,style="italic",color="0.5")
T=pd.read_csv(OUT/"separability_task.csv").dropna(subset=["dur"]).copy()
T=T[T.groupby("assignee")["assignee"].transform("size")>=10].copy()
T["dur_z"]=T.groupby("assignee")["dur"].transform(lambda s:(s-s.mean())/(s.std() if s.std() else 1))
# GT-FREE anomaly score = slow-for-this-person (the significant signal). No labels used.
T=T.sort_values("dur_z",ascending=False).reset_index(drop=True)
n=len(T); E=int(T.err.sum()); base=E/n
frac=np.arange(1,n+1)/n
recall=np.cumsum(T.err.values)/E
auc=roc_auc_score(T.err,T.dur_z)
print(f"tasks={n}, errors={E} (base-rate {base:.2f}), GT-free score AUC={auc:.3f}")
lifts={}
for q in [0.10,0.20,0.30,0.50]:
    k=max(1,int(n*q)); r=T.err.values[:k].sum()/E; lifts[q]=r
    print(f"flag top {int(q*100):2d}% most-anomalous -> catch {r:.0%} of errors (random {q:.0%}), lift {r/q:.2f}x")
fig,ax=plt.subplots(figsize=(5.2,4))
ax.plot(frac*100,recall*100,color="#de2d26",lw=2,label=f"flag by behavioral anomaly (GT-free), AUC={auc:.2f}")
ax.plot([0,100],[0,100],ls="--",c="k",lw=1,label="random (no signal)")
for q in [0.20]:
    k=int(n*q); ax.plot([q*100,q*100],[0,lifts[q]*100],ls=":",c="gray")
    ax.annotate(f"flag 20% → catch {lifts[q]:.0%}",(q*100,lifts[q]*100),fontsize=8,xytext=(6,-4),textcoords="offset points")
ax.set_xlabel("% of tasks flagged for re-review"); ax.set_ylabel("% of errors caught")
ax.set_title("Prospective, ground-truth-free error flagging\nslow-for-this-person tasks are enriched for errors")
ax.legend(fontsize=8,loc="lower right"); ax.set_xlim(0,100); ax.set_ylim(0,100)
plt.tight_layout(); _cav(); plt.savefig(TALK/"fig_prospective_flagging.png",dpi=150)
print("saved fig_prospective_flagging.png")
