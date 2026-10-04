import argparse,subprocess,re,json
p=argparse.ArgumentParser();p.add_argument('video');p.add_argument('--ffmpeg',default='ffmpeg');p.add_argument('--width',type=int,required=True);p.add_argument('--height',type=int,required=True);p.add_argument('--min-duration',type=float,required=True);a=p.parse_args()
r=subprocess.run([a.ffmpeg,'-hide_banner','-i',a.video],capture_output=True,text=True)
s=r.stderr;m=re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)',s)
assert m,'No readable duration';duration=int(m[1])*3600+int(m[2])*60+float(m[3]);assert duration>=a.min_duration
assert f'{a.width}x{a.height}' in s and 'h264' in s and 'yuv420p' in s,'Unexpected video format'
r=subprocess.run([a.ffmpeg,'-v','error','-xerror','-i',a.video,'-f','null','-'],capture_output=True,text=True)
assert r.returncode==0,r.stderr
print(json.dumps({'decode':'passed','duration_seconds':duration,'width':a.width,'height':a.height,'codec':'h264','pixel_format':'yuv420p'},indent=2))
