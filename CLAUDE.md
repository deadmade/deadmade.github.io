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
python3 scripts/check-site.py                         # builds like CI and checks pages, metadata, links, bar, host, sitemap, dates, icon, JSON-LD, motion, the drawings' runs
python3 scripts/generate-favicons.py                  # regenerate static/icons/ (draws with static/fonts/)
python3 scripts/generate-og-image.py                  # regenerate static/images/og.png (share image; colours from tokens.css, text from hugo.toml)
```

## Project Structure

```
hugo.toml                  # site config, [params], [[menu.main]]
content/_index.md          # home: title, description, lede (the introduction)
content/projects.md        # projects page: three projects (name, tag, drawing, runkey, summary, what, stack, source); runbar (the stop / play words)
content/path.md            # path page: steps, toolkit, languages, hobbies
content/now.md             # now page: rows (each line is inline Markdown, so it can link); its "updated" month is now.md's last commit
layouts/baseof.html        # html shell: head partial, top bar, footer
layouts/{home,projects,path,now,404}.html
layouts/_partials/head.html            # title, description, canonical, social tags, icons, JSON-LD (home page), stylesheet
layouts/_partials/drawing-*.html       # the three project drawings (SVG): shapes and labels, plus the run.html and runbar.html calls
layouts/_partials/run.html            # a drawing's run layer (outlines and dots), from data/runs.toml
layouts/_partials/runbar.html         # above each drawing: what the dot carries (runkey) and the stop / play switch
layouts/robots.txt         # robots.txt template (enableRobotsTXT); its Sitemap line comes from baseURL
data/runs.toml             # the drawings' runs: timing values, then per drawing its stops, spans and runs (hops with pauses), each shape and route twice (h wide, v upright)
assets/css/                # tokens.css (colours), fonts.css, base.css, path.css (body.path / body.now), motion.css (all motion, last; a Go template that reads hugo.Data.runs); concatenated into one stylesheet
static/fonts/              # IBM Plex Mono woff2 (400/600/700, latin subset, from @fontsource) + OFL license
static/images/pfp.webp     # home page picture (params.avatarurl)
static/images/og.png       # share image (params.images), generated
static/icons/              # favicons + site.webmanifest (generated; must stay UTF-8)
scripts/                   # check-site.py, generate-favicons.py, generate-og-image.py
```

## Configuration (hugo.toml)

- Locale: English (`locale = "en-US"`, `DefaultContentLanguage = "en"`; `languageCode` is deprecated since Hugo 0.158)
- `[[menu.main]]` drives the top bar and the three links on the home page (entries with a `[menu.main.params] description`); order is `weight`. projects, path and now use `pageRef`; github, linkedin and mail use `url`. Every `url` entry that starts with `https://` also becomes a `sameAs` identity claim in the home page's JSON-LD, so only the owner's own profiles belong there
- `[params]`: `role` (the footer, the page metadata and the share image), `handle` (the name in the bar and the footer), `alternatename` (the name without the umlaut; with `handle`, the alternate names in the JSON-LD), `description` (site default, used when a page has none), `images` (the share image), `avatarurl`, `avataralt`
- Each page's `title` and `description` front matter become its `<title>`, meta description and sharing tags (Open Graph and Twitter card, `summary_large_image` with `params.images`)
- `enableGitInfo` makes Git the source of page dates: the sitemap's `lastmod`, the now page's "updated" month, `article:modified_time` and the JSON-LD's `dateModified` are the last commit of each page's content file. A page's date moves only when its content file is committed (edits to layouts or `hugo.toml` don't move it); CI checks out with `fetch-depth: 0` for this, and `scripts/check-site.py` fails on a shallow checkout. Every build needs a Git checkout with its history and `git` on PATH: without `.git`, Hugo stops with `failed to load Git data`

## Fonts

IBM Plex Mono is self-hosted on purpose (no Google Fonts: GDPR concern, the site is run from Germany). To add a weight, download `ibm-plex-mono-latin-<weight>-normal.woff2` from `cdn.jsdelivr.net/npm/@fontsource/ibm-plex-mono@5/files/` into `static/fonts/` and add a matching `@font-face` block to `assets/css/fonts.css`.

## Gotchas

- The CSS is plain CSS, not Sass: Hugo's built-in LibSass rejects `min()`/`max()` with mixed units (`px` with `vw`), which the styles use.
- The accent colour is one line in `assets/css/tokens.css`. `scripts/generate-favicons.py` keeps its own `ACCENT_COLOR`, so a new accent also means editing that constant and rerunning the script; also rerun `scripts/generate-og-image.py` (it reads tokens.css itself).
- There is no Impressum and no privacy page: the owner decided against both (November 2026).
- The host lives in three places that must agree: `hugo.toml`'s `baseURL` (local builds and `hugo server`), `BASE` in `scripts/check-site.py`, and the custom domain in the repository's Pages settings (CI passes it to the deploy build as `--baseURL` and to the check as `PAGES_BASE_URL`). A new domain means changing all three. `scripts/check-site.py` fails when `baseURL` or, in CI, the Pages address differs from `BASE`, on `deadmade.github.io` anywhere in the build, and on either host in `layouts/`, `content/`, `static/` or `data/`. A mail address on the domain, and the repository's name in `github.com/deadmade/deadmade.github.io`, don't count as the host.
- No JavaScript and no external requests (fonts, analytics, embeds): `scripts/check-site.py` fails on a `<script>` or on a stylesheet, image or font reference that leaves the site. The one exception is the home page's `<script type="application/ld+json">` block, data and not code: a `WebSite` node and a `ProfilePage` whose `mainEntity` is the owner as a `Person`, built in `layouts/_partials/head.html` from `hugo.toml` and the menu. The check fails on any other `<script`, on a second block or one on another page, and on a value in the block that differs from what the built home page shows or a key it does not compare with the page, so a new key needs the page to show it and `check_data` to compare it (Google: mark up only what readers can see).
- A `pageRef` to a page that does not exist renders `href=""` without a warning; `scripts/check-site.py` catches it.
- All motion lives in `assets/css/motion.css`, inside its one `prefers-reduced-motion: no-preference` block, last in the concatenation; `scripts/check-site.py` fails on motion text (animation, transition, keyframes, view transitions, `scroll-behavior`) before that block and on any text after it. Page transitions work in Chrome, Edge and Safari 18.2+ only.
- The projects page's drawings move only through their run layers (owner-approved 2026-11-17) and must look the same at rest; the sheets have no motion; nothing inside a drawing may animate `transform` (it changed Chrome's rendering of the whole drawing at rest, 12,766 px) or `opacity` (fading the run layers with it changed how Chrome painted RustLogger and IsoPrüfi at rest at a device pixel ratio of 2 and 3, so they fade with `fill-opacity` and `stroke-opacity`, which leaves Chrome at a ratio of 1 painting a few dozen edge pixels per drawing (4 to 51 measured, by width and moment) up to 26/255 off between runs; no fade measured was identical at every ratio, a stopped drawing is, and the owner accepted that remainder on 2026-11-22; see `docs/solutions/chromium-paints-drawings-differently-at-rest.md`). "At rest" means between runs while they loop, and with every switch stopped: compare both against the base build, as lossless clips taken a few seconds after load with the drawing in view while it runs (an off-screen drawing isn't painted), at a device pixel ratio of 1 and 2 (stopping alone hides the between-runs difference above); below 760 px, against a base build with the switch row's 32 px `padding-top` added, as that move alone changes Chrome's upright drawings (measured at a ratio of 2 and 3, and at 1 in an 844 px tall window). Its page transition is the browser's plain cross-fade: `main:not(:has(.dwg))` leaves it out of the `content` transition name. It has no visible headline (its `h1` is visually hidden); each project's name is lettered onto the rule above it. Naming its `main`, or leaving a finished `both` fill on the title, each changed how the drawings were painted at rest (measured in Chrome 154).
- Checking motion in the browser tool misleads in four ways (probe says "no transition" on `127.0.0.1`, no frames before a screenshot, JPEG noise, tab state): read `docs/solutions/checking-motion-in-the-browser-tool.md` first.
- Projects-page text, including each drawing's `summary` (the SVG `<title>`) and the run words (`runkey`, `runbar`), lives in `content/projects.md`; the drawing partials hold only shapes and labels, plus the `run.html` and `runbar.html` calls.
- A drawing's runs follow its arrows: `data/runs.toml` holds each hop's points and each stop's outline twice (wide and upright), copied from the drawing partial. Editing a drawing means updating its routes there; `scripts/check-site.py`'s `runs` check fails on a hop off its arrow or not from its stop's box to the next one's, an outline off its component, a drawing that draws another's runs, a run layer screen readers see or one not wired to its keyframes, a drawing without its stop / play switch or a switch whose name lacks its visible words, and anything inside a drawing that moves other than `fill-opacity`, `stroke-opacity` and `stroke-dashoffset` animations, however it is written (a transition, a `view-transition-name`, a prefixed property or `@-webkit-keyframes`, a `style` attribute anywhere on the page, a `<style>` block, an SVG animation tag, a nested rule anywhere in the stylesheet); an animation given through a function other than an easing (`var()`, `attr()`) or a CSS-wide keyword (`inherit`, `unset`, `revert`), or set with `!important` in any case, fails too, as the check can't follow the one and the stop rule can't end the other, and so does an animation, a transition or a view-transition name on anything in a projects sheet outside its run layers or on what holds one (`body` and `main` too; `main:not(:has(.dwg))` is read as leaving the projects page out). It also fails on a stop or span shape written in the wrong form, a stop outlined by anything but one `rect` or one `polygon`, a span's bracket or label more than 48 units from its stops' boxes, a drawing without exactly one run layer, an empty run key, a `run-*` keyframes that animates nothing, and CSS it can't read: a backslash (an escape), a brace inside a quoted string, unbalanced braces, an `@import`. The runs and their switches show only on screen, with motion allowed and where `:has()` works (so a switch can always stop a run); the check fails when anything but the gate's rules in `motion.css` shows them (setting `all` counts), when one of those rules, `base.css`'s hiding rule or its at-rest fades (`.dwg .hl`, `.dwg .pu`) goes missing or is written differently (they are matched as text), when a drawing leaves its `figure.fig`, when a figure holds more than its one switch or the switch sits outside a `label`, and when a switch or anything that holds it is `disabled`, `hidden` or `inert`. It doesn't check specificity (a rule that outranks the stop rules), a switch hidden or made unclickable by CSS (`display:none`, `visibility`, `opacity`, its size, `pointer-events`), a span's `rect` or `polygon` beyond matching some component (only its bracket and label are held to the 48 units, and not to which component they sit on), the title's fill (the `both` fill above), a `::view-transition-*(root)` animation, or an animated image in a drawing; and a selector it can't narrow (`:not()`, `:is()`, `:where()`, `:has()`, `:scope`, `&`, a bare pseudo-class or attribute test) counts as reaching every element, so such a rule can fail although it leaves the drawings and their sheets alone; a rule inside `@scope (root)` is judged with its root. A bad stop name in a hop, a missing timing value, a timing value or a hop's `wait` that isn't a plain number (`ease`: a keyword or `cubic-bezier()`), a run without hops, hop points that aren't `[x, y]` number pairs, or a drawing name or stop id that isn't lowercase letters and digits fails the build.
- The projects page's design is owner-approved and must not change: edit its text in `content/projects.md`, and leave `layouts/projects.html`, the drawing partials and their CSS alone unless the owner asks for a redesign. The drawings' runs are the approved exception (2026-11-17): the run layers, `layouts/_partials/run.html`, `layouts/_partials/runbar.html`, `data/runs.toml`, and their CSS (the run and control rules in `base.css`, the run block in `motion.css`).

## Deployment

`.github/workflows/hugo.yml`: push to `main` → checkout → install Hugo → `python3 scripts/check-site.py` with `PAGES_BASE_URL` set to the Pages address (a failing check stops the deploy, also when that address is not `https://manuelschuelein.de`) → `hugo --gc --minify --baseURL <the Pages address>/` → deploy to GitHub Pages at `https://manuelschuelein.de`. There is no theme checkout.
