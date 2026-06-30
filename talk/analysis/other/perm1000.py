import numpy as np, pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.metrics import roc_auc_score
np.seterr(all="ignore")
T=pd.read_csv('live_out/enriched_task.csv')
T2=T.dropna(subset=['dur']).copy(); T2=T2[T2.groupby('assignee')['assignee'].transform('size')>=10].copy()
catf=['f_spine','f_nucleus','f_dendrite','f_axon','f_soma']
y=T2.err.values; groups=T2.seg_id.values
X=StandardScaler().fit_transform(T2[catf].fillna(0))
def gauc(yy): return roc_auc_score(yy,cross_val_predict(GradientBoostingClassifier(random_state=0),X,yy,cv=GroupKFold(5),groups=groups,method='predict_proba')[:,1])
obs=gauc(y); rng=np.random.RandomState(0); N=1000; hits=0
for i in range(N):
    if gauc(rng.permutation(y))>=obs: hits+=1
    if (i+1)%200==0: print("  ...%d/%d hits=%d"%(i+1,N,hits),flush=True)
p=hits/N if hits else 1.0/(N+1)
print("FINAL obs=%.3f hits=%d/%d  p%s%.4f"%(obs,hits,N,"=" if hits else "<",p),flush=True)
