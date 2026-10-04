from PIL import Image,ImageDraw,ImageFont,ImageFilter
from pathlib import Path
import numpy as np, math,json,subprocess,sys,argparse,shutil
SKILL=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description='Hermes editorial architecture template. Copy and adapt verified labels before use.')
p.add_argument('--output-dir',type=Path,required=True)
p.add_argument('--duration',type=float,default=30)
p.add_argument('--fps',type=int,default=30)
p.add_argument('--speed',type=float,default=160,help='Travel speed in pixels per second')
p.add_argument('--spacing',type=float,default=23,help='Target token spacing in pixels')
p.add_argument('--ffmpeg',default=shutil.which('ffmpeg'))
p.add_argument('--atlas',type=Path,default=SKILL/'assets/mascots/workstreams.png')
p.add_argument('--music',type=Path)
p.add_argument('--poster-only',action='store_true')
for name in ['cn','serif','bold','mono']:
 p.add_argument(f'--{name}-font',type=Path,help='Override this font file for other platforms')
p.add_argument('--fonts-dir',type=Path,default=Path('/System/Library/Fonts/Supplemental'))
args=p.parse_args()
if args.duration<=0 or args.fps<=0 or args.speed<0 or args.spacing<=0:p.error('Invalid duration, fps, speed or spacing')
if not args.poster_only and not args.ffmpeg:p.error('FFmpeg missing: supply --ffmpeg')
ROOT=args.output_dir;ROOT.mkdir(parents=True,exist_ok=True)
FF=args.ffmpeg;W,H,BH,FPS=1080,1600,1480,args.fps;DURATION=args.duration
FONTS={'cn':str(args.fonts_dir/'Arial Unicode.ttf'),'serif':str(args.fonts_dir/'Georgia Bold.ttf'),'bold':str(args.fonts_dir/'Arial Bold.ttf'),'mono':str(args.fonts_dir.parent/'Menlo.ttc')}
for name in FONTS:
 override=getattr(args,name+'_font')
 if override:FONTS[name]=str(override)
 if not Path(FONTS[name]).is_file():p.error(f'Font not found: {FONTS[name]}; supply --{name}-font')
cache={}
def f(n,k='cn'):
 if (n,k) not in cache:cache[n,k]=ImageFont.truetype(FONTS[k],n)
 return cache[n,k]
def txt(d,x,y,s,n=22,c='#252823',k='cn'):d.text((x,y),s,font=f(n,k),fill=c)
def cent(d,x,y,s,n=22,c='#252823',k='cn'):
 b=d.textbbox((0,0),s,font=f(n,k));txt(d,x-(b[2]-b[0])/2,y,s,n,c,k)
def rgb(s):return tuple(int(s[i:i+2],16) for i in (1,3,5))
def pale(s,a=.12):return tuple(round(v*a+250*(1-a)) for v in rgb(s))
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
roles=[('RESEARCH','研究','research',['signals','sources','brief'],'有来源的研究结论','#bf9b1d',48,674),('PRODUCT','产品','product',['scope','design','spec'],'可验收的产品方案','#298caf',384,714),('DEV','开发','dev',['code','tests','build'],'代码与测试证据','#7a7ab5',720,674),('CONTENT','内容','content',['notes','drafts','assets'],'经核实的内容草稿','#b461a8',48,945),('SALES','销售','sales',['leads','fit','proposal'],'线索依据与销售方案','#7e9d40',384,985),('OPS','运营','ops',['browser','deliver','receipt'],'授权执行与真实回执','#c77d8d',720,945)]
boxes=[(r[6],r[7],312,210) for r in roles]
# Render typeset card panels at output resolution.
def panel(w,h,build):
 im=Image.new('RGBA',(w,h));d=ImageDraw.Draw(im);d.rounded_rectangle((0,0,w-1,h-1),22,fill='#ffffff',outline='#d9dbd4',width=1);build(d);return im
shadowcache={}
def pastecard(canvas,im,x,y,alpha=1,accent=None):
 if alpha<=0:return
 key=im.size
 if key not in shadowcache:
  w,h=key;sh=Image.new('RGBA',(w+50,h+50));sd=ImageDraw.Draw(sh);sd.rounded_rectangle((25,25,w+25,h+25),22,fill=(53,58,49,26));shadowcache[key]=sh.filter(ImageFilter.GaussianBlur(11))
 sh=shadowcache[key]
 if alpha<1:
  sh=sh.copy();sh.putalpha(sh.getchannel('A').point(lambda a:int(a*alpha)));im=im.copy();im.putalpha(im.getchannel('A').point(lambda a:int(a*alpha)))
 canvas.alpha_composite(sh,(int(x-25),int(y-17)));canvas.alpha_composite(im,(int(x),int(y)))
 if accent:
  dr=ImageDraw.Draw(canvas);dr.rounded_rectangle((x-2,y-2,x+im.width+1,y+im.height+1),24,outline=accent,width=2)
# Curves are drawn before every card, so particles can never obscure card text.
def B(a,b,c,e,u):v=1-u;return (v**3*a[0]+3*v*v*u*b[0]+3*v*u*u*c[0]+u**3*e[0],v**3*a[1]+3*v*v*u*b[1]+3*v*u*u*c[1]+u**3*e[1])
paths=[]
def add(a,b,c,e,color,delay=0):paths.append((a,b,c,e,color,delay))
for i,r in enumerate(roles):
 x,y,w,h=boxes[i];xx=x+w/2;c=r[5]
 if i<3:add((510+i*30,607),(510+i*30,645),(xx,y-65),(xx,y),c,2+i*.15)
 else:
  edge=30 if i==3 else 1050 if i==5 else 702
  add((555,607),(edge,655),(edge,y-55),(xx,y),c,2+i*.15)
 edge=30 if i%3==0 else 1050 if i%3==2 else 710
 add((xx,y+h),(xx,y+h+75),(edge,1247),(355+i*75,1232),c,3)
add((540,390),(550,425),(530,448),(540,475),'#b88670',1)
add((202,439),(208,520),(220,551),(319,551),'#96a698',1)
add((896,439),(1080,492),(983,601),(760,552),'#96a698',1)
add((540,1318),(535,1330),(545,1342),(540,1353),'#b88670',3)
# Feedback route bends around the left of the whole composition.
add((230,1390),(-40,1380),(-25,600),(360,355),'#c49a87',3)
pts=[[B(*p[:4],j/140) for j in range(141)] for p in paths]
background=Image.new('RGBA',(W,BH),'#f8f8f4');d=ImageDraw.Draw(background)
for y in range(286,BH,22):
 for x in range(40,W-40,22):d.point((x,y),fill='#dfe4da')
txt(d,48,28,'HERMES / SYSTEMS SERIES',15,'#81867c','mono');txt(d,858,28,'COMPANY / 01',14,'#81867c','mono')
txt(d,46,69,'One-person company.',67,k='serif');txt(d,46,149,'Powered by Hermes.',65,k='serif')
txt(d,49,246,'一人企业，由清晰的分工连接起来。',27,'#a36f53');d.line((48,292,1032,292),fill='#dedfd7',width=1)
# Slight color trails with multiple individually separated filaments.
for p,points in zip(paths,pts):
 for offset in [-7,-3,1,5]:
  shifted=[(x+offset,y) for x,y in points];d.line(shifted,fill=pale(p[4],.17),width=3);d.line([(x+offset-1,y) for x,y in points],fill=pale(p[4],.34),width=1)
cardims=[]
for i,r in enumerate(roles):
 en,cn,profile,steps,out,c,x,y=r
 def build(d,en=en,cn=cn,profile=profile,steps=steps,out=out,c=c,i=i):
  d.rounded_rectangle((0,25,4,185),2,fill=c)
  txt(d,18,15,f'0{i+1} / WORKSTREAM',12,'#8e948b','mono')
  txt(d,18,44,en,28,k='bold');txt(d,19,85,cn+' / '+profile,18,'#7e837a')
  for j,s in enumerate(steps):
   xx=17+j*93;d.rounded_rectangle((xx,121,xx+87,151),8,fill=pale(c,.06),outline=pale(c,.28));cent(d,xx+43,126,s,15,k='bold');d.rounded_rectangle((xx+9,155,xx+34,158),1,fill=c)
  d.line((18,168,294,168),fill='#eef0ea');d.rounded_rectangle((19,179,29,193),2,outline=c);d.line((22,183,26,183),fill=c);txt(d,39,175,out,17,'#454c42')
 cardims.append(panel(312,210,build))
human=panel(438,72,lambda d:(txt(d,24,12,'YOU SET THE DIRECTION',24,k='bold'),txt(d,24,43,'目标 / 验收标准 / 授权范围',18,'#82877f')))
context=panel(262,89,lambda d:(txt(d,19,15,'SHARED CONTEXT',21,k='bold'),txt(d,19,50,'目标 · 背景 · 证据',18,'#858b81')))
tools=panel(262,89,lambda d:(txt(d,19,15,'CONNECTED TOOLS',20,k='bold'),txt(d,19,50,'检索 · 代码 · Chrome',17,'#858b81')))
founder=panel(440,132,lambda d:(txt(d,93,19,'FOUNDER',38,k='bold'),txt(d,94,66,'目标拆解 · 分派 · 综合结果',21,'#82877e'),txt(d,94,101,'HERMES NATIVE COORDINATION',12,'#858b81','mono')))
review=panel(720,87,lambda d:(txt(d,26,13,'REVIEWER',29,k='bold'),txt(d,222,18,'独立核验证据',24),txt(d,27,52,'同一张任务卡：通过验收，或退回原执行者修改',20,'#81897d')))
delivery=panel(720,73,lambda d:(txt(d,28,12,'YOU REVIEW + AUTHORIZE',27,k='bold'),txt(d,28,45,'授权执行 / 真实回执 / 反馈与下一轮目标',18,'#83887e')))
# Place the transparent sprite atlas using texture cells, keeping the original intact.
atlaspath=args.atlas
if not atlaspath.exists():raise SystemExit('Mascot atlas not present')
atlas=Image.open(atlaspath).convert('RGBA');sprites=[]
for i in range(6):
 cell=atlas.crop((int(i%3*atlas.width/3),int(i//3*atlas.height/2),int((i%3+1)*atlas.width/3),int((i//3+1)*atlas.height/2)))
 box=cell.getchannel('A').getbbox()
 if box:cell=cell.crop(box)
 cell.thumbnail((105,105),Image.Resampling.LANCZOS);sprites.append(cell)
def scene(t,poster=False):
 im=background.copy();d=ImageDraw.Draw(im);phase=5
 def reveal(delay):return 1
 pastecard(im,human,321,318+12*(1-reveal(.2)),reveal(.2), '#c69b83' if phase==0 else None)
 pastecard(im,context,48,350+12*(1-reveal(.65)),reveal(.65));pastecard(im,tools,770,350+12*(1-reveal(.9)),reveal(.9))
 pastecard(im,founder,320,475+15*(1-reveal(1.1)),reveal(1.1),'#c69b83' if phase==1 else None)
 d=ImageDraw.Draw(im)
 if t>1.2 or poster:
  # Abstract orbit emblem for the coordinator.
  d.ellipse((345,511,386,552),outline='#899281',width=2);cent(d,365,510,'h',30,k='serif')
  for k,c in enumerate([r[5] for r in roles]):
   a=k*math.tau/6;xx=365+28*math.cos(a);yy=532+28*math.sin(a);d.ellipse((xx-4,yy-4,xx+4,yy+4),fill=c)
  d.rounded_rectangle((286,625,794,656),15,fill='#f0f1eb');cent(d,540,631,'company 看板  →  Dispatcher  →  Workers',17)
 for i,(r,box,ci) in enumerate(zip(roles,boxes,cardims)):
  x,y,w,h=box;a=reveal(1.6+i*.2);yy=y+20*(1-a)
  active=False
  pastecard(im,ci,x,yy,a,r[5] if active else None)
  if a>0:
   sp=sprites[i];sp=sp
   if a<1:sp=sp.copy();sp.putalpha(sp.getchannel('A').point(lambda v:int(v*a)))
   im.alpha_composite(sp,(int(x+257-sp.width/2),int(yy+54-sp.height/2)))
 pastecard(im,review,180,1232+15*(1-reveal(3)),reveal(3),'#c69b83' if phase==3 else None)
 pastecard(im,delivery,180,1360+15*(1-reveal(3.3)),reveal(3.3),None)
 d=ImageDraw.Draw(im);txt(d,48,1450,'8 ROLES / 1 COMPANY BOARD / EVIDENCE FIRST',13,'#8a9185','mono')
 return im,phase
# Fixed layout from the first frame. Only connector tokens move.
base_background=background.copy()
background=Image.new('RGBA',(W,BH))
foreground=scene(0,True)[0]
background=base_background

def frame(t,poster=False):
 im=base_background.copy();d=ImageDraw.Draw(im)
 for j,(p,points) in enumerate(zip(paths,pts)):
  length=sum(math.hypot(points[i][0]-points[i-1][0],points[i][1]-points[i-1][1]) for i in range(1,len(points)))
  count=max(4,min(34,round(length/args.spacing)))
  # A constant screen-space travel speed keeps both short and long routes lively.
  distances=np.array([0]+[math.hypot(points[i][0]-points[i-1][0],points[i][1]-points[i-1][1]) for i in range(1,len(points))]).cumsum()
  for k in range(count):
   travel=(t*args.speed+k*length/count+j*length*.081)%length
   u=float(np.interp(travel,distances,np.linspace(0,1,len(points))))
   xx,yy=B(*p[:4],u)
   if yy<302:continue
   if k%5==0:
    d.rounded_rectangle((xx-4,yy-6,xx+4,yy+6),2,fill='white',outline=pale(p[4],.9))
    d.line((xx-2,yy-1,xx+2,yy-1),fill=pale(p[4],.8));d.line((xx-2,yy+2,xx+2,yy+2),fill=pale(p[4],.8))
   else:
    d.ellipse((xx-2.8,yy-2.8,xx+2.8,yy+2.8),fill=pale(p[4],.85),outline='white',width=1)
 im.alpha_composite(foreground)
 out=Image.new('RGB',(W,H),'#f8f8f4');out.paste(im,(0,0),im);d=ImageDraw.Draw(out)
 d.line((48,1483,1032,1483),fill='#dedfd7')
 txt(d,48,1498,'THE LOOP',12,'#a77d66','mono')
 cent(d,540,1525,'目标 → 证据 → 执行 → 验收 → 改进',25)
 cent(d,540,1565,'当前配置架构示意 · 业务结果需逐项验证',15,'#94998e')
 return out
scene(20,True)[0].convert('RGB').save(ROOT/'poster.png')
frame(20,True).save(ROOT/'cover.png')
for i,t in enumerate([0,DURATION*.25,DURATION*.5,DURATION*.75,max(0,DURATION-1/FPS)]):frame(t).save(ROOT/f'keyframe-{i}.png')
if '--poster-only' in sys.argv:print('Poster ready');raise SystemExit
command=[FF,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-']
if args.music:
 command+=['-i',str(args.music),'-map','0:v:0','-map','1:a:0','-c:a','aac','-b:a','192k','-af','apad']
else:command+=['-an']
command+=['-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-t',str(DURATION),'-movflags','+faststart',str(ROOT/'architecture.mp4')]
(ROOT/'render-settings.json').write_text(json.dumps({'duration':DURATION,'fps':FPS,'speed_px_s':args.speed,'spacing_px':args.spacing,'motion':'fixed nodes; connector tokens only','music':bool(args.music)},indent=2)+'\n')
proc=subprocess.Popen(command,stdin=subprocess.PIPE)
for n in range(math.ceil(DURATION*FPS)):
 proc.stdin.write(frame(n/FPS).tobytes())
 if n%(FPS*10)==0:print(f'Rendered {n/FPS:.0f}/{DURATION:.1f}s',flush=True)
proc.stdin.close();assert proc.wait()==0;print('Render complete',flush=True)
