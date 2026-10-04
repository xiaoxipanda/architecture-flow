"""Original instrumental accompaniment: no speech or third-party recordings."""
from pathlib import Path
import math, wave, argparse
import numpy as np
p=argparse.ArgumentParser(description='Generate original soft instrumental music')
p.add_argument('--output',type=Path,required=True)
p.add_argument('--duration',type=float,default=30)
a=p.parse_args()
if a.duration<=0:p.error('Duration must be positive')
a.output.parent.mkdir(parents=True,exist_ok=True)
SR=44100
DURATION=a.duration
n=round(SR*DURATION)
out=np.zeros((n,2),dtype=np.float64)

def note(midi,start,length,gain,pan=0,pad=False):
    a=round(start*SR); count=min(round(length*SR),n-a)
    if count<=0:return
    t=np.arange(count)/SR
    hz=440*2**((midi-69)/12)
    if pad:
        tone=(np.sin(2*np.pi*hz*t)+.25*np.sin(2*np.pi*hz*2*t))/1.25
        env=np.minimum(t/.65,1)*np.minimum((length-t)/.85,1)*.65
    else:
        tone=(np.sin(2*np.pi*hz*t)+.22*np.sin(2*np.pi*hz*2*t)+.08*np.sin(2*np.pi*hz*3*t))/1.3
        env=(1-np.exp(-t/.009))*np.exp(-t/1.15)*np.minimum((length-t)/.15,1)
    signal=tone*np.maximum(env,0)*gain
    out[a:a+count,0]+=signal*math.sqrt((1-pan)/2)
    out[a:a+count,1]+=signal*math.sqrt((1+pan)/2)

beat=60/84
chords=[(48,55,60,64,67),(45,52,57,60,64),(41,48,53,57,60),(43,50,55,59,62)]
for bar in range(math.ceil(DURATION/(beat*4))):
    chord=chords[bar%4];start=bar*beat*4
    for m in chord[1:]:note(m,start,beat*4+.6,.028,pan=(m%5-2)*.2,pad=True)
    note(chord[0]-12,start,beat*3.7,.075)
    for step in range(8):
        pitch=chord[1+([0,1,2,3,2,1,3,1][step])]+12
        note(pitch,start+step*beat/2,2.2,.085,pan=(-.32 if step%2 else .32))
# Gentle stereo delay and fade; bounded peak level.
delay=round(beat*.75*SR)
out[delay:]+=out[:-delay,::-1]*.16
fade=np.minimum(np.arange(n)/SR/2,1)*np.minimum((n-np.arange(n))/SR/3.5,1)
out*=fade[:,None]
peak=np.max(np.abs(out));out*=.38/max(peak,1e-8)
with wave.open(str(a.output),'wb') as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
    w.writeframes((out*32767).astype('<i2').tobytes())
print(f'Original instrumental: {DURATION}s, stereo, peak {np.max(np.abs(out)):.3f}')
