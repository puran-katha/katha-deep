import numpy as np, scipy.signal as sg
SR=48000; rng=np.random.default_rng(11)
def lp(x,f): return sg.sosfilt(sg.butter(2,f,'low',fs=SR,output='sos'),x)
def hp(x,f): return sg.sosfilt(sg.butter(2,f,'high',fs=SR,output='sos'),x)
def bp(x,a,b): return sg.sosfilt(sg.butter(2,[a,b],'band',fs=SR,output='sos'),x)
def norm(a,db): return a*(10**(db/20))/np.sqrt(np.mean(a**2)+1e-12)
def place(buf,clip,t,g=1.0):
    a=int(t*SR); N=len(buf)
    if a>=N: return
    seg=clip[:N-a]; buf[a:a+len(seg)]+=seg*g
def pluck(f,dur=4.0,g=0.996):
    n=int(dur*SR); P=int(SR/f); x=np.zeros(n); x[:P]=rng.uniform(-1,1,P)*np.hanning(P)
    a=np.zeros(P+2); a[0]=1; a[P]=-g/2; a[P+1]=-g/2
    return np.tanh(1.8*sg.lfilter([1],a,x))*np.exp(-np.arange(n)/SR*0.5)
def bed(T):
    N=int(T*SR); tt=np.arange(N)/SR; notes=[pluck(110.0),pluck(146.83),pluck(146.83),pluck(73.42)]
    tan=np.zeros(N); i=0; tp=0.1
    while tp<T-0.5: place(tan,notes[i%4],tp); tp+=0.95 if i%4!=3 else 1.35; i+=1
    pad=sum(a*(2*(((f+d)*tt)%1)-1) for f,a in [(73.42,1),(110,.7),(146.83,.6),(174.61,.35)] for d in (-.4,.4))
    pad=lp(lp(pad,700),900)
    return norm(lp(tan,3000),-24)+norm(pad,-28)
def whoosh(d=0.8,lo=300,hi=2500):
    n=int(d*SR); x=rng.normal(0,1,n); env=np.sin(np.linspace(0,np.pi,n))**2; out=np.zeros(n); seg=n//12
    for j in range(12):
        f=lo+(hi-lo)*(j/11); s=bp(x[j*seg:(j+1)*seg+seg],f*0.7,f*1.3); out[j*seg:j*seg+len(s)]+=s[:len(out)-j*seg]
    return out*env
def rustle(d=0.25):
    n=int(d*SR); x=bp(rng.normal(0,1,n),1500,6000); env=np.exp(-np.arange(n)/SR*14)*(rng.uniform(0.3,1,n)>0.7)
    o=lp(x*env,7000); th=thump(0.08,140); o[:len(th)]+=th*0.4; return o
def squeak(d=0.28):
    t=np.arange(int(d*SR))/SR; f=1800+600*t/d; return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*4)*0.3+bp(rng.normal(0,1,len(t)),2500,5000)*0.3*np.exp(-t*6)
def thump(d=0.18,f0=90):
    t=np.arange(int(d*SR))/SR; return np.sin(2*np.pi*(f0-30*t)*t)*np.exp(-t*24)
def boom(d=3.0,f0=50,g=1.0):
    t=np.arange(int(d*SR))/SR; return (np.sin(2*np.pi*(f0-18*t)*t)*np.exp(-t*1.3)+lp(rng.normal(0,1,len(t)),200)*np.exp(-t*3)*0.6)*g
def bell(f,d=4.0,dec=1.4):
    t=np.arange(int(d*SR))/SR; return sum(g*np.sin(2*np.pi*f*m*t)*np.exp(-t*dec*(1+m*0.3)) for m,g in [(1,1),(2.76,.45),(5.4,.2),(8.9,.08)])
def page(d=0.6):
    n=int(d*SR); x=bp(rng.normal(0,1,n),800,5000); env=np.sin(np.linspace(0,np.pi,n))**1.5; return x*env
def crackle(d):
    out=np.zeros(int(d*SR))
    for j in range(int(d*30)):
        a=int(rng.uniform(0,d)*SR); L=int(rng.uniform(0.004,0.02)*SR)
        c=hp(rng.normal(0,1,L),1200)*np.exp(-np.arange(L)/SR*200)*rng.uniform(.2,1); out[a:a+L]+=c[:len(out)-a]
    return out+lp(rng.normal(0,1,len(out)),180)*0.5
