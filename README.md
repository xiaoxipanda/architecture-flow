# Architecture Motion Video

A reusable Codex skill and Python toolkit for editorial architecture videos: static cards, flowing connectors, fluffy 3D mascots, and optional original instrumental music.

将系统架构制作成动态信息图：节点从第一帧完整显示，只让圆点和文档图标沿连线流动。支持独立调节速度与密度。

![Hermes architecture preview](examples/cover.png)

[查看带背景音乐的演示视频](examples/demo.mp4)

## 包含什么

- `SKILL.md`：参考分析、架构核实、素材选择、渲染、音频和验证流程。
- `assets/mascots/`：两套透明 RGBA 图集，共12个角色，以及角色纹理区域索引。
- `scripts/render_hermes_template.py`：1080×1600 架构示例，固定节点、沿曲线弧长匀速流动。
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

## 作为 Codex Skill 使用

将整个仓库文件夹放入或链接到 `~/.codex/skills/architecture-motion-video`，保留素材、脚本和 references 目录。若该目录已存在，先保留现有版本，不直接覆盖。

然后在 Codex 中请求：

> 用 $architecture-motion-video 为这个架构制作视频，节点固定，只让连线运动，配简单音乐。

## 调整效果

| 参数 | 默认值 | 含义 |
|---|---:|---|
| `--speed` | 160 | 流动速度，像素/秒 |
| `--spacing` | 23 | 目标元素间距，像素；越小越密 |
| `--duration` | 30 | 时长，秒 |
| `--fps` | 30 | 帧率 |

每条路线元素数按弧长计算，限制在4至34个。密度和速度分别调整：觉得太快时只降低 speed，保留 spacing。所有运动元素都在卡片下方，不遮住文字。

修改 Python 模板中的 `roles`、卡片文案和 `paths` 可适配新架构；节点数量变化时也要调整布局和角色区域。模板默认使用第一套六个工作流角色，第二套附带供扩展使用。

## 素材与许可

项目采用 [MIT License](LICENSE)，包括仓库中的代码、文档和随附素材。两套角色由 AI 图像生成工具生成，提示词和来源记录已保留；音乐由附带脚本合成，未使用第三方录音。仓库不附带原参考截图、录屏、私人配置或系统字体。AI 生成素材的来源说明不构成排他权或唯一性保证。

发布前已运行附带模板、检查透明图集与角色区域、核对节点稳定性，并完成 FFmpeg 全视频解码。解码和音量检查不能替代实际试听或视觉审阅。
