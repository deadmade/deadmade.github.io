# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Manuel Schülein's personal website, built with Hugo and deployed to GitHub Pages at `https://manuelschuelein.de` (a custom domain held in the repository's Pages settings; `deadmade.github.io`, `www.` and `http://` redirect there). It has four pages: home (`/`), projects (`/projects/`), path (`/path/`) and now (`/now/`), plus a 404 page (`noindex`, no canonical). The layouts and the CSS are the repository's own; there is no theme. The text is English, and the page text lives in `content/` (front matter), not in the layouts.

## Technology Stack

- **Hugo Extended** v0.166.0+ (CI pins 0.166.0); plain CSS, no Sass
- **GitHub Actions** - CI/CD
- **Python** - `scripts/check-site.py` (stdlib only, Python 3.11+ for `tomllib`), `scripts/generate-favicons.py` and `scripts/generate-og-image.py` (Pillow)
- **Nix flake** (`flake.nix`, `.envrc`) - dev shell with hugo + python (Pillow) and the commands `serve`, `check`, `gen-favicons`, `gen-og-image`

## Development Commands

```bash
hugo server -D                                        # dev server at http://localhost:1313
hugo --gc --minify --baseURL "https://manuelschuelein.de/" -d <dir>   # the CI build, into a directory of your choice
python3 scripts/check-site.py                         # builds like CI and checks pages, metadata, links, bar, host, sitemap, dates, icon, JSON-LD, motion
python3 scripts/generate-favicons.py                  # regenerate static/icons/ (draws with static/fonts/)
python3 scripts/generate-og-image.py                  # regenerate static/images/og.png (share image; colours from tokens.css, text from hugo.toml)
```

## Project Structure

```
hugo.toml                  # site config, [params], [[menu.main]]
content/_index.md          # home: title, description, lede (the introduction)
content/projects.md        # projects page: three projects (name, tag, drawing, summary, what, stack, source)
content/path.md            # path page: steps, toolkit, languages, hobbies
content/now.md             # now page: rows (each line is inline Markdown, so it can link); its "updated" month is now.md's last commit
layouts/baseof.html        # html shell: head partial, top bar, footer
layouts/{home,projects,path,now,404}.html
layouts/_partials/head.html            # title, description, canonical, social tags, icons, JSON-LD (home page), stylesheet
layouts/_partials/drawing-*.html       # the three project drawings (SVG), shapes and labels only
layouts/robots.txt         # robots.txt template (enableRobotsTXT); its Sitemap line comes from baseURL
assets/css/                # tokens.css (colours), fonts.css, base.css, path.css (body.path / body.now), motion.css (all motion, last); concatenated into one stylesheet
static/fonts/              # IBM Plex Mono woff2 (400/600/700, latin subset, from @fontsource) + OFL license
static/images/pfp.webp     # home page picture (params.avatarurl)
static/images/og.png       # share image (params.images), generated
static/icons/              # favicons + site.webmanifest (generated; must stay UTF-8)
scripts/                   # check-site.py, generate-favicons.py, generate-og-image.py
```

## Configuration (hugo.toml)

- Locale: English (`locale = "en-US"`, `DefaultContentLanguage = "en"`; `languageCode` is deprecated since Hugo 0.158)
- `[[menu.main]]` drives the top bar and the three links on the home page (entries with a `[menu.main.params] description`); order is `weight`. projects, path and now use `pageRef`; github, linkedin and mail use `url`. Every `url` entry that starts with `https://` also becomes a `sameAs` identity claim in the home page's JSON-LD, so only the owner's own profiles belong there
- `[params]`: `role` (the footer, the page metadata and the share image; the home page says it in its paragraph, `lede` in `content/_index.md`), `handle` (the name in the bar and the footer), `alternatename` (the name without the umlaut; with `handle`, the alternate names in the JSON-LD), `description` (site default, used when a page has none), `images` (the share image), `avatarurl`, `avataralt`
- Each page's `title` and `description` front matter become its `<title>`, meta description and sharing tags (Open Graph and Twitter card, `summary_large_image` with `params.images`)
- `enableGitInfo` makes Git the source of page dates: the sitemap's `lastmod`, the now page's "updated" month, `article:modified_time` and the JSON-LD's `dateModified` are the last commit of each page's content file. A page's date moves only when its content file is committed (edits to layouts or `hugo.toml` don't move it); CI checks out with `fetch-depth: 0` for this. Every build needs a Git checkout with its history and `git` on PATH: without `.git`, Hugo stops with `failed to load Git data`

## Fonts

IBM Plex Mono is self-hosted on purpose (no Google Fonts: GDPR concern, the site is run from Germany). To add a weight, download `ibm-plex-mono-latin-<weight>-normal.woff2` from `cdn.jsdelivr.net/npm/@fontsource/ibm-plex-mono@5/files/` into `static/fonts/` and add a matching `@font-face` block to `assets/css/fonts.css`.

## Gotchas

- The CSS is plain CSS, not Sass: Hugo's built-in LibSass rejects `min()`/`max()` with mixed units (`px` with `vw`), which the styles use.
- The accent colour is one line in `assets/css/tokens.css`. `scripts/generate-favicons.py` keeps its own `ACCENT_COLOR`, so a new accent also means editing that constant and rerunning the script; also rerun `scripts/generate-og-image.py` (it reads tokens.css itself).
- There is no Impressum and no privacy page: the owner decided against both (November 2026).
- The host lives in three places that must agree: `hugo.toml`'s `baseURL` (local builds and `hugo server`), `BASE` in `scripts/check-site.py`, and the custom domain in the repository's Pages settings (CI passes it to the deploy build as `--baseURL` and to the check as `PAGES_BASE_URL`). A new domain means changing all three. `scripts/check-site.py` fails when `baseURL` or, in CI, the Pages address differs from `BASE`, on `deadmade.github.io` anywhere in the build, and on either host in `layouts/`, `content/` or `static/`.
- No JavaScript and no external requests (fonts, analytics, embeds): `scripts/check-site.py` fails on a `<script>` or on a stylesheet, image or font reference that leaves the site. The one exception is the home page's `<script type="application/ld+json">` block, data and not code: a `WebSite` node and a `ProfilePage` whose `mainEntity` is the owner as a `Person`, built in `layouts/_partials/head.html` from `hugo.toml` and the menu. The check fails on any other `<script`, on a second block or one on another page, and on a value in the block that differs from what the built home page shows (Google: mark up only what readers can see).
- A `pageRef` to a page that does not exist renders `href=""` without a warning; `scripts/check-site.py` catches it.
- All motion lives in `assets/css/motion.css`, inside its one `prefers-reduced-motion: no-preference` block, last in the concatenation; `scripts/check-site.py` fails on motion text (animation, transition, keyframes, view transitions, `scroll-behavior`) before that block and on any text after it. Page transitions work in Chrome, Edge and Safari 18.2+ only.
- The projects page's drawings and sheets have no motion (the owner rejected it) and must look the same at rest. Its page transition is the browser's plain cross-fade: `main:not(:has(.dwg))` leaves it out of the `content` transition name. It has no visible headline (its `h1` is visually hidden); each project's name is lettered onto the rule above it. Naming its `main`, or leaving a finished `both` fill on the title, each changed how the drawings were painted at rest (measured in Chrome 154).
- Checking motion in the browser tool misleads in four ways (probe says "no transition" on `127.0.0.1`, no frames before a screenshot, JPEG noise, tab state): read `docs/solutions/checking-motion-in-the-browser-tool.md` first.
- Projects-page text, including each drawing's `summary` (the SVG `<title>`), lives in `content/projects.md`; the drawing partials hold only shapes and labels.
- The projects page's design is owner-approved and must not change: edit its text in `content/projects.md`, and leave `layouts/projects.html`, the drawing partials and their CSS alone unless the owner asks for a redesign.

## Deployment

`.github/workflows/hugo.yml`: push to `main` → checkout → install Hugo → `python3 scripts/check-site.py` with `PAGES_BASE_URL` set to the Pages address (a failing check stops the deploy, also when that address is not `https://manuelschuelein.de`) → `hugo --gc --minify --baseURL <the Pages address>/` → deploy to GitHub Pages at `https://manuelschuelein.de`. There is no theme checkout.
