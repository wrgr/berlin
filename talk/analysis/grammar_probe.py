"""#2b behavioral GRAMMAR over the action streams (live_out/streams.json from extract_streams.py).
A first-order Markov (n-gram) grammar recovers expertise at LOO AUC ~0.95 (= the designed tier) — the
'language of proofreading' is real. A more expressive HMM latent grammar collapses (0.39-0.59) at
n=15: expressive models (HMM, transformers) are data-starved here -> the scale-up, not a present
result. Offline; override paths with BERLIN_DATA."""
import os, json
from pathlib import Path
from itertools import product
from collections import Counter, defaultdict
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.metrics import roc_auc_score
np.seterr(all="ignore")
HERE=Path(__file__).resolve().parent; OUT=Path(os.environ.get("BERLIN_DATA", HERE/"live_out"))
DATA=json.load(open(OUT/'streams.json'))
ann=list(DATA); y=np.array([1 if DATA[a]['cohort']=='expert' else 0 for a in ann])
ALPH=['N','S','A','O']; m={c:i for i,c in enumerate(ALPH)}
def toks(a): return [[t[0] for t in s] for s in DATA[a]['sessions']]
def ngram(a,n):
    cnt=Counter()
    for s in toks(a):
        for i in range(len(s)-n+1): cnt[tuple(s[i:i+n])]+=1
    tot=sum(cnt.values()) or 1
    return np.array([cnt[g]/tot for g in product(ALPH,repeat=n)])
def cond_ent(a):
    nxt=defaultdict(Counter)
    for s in toks(a):
        for i in range(len(s)-1): nxt[s[i]][s[i+1]]+=1
    num=den=0
    for st,c in nxt.items():
        tot=sum(c.values()); p=np.array(list(c.values()))/tot; num+=-(p*np.log2(p+1e-9)).sum()*tot; den+=tot
    return num/max(1,den)
X2=np.array([ngram(a,2) for a in ann]); ent=np.array([[cond_ent(a)] for a in ann])
def loo(X):
    X=StandardScaler().fit_transform(np.nan_to_num(X))
    return roc_auc_score(y,cross_val_predict(LogisticRegression(max_iter=1000,class_weight='balanced'),X,y,cv=LeaveOneOut(),method='predict_proba')[:,1])
print("GRAMMAR probe — expert vs proto-expert (n=%d, %d expert):"%(len(ann),y.sum()))
print("  bigram-syntax (16 feats) LOO AUC=%.2f"%loo(X2))
print("  bigram + next-token entropy LOO AUC=%.2f"%loo(np.column_stack([X2,ent])))
try:
    from hmmlearn import hmm
    seqs=[[m[t] for s in toks(a) for t in s] for a in ann]
    Xc=np.concatenate([np.array(s).reshape(-1,1) for s in seqs]); L=[len(s) for s in seqs]
    for K in [4,6]:
        mod=hmm.CategoricalHMM(n_components=K,random_state=0,n_iter=60); mod.fit(Xc,L)
        occ=np.array([[np.mean(mod.predict(np.array(s).reshape(-1,1))==k) for k in range(K)] for s in seqs])
        print("  HMM(%d-state) latent-grammar occupancy LOO AUC=%.2f"%(K,loo(occ)))
except Exception as e:
    print("  (hmmlearn unavailable: %s) -- n-gram grammar only"%str(e)[:50])
print("reference: k-means learned tier 0.90; designed 0.95 (hand-built grammar incl. bigrams)")
