import subprocess, json, numpy as np, scipy.io.wavfile as w, scipy.signal as sg, scipy.fft as sf, re
from dscript import LINES
P="/tmp/claude-0/-home-claude/dd9cea56-86c2-5e24-a31a-ae9758e07761/scratchpad/tts/piper_dist/piper/piper"
M="/mnt/user-data/uploads/Reels/hi_IN-pratham-medium.onnx"; SR=16000; HOP=0.02
def mfcc(x, sr):
    x=sg.resample_poly(x,SR,sr) if sr!=SR else x
    f,t,Z=sg.stft(x,SR,nperseg=400,noverlap=400-int(HOP*SR)); P_=np.abs(Z)**2
    mel=lambda h:2595*np.log10(1+h/700); imel=lambda m:700*(10**(m/2595)-1)
    pts=imel(np.linspace(mel(60),mel(7600),28)); fb=np.zeros((26,len(f)))
    for i in range(26):
        l,c,r=pts[i],pts[i+1],pts[i+2]; fb[i]=np.clip(np.minimum((f-l)/(c-l),(r-f)/(r-c)),0,None)
    E=np.log(fb@P_+1e-9); C=sf.dct(E,axis=0,norm='ortho')[1:14]
    C=(C-C.mean(1,keepdims=True))/(C.std(1,keepdims=True)+1e-9)
    en=E.mean(0); return C.T, en
# reference: Piper, line by line, with known boundaries
ref=[]; bounds=[]; T=0
for ln in LINES:
    r=subprocess.run([P,"-m",M,"-c",M+".json","--sentence_silence","0","--output_raw"],input=ln[0].encode(),capture_output=True)
    a=np.frombuffer(r.stdout,dtype=np.int16).astype(float)/32768; nz=np.where(np.abs(a)>0.01)[0]; a=a[nz[0]:nz[-1]+1]
    s=T; ref.append(a); T+=len(a)/22050; bounds.append((s,T)); ref.append(np.zeros(int(0.3*22050))); T+=0.3
ref=np.concatenate(ref)
sr,x=w.read("dv_raw.wav"); x=x.astype(float); x/=32768 if np.abs(x).max()>2 else 1
x=x[:int(99.2*sr)]
A,ea=mfcc(ref,22050); B,eb=mfcc(x,sr)
n,m=len(A),len(B); print("frames",n,m)
# banded DTW on cosine distance
An=A/np.linalg.norm(A,axis=1,keepdims=True); Bn=B/np.linalg.norm(B,axis=1,keepdims=True)
band=int(25/HOP); INF=1e18
D=np.full((n,m),INF,dtype=np.float32); bp=np.zeros((n,m),dtype=np.int8)
for i in range(n):
    c=int(i*m/n); j0,j1=max(0,c-band),min(m,c+band)
    cost=1-Bn[j0:j1]@An[i]
    if i==0:
        acc=np.cumsum(cost); D[0,j0:j1]=acc; continue
    up=D[i-1,j0:j1]; diag=np.concatenate([[INF],D[i-1,j0:j1-1]]) if j0==0 else D[i-1,j0-1:j1-1]
    best=np.minimum(up,diag); arg=np.where(diag<=up,0,1)
    row=np.empty(j1-j0,dtype=np.float32); prev=INF
    for k in range(j1-j0):
        v=best[k]; a_=arg[k]
        if prev<v: v=prev; a_=2
        row[k]=cost[k]+v; bp[i,j0+k]=a_; prev=row[k]
    D[i,j0:j1]=row
# backtrack
i,j=n-1,int(np.argmin(D[n-1])); path={}
while i>0 and j>0:
    path.setdefault(i,j); a_=bp[i,j]
    if a_==0: i-=1; j-=1
    elif a_==1: i-=1
    else: j-=1
def map_t(t): i=min(n-1,int(t/HOP)); 
for _ in [0]: pass
def mt(t):
    i=min(n-1,max(1,int(t/HOP)))
    while i not in path and i>1: i-=1
    return path.get(i,0)*HOP
spans=[(mt(s),mt(e)) for s,e in bounds]
# snap to nearby silences in the original
r=subprocess.run(["ffmpeg","-i","dv_raw.wav","-af","silencedetect=n=-40dB:d=0.2","-f","null","-"],capture_output=True,text=True).stderr
st=[float(v) for v in re.findall(r"silence_start: ([0-9.]+)",r)]; en=[float(v) for v in re.findall(r"silence_end: ([0-9.]+)",r)]
def snap_start(t):
    c=[b for b in en if abs(b-t)<0.6]; return min(c,key=lambda b:abs(b-t)) if c else t
def snap_end(t):
    c=[a for a in st if abs(a-t)<0.6]; return min(c,key=lambda a:abs(a-t)) if c else t
spans=[(snap_start(s) if k else 0.3, snap_end(e)) for k,(s,e) in enumerate(spans)]
json.dump(spans,open("raw_spans.json","w"))
for k,(s,e) in enumerate(spans): print(f"{k:2d} {s:7.2f}-{e:7.2f} ({e-s:4.1f}s vs piper {bounds[k][1]-bounds[k][0]:4.1f})  {LINES[k][0][:30]}")
