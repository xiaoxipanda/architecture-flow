# Architecture Motion Video

A reusable Codex skill and Python toolkit for editorial architecture videos: three styles: plush mascot infographics, dark terminal panels, and light pastel panels, with optional original instrumental music.

将系统架构制作成动态信息图：节点从第一帧完整显示，只让圆点和文档图标沿连线流动。支持独立调节速度与密度。

![Hermes architecture preview](examples/cover.png)

[查看带背景音乐的演示视频](examples/demo.mp4)

## 包含什么

- `SKILL.md`：参考分析、架构核实、素材选择、渲染、音频和验证流程。
- `assets/mascots/`：两套透明 RGBA 图集，共12个角色，以及角色纹理区域索引。
- `scripts/render_hermes_template.py`：毛绒角色架构示例（1080×1600），固定节点、沿曲线弧长匀速流动。
- `scripts/make_music.py`：原创键盘琶音与和弦生成器，不含语音。
- `scripts/validate_video.py`：尺寸、时长、编码格式与完整解码检查。
- `references/`：使用说明、素材用途与图像生成提示词。

这是视频制作工具，Hermes 一人企业仅作为可编辑案例。它不会安装或配置 Hermes，也不代表示例中各项业务已成功自动执行。财务、客服、法务和数据分析角色是备用素材。

## 快速开始

需要 Python 3、FFmpeg 和支持中文的字体。默认字体适配 macOS；其他系统可以显式指定字体文件。仓库不附带系统字体或 FFmpeg。

```sh
git clone https://github.com/xiaoxipanda/architecture-motion-video.git
cd architecture-motion-video
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python scripts/make_music.py --output output/music.wav --duration 30
python scripts/render_hermes_template.py --output-dir output --duration 30 --poster-only
# 检查 output/cover.png 后渲染：
python scripts/render_hermes_template.py --output-dir output --duration 30 \
  --speed 160 --spacing 23 --music output/music.wav
python scripts/validate_video.py output/architecture.mp4 \
  --width 1080 --height 1600 --min-duration 29
```

FFmpeg 不在 PATH 时传入 `--ffmpeg /path/to/ffmpeg`。省略 `--music` 则生成无声视频。输出包含 MP4、封面、关键帧和渲染参数。

其他系统用 `--cn-font`、`--serif-font`、`--bold-font`、`--mono-font` 指定四个字体文件；中文字体必须包含所需字形。

## 终端命令

```sh
python -m pip install .
architecture-motion-video render --out output/demo.mp4
architecture-motion-video render --out output/slow.mp4 --speed 100 --spacing 23 --duration 20
architecture-motion-video render --out output/silent.mp4 --music none
architecture-motion-video render --out output/custom.mp4 --music /path/to/music.wav
architecture-motion-video check output/demo.mp4
```

默认自动生成原创纯音乐、导出视频并完整解码验证。封面、关键帧、音乐及参数保存在 `demo-assets/` 等对应目录。已有输出不会被静默覆盖，需指定新名称或 `--force`。

先生成配置，再修改、渲染：

```sh
architecture-motion-video init --out render.json
architecture-motion-video render --config render.json --out output/configured.mp4
architecture-motion-video render --config render.json --out output/cover.mp4 --poster-only
```

JSON支持 `style`、`chrome`、`panel_config`、`duration`、`fps`、`speed`、`spacing`、`music`、`ffmpeg`、`atlas`、`cn_font`、`serif_font`、`bold_font`、`mono_font`。命令行参数覆盖JSON。JSON中的音乐、图集和字体相对路径以配置文件所在目录为基准。

`plush`的JSON配置渲染参数，布局仍在Python模板中编辑；两种面板风格另用 `panel_config` 指向完整的面板内容JSON。`--poster-only`只生成封面和关键帧，不输出MP4，也不需要FFmpeg；面板风格仍需要Chrome。

## 作为 Codex Skill 使用

将整个仓库文件夹放入或链接到 `~/.codex/skills/architecture-motion-video`，保留素材、脚本和 references 目录。若该目录已存在，先保留现有版本，不直接覆盖。

然后在 Codex 中请求：

> 用 $architecture-motion-video 为这个架构制作视频，节点固定，只让连线运动，配简单音乐。

## 三种风格

```sh
architecture-motion-video render --style plush --out output/plush.mp4
architecture-motion-video render --style terminal-dark --out output/terminal.mp4
architecture-motion-video render --style light-pastel --out output/pastel.mp4
```

| 风格 | 效果 | 渲染依赖 |
|---|---|---|
| `plush`（默认） | 浅色排版、毛绒角色、圆点与文档流动 | Pillow、NumPy、FFmpeg |
| `terminal-dark` | 深色终端、等宽字、光点、状态与模拟日志 | Chrome/Chromium、FFmpeg |
| `light-pastel` | 浅色粉彩卡片、光点、状态与模拟日志 | Chrome/Chromium、FFmpeg |

面板使用独立 headless Chrome 临时配置，不读取用户浏览器登录状态。Chrome不在PATH时传 `--chrome /path/to/chrome`；macOS会检测标准安装位置。

[深色演示](examples/terminal-dark.mp4) · [粉彩演示](examples/light-pastel.mp4)

![Dark terminal panel](examples/terminal-dark.png)
![Light pastel panel](examples/light-pastel.png)

深色默认画布1200×1600，粉彩默认1080×1440。`check`自动识别视频尺寸。两个面板风格默认使用本项目独立编排的Hermes布局，不包含live-panel中的第三方复刻示例。深色版包含侧栏触发、打字反馈、证据状态条、计数器、六工作流状态、滚动日志与终端状态行；粉彩版由同一阶段机驱动主流程、工具栏和工作流的联动高亮。状态和日志来自确定性模拟，不连接真实业务数据。生成目录附带 `panel.html`，可直接在浏览器打开并持续播放。

面板可以用JSON定义节点、连线、状态机和日志：

```sh
architecture-motion-video init --style terminal-dark --out terminal.json
# 编辑自动生成的 terminal-panel.json（内容）与 terminal.json（渲染参数）
architecture-motion-video render --config terminal.json --out output/custom-terminal.mp4
# 或直接使用面板内容配置：
architecture-motion-video render --style light-pastel --panel-config terminal-panel.json --out output/custom-pastel.mp4
```

`--style`优先于渲染JSON。面板内容格式见 [panel-config-schema](references/panel-config-schema.md)。渲染时自动检查120余个时刻的布局，并重复seek检查回放一致性；日志与节点状态来自同一状态机。速度和密度会统一调整连线上的流动元素。

## 调整效果

| 参数 | 默认值 | 含义 |
|---|---:|---|
| `--speed` | plush:160 / panels:80 | 流动速度，像素/秒 |
| `--spacing` | plush:23 / panels:180 | 目标元素间距，像素；越小越密 |
| `--duration` | 30 | 时长，秒 |
| `--fps` | 30 | 帧率 |

每条路线元素数按长度计算：plush限制4至34个，面板限制1至34个。面板默认稀疏光点配短拖尾，保留原live-panel的节奏。密度和速度分别调整：觉得太快时只降低 speed，保留 spacing。所有运动元素都在卡片下方，不遮住文字。

修改 Python 模板中的 `roles`、卡片文案和 `paths` 可适配新架构；节点数量变化时也要调整布局和角色区域。模板默认使用第一套六个工作流角色，第二套附带供扩展使用。

## 素材与许可

项目采用 [MIT License](LICENSE)，包括仓库中的代码、文档和随附素材。两套角色由 AI 图像生成工具生成，提示词和来源记录已保留；音乐由附带脚本合成，未使用第三方录音。仓库不附带原参考截图、录屏、私人配置或系统字体。AI 生成素材的来源说明不构成排他权或唯一性保证。

发布前已运行附带模板、检查透明图集与角色区域、核对节点稳定性，并完成 FFmpeg 全视频解码。解码和音量检查不能替代实际试听或视觉审阅。

面板渲染复用 MIT 的 live-panel 引擎，许可与来源保留在 [vendor/live_panel](vendor/live_panel/NOTICE.md)。引擎上游注明动效灵感来自 @thedelost；未复制其第三方视觉复刻示例。
