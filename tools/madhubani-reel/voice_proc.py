import json, re, subprocess, numpy as np, scipy.io.wavfile as w
SRC="dv_raw.wav"; TEMPO=1.5; LEAD=0.35; START=4.40
sr,x=w.read(SRC); x=x.astype(float); x/=32768 if np.abs(x).max()>2 else 1
if x.ndim>1: x=x.mean(1)
spans=[(0.0,3.19),(3.96,18.75),(19.78,30.09),(30.98,43.25),(44.25,59.58),(60.24,70.90),(71.51,86.72),(87.72,97.16)]
r=subprocess.run(["ffmpeg","-i",SRC,"-af","silencedetect=n=-40dB:d=0.15","-f","null","-"],capture_output=True,text=True).stderr
st=[float(v) for v in re.findall(r"silence_start: ([0-9.]+)",r)]; en=[float(v) for v in re.findall(r"silence_end: ([0-9.]+)",r)]
sil=list(zip(st,en))
out=[np.zeros(int(LEAD*sr))]; T=LEAD; new=[]
for li,(s,e) in enumerate(spans):
    # speech pieces inside the line: split at internal silences
    cuts=[(a,b) for a,b in sil if s<a and b<e]
    pieces=[]; p=s
    for a,b in cuts: pieces.append((p,a,b-a)); p=b
    pieces.append((p,e,0))
    s_out=T
    for a,b,g in pieces:
        seg=x[int(max(0,a-0.03)*sr):int((b+0.06)*sr)]; out.append(seg); T+=len(seg)/sr
        if g: ng=min(g,0.22); out.append(np.zeros(int(ng*sr))); T+=ng
    new.append((s_out,T))
    if li<len(spans)-1:
        g=spans[li+1][0]-e; ng=max(0.12,min(g,0.38)); out.append(np.zeros(int(ng*sr))); T+=ng
out.append(np.zeros(int(0.5*sr)))
y=np.concatenate(out); y*=0.9/np.abs(y).max()
w.write("dv_tight.wav",sr,(y*32767).astype(np.int16))
subprocess.run(["ffmpeg","-v","error","-y","-i","dv_tight.wav","-af",f"rubberband=tempo={TEMPO}:pitchq=quality:formant=preserved","dv_final.wav"],check=True)
vs=[(a/TEMPO,b/TEMPO) for a,b in new]
json.dump(vs,open("dv_spans.json","w"))
print("final voice length",round(len(y)/sr/TEMPO,1),"s")
print([ (round(a,1),round(b,1)) for a,b in vs[:6]], "...", [(round(a,1),round(b,1)) for a,b in vs[-3:]])
