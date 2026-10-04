---
name: architecture-motion-video
description: Create and revise editorial architecture MP4 videos from reference images or videos and verified project evidence, in plush mascot, dark terminal, or light pastel panel styles, with flowing connectors and optional original instrumental music, editable rendering source, and export validation.
---

# Architecture motion video

交付可播放的 MP4、封面、可编辑源码和验证记录。本 Skill 附带 12 个透明毛绒角色、固定节点渲染模板、原创音乐生成器和视频验证器。

## 制作流程

1. **核实内容**：读取当前项目架构与配置，记录事实到来源的映射。区分架构设计、已配置能力与实际成功执行。附带 Hermes 模板仅是案例，使用前重新核实岗位与交付描述；素材中的备用角色不代表已经存在的岗位。
2. **分析参考**：图片用于提取排版、字体层级、配色、角色材质与连线密度；视频还需抽查起始、中间、结束画面，判断节点、镜头、角色、连线分别如何运动。截图不能证明原视频的运动方式。
3. **确定动效**：遵循用户要求与实际参考。本套素材对应的方式是所有节点从第一帧完整可见，卡片、文字、角色、镜头固定，只让圆点和文档图标沿连线移动。仅在用户需要时添加渐入、角色动作或镜头推进。
4. **选用素材和模板**：读 [素材说明](references/assets.md) 选择角色。需要继续扩充时使用 imagegen，以已有图集为风格参考，保留真实透明 alpha，并保存提示词及角色区域索引。不要把文字交给图像模型生成。
5. **先看封面，再渲染**：读 [运行与调整](references/rendering.md)，复制模板到任务项目并修改内容。先检查封面中的字号、留白、遮挡与完整边界，再输出视频。保留之前版本。
6. **配置音频**：按用户选择无声、音乐或解说。纯音乐模式排除全部语音音轨，使用原创音乐或明确可复用的音乐来源；保留生成源码或许可信息，检查音量和淡入淡出。
7. **验证后交付**：用 scripts/validate_video.py 检查尺寸、时长、H.264/yuv420p 和完整解码；检查实际解码的首帧、中间与尾帧。确认节点显示完整、动画确实变化且文字不被遮挡。未试听时明确记录该验证边界。交付 MP4 和封面链接，保存素材、源码、参数与事实依据。

## 动效调整原则

密度与速度分开设置，用户只要求调速时保留密度。用曲线弧长均匀分布元素，用像素/秒设置速度；避免归一化参数让长短路线出现不同速度。流动元素画在节点下面，确保不遮住文字。密度提高后仍不明显时检查点的颜色、大小与可见路径长度。

本次迭代形成的**可选起点**：1080×1600、30fps、约每23像素一个元素、每条4至34个、160像素/秒。用户曾认为同一密度下300像素/秒过快，因此160是当前候选值，尚未得到最终效果确认。按新的参考与用户反馈调整，不将这些数字作为所有视频的硬性要求。

## 风格选择

统一使用 `--style plush|terminal-dark|light-pastel`。毛绒角色、宣传型信息图选plush；深色终端运行面板选terminal-dark；浅色粉彩运行面板选light-pastel。深色包含侧栏触发、状态条、模拟日志与终端状态行；粉彩包含侧栏、主流程和工具栏的阶段联动高亮。，不代表连接了真实遥测。不要为仅要求流动连线的用户强制添加状态日志。

面板读取 `--panel-config` 的JSON定义，默认使用附带原创Hermes布局。`init --style terminal-dark --out terminal.json` 同时生成渲染设置和面板内容配置。配置参考 [面板schema](references/panel-config-schema.md)。面板额外需要Chrome/Chromium；自动检查几何和回放一致性，并保留可持续播放的panel.html。保持 [live-panel许可与来源](vendor/live_panel/NOTICE.md)，不要合入未获授权的第三方复刻示例。

## 终端命令

仓库支持 `pip install .`，然后用 `architecture-motion-video render --out demo.mp4` 自动生成音乐、视频并解码检查；`init --out render.json` 保存渲染配置，`check demo.mp4` 验证视频。命令行参数优先于JSON。plush的JSON仅保存渲染参数；面板可另用panel_config定义节点、连线与模拟状态。详见运行说明。

## 附带资源

- [角色索引](assets/mascots/manifest.json)：两套图集、12个角色、纹理矩形。
- scripts/render_hermes_template.py：固定节点、弧长匀速连线的可编辑案例。
- scripts/make_music.py：原创柔和键盘琶音与和弦，支持指定时长。
- scripts/validate_video.py：完整解码与输出格式检查。
- [运行与调整](references/rendering.md)：命令、依赖、参数及检查方式。
- [素材说明](references/assets.md)：角色用途、来源及扩充方式；链接原始生成提示词。

只处理当前制作任务的文件，不改变 Hermes 生产服务配置；未经请求不对外发布。不要通过系统剪贴板复制大文件。
