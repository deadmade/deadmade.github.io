# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Manuel Schülein's personal website, built with Hugo and deployed to GitHub Pages. It has five pages: home (`/`), projects (`/projects/`), path (`/path/`), now (`/now/`) and privacy (`/privacy/`, linked from the footer), plus a 404 page (`noindex`, no canonical). The layouts and the CSS are the repository's own; there is no theme. The text is English, and the page text lives in `content/` (front matter), not in the layouts.

## Technology Stack

- **Hugo Extended** v0.166.0+ (CI pins 0.166.0); plain CSS, no Sass
- **GitHub Actions** - CI/CD
- **Python** - `scripts/check-site.py` (stdlib only), `scripts/generate-favicons.py` and `scripts/generate-og-image.py` (Pillow)
- **Nix flake** (`flake.nix`, `.envrc`) - dev shell with hugo + python (Pillow)

## Development Commands

```bash
hugo server -D                                        # dev server at http://localhost:1313
hugo --gc --minify --baseURL "https://deadmade.github.io/" -d <dir>   # the CI build, into a directory of your choice
python3 scripts/check-site.py                         # builds like CI and checks pages, metadata, links, bar, sitemap, motion
python3 scripts/generate-favicons.py                  # regenerate static/icons/ (draws with static/fonts/)
python3 scripts/generate-og-image.py                  # regenerate static/images/og.png (share image; colours from tokens.css, text from hugo.toml)
```

## Project Structure

```
hugo.toml                  # site config, [params], [[menu.main]]
content/_index.md          # home: title, description, lede (the introduction)
content/projects.md        # projects page: three projects (name, tag, drawing, summary, what, stack, source)
content/path.md            # path page: steps, toolkit, languages, hobbies
content/now.md             # now page: rows (each line is inline Markdown, so it can link) and the updated date
content/privacy.md         # privacy notice, Markdown body (GitHub Pages hosting, mail, GDPR rights)
layouts/baseof.html        # html shell: head partial, top bar, footer
layouts/{home,projects,path,now,privacy,404}.html
layouts/_partials/head.html            # title, description, canonical, social tags, icons, stylesheet
layouts/_partials/drawing-*.html       # the three project drawings (SVG), shapes and labels only
assets/css/                # tokens.css (colours), fonts.css, base.css, path.css (body.path / body.now), motion.css (all motion, last); concatenated into one stylesheet
static/fonts/              # IBM Plex Mono woff2 (400/600/700, latin subset, from @fontsource) + OFL license
static/images/pfp.webp     # home page picture (params.avatarurl)
static/images/og.png       # share image (params.images), generated
static/icons/              # favicons + site.webmanifest (generated; must stay UTF-8)
static/robots.txt
scripts/                   # check-site.py, generate-favicons.py, generate-og-image.py
```

## Configuration (hugo.toml)

- Locale: English (`locale = "en-US"`, `DefaultContentLanguage = "en"`; `languageCode` is deprecated since Hugo 0.158)
- `[[menu.main]]` drives the top bar and the three links on the home page (entries with a `[menu.main.params] description`); order is `weight`. projects, path and now use `pageRef`; github, linkedin and mail use `url`
- `[params]`: `role` (the footer, the page metadata and the share image; the home page says it in its paragraph, `lede` in `content/_index.md`), `handle` (the name in the bar and the footer), `description` (site default, used when a page has none), `images` (the share image), `avatarurl`, `avataralt`
- Each page's `title` and `description` front matter become its `<title>`, meta description and sharing tags (Open Graph and Twitter card, `summary_large_image` with `params.images`)

## Fonts

IBM Plex Mono is self-hosted on purpose (no Google Fonts: GDPR concern, the site is run from Germany). To add a weight, download `ibm-plex-mono-latin-<weight>-normal.woff2` from `cdn.jsdelivr.net/npm/@fontsource/ibm-plex-mono@5/files/` into `static/fonts/` and add a matching `@font-face` block to `assets/css/fonts.css`.

## Gotchas

- The CSS is plain CSS, not Sass: Hugo's built-in LibSass rejects `min()`/`max()` with mixed units (`px` with `vw`), which the styles use.
- The accent colour is one line in `assets/css/tokens.css`. `scripts/generate-favicons.py` keeps its own `ACCENT_COLOR`, so a new accent also means editing that constant and rerunning the script; also rerun `scripts/generate-og-image.py` (it reads tokens.css itself).
- There is no Impressum yet (the owner decided to skip it for now); the privacy page names no postal address.
- `static/robots.txt` hard-codes the host in its Sitemap line; change it if a custom domain is added.
- No JavaScript and no external requests (fonts, analytics, embeds): `scripts/check-site.py` fails on a `<script>` or on a stylesheet, image or font reference that leaves the site.
- A `pageRef` to a page that does not exist renders `href=""` without a warning; `scripts/check-site.py` catches it.
- All motion lives in `assets/css/motion.css`, inside its one `prefers-reduced-motion: no-preference` block, last in the concatenation; `scripts/check-site.py` fails on motion text (animation, transition, keyframes, view transitions, `scroll-behavior`) before that block and on any text after it. Page transitions work in Chrome, Edge and Safari 18.2+ only.
- The projects page's drawings and sheets have no motion (the owner rejected it) and must look the same at rest. Its page transition is the browser's plain cross-fade: `main:not(:has(.dwg))` leaves it out of the `content` transition name. It has no visible headline (its `h1` is visually hidden); each project's name is lettered onto the rule above it. Naming its `main`, or leaving a finished `both` fill on the title, each changed how the drawings were painted at rest (measured in Chrome 154).
- Checking motion in the browser tool misleads in four ways (probe says "no transition" on `127.0.0.1`, no frames before a screenshot, JPEG noise, tab state): read `docs/solutions/checking-motion-in-the-browser-tool.md` first.
- Projects-page text, including each drawing's `summary` (the SVG `<title>`), lives in `content/projects.md`; the drawing partials hold only shapes and labels.
- The projects page's design is owner-approved and must not change: edit its text in `content/projects.md`, and leave `layouts/projects.html`, the drawing partials and their CSS alone unless the owner asks for a redesign.

## Deployment

`.github/workflows/hugo.yml`: push to `main` → checkout → install Hugo → `python3 scripts/check-site.py` (a failing check stops the deploy) → `hugo --gc --minify` → deploy to GitHub Pages. There is no theme checkout.
