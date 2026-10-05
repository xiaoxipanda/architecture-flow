# Architecture Flow

**English** · [简体中文](README.zh-CN.md)

Create architecture videos and live web pages in three styles: plush mascot infographics, dark terminal panels, and light pastel panels. Includes a CLI, a reusable AI skill, editable sources, and original instrumental music.

**Every node is visible from the first frame; connectors keep flowing.** Panel styles also include changing states and coordinated highlights, with scrolling logs in the dark theme. Adjust motion speed and density independently. No voiceover is required.

## Three styles

| Plush mascots · `plush` | Dark terminal · `terminal-dark` | Light pastel · `light-pastel` |
|---|---|---|
| ![Plush architecture](examples/cover.png) | ![Dark terminal panel](examples/terminal-dark.png) | ![Light pastel panel](examples/light-pastel.png) |
| [Watch video](examples/demo.mp4) | [Watch video](examples/terminal-dark.mp4) | [Watch video](examples/light-pastel.mp4) |
| Large headlines, plush characters, bundled curves, flowing dots and document icons | Monospaced text, trigger rail, evidence bars, workstreams, counters, and scrolling logs | Editorial layout, pastel cards, context and tool sidebars, coordinated phase highlights |
| Default: 1080×1600 | Default: 1200×1600 | Default: 1080×1440 |

The plush example also includes a [live web page](examples/plush.html). Download it and open it in a browser.

The examples depict a **Hermes one-person company architecture**, with Chinese and English labels. Panel states, counters, and logs are deterministic simulations, not live business telemetry. This tool does not install or configure Hermes. Each panel style has its own layout and reuses the live-panel animation engine.

## Install and get started

All three styles use **HTML/CSS/SVG + JavaScript + Python**. The browser draws the scene and animation; Python handles screenshots, audio, and validation; FFmpeg encodes the video. Pillow is used only for mascot cropping and font metrics, not for drawing video frames.

You need **Python 3.10+, Chrome or Chromium, and FFmpeg**. The plush style also needs Chinese and display fonts. These programs and system fonts are not bundled.

```sh
git clone https://github.com/xiaoxipanda/architecture-flow.git
cd architecture-flow
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .

# Each command creates a 30-second video with original background music.
architecture-flow render --style plush --out output/plush.mp4
architecture-flow render --style terminal-dark --out output/terminal.mp4
architecture-flow render --style light-pastel --out output/pastel.mp4
```

The project is now named `architecture-flow`, with the Python package `architecture_flow`. The previous CLI name, `architecture-motion-video`, remains available as a compatibility alias.

Omitting `--style` selects `plush`. Every video export checks the codec, dimensions, duration, and full decoding. The default format is H.264 / yuv420p MP4 at 30 fps.

On macOS, the tool detects Chrome at its standard installation location, and the plush template uses macOS fonts by default. For other systems or custom locations, supply explicit paths:

```sh
architecture-flow render --style terminal-dark --out output/dark.mp4 \
  --chrome /path/to/chrome --ffmpeg /path/to/ffmpeg

architecture-flow render --style plush --out output/custom-fonts.mp4 \
  --cn-font /path/to/chinese.ttf --serif-font /path/to/serif.ttf \
  --bold-font /path/to/bold.ttf --mono-font /path/to/mono.ttf
```

The Chinese font must contain all glyphs used in your labels. Configure panel fonts in the panel content JSON; the four plush font flags do not apply to panel styles.

## Adjust motion and music

```sh
# Reduce speed while keeping the same density.
architecture-flow render --out output/slower.mp4 --speed 100 --spacing 23

# Panels default to 80 px/s. Smaller spacing adds more packets.
architecture-flow render --style terminal-dark --out output/denser.mp4 \
  --speed 80 --spacing 120 --duration 20

# Export without audio, or supply your own music.
architecture-flow render --out output/silent.mp4 --music none
architecture-flow render --out output/custom-music.mp4 --music /path/to/music.wav
```

| Option | Default | Purpose |
|---|---|---|
| `--speed` | Plush: 160; panels: 80 | Motion speed in pixels per second |
| `--spacing` | Plush: 23; panels: 180 | Target spacing in pixels; smaller values increase density |
| `--duration` | 30 | Video duration in seconds |
| `--fps` | 30 | Frames per second |
| `--music` | `auto` | Original instrumental music; use `none` for silence or an audio file path |

Token counts depend on route length: 4–34 per route for plush, and 1–34 for panels. Panels default to sparse packets with short trails. Speed and density are independent, so reducing speed does not remove tokens.

The CLI generates music by default. When calling `scripts/render_hermes_template.py` directly, omitting `--music` produces a silent video.

## Configure your architecture

There are two types of JSON configuration:

- **Render settings:** style, duration, speed, density, music, executable paths, and related options.
- **Panel content:** canvas, nodes, connectors, state machines, and logs. This format applies to both panel styles.

### Dark terminal and light pastel

```sh
architecture-flow init --style terminal-dark --out terminal.json
# Creates terminal.json (render settings) and terminal-panel.json (content).
# Edit the content, then render.
architecture-flow render --config terminal.json --out output/my-terminal.mp4

architecture-flow init --style light-pastel --out pastel.json
architecture-flow render --config pastel.json --out output/my-pastel.mp4
```

You can also provide panel content directly:

```sh
architecture-flow render --style light-pastel \
  --panel-config pastel-panel.json --out output/custom-panel.mp4
```

See the [panel configuration schema](references/panel-config-schema.md). The built-in layouts are available in the [dark configuration](assets/panel-terminal.json) and [pastel configuration](assets/panel-pastel.json). When changing the number of nodes, update their positions and connectors together.

### Plush mascots

```sh
architecture-flow init --out render.json
architecture-flow render --config render.json --out output/my-plush.mp4
```

The plush input JSON controls render settings. Edit architecture labels, characters, cards, and routes in the [scene definition](scripts/plush_scene.py), including `ROLES`. The webpage and animation template live in [assets/plush.html](assets/plush.html). The default uses six workstream mascots; six additional characters are included for other architectures.

Render JSON supports `style`, `duration`, `fps`, `speed`, `spacing`, `music`, `ffmpeg`, `chrome`, `panel_config`, `atlas`, `cn_font`, `serif_font`, `bold_font`, and `mono_font`. CLI arguments take precedence. Relative paths for music, atlases, fonts, and panel content are resolved from the render JSON's directory.

## Preview and validate

```sh
# Inspect the cover and keyframes before exporting the full video.
architecture-flow render --style light-pastel \
  --out output/preview.mp4 --poster-only

# Detect dimensions and fully decode an existing video.
architecture-flow check output/pastel.mp4
```

For `output/pastel.mp4`, supporting files go into `output/pastel-assets/`: the cover, keyframes, render settings, and automatically generated music. Plush exports also include `plush.json`, `plush.html`, and `web-validation.json`. Panel exports include `panel.json`, `panel.html`, and layout-check frames.

All three styles produce HTML that can play continuously in a browser. Mascot images are embedded in the plush page. Default plush fonts use system fallbacks; explicit font overrides embed the selected font in the generated page. Default typography can vary between machines.

`--poster-only` creates no MP4 or music and does not need FFmpeg. All three preview styles still need Chrome. Plush validation samples 121 times to check fixed content, text bounds, and replay consistency; panel validation checks more than 120 times for layout and replay consistency. Chrome runs with a separate temporary profile and does not access your signed-in browser session.

Existing outputs are protected against accidental overwriting. Choose a new output name or add `--force` to regenerate them. Automated checks do not replace visual review or listening to the audio.

## Use as a skill

The repository is also a reusable skill, with [SKILL.md](SKILL.md) as its entry point. Keep its scripts, assets, references, and vendor directories together:

| Environment | Installation directory |
|---|---|
| Codex | `~/.codex/skills/architecture-flow` |
| Hermes | `~/.hermes/skills/architecture-flow` |

Place the complete repository in the appropriate directory, or link your existing checkout. Preserve an existing installation before replacing it. Prepare the Python environment, FFmpeg, and Chrome dependencies as described above.

Example Codex prompt:

> Use $architecture-flow to create a video of the Hermes one-person company architecture in terminal-dark style. Show all nodes from the first frame, keep connectors flowing, and add simple instrumental music without voiceover.

Choose `light-pastel` for a pastel running panel or `plush` for a mascot infographic. In Hermes, mention `architecture-flow` by name and describe the desired style, architecture, and output.

The skill covers reference analysis, architecture verification, asset selection, editable source generation, rendering, and validation. The separate `live-panel` skill can remain installed; no merge or removal is needed.

## Assets and project structure

| Path | Contents |
|---|---|
| `SKILL.md` | Video creation and validation workflow |
| `cli.py` | `render`, `init`, `music`, and `check` commands |
| `assets/mascots/` | Two transparent RGBA atlases, 12 characters, and texture-region indexes |
| `assets/plush.html` / `scripts/plush_scene.py` | Plush web animation and editable scene |
| `assets/panel-*.json` | Default architecture content for both panels |
| `scripts/` | Renderers, original music synthesis, and video validation |
| `references/` | Configuration guide, asset notes, and image-generation prompts |
| `vendor/live_panel/` | Panel engine, license, and attribution |
| `examples/` | Preview images and demo videos for all three styles |

Additional characters include Founder, Reviewer, finance, support, legal, and data analysis. The last four are optional design assets; their inclusion does not mean those roles are configured in Hermes.

## License and attribution

The project uses the [MIT License](LICENSE). Mascot assets were created with AI image generation; prompts and provenance notes are retained in `references/`. Original music is synthesized by the included scripts without third-party recordings. Reference screenshots, screen recordings, private configurations, and system fonts are not bundled. AI provenance notes do not guarantee exclusive rights or uniqueness.

The panels reuse the MIT-licensed live-panel engine. Its license and attribution are retained in [vendor/live_panel/NOTICE.md](vendor/live_panel/NOTICE.md). The upstream engine credits @thedelost as animation inspiration; this repository does not include its third-party visual recreations.
