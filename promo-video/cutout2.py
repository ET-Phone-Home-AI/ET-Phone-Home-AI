# usage: python3 cutout2.py <source-photo.png> rodney.png
import sys
from PIL import Image, ImageFilter
import numpy as np
from collections import deque
im=Image.open(sys.argv[1]).convert('RGB'); a=np.array(im).astype(float); H,W,_=a.shape
sat=a.max(2)-a.min(2)
def flood(dark_ok, extra):
  bg=np.zeros((H,W),bool); q=deque()
  ok=lambda y,x: sat[y,x]<22 and (dark_ok or a[y,x].mean()>18)
  seeds=[(y,x) for x in range(W) for y in (0,H-1)]+[(y,x) for y in range(H) for x in (0,W-1)]+extra
  for y,x in seeds:
    if ok(y,x) and not bg[y,x]: bg[y,x]=True; q.append((y,x))
  while q:
    y,x=q.popleft()
    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
      ny,nx=y+dy,x+dx
      if 0<=ny<H and 0<=nx<W and not bg[ny,nx] and ok(ny,nx) and np.abs(a[ny,nx]-a[y,x]).sum()<14:
        bg[ny,nx]=True; q.append((ny,nx))
  return bg
holes=[(77,63),(72,173),(233,58),(225,55)]
b1=flood(False,holes); b2=flood(True,holes)
bg=b1.copy(); bg[:265]=b2[:265]
alpha=(~bg).astype(float)
# fade bottom
ys=np.arange(H)[:,None]; fade=np.clip((H*0.97-ys)/(H*0.22),0,1); alpha*=fade
m=Image.fromarray((alpha*255).astype(np.uint8))
m=m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.0))
S=3
big=im.resize((W*S,H*S),Image.LANCZOS).filter(ImageFilter.UnsharpMask(2,80,2))
big.putalpha(m.resize((W*S,H*S),Image.LANCZOS)); big.save(sys.argv[2])
prev=Image.new('RGB',big.size,(20,20,24)); prev.paste(big,(0,0),big); prev.save(sys.argv[2].replace('.png','_preview.png'))
