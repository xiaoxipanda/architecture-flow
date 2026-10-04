"""Editable plush architecture scene. Pillow is used only for sprite crops/font metrics.
All typography, cards, curves and moving tokens are rendered by SVG in the browser.
"""
import base64
import io
import math
from pathlib import Path
from PIL import Image, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ROLES = [
 ('RESEARCH','研究','research',['signals','sources','brief'],'有来源的研究结论','#bf9b1d',48,674),
 ('PRODUCT','产品','product',['scope','design','spec'],'可验收的产品方案','#298caf',384,714),
 ('DEV','开发','dev',['code','tests','build'],'代码与测试证据','#7a7ab5',720,674),
 ('CONTENT','内容','content',['notes','drafts','assets'],'经核实的内容草稿','#b461a8',48,945),
 ('SALES','销售','sales',['leads','fit','proposal'],'线索依据与销售方案','#7e9d40',384,985),
 ('OPS','运营','ops',['browser','deliver','receipt'],'授权执行与真实回执','#c77d8d',720,945),
]

def pale(color, amount=.12):
    return '#'+''.join(f'{round(int(color[i:i+2],16)*amount+250*(1-amount)):02x}' for i in (1,3,5))

def bezier(points, t):
    a,b,c,d=points; v=1-t
    return [v**3*a[i]+3*v*v*t*b[i]+3*v*t*t*c[i]+t**3*d[i] for i in (0,1)]

def route(points, color, speed, spacing):
    samples=[bezier(points, i/140) for i in range(141)]
    distances=[0.]
    for a,b in zip(samples,samples[1:]):
        distances.append(distances[-1]+math.dist(a,b))
    length=distances[-1]
    return dict(points=points,color=color,samples=samples,distances=distances,length=length,
                count=max(4,min(34,round(length/spacing))),speed=speed)

class Scene:
    def __init__(self, fonts):
        self.fonts=fonts
        self.cache={}
        self.items=[]

    def text(self,x,y,text,size=22,color='#252823',font='cn',center=False):
        key=(font,size)
        if key not in self.cache:
            self.cache[key]=ImageFont.truetype(str(self.fonts[font]),size)
        face=self.cache[key]
        # PIL's default text anchor is top + ascent; preserve that exact baseline.
        self.items.append(dict(type='text',x=x,y=y+face.getmetrics()[0],text=text,
            size=size,color=color,font=font,center=center))

    def rect(self,x,y,w,h,r=0,fill='none',stroke='none',width=1,shadow=False):
        self.items.append(dict(type='rect',x=x,y=y,w=w,h=h,r=r,fill=fill,stroke=stroke,width=width,shadow=shadow))

    def line(self,x1,y1,x2,y2,color,width=1):
        self.items.append(dict(type='line',x1=x1,y1=y1,x2=x2,y2=y2,color=color,width=width))

    def circle(self,x,y,r,fill='none',stroke='none',width=1):
        self.items.append(dict(type='circle',x=x,y=y,r=r,fill=fill,stroke=stroke,width=width))

    def card(self,x,y,w,h):
        self.rect(x,y,w-1,h-1,22,'#ffffff','#d9dbd4',shadow=True)


def default_fonts(overrides=None, fonts_dir=Path('/System/Library/Fonts/Supplemental')):
    files={key:fonts_dir/name for key,name in [('cn','Arial Unicode.ttf'),('serif','Georgia Bold.ttf'),('bold','Arial Bold.ttf')]}
    files['mono']=fonts_dir.parent/'Menlo.ttc'
    files.update({key:Path(value) for key,value in (overrides or {}).items() if value})
    for key,file in files.items():
        if not file.is_file():
            raise ValueError(f'Font not found: {file}; supply --{key}-font')
    return files


def build_scene(duration=30, speed=160, spacing=23, atlas=None, fonts=None, font_overrides=None):
    if not all(math.isfinite(v) for v in (duration,speed,spacing)) or duration<=0 or speed<0 or spacing<=0:
        raise ValueError('Invalid duration, speed or spacing')
    fonts=fonts or default_fonts(font_overrides)
    s=Scene(fonts)
    routes=[]
    def add(points,color): routes.append(route(points,color,speed,spacing))
    for i,r in enumerate(ROLES):
        x,y=r[6:]; xx=x+156; color=r[5]
        if i<3:
            start=510+i*30
            add([[start,607],[start,645],[xx,y-65],[xx,y]],color)
        else:
            edge=30 if i==3 else 1050 if i==5 else 702
            add([[555,607],[edge,655],[edge,y-55],[xx,y]],color)
        edge=30 if i%3==0 else 1050 if i%3==2 else 710
        add([[xx,y+210],[xx,y+285],[edge,1247],[355+i*75,1232]],color)
    for points,color in [
        ([[540,390],[550,425],[530,448],[540,475]],'#b88670'),
        ([[202,439],[208,520],[220,551],[319,551]],'#96a698'),
        ([[896,439],[1080,492],[983,601],[760,552]],'#96a698'),
        ([[540,1318],[535,1330],[545,1342],[540,1353]],'#b88670'),
        ([[230,1390],[-40,1380],[-25,600],[360,355]],'#c49a87')]: add(points,color)
    s.text(48,28,'HERMES / SYSTEMS SERIES',15,'#81867c','mono')
    s.text(858,28,'COMPANY / 01',14,'#81867c','mono')
    s.text(46,69,'One-person company.',67,font='serif')
    s.text(46,149,'Powered by Hermes.',65,font='serif')
    s.text(49,246,'一人企业，由清晰的分工连接起来。',27,'#a36f53')
    s.line(48,292,1032,292,'#dedfd7')
    # Coordinator / context / tools: fixed from frame zero.
    s.card(321,318,438,72)
    s.text(345,330,'YOU SET THE DIRECTION',24,font='bold')
    s.text(345,361,'目标 / 验收标准 / 授权范围',18,'#82877f')
    for x,title,subtitle,size in [(48,'SHARED CONTEXT','目标 · 背景 · 证据',21),(770,'CONNECTED TOOLS','检索 · 代码 · Chrome',20)]:
        s.card(x,350,262,89);s.text(x+19,365,title,size,font='bold');s.text(x+19,400,subtitle,18 if x==48 else 17,'#858b81')
    s.card(320,475,440,132)
    s.text(413,494,'FOUNDER',38,font='bold')
    s.text(414,541,'目标拆解 · 分派 · 综合结果',21,'#82877e')
    s.text(414,576,'HERMES NATIVE COORDINATION',12,'#858b81','mono')
    s.circle(365.5,531.5,20.5,stroke='#899281',width=2)
    s.text(365,510,'h',30,font='serif',center=True)
    for k,r in enumerate(ROLES):
        angle=k*math.tau/6;s.circle(365+28*math.cos(angle),532+28*math.sin(angle),4,r[5])
    s.rect(286,625,508,31,15,'#f0f1eb')
    s.text(540,631,'company 看板  →  Dispatcher  →  Workers',17,center=True)
    atlas_image=Image.open(atlas or ROOT/'assets/mascots/workstreams.png').convert('RGBA')
    for i,r in enumerate(ROLES):
        en,cn,profile,steps,out,color,x,y=r
        s.card(x,y,312,210);s.rect(x,y+25,4,160,2,color)
        s.text(x+18,y+15,f'0{i+1} / WORKSTREAM',12,'#8e948b','mono')
        s.text(x+18,y+44,en,28,font='bold');s.text(x+19,y+85,cn+' / '+profile,18,'#7e837a')
        for j,step in enumerate(steps):
            xx=x+17+j*93
            s.rect(xx,y+121,87,30,8,pale(color,.06),pale(color,.28))
            s.text(xx+43,y+126,step,15,font='bold',center=True)
            s.rect(xx+9,y+155,25,3,1,color)
        s.line(x+18,y+168,x+294,y+168,'#eef0ea')
        s.rect(x+19,y+179,10,14,2,stroke=color);s.line(x+22,y+183,x+26,y+183,color)
        s.text(x+39,y+175,out,17,'#454c42')
        cell=atlas_image.crop((int(i%3*atlas_image.width/3),int(i//3*atlas_image.height/2),int((i%3+1)*atlas_image.width/3),int((i//3+1)*atlas_image.height/2)))
        bbox=cell.getchannel('A').getbbox()
        if bbox:cell=cell.crop(bbox)
        cell.thumbnail((105,105),Image.Resampling.LANCZOS)
        buffer=io.BytesIO();cell.save(buffer,format='PNG')
        s.items.append(dict(type='image',x=int(x+257-cell.width/2),y=int(y+54-cell.height/2),w=cell.width,h=cell.height,
            src='data:image/png;base64,'+base64.b64encode(buffer.getvalue()).decode()))
    s.card(180,1232,720,87);s.text(206,1245,'REVIEWER',29,font='bold');s.text(402,1250,'独立核验证据',24)
    s.text(207,1284,'同一张任务卡：通过验收，或退回原执行者修改',20,'#81897d')
    s.card(180,1360,720,73);s.text(208,1372,'YOU REVIEW + AUTHORIZE',27,font='bold')
    s.text(208,1405,'授权执行 / 真实回执 / 反馈与下一轮目标',18,'#83887e')
    s.text(48,1450,'8 ROLES / 1 COMPANY BOARD / EVIDENCE FIRST',13,'#8a9185','mono')
    s.line(48,1483,1032,1483,'#dedfd7');s.text(48,1498,'THE LOOP',12,'#a77d66','mono')
    s.text(540,1525,'目标 → 证据 → 执行 → 验收 → 改进',25,center=True)
    s.text(540,1565,'当前配置架构示意 · 业务结果需逐项验证',15,'#94998e',center=True)
    # Default system fonts are named, never embedded in published examples.
    # Explicit font overrides are embedded only in the user's generated artifact.
    faces={}
    for key,path in (font_overrides or {}).items():
        if path:faces[key]='data:font/ttf;base64,'+base64.b64encode(Path(path).read_bytes()).decode()
    return dict(width=1080,height=1600,duration=duration,speed=speed,spacing=spacing,
                fonts=faces,items=s.items,routes=routes)
