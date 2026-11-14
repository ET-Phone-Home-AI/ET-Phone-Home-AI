import numpy as np, scipy.signal as ss, scipy.io.wavfile as wf
SR=44100; DUR=78; N=SR*DUR; B=0.5
rng=np.random.default_rng(7)
L=np.zeros(N); Rr=np.zeros(N); rev=np.zeros(N)
def add(sig,t,gain=1.0,pan=0.0,send=0.0):
    i=int(t*SR); 
    if i>=N: return
    s=sig[:N-i]*gain; l=s*np.sqrt((1-pan)/2); r=s*np.sqrt((1+pan)/2)
    L[i:i+len(s)]+=l; Rr[i:i+len(s)]+=r; rev[i:i+len(s)]+=s*send
def tt(d): return np.arange(int(d*SR))/SR
def mtof(m): return 440*2**((m-69)/12)
def lp(x,fc,order=2): b,a=ss.butter(order,fc/(SR/2)); return ss.lfilter(b,a,x)
def hp(x,fc,order=2): b,a=ss.butter(order,fc/(SR/2),'high'); return ss.lfilter(b,a,x)
def bp(x,lo,hi): b,a=ss.butter(2,[lo/(SR/2),hi/(SR/2)],'band'); return ss.lfilter(b,a,x)
# --- instruments
def kick():
    t=tt(0.45); f=45+110*np.exp(-t*28); ph=2*np.pi*np.cumsum(f)/SR
    s=np.sin(ph)*np.exp(-t*7)+0.4*np.exp(-t*300)*rng.standard_normal(len(t))*0.3
    return np.tanh(s*1.6)
def clap():
    t=tt(0.35); n=rng.standard_normal(len(t)); env=np.zeros(len(t))
    for d in (0,0.011,0.022): env+=np.where(t>=d,np.exp(-(t-d)*60),0)
    env+=np.exp(-t*14)*0.4
    return bp(n,900,5000)*env*0.9
def hat(open_=False):
    t=tt(0.25 if open_ else 0.06); return hp(rng.standard_normal(len(t)),7000)*np.exp(-t*(14 if open_ else 70))
def snare():
    t=tt(0.2); return (bp(rng.standard_normal(len(t)),1500,8000)*0.8+np.sin(2*np.pi*190*t)*0.5)*np.exp(-t*22)
def saw(f,t,nh=24):
    s=np.zeros(len(t))
    for k in range(1,nh+1):
        if f*k>SR/2.2: break
        s+=np.sin(2*np.pi*f*k*t)/k
    return s
def supersaw(f,d):
    t=tt(d); s=np.zeros(len(t))
    for det in (-0.12,-0.05,0,0.05,0.12): s+=saw(f*2**(det/12),t+rng.random(),10)
    return s/5
def pluck(f,d=0.3):
    t=tt(d); s=np.sign(np.sin(2*np.pi*f*t))*0.5+saw(f,t,8)*0.5
    return lp(s,3500)*np.exp(-t*11)
def bass(f,d):
    t=tt(d); s=saw(f,t,12)+np.sin(2*np.pi*f/2*t)*0.8
    env=np.minimum(1,t*200)*np.exp(-t*3); return lp(s,900)*env
def impact():
    t=tt(3.0); boom=np.sin(2*np.pi*(38+60*np.exp(-t*10))*t)*np.exp(-t*1.6)
    crash=hp(rng.standard_normal(len(t)),3000)*np.exp(-t*2.2)*0.35
    return np.tanh(boom*1.5)*0.9+crash
def riser(d):
    t=tt(d); n=rng.standard_normal(len(t)); out=np.zeros(len(t)); seg=int(0.05*SR)
    for i in range(0,len(t),seg):
        fc=300+ (i/len(t))**2*9000; c=n[i:i+seg]; out[i:i+seg]=hp(c,min(fc,15000),1) if len(c)>20 else c
    sweep=np.sin(2*np.pi*np.cumsum(200+1800*(t/d)**3)/SR)*0.15
    return (out*0.5+sweep)*(t/d)**2
def click():
    t=tt(0.03); return hp(rng.standard_normal(len(t)),2500)*np.exp(-t*250)
# chords Am F C G (midi)
CH=[[57,60,64],[53,57,60],[60,64,67],[55,59,62]]; ROOT=[45,41,48,43]
def drop(t): return (6<=t<58) or (62<=t<74)
# --- typing clicks (mirrors stage.js S1)
for s,t0,cps in [('~/engr126 $ claude',0.3,30),('> I have never written a line of code.',1.2,30),('> Can I still build something amazing?',2.7,30)]:
    for i in range(len(s)): add(click(),t0+i/cps,0.25,rng.uniform(-.3,.3))
for i in range(34): add(pluck(mtof(81+[0,3,7,12][i%4]),0.1),4.3+i/40,0.04,0.3,0.2)
# --- pads all the way (filtered in intro/breakdown)
pad=np.zeros(N)
for bar in range(39):
    t0=bar*2; c=CH[bar%4]; s=sum(supersaw(mtof(m),2.2) for m in c)/3
    env=np.minimum(1,tt(2.2)*4)*np.minimum(1,(2.2-tt(2.2))*5)
    i=int(t0*SR); seg=(s*env)[:N-i]; pad[i:i+len(seg)]+=seg
tA=np.arange(N)/SR
padd=lp(pad,1800)*0.32; padd_lo=lp(pad,500)*0.45
inbreak=((tA<6)|((tA>=58)&(tA<62))|(tA>=74)).astype(float)
inbreak=np.convolve(inbreak,np.ones(2000)/2000,'same')
# sidechain
sc=np.ones(N)
for b in np.arange(0,DUR,B):
    if drop(b):
        i=int(b*SR); k=np.minimum(1,tt(0.4)/0.25)**1.5; sc[i:i+len(k)]=np.minimum(sc[i:i+len(k)],0.25+0.75*k)
fade_in=np.clip(tA/4,0,1); tail=np.clip((78-tA)/4,0,1)
padmix=(padd*(1-inbreak)*sc+padd_lo*inbreak)*fade_in*tail
L+=padmix; Rr+=padmix; rev+=padmix*0.3
# --- drums & bass & arp per beat
for k in range(int(DUR/B)):
    t=k*B; bar=int(t//2); ci=bar%4
    if drop(t):
        add(kick(),t,0.95)
        if k%2==1: add(clap(),t,0.55,0,0.25)
        add(hat(),t+0.25,0.22,0.3); add(hat(),t+0.125,0.08,-0.3); add(hat(),t+0.375,0.08,-0.3)
        if k%4==3: add(hat(True),t+0.25,0.1,0.4)
        for off in (0.25,):
            add(bass(mtof(ROOT[ci]),0.24),t+off,0.42)
        add(bass(mtof(ROOT[ci]),0.12),t,0.2)
    # arp 16ths
    if t>=2 and t<76:
        notes=[CH[ci][0]+12,CH[ci][1]+12,CH[ci][2]+12,CH[ci][1]+24]
        for j in range(4):
            g=0.11 if drop(t) else 0.07
            if t<6: g*=np.clip((t-2)/4,0,1)
            add(pluck(mtof(notes[(k*4+j)%4]),0.25),t+j*0.125,g,0.35 if j%2 else -0.35,0.35)
# fills, risers, impacts
for t0 in (5.0,33.0,61.0):
    for j in range(16): add(snare(),t0+j/16,0.15+0.35*j/16,0,0.2)
add(riser(3.0),3.0,0.5,0,0.3); add(riser(4.0),58.0,0.55,0,0.3); add(riser(1.5),18.5,0.25,0,0.3)
for t0,gn in ((6,1.0),(20.5,0.7),(62,1.0),(68,0.8),(74,0.9)): add(impact(),t0,gn,0,0.5)
for t0 in (12,26,34,54): add(hat(True),t0,0.4,0,0.5)
# final sustained chord
add(supersaw(mtof(45),4)*np.exp(-tt(4)*0.8),74,0.25,0,0.5)
# --- reverb (noise IR)
ir_t=tt(2.2); ir=rng.standard_normal(len(ir_t))*np.exp(-ir_t*2.8); ir=lp(ir,6000); ir/=np.sqrt((ir**2).sum())
wet=ss.fftconvolve(rev,ir)[:N]*0.5
L+=wet; Rr+=np.roll(wet,int(0.013*SR))
mix=np.stack([L,Rr],1)
mix=hp(mix.T,30).T
mix=np.tanh(mix*1.1)/np.tanh(1.1)
mix*=0.79/np.abs(mix).max()
wf.write('music.wav',SR,(mix*32767).astype(np.int16))
print('ok',mix.shape)
