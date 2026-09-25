# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Manuel Schülein's personal website, built with Hugo and deployed to GitHub Pages. It is currently a single homepage (avatar/info + social links) using the hugo-coder theme. Resume and projects pages were removed; there is no main menu.

## Technology Stack

- **Hugo Extended** v0.166.0+ (SCSS compiled with Hugo's built-in LibSass via the theme's `toCSS`; no Dart Sass needed)
- **hugo-coder theme** - git submodule in `themes/hugo-coder/` (clone with `--recurse-submodules`, or run `git submodule update --init`)
- **GitHub Actions** - CI/CD
- **Nix flake** (`flake.nix`, `.envrc`) - dev shell with hugo + python (Pillow for `scripts/generate-favicons.py`)

## Development Commands

```bash
hugo server -D                                        # dev server at http://localhost:1313
hugo --minify --baseURL "https://deadmade.github.io/"  # production build into public/
hugo new blog/post-name.md                            # new blog post
python3 scripts/generate-favicons.py                  # regenerate static/icons/
```

## Project Structure

```
content/_index.md          # Homepage (empty, theme renders it from hugo.toml params)
assets/scss/custom.scss    # customSCSS entry point, imports _fonts.scss
assets/scss/_fonts.scss    # @font-face for self-hosted IBM Plex Mono + font overrides
static/fonts/              # IBM Plex Mono woff2 (400/600/700, latin subset, from @fontsource) + OFL license
static/images/avatar.jpg   # homepage avatar (theme placeholder; replace with a photo, set via params.avatarurl)
static/icons/              # favicons + site.webmanifest (must stay UTF-8)
static/robots.txt
```

## Configuration (hugo.toml)

- Locale: German (`locale = "de-DE"`; `languageCode` is deprecated since Hugo 0.158); content is German
- Social links: GitHub, LinkedIn, Email, Discord (`[[params.social]]`)
- Footer year range comes from `params.since`
- No `[menu]` section; add `[[menu.main]]` entries if pages are added again
- `customSCSS = ["scss/custom.scss"]`

## Fonts

IBM Plex Mono is self-hosted on purpose (no Google Fonts: GDPR concern for a German site). To add a weight, download `ibm-plex-mono-latin-<weight>-normal.woff2` from `cdn.jsdelivr.net/npm/@fontsource/ibm-plex-mono@5/files/` into `static/fonts/` and add the weight to the `@each` list in `_fonts.scss`.

## Theme gotchas

- **Do not** edit files in `themes/hugo-coder/`; override by creating the same path under `layouts/`.
- To update the theme: `git submodule update --remote themes/hugo-coder`, rebuild, commit. Dependabot (`.github/dependabot.yml`, `gitsubmodule`) also opens weekly update PRs.
- The theme loads custom SCSS with `media="screen"`, so `@media print` rules in custom SCSS never apply.
- The theme has a light/dark toggle that sets `body.colorscheme-dark` / `colorscheme-light` / `colorscheme-auto`. Dark-mode custom styles must key off these classes (see the theme's `_*_dark.scss`), not just `@media (prefers-color-scheme: dark)`.

## Deployment

`.github/workflows/hugo.yml`: push to `main` → checkout (with submodules) → install Hugo → `hugo --gc --minify` → deploy to GitHub Pages.
