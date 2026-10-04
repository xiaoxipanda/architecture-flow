"""Adapt the MIT live-panel engine without bundling its recreated examples."""
import argparse
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / 'vendor/live_panel'
sys.path.insert(0, str(ENGINE / 'scripts'))
import livepanel as lp

p = argparse.ArgumentParser()
p.add_argument('--output-dir', type=Path, required=True)
p.add_argument('--style', choices=['terminal-dark', 'light-pastel'], required=True)
p.add_argument('--panel-config', type=Path, default=None)
p.add_argument('--duration', type=float, default=30)
p.add_argument('--fps', type=int, default=30)
p.add_argument('--speed', type=float, default=160)
p.add_argument('--spacing', type=float, default=23)
p.add_argument('--chrome')
p.add_argument('--ffmpeg')
p.add_argument('--music', type=Path)
p.add_argument('--poster-only', action='store_true')
a = p.parse_args()
chrome = a.chrome or next((shutil.which(name) for name in lp.CHROME_NAMES if shutil.which(name)), None)
if not chrome:
    candidate = Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
    if candidate.is_file():
        chrome = str(candidate)
if not chrome:
    p.error('Panel styles need Chrome/Chromium; supply --chrome')
root = a.output_dir
root.mkdir(parents=True, exist_ok=True)
source = a.panel_config or ROOT / ('assets/panel-terminal.json' if a.style == 'terminal-dark' else 'assets/panel-pastel.json')
cfg = json.loads(source.read_text())
if not isinstance(cfg, dict) or not isinstance(cfg.get('elements'), list):
    p.error('Panel JSON requires an elements list; see references/panel-config-schema.md')
cfg.setdefault('canvas', {}).update(duration=a.duration, fps=a.fps)
cfg.setdefault('theme', {})['preset'] = a.style
colors = cfg['theme'].setdefault('colors', {})
colors.setdefault('pk', '#dd91bd')
colors.setdefault('rd', '#efaa9c')
if a.style == 'light-pastel':
    palette = {'cy': '#327a92', 'ye': '#a78a30', 'pu': '#7773a4', 'pk': '#ad6098', 'gr': '#60843c', 'rd': '#b46c71'}
    fills = {'cy': '#eaf6fa', 'ye': '#fff8df', 'pu': '#f0edfa', 'pk': '#fbeaf6', 'gr': '#eff6e5', 'rd': '#fbeeed'}
    for name, value in palette.items():
        colors.setdefault(name, value)
    colors['pk'] = palette['pk']; colors['rd'] = palette['rd']
    for name, value in fills.items():
        colors['fill_' + name] = value
    for element in cfg['elements']:
        if element.get('type') == 'box' and element.get('fill') == 'bar':
            element['fill'] = 'fill_' + element.get('color', 'cy')
for e in cfg['elements']:
    flow = e.get('flow') if e.get('type') == 'path' else e if e.get('type') == 'flow' else None
    if flow is None:
        continue
    points = e.get('points', e.get('path', []))
    length = sum(math.dist(first, second) for first, second in zip(points, points[1:]))
    if length <= 0:
        continue
    count = max(1, min(34, round(length / a.spacing)))
    flow['period'] = length / a.speed if a.speed else 1e12
    flow['offsets'] = [flow['period'] * i / count for i in range(count)]
config = root / 'panel.json'
config.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + '\n')
width, height, _, _ = lp.canvas(cfg)
width -= width % 2
height -= height % 2
page = root / 'panel.html'
lp.build_page(config, page)
# Measure many states and repeat seeks before encoding.
subprocess.run([sys.executable, str(ENGINE / 'scripts/check_frames.py'), '--config', str(config),
                '--out-dir', str(root / 'checked-frames'), '--chrome', chrome,
                '--samples', '120', '--png', '3', '--repeat'], check=True)
with lp.Chrome(chrome, width, height) as browser:
    browser.open(page.resolve().as_uri() + '?manual')
    for i, t in enumerate([0, a.duration / 2, max(0, a.duration - 1 / a.fps)]):
        browser.seek(t)
        if browser.eval("document.body.innerText.includes('undefined') || !!window.__error"):
            raise ValueError('Panel contains an undefined state label or a JavaScript error')
        image = browser.shot()
        (root / f'keyframe-{i}.png').write_bytes(image)
        if i == 0:
            (root / 'cover.png').write_bytes(image)
if not a.poster_only:
    raw = root / 'panel-silent.mp4'
    subprocess.run([sys.executable, str(ENGINE / 'scripts/render.py'), '--config', str(config),
                    '--out', str(raw), '--chrome', chrome, '--ffmpeg', a.ffmpeg,
                    '--audio', 'none', '--html-out', str(page)], check=True)
    if a.music:
        subprocess.run([a.ffmpeg, '-y', '-v', 'error', '-i', str(raw), '-i', str(a.music),
                        '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac',
                        '-b:a', '192k', '-af', 'apad', '-t', str(a.duration),
                        '-movflags', '+faststart', str(root / 'architecture.mp4')], check=True)
        raw.unlink()
    else:
        raw.replace(root / 'architecture.mp4')
(root / 'render-settings.json').write_text(json.dumps({'style': a.style, 'width': width, 'height': height,
 'duration': a.duration, 'fps': a.fps, 'speed_px_s': a.speed, 'spacing_px': a.spacing,
 'state': 'illustrative; not real telemetry', 'music': bool(a.music)}, indent=2) + '\n')
print(f'{a.style}: validated layout and deterministic replay; live page: {page}')
