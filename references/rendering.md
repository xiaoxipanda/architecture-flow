# 运行与调整

## 依赖与案例边界

Python 3.10+、Pillow、NumPy、Chrome/Chromium、FFmpeg。三种风格均以HTML/CSS/SVG和JavaScript绘制，Python驱动Chrome截图与导出。Pillow仅处理角色图片和字体度量。模板预设 macOS 系统字体，不打包字体或 FFmpeg。其他环境用 --fonts-dir 指定字体目录，或显式指定 --cn-font、--serif-font、--bold-font、--mono-font，使中文字体、衬线标题与粗体正确解析；不能静默使用缺失中文字形的字体。选择环境已有运行时，不为了视频更改生产服务。

模板目前是 Hermes 的六工作流案例；修改 scripts/plush_scene.py 中的 ROLES、卡片位置、文案和路线 即可适配新架构。节点数量变化需调整图集索引、卡片和连线，不能只改岗位标题。不得用扩展图集冒充已新增岗位。

## 示例命令

下面的路径均是相对于 Skill 文件夹的路径；实际运行时转换为绝对路径。输出必须是任务项目中的新目录。

```sh
python3 scripts/make_music.py --output /absolute/output/music.wav --duration 30
python3 scripts/render_hermes_template.py --output-dir /absolute/output --duration 30 --speed 160 --spacing 23 --poster-only
python3 scripts/render_hermes_template.py --output-dir /absolute/output --duration 30 --speed 160 --spacing 23 --music /absolute/output/music.wav --ffmpeg /absolute/path/to/ffmpeg
python3 scripts/validate_video.py /absolute/output/architecture.mp4 --ffmpeg /absolute/path/to/ffmpeg --width 1080 --height 1600 --min-duration 29
```

复制完整仓库到项目修改，保留 scripts、assets 与 vendor 的相对结构。脚本使用 ROOT 定位资源，可显式传 --atlas 指向图集、--chrome 指向浏览器。独立发给别人时同时带上素材和依赖说明。

--duration / --fps 控制时长与帧率；--speed 是像素/秒，--spacing 是目标间隔；--atlas 指向与模板角色顺序一致的图集。没有 --music 时输出无声视频，不会自动添加解说。输出含 architecture.mp4、cover.png、poster.png、5张关键帧、render-settings.json、plush.json、plush.html和web-validation.json。plush.html可独立打开持续播放；默认字体由目标机器提供，显式字体参数会嵌入所选字体，分发时确认字体许可。纯音乐用显式音轨映射，保持原视频不变时也可重新混音。

毛绒网页源码为assets/plush.html，动画通过window.seek(t)按绝对时间定位，requestAnimationFrame只用于实时播放。默认角色从首帧显示，画面中卡片和文字全为原生SVG，图片只用于毛绒角色。

## 检查

- 网页检查121个时刻的节点不变性、文字画布与卡片边界，并重复定位同一时刻检查截图；仅允许Chrome细微抗锯齿差异（沿用live-panel最多50个超过24色阶的像素差异容限）。
- 首帧必须完整显示所有节点；抽取实际编码画面确认，不能只检查源码生成的封面。
- 节点内区在不同时间应一致；连线路径应有像素变化。比较无损源帧，避免压缩差异误报为节点动画。
- 流动位置用曲线累计弧长插值，节点覆盖绘制在最上层。长路线元素上限34，最短路线最少4；若短线堆积，按实际可见长度降低下限。
- 完整解码失败时修复后重新检查；视觉检查与解码检查分别记录。
- 用FFmpeg volumedetect检查音乐平均值与峰值，避免削波；工具检查不能替代试听。当前原创生成器峰值约0.38，开头2秒、结尾3.5秒淡入淡出。
- 保存参考来源、架构事实依据、渲染参数、音频来源与验证报告；最终说明视频是架构示意还是实际业务执行记录。

## 运行面板风格

CLI `render --style terminal-dark` 或 `--style light-pastel` 使用vendor/live_panel中的MIT引擎及assets/panel-terminal.json或assets/panel-pastel.json。默认所有节点完整显示，状态与日志是确定性模拟。需要Chrome/Chromium，可用--chrome显式指定；不会使用用户的登录配置。速度、密度和音乐仍由统一CLI处理。

`init --style terminal-dark --out terminal.json`会生成terminal.json与terminal-panel.json，前者是渲染参数，后者是架构内容。面板JSON允许不同画布尺寸，输出尺寸由canvas解析；完整解码校验使用实际尺寸。主题由CLI选定风格覆盖。适配器均匀设置流动点的时间偏移，并在每个节点上层绘制节点文本。

输出附带panel.html、panel.json、封面、关键帧和布局检查截图。使用上游checker抽查120余个时间点并重放，检查文字溢出、节点重叠和确定性；再验证最终MP4。参考panel-config-schema.md定义新架构，务必在画面上标明模拟状态。

风格默认速度与密度分别设置：plush为160像素/秒、23像素间距；两种运行面板为80像素/秒、180像素间距，以接近原live-panel的稀疏包与短拖尾。用户可显式覆盖。深色版默认1200×1600；粉彩版1080×1440。两个主题使用不同布局，而非给同一网格换色。
