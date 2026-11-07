import numpy as np, scipy.io.wavfile as w
from sfx import *
import json
LEAD=1.0; vs=[(x+LEAD,y+LEAD) for x,y in json.load(open("dv_spans.json"))]
S=[0.0]+[x-0.1 for x,y in vs[1:]]; T=vs[-1][1]+5.0; B=vs[-1][1]+0.4
N=int(T*SR); fx=np.zeros(N); music=bed(T)
for s in S[1:]: place(fx,page(1.1),s,0.35); place(fx,whoosh(1.0,300,2500),s+0.1,0.18)
place(fx,bell(587.3,5,0.8),0.6,0.25); place(fx,bell(880,4,1.0),1.1,0.15)
r=np.random.default_rng(2)
for k in range(14):                         # forest birds
    t0=r.uniform(S[1]+0.5,S[2]-0.5); d=0.09; ts=np.arange(int(d*SR))/SR; f=r.uniform(2800,4200)+r.uniform(-1500,1500)*ts/d
    ch=np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*ts/d)
    for rep in range(2): place(fx,ch,t0+rep*0.12,0.05)
for k in range(8): place(fx,rustle(0.25),S[1]+0.7+k*0.55,0.12)       # footsteps
place(fx,boom(3,40,1.0),S[2]+1.3,0.6); place(fx,whoosh(0.9,150,900),S[2]+1.2,0.4)   # ravana arrives
n=int((S[4]-S[3])*SR); sea=lp(rng.normal(0,1,n),700)*(0.6+0.4*np.sin(np.arange(n)/SR*1.3))
env=np.minimum(1,np.arange(n)/SR/0.8)*np.minimum(1,(n-np.arange(n))/SR/0.8); place(fx,sea*env,S[3],0.3)
place(fx,whoosh(2.2,200,3000),S[3]+0.6,0.6); place(fx,thump(0.3,60),S[3]+5.3,0.7)  # leap + landing
for b in np.arange(S[4]+0.3,S[5]-0.5,0.42): place(fx,thump(0.25,70),b,0.85 if int((b-S[4]-0.3)/0.42)%4==0 else 0.45)
place(fx,whoosh(0.5,600,4500),S[4]+1.0,0.6); place(fx,boom(3,45,1.0),S[4]+2.6,0.7); place(fx,bell(880,3,1.4),S[4]+3.0,0.15)
place(fx,whoosh(6.5,250,1800),S[5]+0.3,0.35)                                    # viman flight
for j,f in enumerate((587.3,740,880)): place(fx,bell(f,3,1.2),S[5]+2+j*1.3,0.08)
for i in range(18): place(fx,whoosh(0.18,800,3000),S[6]+0.8+i*0.18,0.15); place(fx,crackle(0.3),S[6]+0.85+i*0.18,0.05)  # diyas light
for j,f in enumerate((587.3,880,1174.7)): place(fx,bell(f,4,1.0),S[7]+0.5+j*0.35,0.14)
place(fx,bell(293.7,7,0.5),B,0.3); place(fx,bell(587.3,6,0.7),B+0.02,0.12)
fx=norm(fx,-20); bg=music*0.9+fx
import subprocess
subprocess.run(["ffmpeg","-v","error","-y","-i","dv_final.wav","-ar",str(SR),"-ac","1","dv48.wav"],check=True)
_,v=w.read("dv48.wav"); v=v.astype(float)/32768; voice=np.zeros(N); voice[int(LEAD*SR):int(LEAD*SR)+len(v)]=v[:N-int(LEAD*SR)]
env=np.convolve(np.abs(voice),np.ones(int(0.25*SR))/int(0.25*SR),'same'); duck=np.where(env>0.01,0.4,1.0)
duck=np.convolve(duck,np.ones(int(0.3*SR))/int(0.3*SR),'same')
voice=norm(voice,-16)*1.0; bgn=norm(bg,-20)
mix=voice+bgn*duck
fo=int(1.0*SR); mix[-fo:]*=np.linspace(1,0,fo); mix[:int(0.3*SR)]*=np.linspace(0,1,int(0.3*SR))
mix*=0.89/np.abs(mix).max(); w.write("diwali_audio.wav",SR,(mix*32767).astype(np.int16)); print("ok")
