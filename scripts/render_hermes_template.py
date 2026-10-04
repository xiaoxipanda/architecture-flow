"""Render the editable plush SVG/HTML scene with Chrome and FFmpeg.
The historical script name and arguments are retained for compatibility.
"""
import argparse
import hashlib
import io
import numpy as np
from PIL import Image
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'vendor/live_panel/scripts'))
import livepanel as lp
from plush_scene import build_scene,default_fonts


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--duration',type=float,default=30)
    p.add_argument('--fps',type=int,default=30)
    p.add_argument('--speed',type=float,default=160)
    p.add_argument('--spacing',type=float,default=23)
    p.add_argument('--ffmpeg',default=shutil.which('ffmpeg'))
    p.add_argument('--chrome')
    p.add_argument('--atlas',type=Path,default=ROOT/'assets/mascots/workstreams.png')
    p.add_argument('--music',type=Path)
    p.add_argument('--poster-only',action='store_true')
    p.add_argument('--fonts-dir',type=Path,default=Path('/System/Library/Fonts/Supplemental'))
    for key in ['cn','serif','bold','mono']:p.add_argument(f'--{key}-font',type=Path)
    a=p.parse_args()
    if a.fps<=0:p.error('fps must be positive')
    chrome=a.chrome or next((shutil.which(n) for n in lp.CHROME_NAMES if shutil.which(n)),None)
    if not chrome:
        candidate=Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
        if candidate.is_file():chrome=str(candidate)
    if not chrome:p.error('All styles need Chrome/Chromium; supply --chrome')
    if not a.poster_only and not a.ffmpeg:p.error('FFmpeg missing; supply --ffmpeg')
    overrides={key:getattr(a,key+'_font') for key in ['cn','serif','bold','mono']}
    fonts=default_fonts(overrides,a.fonts_dir)
    # A nondefault font directory should also yield a portable generated page.
    if a.fonts_dir!=Path('/System/Library/Fonts/Supplemental'):overrides=fonts
    cfg=build_scene(a.duration,a.speed,a.spacing,a.atlas,fonts,overrides)
    out=a.output_dir;out.mkdir(parents=True,exist_ok=True)
    (out/'plush.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')
    template=(ROOT/'assets/plush.html').read_text()
    blob=json.dumps(cfg,ensure_ascii=False).replace('</','<\\/')
    page=out/'plush.html'
    page.write_text(template.replace('<!--PLUSH_CONFIG-->',f'<script id="plush-config" type="application/json">{blob}</script>'))
    settings=dict(style='plush',renderer='html-css-svg-javascript-chrome',width=cfg['width'],height=cfg['height'],
                  duration=a.duration,fps=a.fps,speed_px_s=a.speed,spacing_px=a.spacing,
                  motion='fixed nodes; connector tokens only',music=bool(a.music))
    with lp.Chrome(chrome,cfg['width'],cfg['height']) as browser:
        browser.open(page.resolve().as_uri()+'?manual')
        original=browser.eval('window.inspectLayout()')
        if original['problems']:raise ValueError(f"Content outside canvas: {original['problems']}")
        if original['mascots']!=6:raise ValueError('Expected six mascot sprites')
        # Sample all animation phases; all fixed content must remain identical.
        for i in range(121):
            browser.seek(a.duration*i/120)
            if browser.eval('window.__error || window.inspectLayout().fixed')!=original['fixed']:
                raise ValueError('Fixed nodes changed or page failed during playback')
        times=[0,a.duration*.25,a.duration*.5,a.duration*.75,max(0,a.duration-1/a.fps)]
        hashes=[]
        for i,t in enumerate(times):
            browser.seek(t);png=browser.shot();hashes.append(hashlib.sha256(png).hexdigest())
            (out/f'keyframe-{i}.png').write_bytes(png)
            if i==0:
                (out/'cover.png').write_bytes(png)
                (out/'poster.png').write_bytes(png)
        browser.seek(times[2]);first=browser.shot();browser.seek(times[-1]);browser.seek(times[2])
        again=browser.shot()
        difference=np.abs(np.asarray(Image.open(io.BytesIO(first))).astype(int)-np.asarray(Image.open(io.BytesIO(again))).astype(int))
        # Chrome can repaint SVG edges one channel level differently. Compare pixels,
        # using the same small-noise allowance as the existing live-panel checker.
        visible_pixels=int((difference.max(axis=2)>24).sum())
        max_delta=int(difference.max())
        if visible_pixels>50:raise ValueError(f'Replay was not deterministic: {visible_pixels} visibly changed pixels')
        if a.speed and len(set(hashes))<2:raise ValueError('Connector animation did not change')
        (out/'web-validation.json').write_text(json.dumps(dict(samples=121,fixed_nodes=True,
            repeat_seek=True,replay_visible_pixels=visible_pixels,replay_max_channel_delta=max_delta,motion_changes=bool(a.speed),mascots=6,tokens=original['tokens'],
            canvas_overflow=original['problems']),indent=2)+'\n')
        if not a.poster_only:
            command=[a.ffmpeg,'-y','-v','error','-f','image2pipe','-framerate',str(a.fps),'-c:v','png','-i','-']
            if a.music:
                command+=['-i',str(a.music),'-map','0:v:0','-map','1:a:0','-c:a','aac','-b:a','192k','-af','apad']
            else:command+=['-an']
            command+=['-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-t',str(a.duration),
                '-movflags','+faststart',str(out/'architecture.mp4')]
            proc=subprocess.Popen(command,stdin=subprocess.PIPE)
            try:
                for i in range(math.ceil(a.duration*a.fps)):
                    browser.seek(i/a.fps);proc.stdin.write(browser.shot())
                    if i%(a.fps*5)==0:print(f'Rendered {i/a.fps:.0f}/{a.duration:.1f}s',flush=True)
                proc.stdin.close()
                if proc.wait()!=0:raise RuntimeError('FFmpeg encoding failed')
            except BaseException:
                if proc.stdin and not proc.stdin.closed:proc.stdin.close()
                proc.terminate();proc.wait()
                raise
    (out/'render-settings.json').write_text(json.dumps(settings,indent=2)+'\n')
    print(f'Plush web render complete; live page: {page}')

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,RuntimeError) as error:
        raise SystemExit(f'Error: {error}')
