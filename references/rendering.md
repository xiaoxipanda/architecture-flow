# 运行与调整

## 依赖与案例边界

Python 3，Pillow、NumPy，FFmpeg。模板预设 macOS 系统字体，不打包字体或 FFmpeg。其他环境用 --fonts-dir 指定字体目录，或修改FONTS使中文字体、衬线标题与粗体正确解析；不能静默使用缺失中文字形的字体。选择环境已有运行时，不为了视频更改生产服务。

模板目前是 Hermes 的六工作流案例；修改 roles、卡片位置、文案和 paths 即可适配新架构。节点数量变化需调整图集索引、卡片和连线，不能只改岗位标题。不得用扩展图集冒充已新增岗位。

## 示例命令

下面的路径均是相对于 Skill 文件夹的路径；实际运行时转换为绝对路径。输出必须是任务项目中的新目录。

```sh
python3 scripts/make_music.py --output /absolute/output/music.wav --duration 30
python3 scripts/render_hermes_template.py --output-dir /absolute/output --duration 30 --speed 160 --spacing 23 --poster-only
python3 scripts/render_hermes_template.py --output-dir /absolute/output --duration 30 --speed 160 --spacing 23 --music /absolute/output/music.wav --ffmpeg /absolute/path/to/ffmpeg
python3 scripts/validate_video.py /absolute/output/architecture.mp4 --ffmpeg /absolute/path/to/ffmpeg --width 1080 --height 1600 --min-duration 29
```

复制源码到项目修改时，脚本中的 SKILL 路径需指向本 Skill 的实际路径，或显式传 --atlas 指向图集。独立发给别人时同时带上素材和依赖说明。

--duration / --fps 控制时长与帧率；--speed 是像素/秒，--spacing 是目标间隔；--atlas 指向与模板角色顺序一致的图集。没有 --music 时输出无声视频，不会自动添加解说。输出含 architecture.mp4、cover.png、poster.png、5张关键帧和render-settings.json。纯音乐用显式音轨映射，保持原视频不变时也可重新混音。

## 检查

- 首帧必须完整显示所有节点；抽取实际编码画面确认，不能只检查源码生成的封面。
- 节点内区在不同时间应一致；连线路径应有像素变化。比较无损源帧，避免压缩差异误报为节点动画。
- 流动位置用曲线累计弧长插值，节点覆盖绘制在最上层。长路线元素上限34，最短路线最少4；若短线堆积，按实际可见长度降低下限。
- 完整解码失败时修复后重新检查；视觉检查与解码检查分别记录。
- 用FFmpeg volumedetect检查音乐平均值与峰值，避免削波；工具检查不能替代试听。当前原创生成器峰值约0.38，开头2秒、结尾3.5秒淡入淡出。
- 保存参考来源、架构事实依据、渲染参数、音频来源与验证报告；最终说明视频是架构示意还是实际业务执行记录。
