import subprocess,numpy as np,scipy.io.wavfile as w
import importlib.util,sys
src=open('dalign.py').read(); exec(src[:src.index('# reference')])   # get mfcc()
P="/tmp/claude-0/-home-claude/dd9cea56-86c2-5e24-a31a-ae9758e07761/scratchpad/tts/piper_dist/piper/piper";Mo="/mnt/user-data/uploads/Reels/hi_IN-pratham-medium.onnx"
ph=["वनवास की अवधि पूरी हुई","और श्रीराम, सीता, लक्ष्मण एवं हनुमान","पुष्पक विमान में सवार होकर अयोध्या की ओर लौट चले","वह कार्तिक मास की अमावस्या की घोर स्याह रात थी","मगर अवधवासियों ने अपने आंगनों में दीप जलाकर","समूची नगरी को जगमगाती रोशनी से नहला दिया","उसी पावन क्षण की स्मृति में","हर वर्ष हम दीपों की लौ जलाते हैं","और इस दीपोत्सव को मनाते हैं","जय श्री राम!","आप सभी को","दीपावली की अनंत मंगलकामनाएँ!"]
ref=[];b=[];T=0
for t in ph:
    r=subprocess.run([P,"-m",Mo,"-c",Mo+".json","--output_raw"],input=t.encode(),capture_output=True)
    a=np.frombuffer(r.stdout,dtype=np.int16).astype(float)/32768; nz=np.where(np.abs(a)>0.01)[0]; a=a[nz[0]:nz[-1]+1]
    b.append(T); ref.append(a); T+=len(a)/22050; ref.append(np.zeros(int(0.25*22050))); T+=0.25
ref=np.concatenate(ref)
sr,x=w.read("dv_raw.wav"); x=x.astype(float)/32768; x=x[int(60.1*sr):int(98.7*sr)]
A,_=mfcc(ref,22050); B,_=mfcc(x,sr); A/=np.linalg.norm(A,axis=1,keepdims=True); B/=np.linalg.norm(B,axis=1,keepdims=True)
C=1-A@B.T; n,m=C.shape
# subsequence in ref: audio must be fully used, ref may end early. D over (i ref, j audio)
D=np.full((n,m),np.inf); D[0,0]=C[0,0]
for j in range(1,m): D[0,j]=D[0,j-1]+C[0,j]
for i in range(1,n):
    D[i,0]=D[i-1,0]+C[i,0]
    for j in range(1,m): D[i,j]=C[i,j]+min(D[i-1,j-1],D[i-1,j],D[i,j-1])
endnorm=D[:,m-1]/(np.arange(n)+m)
ie=int(np.argmin(endnorm)); print("audio end maps to ref t=",round(ie*0.02,2),"of",round(n*0.02,2))
# backtrack
i,j=ie,m-1; path={}
while i>0 or j>0:
    path.setdefault(i,j)
    if i==0: j-=1; continue
    if j==0: i-=1; continue
    k=np.argmin([D[i-1,j-1],D[i-1,j],D[i,j-1]]); i,j=[(i-1,j-1),(i-1,j),(i,j-1)][k]
for k,t in enumerate(ph):
    fi=int(b[k]/0.02)
    print(f"{60.1+path.get(min(fi,ie),m-1)*0.02:6.2f}" if fi<=ie else "  --  ", t)
