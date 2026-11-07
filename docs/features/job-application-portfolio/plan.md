# Job application portfolio Implementation Plan

<!-- glance -->
```
Plan: Job application portfolio · 7 tasks · ~1075 lines · 33 files
 1  [1 Build check script]
 2  [2 Own layouts, home page,… ←1]
 3  [3 Path and now pages ←2]
 4  [4 Work page ←3]
 5  [5 Favicons and manifest i… ←4]  [6 Update CLAUDE.md ←4]
 6  [7 Final verification ←5,6]

#  does                                                          files  adds                            size
1  Adds `scripts/check-site.py`, which builds the site as CI d…  1      `scripts/check-site.py`         ~110
2  Removes the hugo-coder submodule with its deploy and Depend…  18     own base layout, CSS pipeline…  ~470
3  Adds the path and now pages from study 10a: one column of r…  4      path page, now page             ~130
4  Adds the work page with the three project drawings, copied …  5      work page, three drawing part…  ~300
5  Regenerates the favicon set and `site.webmanifest` in the p…  4      palette favicons                ~25
6  Makes `CLAUDE.md` describe the own-layout site, so the next…  1      current CLAUDE.md               ~40
7  Measures the built site against the spec's numbers and the …  0      nothing (a measurement report…  ~0
```
<!-- /glance -->

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the hugo-coder homepage with a four-page site (home, work, path, now) that is built from its own Hugo layouts, follows the approved study-11 design and gives each page its own search metadata.

**Architecture:** Hugo joins, minifies and fingerprints the plain CSS files in `assets/css/`; the studies' CSS and SVG drawings move over unchanged. Layouts hold structure only. Text lives in `content/*.md` front matter, the navigation lives in `[[menu.main]]`, and one head partial writes every page's metadata. A stdlib Python script (`scripts/check-site.py`) builds the site as CI does and checks the output; browser measurements cover what HTML checks cannot.

**Tech Stack:** Hugo 0.166.0 extended (nix dev shell and CI), plain CSS, Python 3 standard library for the check script, Pillow for `scripts/generate-favicons.py`. No JavaScript ships.

**Spec:** [spec.md](spec.md). Design reference: `mockups/study-11/` (`index.html`, `work.html`, `path.html`, `now.html`, `style.css`, `path.css`, `pfp.png`; `study.js` is not part of the product). Prior art: [prior-art.md](prior-art.md).

## Global Constraints

These constraints are copied from the spec, without its evidence labels (measured, verified, inferred). Every task's requirements include them.

- R1. The site has four pages at `/`, `/work/`, `/path/` and `/now/`, each rendered from `content/` and `layouts/`. They share one top bar and one footer, and the current page's item carries `aria-current`. The top bar and the home page's links come from `[[menu.main]]`.
- R2. The home page fits one screen without a scrollbar from 768 px wide and 640 px high. Below that size it scrolls, as `style.css` documents. On phones it scrolls.
- R3. No page overflows horizontally at any width from 320 to 2560 px.
- R4. Text contrast is at least 4.5:1. Reading text on the path and now pages is 15 px or larger. The smallest text in the work drawings is 10.2 px from 360 px wide and 8.8 px at 320 px: a known shortfall below 360 px.
- R5. No request leaves the site: fonts are self-hosted (`static/fonts`), and there is no CDN, no analytics and no embeds. No JavaScript ships.
- R6. Search: each page has its own `<title>` and meta description, set in its front matter; `<html lang="en">`; one canonical URL per page; `sitemap.xml` and the existing `robots.txt`; Open Graph and Twitter tags; descriptive link text; alt text on the picture. The `keywords` parameter goes. Inspect the generated HTML before adding any tag by hand, so that none is doubled.
- R7. The text the owner will edit (path steps, now rows, hobbies, home introduction, project descriptions) lives in `content/` or front matter; the layouts and the SVG partials hold structure only. The work drawings keep their wide and upright versions.
- R8. Build and deploy stay the same in kind: the GitHub Pages workflow builds with Hugo 0.166.0 and `--minify`. The workflow's submodule checkout and the Dependabot `gitsubmodule` entry are removed. `CLAUDE.md` is updated after the work, because it still describes the theme.
- R9. Nothing is committed or pushed without the owner asking. (An approved plan's commit steps below are that request for local commits; nothing is ever pushed.)
- Seam, accent colour: resolved in the CSS token file (one `--accent` line, palette A pink or B red); never seen by templates or content.
- Seam, profile picture: resolved in `params.avatarurl` and one file under `static/images/`; never seen by any template except the home page's.
- Seam, navigation: resolved in `[[menu.main]]` in `hugo.toml` (name, weight, and a description for the home page's links); never seen by the page templates, which do not list their siblings.
- Seam, page text: resolved in `content/*.md` and front matter; never seen by the layouts or the SVG partials.
- Seam, per-page search metadata (title, description, canonical, sharing preview): resolved in one head partial from front matter, with site defaults; never seen by the page templates.
- Seam, fonts: resolved in the CSS font file, with the files in `static/fonts`; no page references a font URL.
- `home.html` is the one page template that reads the menu, because R1 says the home page's links come from `[[menu.main]]`; the work, path and now templates do not.
- One implementation gets no interface; one caller gets no helper; no option nobody sets.
- The work page keeps its design: its markup, drawings and CSS are copied from `mockups/study-11/work.html` and `style.css`, not redrawn.
- Palette A: `--bg:#1A1626; --fg:#E6DCF7; --muted:#BDB4DE; --quiet:#9A90C2; --line:#4B4370; --accent:#F08BB4`. The font is IBM Plex Mono only.
- Commits: one sentence, no co-author lines, `git add -- <paths>`, never `git add -A`, never stage `flake.lock`, never push. `CLAUDE.md` and `hugo.toml` already carry uncommitted owner edits; Tasks 2 and 6 rewrite those files, so their commits include those edits.
- CSS is plain CSS, not SCSS. Measured in a scratch site: Hugo's LibSass fails on the studies' CSS (`Incompatible units: 'px' and 'vw'`), while `resources.Concat | minify | fingerprint` keeps `max(72px,min(12.4vw,215px,calc(52svh - 232px)))` intact.
- Hugo behaviors and tool facts this plan relies on:
  - Measured in a scratch site (0.166.0): a `[[menu.main]]` entry whose `pageRef` page does not exist builds without a warning and renders `href=""`; a `url` starting with `/` gets the base path prefix; `{{ template "_internal/opengraph.html" . }}` and `{{ template "_internal/twitter_cards.html" . }}` emit tags from `.Description`; the default build also writes taxonomy pages and `index.xml`, so the config sets `disableKinds = ["taxonomy","term","RSS"]`.
  - Reported by a reviewer, not re-run: `--minify` rewrites SVG path data (`M200 104H144` becomes `M2e2 104H144`). The markup comparison therefore runs on unminified builds, and the shipped minified build is checked by geometry (Task 7, step 5).
  - Measured: `hugo --panicOnWarning` exists in 0.166.0; Pillow 12.3.0 in the dev shell loads `static/fonts/ibm-plex-mono-latin-700-normal.woff2`; `/usr/share/fonts` does not exist on the dev machine.

## Review Focus

These are the classes of input the tests do not already cover, the most likely first. The test that pins each one sits in the task that owns it.

1. **Owner edits that change a content shape:** a path step with no `details`, a now row with two paragraphs, a project with a long stack list, text containing `&`, `'` or `ü`. Expected: no empty element, text escaped, nothing breaks. Pinned in Task 3 (step 4) and Task 4 (step 5).
2. **Short windows:** 1440×600 and 768×639. Expected: the home page scrolls, nothing is clipped, and the links stay reachable. Pinned in Task 2 (step 5) for the home page and in Task 7 for all pages.
3. **Windows wider than 1892 px up to 2560 px** (never measured): no horizontal overflow, the name stays capped, the drawings stay capped. Pinned in Task 2 (step 5), Task 4 (step 4) and Task 7.
4. **A hard-coded host:** the site is a root user site, so `static/robots.txt` and the root-relative `/icons/`, `/fonts/` and `/images/` paths assume the root. Expected: no layout or content file contains the site's host name, so canonical, sitemap and sharing URLs follow `--baseURL`. Pinned in Task 1 (check `seams`). If a custom domain is added later, `robots.txt`'s Sitemap line has to be changed by hand.
5. **Windows narrower than 360 px:** no overflow, and the upright drawings are in use; the 8.8 px text at 320 px stays the known shortfall. Pinned in Task 2 (step 5), Task 4 (step 4) and Task 7.

## Test seams

1. `scripts/check-site.py` against the built HTML (Task 1; the pages arrive in Tasks 2 to 4, and the script passes from Task 4 on).
2. A throwaway markup comparison of each built page's `<main>` against its study-11 counterpart (Tasks 2 to 4; a script in the scratchpad, not committed).
3. Browser measurements of the built pages against the spec's numbers (Task 7).
4. The CI build command with `--minify` (Task 7).

---

### Task 1: Build check script

**Does:** Adds `scripts/check-site.py`, which builds the site as CI does and fails when a page, tag, link or seam rule is wrong. It is written first and must fail on the current theme site.
**Depends on:** none
**Adds:** `scripts/check-site.py`
**Size:** ~110

**Files:**
- Create: `scripts/check-site.py`

**Interfaces:**
- Produces: `python3 scripts/check-site.py`, which takes no arguments. It builds with `hugo -s <repo root, found from __file__> --minify --panicOnWarning --baseURL https://deadmade.github.io/ -d <temp dir>`, so it works from any directory. It prints one `PASS <id> <page>` or `FAIL <id> <page>: <reason>` line per check and page, removes its temp dir, and exits 1 on any FAIL. It uses the Python standard library only (`html.parser`, `xml.etree`, `subprocess`, `tempfile`).

The checks, by id and assertion, run over the four pages `/`, `/work/`, `/path/`, `/now/` unless a row states otherwise:

| id | assertion |
| --- | --- |
| `build` | hugo exits 0 (`--panicOnWarning` turns any WARN into a failure) |
| `files` | the `.html` files in the output are exactly `index.html`, `work/index.html`, `path/index.html`, `now/index.html`, `404.html` |
| `head` | `<html lang="en">`; exactly one non-empty `<title>` inside `<head>` (the work page's drawings carry six more `<title>` elements, which are not counted) and one non-empty `meta[name=description]` per page; titles unique; descriptions unique; exactly one `link[rel=canonical]` equal to `https://deadmade.github.io` plus the page's path; no `meta[name=keywords]` |
| `social` | `og:title`, `og:description`, `og:url` and `twitter:card` each appear exactly once; no `og:image`, no `twitter:image` |
| `links` | no `<script` and no `.woff2` text in any page; every `src` and every `<link href>` is site-relative or starts with `https://deadmade.github.io/` (the canonical link is absolute); the built CSS has no `url()` or `@import` to another host; every site-relative `href`/`src` in a page and every `url()` in the CSS is non-empty and names a file in the output (a trailing `/` means its `index.html`); `<a href>` may leave the site |
| `nav` | the links in `header.bar nav` read `work`, `path`, `now`, `github`, `linkedin`, `mail` in that order; exactly one `aria-current="page"` per page, on the link whose path is the page's (on `/` the `deadmade` mark); the home page has three `ul.go a` to `/work/`, `/path/`, `/now/` |
| `a11y` | every `<img>` has non-empty `alt`; every `<a>` has text or `aria-label` |
| `sitemap` | `sitemap.xml` lists exactly the four URLs under `https://deadmade.github.io`; `robots.txt` contains `Sitemap: https://deadmade.github.io/sitemap.xml` |
| `seams` | `--accent:` is declared once in the built CSS; `F08BB4` and `FF544A` (any case) appear in no file under `layouts/`, `content/` or `hugo.toml`; `deadmade.github.io` appears in no file under `layouts/` or `content/` |

Until all four pages exist (after Task 4), two kinds of FAIL line are expected and are not defects: any line naming a page that is not built yet, and the checks `files`, `sitemap`, `links` and `nav` (the menu renders `href=""` for a page that does not exist). Any other FAIL is a defect. Tasks 2 to 4 refer to this note.

- [ ] **Step 1: Write `scripts/check-site.py`** with the checks above; one function per row of the table, a `main() -> int` that runs them and returns the exit code.
- [ ] **Step 2: Run it against the current theme site.** Run: `python3 scripts/check-site.py`. Expected: exit 1, with FAIL lines at least for `files` (no work, path or now page) and `links` (the theme ships JavaScript). Read the other FAIL lines and confirm each names a real defect of the theme site; a check that fails for a reason of its own (a parse error, a wrong selector) is fixed now.
- [ ] **Step 3: Commit.**

```bash
git add -- scripts/check-site.py
git commit -m "Add a build check for the site's pages, metadata and links."
```

---

### Task 2: Own layouts, home page, 404 page, theme removed

**Does:** Removes the hugo-coder submodule with its deploy and Dependabot entries, and adds the base layout (head, bar and footer), the CSS pipeline, the config, and the home and 404 pages.
**Depends on:** Task 1
**Adds:** own base layout, CSS pipeline, home page
**Size:** ~470

**Files:**
- Modify: `hugo.toml` (rewritten)
- Modify: `.github/workflows/hugo.yml` (delete `submodules: recursive`; keep `fetch-depth: 0`)
- Modify: `.github/dependabot.yml` (delete the `gitsubmodule` block and fix the file's header comment; keep `github-actions`)
- Remove (`git rm`): `.gitmodules`
- Remove (`git rm`): `themes/hugo-coder`
- Remove (`git rm`): `assets/scss/custom.scss`
- Remove (`git rm`): `assets/scss/_fonts.scss`
- Remove (`git rm`): `static/images/avatar.jpg`
- Create: `assets/css/tokens.css`
- Create: `assets/css/fonts.css`
- Create: `assets/css/base.css`
- Create: `assets/css/path.css` (copy of `study-11/path.css`, comment header kept; every rule is scoped by `body.path`, so it is inert on other pages)
- Create: `layouts/baseof.html`
- Create: `layouts/_partials/head.html`
- Create: `layouts/home.html`
- Create: `layouts/404.html`
- Create: `static/images/pfp.png`
- Rewrite: `content/_index.md`

**Interfaces:**
- Produces, `hugo.toml`: `title = "Manuel Schülein"`, `baseURL = "https://deadmade.github.io/"`, `locale = "en-US"`, `DefaultContentLanguage = "en"`, `disableKinds = ["taxonomy","term","RSS"]`; `[params]` `role = "Backend developer"`, `handle = "deadmade"`, `description` (site default, one sentence), `avatarurl = "/images/pfp.png"`, `avataralt`; six `[[menu.main]]` entries in this order and weight (10 to 60): `work`, `path`, `now` with `pageRef = "/work"` etc. and `[menu.main.params] description`, then `github` (`https://github.com/deadmade`), `linkedin` (`https://www.linkedin.com/in/manuel-sch%C3%BClein-408421247/`), `mail` (`mailto:info@manuelschuelein.de`) with `url`. Descriptions: work "three projects, one built alone", path "apprenticeship, studies, work", now "work, learning, priorities". No other keys: drop `theme`, `keywords`, `colorScheme`, `social`, `faviconSVG` and the other icon keys, `since`, `markup`, `pagination`, `imageProcessing`, `enableEmoji`, `hasCJKLanguage`, `customSCSS`.
- Produces, front matter on every content page: `title` (the full `<title>` and `og:title` text), `description`, and `layout` for work, path and now. Titles: `Manuel Schülein — Backend developer`, `Work — Manuel Schülein`, `Path — Manuel Schülein`, `Now — Manuel Schülein`. Descriptions (provisional, the owner edits them with the text):
  - home: `Manuel Schülein, backend developer from Bavaria, Germany. APIs, business systems and developer tools; C# and .NET at work.`
  - work: `Three projects drawn as architecture diagrams: fangtype, a VS Code tool for Python type annotations, and the team builds RustLogger and IsoPrüfi.`
  - path: `From apprenticeship to dual study to a full-time job as Business Solution Developer at 4SELLERS: Manuel Schülein's path, toolkit and languages.`
  - now: `What Manuel Schülein is working on, learning and prioritising at the moment.`
- Produces, `content/_index.md` front matter: `title`, `description`, `lede` (the introduction, copied from `study-11/index.html`).
- Produces, `layouts/baseof.html`: `<html lang="{{ site.Language.Lang }}">`, `{{ partial "head.html" . }}`, `<body{{ block "bodyclass" . }}{{ end }}>`, then the bar, `{{ block "main" . }}` and the footer, written inline (each has one caller). A page layout defines `bodyclass` as ` class="home"` (home) or ` class="path"` (path, now); the work page defines none. The bar is `header.bar` as in the studies: the mark links to `/`, shows `site.Params.handle` and carries `aria-current="page"` on the home page; the nav lists `site.Menus.main` and sets each item's `aria-current="page"` from `$.IsMenuCurrent "main" .`. The footer is `footer.plain > div.foot` with two spans: `site.Title` and `lower site.Params.role` joined by ` · `, and `github.com/` plus `site.Params.handle`; the only literals are the ` · ` and `github.com/`.
- Produces, `head.html`: charset, viewport, `<title>{{ .Title }}</title>`, the description (page's, else `site.Params.description`), `<link rel="canonical" href="{{ .Permalink }}">`, the two `_internal` social templates, the icon links to `/icons/` (`favicon.svg`, `favicon-32x32.png`, `favicon-16x16.png`, `apple-touch-icon.png`, `site.webmanifest`; no `mask-icon`, whose `color` would be a second copy of the accent), and `<link rel="stylesheet">` of `resources.Concat "css/main.css"` over `tokens.css`, `fonts.css`, `base.css`, `path.css`, piped to `minify | fingerprint`.
- Produces, `home.html`: markup of `study-11/index.html` `<main>`; the name's two `<span>`s from splitting `site.Title`; the role from `site.Params.role`; the list from the menu entries that have `.Params.description`.
- Produces, `tokens.css`: `:root{` with one custom property per line, `--accent:#F08BB4` on its own line, and a comment giving palette B (`#FF544A`). `fonts.css`: the three `@font-face` blocks of `style.css` with `src:url(/fonts/ibm-plex-mono-latin-<weight>-normal.woff2)`. `base.css`: `style.css` from the `*{box-sizing}` rule on, keeping `--pad` in its own `:root{--pad:clamp(20px,5vw,80px)}` and leaving out the three `@font-face` blocks, the `:root[data-palette="b"]` rule, the `:root` colour line and every `.chip` rule (two lines, plus one line inside the `@media(max-width:860px)` block).

- [ ] **Step 1: Add the markup comparison script** `compare-main.py` in the scratchpad (not the repo): `python3 compare-main.py <built.html> <study.html>` parses both `<main>` subtrees with `html.parser`, drops comments, collapses whitespace, ignores end tags, and compares the sequence of start tags with their attributes and the text nodes. The values of `href`, `src`, and of `id`/`aria-labelledby` on `h2` and `section` are ignored (their presence is compared). It prints the first difference and exits 1.
- [ ] **Step 2: Remove the theme and the deploy entries.** Run `git rm -- themes/hugo-coder .gitmodules assets/scss/custom.scss assets/scss/_fonts.scss static/images/avatar.jpg`, then edit the workflow and `dependabot.yml` as listed. Expected: `git submodule status` prints nothing; `grep -n "submodule" .github -r` matches nothing.
- [ ] **Step 3: Write the config, CSS, layouts, `content/_index.md` and `static/images/pfp.png`** (copy of `mockups/study-11/pfp.png`) to the interfaces above. `<img>` keeps `width="460" height="460"` and takes `src` from `avatarurl` and `alt` from `avataralt` (`Profile picture: a hooded figure with a wide grin and one glowing red eye`). `404.html` extends `baseof.html` by defining only `main` (so it gets the bar and footer from there): an `<h1>` `404`, one sentence and a link to `/` with descriptive text.
- [ ] **Step 4: Check the build.** Run: `hugo -d <fresh directory in the scratchpad>`, then `python3 compare-main.py <that directory>/index.html docs/features/job-application-portfolio/mockups/study-11/index.html`. Expected: the build prints no WARN or ERROR; the comparison exits 0. Run `python3 scripts/check-site.py`. Expected: only the FAIL lines that Task 1's note lists as expected while three pages are missing.
- [ ] **Step 5: Browser check of the home page (Review Focus 2, 3, 5).** Assemble a scratch directory with the build at its root and a copy of `mockups/study-11/` at `study/`, and serve it with `python3 -m http.server` (one origin, so a measuring page can read a built page and its study counterpart in iframes; a `file://` page or a second port blocks that). In a browser tool, load `/` in iframes of 768×640, 1440×800 and 1920×1080: expected `scrollHeight <= clientHeight`. At 1440×600 and 768×639 the page may scroll; the three links stay reachable and nothing is clipped. At 320, 390 and 2560 px wide: expected `scrollWidth <= width`. If no browser tool is available, say so in the report: the step then stays open for Task 7 and for the owner.
- [ ] **Step 6: Commit.**

```bash
git add -- hugo.toml .github/workflows/hugo.yml .github/dependabot.yml assets/css layouts content/_index.md static/images/pfp.png
git commit -m "Replace the hugo-coder theme with own layouts and styles, and build the home and 404 pages from them."
```
(The `git rm` changes are already staged. Do not stage `flake.lock`.)

---

### Task 3: Path and now pages

**Does:** Adds the path and now pages from study 10a: one column of rows, text in front matter.
**Depends on:** Task 2
**Adds:** path page, now page
**Size:** ~130

**Files:**
- Create: `content/path.md`
- Create: `content/now.md`
- Create: `layouts/path.html`
- Create: `layouts/now.html`

**Interfaces:**
- Consumes: `baseof.html` blocks `bodyclass` and `main` (Task 2).
- Produces, `content/path.md` front matter (all text copied from `study-11/path.html`): `layout: path`; `steps:` a list, newest first, each `years`, `title`, optional `details:` a list of strings (one `<p>` each); the first step is the current one and its `li` gets the class `now`; `toolkit:` with `main` (`C# · .NET · SQL`) and `others` (a list of nine strings); `languages` (string); `hobbies` (string, with NixOS).
- Produces, `content/now.md` front matter (text from `study-11/now.html`): `layout: now`; `rows:` a list of `label` and `text` (a list of strings, one `<p>` each), in the order at work, learning, priorities; `updated: November 2025`.
- Produces, `layouts/path.html` and `layouts/now.html`: the markup of the studies' `<main>`; headings `path` and `now` and the row labels `toolkit`, `languages`, `hobbies`, `updated` are literal; the first row of `now` has no `p-sec` class; a now row with one string renders a bare `<p>` and a row with several renders a `<div>` of `<p>`s, as the study does; an empty `details` produces no `<p>`; the section ids come from the row index.

- [ ] **Step 1: Write the content and the layouts.**
- [ ] **Step 2: Compare.** Build into a fresh directory, then run `compare-main.py` for `path/index.html` against `study-11/path.html` and `now/index.html` against `study-11/now.html`. Expected: both exit 0.
- [ ] **Step 3: Run `python3 scripts/check-site.py`.** Expected: `/path/` and `/now/` pass every per-page check; the only FAIL lines are those Task 1's note lists as expected while the work page is missing.
- [ ] **Step 4: Pin Review Focus 1.** Copy `content/` to a scratch directory, change the copy (remove one step's `details`; give a now row two strings; put `Q&A 'x' ü` in `hobbies`), and run `hugo --contentDir <copy> -d <fresh dir>`. Expected: no empty `<p>`, `&` becomes `&amp;` (an unminified build; a minified one prints a bare `&` where that is unambiguous), the build prints no WARN.
- [ ] **Step 5: Commit.**

```bash
git add -- content/path.md content/now.md layouts/path.html layouts/now.html
git commit -m "Add the path and now pages."
```

---

### Task 4: Work page

**Does:** Adds the work page with the three project drawings, copied unchanged from study 11.
**Depends on:** Task 3
**Adds:** work page, three drawing partials
**Size:** ~300

**Files:**
- Create: `content/work.md`
- Create: `layouts/work.html`
- Create: `layouts/_partials/drawing-fangtype.html`
- Create: `layouts/_partials/drawing-rustlogger.html`
- Create: `layouts/_partials/drawing-isopruefi.html`

**Interfaces:**
- Consumes: `baseof.html` block `main`, no `bodyclass` (Task 2).
- Produces, `content/work.md` front matter: `layout: work`; `intro` (the sentence under the heading, from `study-11/work.html`); `projects:` three items in the order fangtype, RustLogger, IsoPrüfi, each `name`, `tag`, `drawing` (`fangtype`, `rustlogger`, `isopruefi`), `summary` (the description that the drawing's two `<title>` elements carry; copied from them), `what`, `stack` (list), `source` (the repository URL). Text is copied from `study-11/work.html`.
- Produces, each `drawing-<key>.html`: it takes the project (a map from `projects`) as its context. Its content is the `<figure class="fig">…</figure>` of that project from `study-11/work.html` byte for byte (both SVGs and the legend with its swatch SVGs, including the "not to scale" caption), except that the body of each of the two `<title id="…">` elements is `{{ .summary }}` (the wide and upright texts are identical; measured). Labels inside the drawings stay in the partials: the drawing is the structure.
- Produces, `layouts/work.html`: `<main class="page">` with the `head` block (`<h1>work</h1>` and `intro`); the first project as `article.sheet.lead` (corner marks, `header.sh` with the `tri` mark, `div.body`); the rest inside `div.sheet.pair` as `article.view` (`div.vb`); each project's figure from `partial (printf "drawing-%s.html" .drawing) .` and its `aside.tb` with the cells `what`, `stack`, `source`; the source link text is `source` without its `https://github.com/` prefix (`strings.TrimPrefix`).

- [ ] **Step 1: Cut the three partials** from `study-11/work.html` with a short script kept in the scratchpad, not the repo (the figure ranges are lines 39–100, 120–213 and 228–288), replace the six `<title>` bodies by `{{ .summary }}`, move those texts into `content/work.md`, and write the layout.
- [ ] **Step 2: Compare.** Build into a fresh directory and run `compare-main.py` for `work/index.html` against `study-11/work.html`. Expected: exit 0, which includes every SVG node and the six `<title>` texts.
- [ ] **Step 3: Run `python3 scripts/check-site.py`.** Expected: exit 0, every check passes (the drawings use classes, not hex colours: the study has none; verified by grep).
- [ ] **Step 4: Browser check of the work page (Review Focus 3, 5).** Serve as in Task 2 step 5. Load `/work/` in iframes at 320, 360, 390 and 2560 px wide: expected `scrollWidth <= width`; at 360 px and below the upright drawings (`.dwg.v`) are displayed and the wide ones (`.dwg.h`) are not.
- [ ] **Step 5: Pin Review Focus 1.** On a content copy (as in Task 3 step 4) give one project nine stack items and a `what` and a `summary` containing `&` and `'`. Expected: the build prints no WARN and the text is escaped (`&amp;` in an unminified build).
- [ ] **Step 6: Commit.**

```bash
git add -- content/work.md layouts/work.html layouts/_partials/drawing-fangtype.html layouts/_partials/drawing-rustlogger.html layouts/_partials/drawing-isopruefi.html
git commit -m "Add the work page with the three project drawings."
```

---

### Task 5: Favicons and manifest in the site palette

**Does:** Regenerates the favicon set and `site.webmanifest` in the palette, drawing the letter with the site's own font, and drops two icon files that nothing links.
**Depends on:** Task 4
**Adds:** palette favicons
**Size:** ~25

**Files:**
- Modify: `scripts/generate-favicons.py`
- Modify: `static/icons/` (the eight files the script writes: `favicon-16x16.png`, `favicon-32x32.png`, `android-chrome-192x192.png`, `android-chrome-512x512.png`, `apple-touch-icon.png`, `favicon.ico`, `favicon.svg`, `site.webmanifest`)
- Remove (`git rm`): `static/icons/browserconfig.xml`
- Remove (`git rm`): `static/icons/safari-pinned-tab.svg` (the head partial links neither)

**Interfaces:**
- Produces: `ACCENT_COLOR = "#F08BB4"` (the disc) and `TEXT_COLOR = "#1A1626"` (the letter); `theme_color` and `background_color` in the manifest both `#1A1626`. The letter is drawn with `ImageFont.truetype("static/fonts/ibm-plex-mono-latin-700-normal.woff2", int(size * 0.7))` (path relative to the repo root, like `OUTPUT_DIR`), with no system-font lookup and no fallback chain; the SVG favicon keeps `font-family="monospace"` as it is. `create_safari_pinned_tab`, `create_browserconfig` and their calls in `main` are deleted. The script's name, usage and `INITIALS = "M"` stay. The accent hex stays a constant in this script, outside the accent seam, which covers templates and content: a new accent also means editing `ACCENT_COLOR` and rerunning the script (Task 6 documents this).

- [ ] **Step 1: Edit the script** as above: the two constants, the font line, the two `theme_color`/`background_color` strings, and delete the two functions and their calls. Then `git rm -- static/icons/browserconfig.xml static/icons/safari-pinned-tab.svg`.
- [ ] **Step 2: Run it in the dev shell.** Run: `python3 scripts/generate-favicons.py`. Expected: ends with `[SUCCESS]`; `git status --short` shows, besides the entries already in the tree before this task (`M flake.lock`, `?? docs/`, `?? .superpowers/`, and `M CLAUDE.md` if Task 6 has not committed yet), only `scripts/generate-favicons.py` and files under `static/icons/`.
- [ ] **Step 3: Look at the result.** Open `static/icons/android-chrome-512x512.png` and confirm the letter M fills roughly half the pink disc (measured with this font at size 358: the inked letter is about 187 px wide in a disc of about 410 px). If it is tiny, the font did not load: stop and report it instead of committing.
- [ ] **Step 4: Commit.**

```bash
git add -- scripts/generate-favicons.py static/icons
git commit -m "Regenerate the favicons and manifest in the site palette."
```

---

### Task 6: Update CLAUDE.md

**Does:** Makes `CLAUDE.md` describe the own-layout site, so the next session does not look for the theme.
**Depends on:** Task 4
**Adds:** current CLAUDE.md
**Size:** ~40

**Files:**
- Modify: `CLAUDE.md` (it already carries uncommitted owner edits, which this commit includes)

**Interfaces:**
- Produces: these sections, updated:
  - project overview (four pages);
  - stack (Hugo 0.166.0 extended, no theme, no Sass, Python for the check and favicon scripts);
  - commands (`hugo server -D`, the CI build command, `python3 scripts/check-site.py`, `python3 scripts/generate-favicons.py`; delete `hugo new blog/…`);
  - structure (`assets/css/`, `layouts/`, `content/{_index,work,path,now}.md`, `scripts/`);
  - configuration (`[[menu.main]]` drives the bar and the home links, `params.role`, `handle`, `description`, `avatarurl`, `avataralt`);
  - fonts (`assets/css/fonts.css`);
  - a "gotchas" section replacing the theme one:
    - plain CSS because LibSass rejects `min()`/`max()` with mixed units;
    - the accent is one line in `assets/css/tokens.css`, but the favicon script keeps its own `ACCENT_COLOR`, so a new accent also means editing that and rerunning the script;
    - `static/robots.txt` hard-codes the host in its Sitemap line (change it if a custom domain is added);
    - no JavaScript and no external requests;
    - `pageRef` to a missing page renders `href=""`;
    - work-page text, including each drawing's `summary`, lives in `content/work.md`, and the drawing partials hold only shapes and labels;
  - deployment (no theme checkout, no CI check step: `scripts/check-site.py` is run by hand).

- [ ] **Step 1: Edit `CLAUDE.md`** to the list above.
- [ ] **Step 2: Check it.** Run: `grep -n -i "hugo-coder\|submodule\|scss\|toCSS\|customSCSS\|colorscheme" CLAUDE.md`. Expected: no output. Every path it names exists (`ls` each one) and `python3 scripts/check-site.py` runs; do not run `scripts/generate-favicons.py` here, which belongs to Task 5.
- [ ] **Step 3: Commit.**

```bash
git add -- CLAUDE.md
git commit -m "Update CLAUDE.md for the own-layout site."
```

---

### Task 7: Final verification

**Does:** Measures the built site against the spec's numbers and the CI command, and finds anything the HTML checks cannot see. It changes no file unless a measurement fails.
**Depends on:** Task 5 and Task 6
**Adds:** nothing (a measurement report in flow.md)
**Size:** ~0

**Files:**
None expected. If a measurement fails, the fix goes into the owning task's file and is committed with its own one-sentence message.

**Interfaces:**
- Consumes: the whole site.

- [ ] **Step 1: Build as CI does.** Run: `hugo --gc --minify --baseURL "https://deadmade.github.io/" -d <fresh dir>`. Expected: exit 0, no WARN. Serve it as in Task 2 step 5 (the build at the root, a copy of `mockups/study-11/` at `study/`, one origin).
- [ ] **Step 2: Overflow (R3).** In a browser, load each page and `404` in iframes at 320, 360, 390, 768, 1024, 1440, 1892 and 2560 px wide. Expected: `scrollWidth <= width` everywhere.
- [ ] **Step 3: Home fit (R2).** Iframes at 768×640, 1024×700, 1440×800, 1920×1080. Expected: `scrollHeight <= clientHeight`. At 1440×600 and 768×639 the page may scroll; confirm the footer is reachable and no link is covered (Review Focus 2).
- [ ] **Step 4: Text (R4).** Contrast of `--fg`, `--muted`, `--quiet` and `--accent` against `--bg`, computed from the hex values: each at least 4.5. The smallest computed font size of text in `main` on path and now at 360, 390 and 1440 px: at least 15 px. The smallest effective text of `svg.dwg text` in the work drawings (SVG `font-size` times rendered width over viewBox width): 10.2 px at 360 and 8.8 px at 320, equal to study-11 at the same widths (Review Focus 5). Report any `.legend text` separately: `style.css` fixes it at 9 px at every width, a value the spec's figure did not include.
- [ ] **Step 5: Geometry against the design.** For `main` descendants of each page, compare bounding boxes with the study-11 page at 390, 768 and 1440 px: within 1 px. Report any element that differs. This step is the only check of the minified build against the design, because Hugo's minifier rewrites SVG path data.
- [ ] **Step 6: The accent is one line.** Change `--accent` in `assets/css/tokens.css` to `#FF544A`, build into a fresh directory, and compare with the previous build. Expected: the stylesheet differs, and each HTML page differs only in the stylesheet's fingerprinted file name. Restore the line; `git diff -- assets` prints nothing.
- [ ] **Step 7: Repository state.** Run `git status --short` and `git log --oneline -7`. Expected: six new commits; `flake.lock` modified and unstaged; `docs/` and `.superpowers/` untracked; nothing pushed.
- [ ] **Step 8: Report** each measurement with its value, and end with a "Not checked" line (for example: other browsers, screen readers, the live GitHub Pages deploy, real devices).
