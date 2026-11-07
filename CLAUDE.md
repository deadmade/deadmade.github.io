# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Manuel Schülein's personal website, built with Hugo and deployed to GitHub Pages. It has four pages: home (`/`), work (`/work/`), path (`/path/`) and now (`/now/`), plus a 404 page. The layouts and the CSS are the repository's own; there is no theme. The text is English, and the page text lives in `content/` (front matter), not in the layouts.

## Technology Stack

- **Hugo Extended** v0.166.0+ (CI pins 0.166.0); plain CSS, no Sass
- **GitHub Actions** - CI/CD
- **Python** - `scripts/check-site.py` (stdlib only) and `scripts/generate-favicons.py` (Pillow)
- **Nix flake** (`flake.nix`, `.envrc`) - dev shell with hugo + python (Pillow)

## Development Commands

```bash
hugo server -D                                        # dev server at http://localhost:1313
hugo --gc --minify --baseURL "https://deadmade.github.io/" -d <dir>   # the CI build, into a directory of your choice
python3 scripts/check-site.py                         # builds like CI and checks pages, metadata, links, bar, sitemap
python3 scripts/generate-favicons.py                  # regenerate static/icons/ (draws with static/fonts/)
```

## Project Structure

```
hugo.toml                  # site config, [params], [[menu.main]]
content/_index.md          # home: title, description, lede (the introduction)
content/work.md            # work page: intro and three projects (name, tag, drawing, summary, what, stack, source)
content/path.md            # path page: steps, toolkit, languages, hobbies
content/now.md             # now page: rows and the updated date
layouts/baseof.html        # html shell: head partial, top bar, footer
layouts/{home,work,path,now,404}.html
layouts/_partials/head.html            # title, description, canonical, social tags, icons, stylesheet
layouts/_partials/drawing-*.html       # the three project drawings (SVG), shapes and labels only
assets/css/                # tokens.css (colours), fonts.css, base.css, path.css; concatenated into one stylesheet
static/fonts/              # IBM Plex Mono woff2 (400/600/700, latin subset, from @fontsource) + OFL license
static/images/pfp.png      # home page picture (params.avatarurl)
static/icons/              # favicons + site.webmanifest (generated; must stay UTF-8)
static/robots.txt
scripts/                   # check-site.py, generate-favicons.py
```

## Configuration (hugo.toml)

- Locale: English (`locale = "en-US"`, `DefaultContentLanguage = "en"`; `languageCode` is deprecated since Hugo 0.158)
- `[[menu.main]]` drives the top bar and the three links on the home page (entries with a `[menu.main.params] description`); order is `weight`. work, path and now use `pageRef`; github, linkedin and mail use `url`
- `[params]`: `role`, `handle` (the name in the bar and the footer), `description` (site default, used when a page has none), `avatarurl`, `avataralt`
- Each page's `title` and `description` front matter become its `<title>`, meta description and sharing tags (Open Graph and Twitter card, text only, no image)

## Fonts

IBM Plex Mono is self-hosted on purpose (no Google Fonts: GDPR concern, the site is run from Germany). To add a weight, download `ibm-plex-mono-latin-<weight>-normal.woff2` from `cdn.jsdelivr.net/npm/@fontsource/ibm-plex-mono@5/files/` into `static/fonts/` and add a matching `@font-face` block to `assets/css/fonts.css`.

## Gotchas

- The CSS is plain CSS, not Sass: Hugo's built-in LibSass rejects `min()`/`max()` with mixed units (`px` with `vw`), which the styles use.
- The accent colour is one line in `assets/css/tokens.css`. `scripts/generate-favicons.py` keeps its own `ACCENT_COLOR`, so a new accent also means editing that constant and rerunning the script.
- `static/robots.txt` hard-codes the host in its Sitemap line; change it if a custom domain is added.
- No JavaScript and no external requests (fonts, analytics, embeds): `scripts/check-site.py` fails on a `<script>` or on a stylesheet, image or font reference that leaves the site.
- A `pageRef` to a page that does not exist renders `href=""` without a warning; `scripts/check-site.py` catches it.
- Work-page text, including each drawing's `summary` (the SVG `<title>`), lives in `content/work.md`; the drawing partials hold only shapes and labels.
- The work page's design is owner-approved and must not change: edit its text in `content/work.md`, and leave `layouts/work.html`, the drawing partials and their CSS alone unless the owner asks for a redesign.

## Deployment

`.github/workflows/hugo.yml`: push to `main` → checkout → install Hugo → `hugo --gc --minify` → deploy to GitHub Pages. There is no theme checkout and no CI check step: run `scripts/check-site.py` by hand.
