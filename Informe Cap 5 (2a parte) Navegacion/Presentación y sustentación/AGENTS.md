# AGENTS.md — Slidev deck project

Reusable Slidev template. Duplicate the folder per talk and rewrite
`slides.md`. `demo.md` is the syntax reference; keep it as is.

## Starting a new deck

```bash
cp -r ~/slides/_template ~/slides/<deck>
rm -rf ~/slides/<deck>/node_modules
cd ~/slides/<deck>
pnpm install        # ~2 s: hardlinks from the pnpm store, no real extra disk
pnpm dev
```

Copying `node_modules` would duplicate ~700 MB of real blocks. Installing
instead links from `~/.local/share/pnpm/store`, so every deck shares the same
packages on disk.

## Project layout

| Path | Purpose |
| --- | --- |
| `slides.md` | The deck you edit |
| `demo.md` | Syntax and component reference |
| `global-bottom.vue` | Footer layer: deck title + page number |
| `public/cover.svg` | Local background used by the cover |
| `opencode.jsonc` | Slidev MCP server for OpenCode |
| `pnpm-workspace.yaml` | Allows the Playwright install script |
| `AGENTS.md` | This file |

## Commands

| Task | Command |
| --- | --- |
| Live preview | `pnpm dev` |
| Reference deck | `pnpm dev:demo` |
| Static build | `pnpm build` |
| Export PDF | `pnpm export` |
| Format markdown | `pnpm format` |

Dev server: <http://localhost:3030>. `pnpm export` writes `slides.pdf` and needs
the bundled `playwright-chromium` (installed). `slidev export` defaults to
`<entry>-export.pdf`, so always pass `--output` when the name matters.

## Conventions

- Deck configuration lives in the **first** frontmatter block of `slides.md`.
- One idea per slide. Two headlines means two slides.
- Keep `aspectRatio: 16/9` and `canvasWidth: 980` unless the venue needs 4:3.
- Theme: `default` with `colorSchema: light` (projector-safe). Also installed:
  `seriph`, `apple-basic`, `bricks`, `shibainu` — the official set from
  <https://github.com/slidevjs/themes>. Dark mode looks better on a good
  projector but washes out on weak ones.
- Code highlight sequences end with `{all}` (`{2|3-4|all}`). PDF export renders
  the **last** click state, so a partial ending dims the exported slide.
- Code blocks go full width; inside a `two-cols` column the font shrinks until
  it is unreadable on a projector.
- Do not add `fonts:` without checking network access: `provider: google`
  downloads at build/export time. Offline, keep the theme defaults.
- Slide content follows the language of the talk. Code, identifiers, and
  comments stay in English.

## Assets

- Images and backgrounds go in `public/`, referenced as `/name.ext`.
- Icon collections installed: `ph`, `carbon`, `svg-spinners` (bundled with the
  CLI) plus `mdi`, `lucide`, `logos`, `twemoji`, `simple-icons`.
- A collection that is not installed breaks the **whole build** with
  `Error: Icon '<collection>/<name>' not found`. Install it first:
  `pnpm add @iconify-json/<collection>`.
- Local backgrounds keep exports reproducible. Remote ones need
  `remoteAssets: true` to be inlined in the PDF.
- Add a theme: `pnpm add -D @slidev/theme-<name>`, then `theme: <name>`.
  To customize one, `slidev theme eject` copies it to `./theme/` — never edit
  `node_modules`.

## Editing rules

- Prefer the Slidev MCP tools (`slidev-insert-slide`, `slidev-update-slide`,
  `slidev-move-slide`, `slidev-remove-slide`) over raw text edits: they handle
  slide separators and numbered addressing correctly.
- Slide numbers are rendered 1-based numbers.
- The first slide cannot be removed or moved (its frontmatter is the deck
  headmatter).
- The footer lives in `global-bottom.vue`. Do not hardcode a footer per slide.
- Run `pnpm build` before claiming a deck is done; `pnpm export` is the final
  check, because it renders every slide and exposes overflow a build never sees.
