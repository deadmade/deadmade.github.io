# SEO Implementation Plan

<!-- glance -->
```
Plan: SEO · 6 tasks · ~257 lines · 17 files
 1  [1 One host and a generate…]
 2  [2 Dates from Git ←1]
 3  [3 Share-image details and… ←2]
 4  [4 One JSON-LD block on th… ←2,3]
 5  [5 Decide's picks in the ch… ←4]
 6  [6 The CLAUDE.md corrections ←5]

#  does                                                          files  adds                            size
1  Makes every URL the build writes use `https://manuelschuele…  6      `layouts/robots.txt`; config …  ~55
2  Gives every page in the sitemap the date of its content fil…  5      config key `enableGitInfo`; f…  ~40
3  Adds the share image's width, height and alt text and a 192…  2      function `png_size(path)` and…  ~50
4  Puts the site name and the owner's profile into one JSON-LD…  4      `[params] alternatename`; `Pa…  ~95
5  Makes the check print a FAIL line, not a traceback, on a lis…  1      the constant `OLD_HOST` in `s…  ~15
6  Says in `CLAUDE.md` that the check fails on a shallow checko…  1      none                            ~2
```
<!-- /glance -->

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `https://manuelschuelein.de` show up and look like its owner in name searches, and give AI agents his facts, through one host, Git dates, share-image details, a search icon and one JSON-LD block on the home page, all pinned by `scripts/check-site.py`.

**Architecture:** Everything is build output: `hugo.toml` holds the host and the owner's facts, Git holds the dates, the image file holds its size, and `layouts/_partials/head.html` writes the tags and the JSON-LD from them. `scripts/check-site.py`, CI's deploy gate, gets each new assertion first (red), then the template or config change turns it green.

**Tech Stack:** Hugo Extended 0.166.0 (CI pin) with Go templates; Python 3 standard library for the check.

**Spec:** [spec.md](spec.md) (Gate 1 approved 2026-11-15; G1 reopened in plan review round 1 for the Pages-address check). Measurements behind this plan (a throwaway build of a scratch clone with Hugo 0.169.0, 2026-11-15): `layouts/robots.txt` with `enableRobotsTXT` writes `Sitemap: https://manuelschuelein.de/sitemap.xml`; `enableGitInfo` gives all four sitemap URLs a `<lastmod>` such as `2026-11-10T15:24:09+01:00`; `images.Config "/static/images/og.png"` gives 1200 and 630, also when Hugo runs from another folder with `-s`; a `dict` printed inside `<script type="application/ld+json">` comes out as JSON, with and without `--minify`; the now page's `.Lastmod.Format "January 2006"` prints `November 2026`, and inside `with $.Lastmod` prints nothing when Git info is off; a content file whose last commit is dated `+00:00` gets `2026-11-15T10:00:00Z` as the JSON-LD's `dateModified` but `2026-11-15T10:00:00+00:00` in the sitemap, so the two are compared as instants, never as strings; regular pages gain `article:modified_time`; no warnings under `--panicOnWarning`. The unchanged repository passes every check (measured, Hugo 0.169.0, Python 3.13).

## Global Constraints

- Site host: resolved in `hugo.toml` `baseURL` (in CI, the Pages address passed as `--baseURL`); never seen by `layouts/`, `content/` or `static/` (robots.txt is rendered from it).
- Owner facts (name, alternate name, role, handle, profiles, picture): resolved in `hugo.toml` (`title`, `[params]`, `[[menu.main]]`); never seen by `content/`, and read but never restated by the structured-data block.
- Page dates: resolved in Git (`enableGitInfo`); never seen by `content/` front matter.
- Share image size: resolved in the image file (`images.Config` at build time); never seen by `hugo.toml` or the layouts as numbers.
- Structured data: resolved in `layouts/_partials/head.html`, on the home page only; never seen by the page layouts.
- One implementation gets no interface; one caller gets no helper; no option nobody sets.
- Stack skill: none (no stack pack matches Hugo templates and standard-library Python; no new page or component).
- `CLAUDE.md` rules hold: no JavaScript and no external requests (the one exception is the home page's `application/ld+json` block, added in Task 4); page text lives in `content/` front matter or `hugo.toml`, not in layouts; `layouts/projects.html`, the drawing partials and their CSS stay untouched; `scripts/check-site.py` stays standard-library Python.
- Scratch work (the Hugo download, the throwaway clones of Review Focus 1, 2 and 3) goes in a folder outside the repository: this session's scratchpad, `C:\Users\manue\AppData\Local\Temp\claude\a27a45fc92e97350\b106f7b8-feca-45f0-8d75-aa86c438e5f8\scratchpad` (`$SCRATCH` below).
- Running the check (Git Bash, repository root): `PATH="$SCRATCH/hugo-0.166.0:$PATH" "/c/Users/manue/AppData/Local/Programs/Python/Python313/python.exe" scripts/check-site.py`. Every run uses CI's Hugo 0.166.0 from Task 1 Step 1; Task 4's last step also runs it with the installed 0.169.0 (`/c/Users/manue/AppData/Local/Microsoft/WinGet/Packages/Hugo.Hugo.Extended_Microsoft.Winget.Source_8wekyb3d8bbwe`) first on PATH. A run passes when it prints no `FAIL` line and exits 0.
- Commits: one sentence, no co-author lines; each commit stages only its task's paths with `git add -- <paths>`.

## Test seams

- `scripts/check-site.py` (the CLI CI runs before deploying; it builds the site with `--minify --panicOnWarning` and reads the output). Catches: a wrong or old host anywhere in the build (in CI also a Pages address other than its own host), a missing or doubled tag, image tags that disagree with the image file, an icon whose file is not the size it claims, a sitemap URL without a date, a now-page date that disagrees with the sitemap, a JSON-LD block that is missing, invalid, doubled, on the wrong page or out of step with the page, and any other `<script`. Misses: how Google actually reads the markup (owner step: URL Inspection), how an AI agent's tools turn the page into text, and anything only a browser shows.

## Review Focus

1. A title holding `"`, `<`, `&` or `</script>`: the JSON-LD stays valid JSON, cannot end its script element, and still equals the page. Pinned in Task 4, Step 7.
2. A second script of any kind, including a second JSON-LD block or one on the 404 page (which is served at every missing URL): the check fails. Pinned in Task 4, Step 8.
3. A content file whose last commit is dated `+00:00` (made on a machine or in an editor set to UTC): the JSON-LD writes its date with `Z`, the sitemap with `+00:00` (measured), and the check still passes. Pinned in Task 4, Step 9.
4. Hugo 0.166.0 in CI versus 0.169.0 installed here: the whole check passes under both. Pinned in Task 4, Step 10.
5. A content file edited but not committed, the owner's normal state while writing: its page keeps the date of its last commit and the check still passes. Pinned in Task 2, Step 7.

---

### Task 1: One host and a generated robots.txt

**Does:** Makes every URL the build writes use `https://manuelschuelein.de`, renders robots.txt from that address and makes the check fail on the old host anywhere.
**Depends on:** none
**Adds:** `layouts/robots.txt`; config key `enableRobotsTXT`; check `host`; environment variable `PAGES_BASE_URL` (set by CI for the check)
**Size:** ~55

**Files:**
- Modify: `scripts/check-site.py`
- Modify: `hugo.toml`
- Create: `layouts/robots.txt`
- Delete: `static/robots.txt`
- Modify: `.github/workflows/hugo.yml`
- Modify: `CLAUDE.md`

**Interfaces:**
- Produces: `BASE = "https://manuelschuelein.de"` in `scripts/check-site.py`, used by every later check.

- [ ] **Step 1: Get CI's Hugo.** In a new folder `$SCRATCH/hugo-0.166.0`, download `https://github.com/gohugoio/hugo/releases/download/v0.166.0/hugo_extended_0.166.0_windows-amd64.zip` and `hugo_0.166.0_checksums.txt` from the same release, check the zip's SHA-256 against its line in the checksums file, and extract `hugo.exe` there. Expected: `hugo.exe version` prints `v0.166.0` and `+extended`. If an asset is missing or the checksum differs, stop and report it.

- [ ] **Step 2: Write the failing checks** in `scripts/check-site.py`:
  - `BASE = "https://manuelschuelein.de"` (line 18).
  - New check `host`, page `-`: one problem per built file whose bytes contain `deadmade.github.io`, worded `old host in <path relative to the output folder>`; one when `hugo.toml`'s `baseURL` (read with `tomllib`) is not `BASE + "/"`, since the check builds with `--baseURL` and would otherwise never see it; and one when the environment variable `PAGES_BASE_URL` is set and, without a trailing `/`, is not `BASE`, worded `Pages address <value> is not <BASE>` (CI sets it to the address the deploy build uses).
  - `sitemap`: also fails on a robots.txt line `Disallow:` with a value after it (spec G6: every crawler stays allowed).
  - `seams`: the host rule covers `static/` as well as `layouts/` and `content/`, and fails on `deadmade.github.io` and on `manuelschuelein.de` in any of those files (today only the first, and not in `static/`). The accent-colour rule keeps its files (`hugo.toml`, `layouts/`, `content/`): `static/icons/favicon.svg:3` holds the accent on purpose, written by `scripts/generate-favicons.py`.
  - The docstring names this plan next to the old one as where the checks are listed.

- [ ] **Step 3: Run the check to verify it fails.** Expected FAIL lines, and no others: `sitemap -` (robots.txt lacks `Sitemap: https://manuelschuelein.de/sitemap.xml`), `host -` (`old host in robots.txt`; `hugo.toml` `baseURL` is `https://deadmade.github.io/`), `seams -` (`site host in static/robots.txt`).

- [ ] **Step 4: Implement.** In `hugo.toml`: `baseURL = "https://manuelschuelein.de/"` and `enableRobotsTXT = true`. Create `layouts/robots.txt` with exactly this text:

  ```text
  # https://www.robotstxt.org/robotstxt.html
  User-agent: *
  Allow: /

  Sitemap: {{ "sitemap.xml" | absURL }}
  ```

  Delete `static/robots.txt` with `git rm`. In `.github/workflows/hugo.yml`, the "Check the site" step (`:62-63`, after "Setup Pages" at `:30-32`) gets `env: PAGES_BASE_URL: ${{ steps.pages.outputs.base_url }}`, the same value the deploy build passes as `--baseURL` (`:70`).

- [ ] **Step 5: Run the check to verify it passes.** Expected: no `FAIL` line, exit 0. Then run it with `PAGES_BASE_URL=https://deadmade.github.io` in front: expected only `FAIL host -` naming that Pages address; and with `PAGES_BASE_URL=https://manuelschuelein.de`: no `FAIL` line.

- [ ] **Step 6: Update `CLAUDE.md`:** the overview says the site is deployed to GitHub Pages at `https://manuelschuelein.de` (a custom domain held in the repository's Pages settings; `deadmade.github.io` redirects there); the CI-build command uses `--baseURL "https://manuelschuelein.de/"`; the structure lists `layouts/robots.txt` (robots.txt template; its Sitemap line comes from `baseURL`) instead of `static/robots.txt`; the gotcha about `static/robots.txt` hard-coding the host is replaced by: the host lives in three places that must agree, `hugo.toml`'s `baseURL` (local builds and `hugo server`), `BASE` in `scripts/check-site.py`, and the custom domain in the repository's Pages settings (CI passes it to the deploy build as `--baseURL` and to the check as `PAGES_BASE_URL`), so a new domain means changing all three; `check-site.py` fails when `baseURL` or, in CI, the Pages address differs from `BASE`, on `deadmade.github.io` anywhere in the build and on either host in `layouts/`, `content/` or `static/`; the Technology Stack's Python line says the check needs Python 3.11+ (`tomllib`); Deployment names the custom domain and the Pages-address check.

- [ ] **Step 7: Commit.** Step 4's `git rm` already staged the deletion of `static/robots.txt`; naming it in `git add` would fail the whole command (`fatal: pathspec … did not match any files`, measured).

  ```bash
  git add -- scripts/check-site.py hugo.toml layouts/robots.txt .github/workflows/hugo.yml CLAUDE.md
  git commit -m "Serve every URL from manuelschuelein.de, render robots.txt from baseURL and fail the check on the old host."
  ```

### Task 2: Dates from Git

**Does:** Gives every page in the sitemap the date of its content file's last commit and shows that month on the now page instead of a typed date.
**Depends on:** Task 1
**Adds:** config key `enableGitInfo`; function `lastmods(out)` in `scripts/check-site.py`; check `dates`
**Size:** ~40

**Files:**
- Modify: `scripts/check-site.py`
- Modify: `hugo.toml`
- Modify: `layouts/now.html`
- Modify: `content/now.md`
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: `BASE` (Task 1).
- Produces: `lastmods(out: Path) -> dict[str, str | None]` in `scripts/check-site.py`: each sitemap `<loc>` mapped to its `<lastmod>` text, or `None` when the URL has none. `check_sitemap` and the `dates` check use it; Task 4 reads `lastmods(out)[BASE + "/"]`.

- [ ] **Step 1: Write the failing checks.**
  - `sitemap`: besides today's URL set and robots line, one problem per URL whose lastmod is missing or does not match `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})$`, worded `no lastmod for <url>` or `lastmod <value> for <url> is not RFC 3339`.
  - New check `dates`, page `/now/`: the built now page contains `updated <Month> <Year>` exactly once, with the English month name and the year of `lastmods(out)[BASE + "/now/"]` (read with `datetime.fromisoformat`); otherwise the problem names both values.

- [ ] **Step 2: Run the check to verify it fails.** Expected FAIL lines, and no others: `sitemap -` (`no lastmod for` each of the four URLs) and `dates /now/` (no lastmod to compare with `updated November 2026`).

- [ ] **Step 3: Implement.** `hugo.toml`: `enableGitInfo = true`. `layouts/now.html`: the first row's tag prints `updated` and `$.Lastmod.Format "January 2006"`, inside `with $.Lastmod`, so a page without a date shows no tag. `content/now.md`: delete the `updated:` line.

- [ ] **Step 4: Run the check to verify it passes.** Expected: no `FAIL` line, exit 0.

- [ ] **Step 5: Update `CLAUDE.md`:** the structure's `content/now.md` line drops "and the updated date" and says the "updated" month is now.md's last commit; a new Configuration line: `enableGitInfo` makes Git the source of page dates (the sitemap's lastmod, the now page's month, `article:modified_time`); a page's date moves only when its content file is committed, and CI checks out with `fetch-depth: 0` for this; every build now needs a Git checkout with its history and `git` on PATH (without `.git`, Hugo stops with `failed to load Git data`).

- [ ] **Step 6: Commit.**

  ```bash
  git add -- scripts/check-site.py hugo.toml layouts/now.html content/now.md CLAUDE.md
  git commit -m "Take page dates from Git for the sitemap and the now page."
  ```

- [ ] **Step 7: Edited, not committed (Review Focus 5).** Change one word in a `text` line of `content/now.md` without committing, run the check, then restore the file with `git checkout -- content/now.md`. Expected: no `FAIL` line, and the now page still shows the month of now.md's last commit.

### Task 3: Share-image details and a search icon

**Does:** Adds the share image's width, height and alt text and a 192 px PNG icon to every page's head, checked against the real image files.
**Depends on:** Task 2 (order only: both edit `scripts/check-site.py`)
**Adds:** function `png_size(path)` and `Page` fields `content`, `name`, `role` in `scripts/check-site.py`; check `icon`
**Size:** ~50

**Files:**
- Modify: `scripts/check-site.py`
- Modify: `layouts/_partials/head.html`

**Interfaces:**
- Consumes: `BASE` (Task 1).
- Produces, in `scripts/check-site.py`: `png_size(path: Path) -> tuple[int, int]` (width and height from a PNG's IHDR; raises `ValueError` on a file without the PNG signature); `Page.content: dict[str, str]` (each meta's `name` or `property` mapped to its `content`); `Page.name` and `Page.role` (the footer's first span split on ` · `: `Manuel Schülein` and `backend developer` today). Task 4 reads `Page.role`.

- [ ] **Step 1: Write the failing checks.**
  - `social`: `want` gains `og:image:width`, `og:image:height`, `og:image:alt` and `twitter:image:alt` (each exactly once); `og:image:width` and `og:image:height` equal `png_size` of the built `OG_IMAGE`; `og:image:alt` and `twitter:image:alt` both equal `f"{p.name}, {p.role}"`, which is `Manuel Schülein, backend developer` today; `og:url` equals `BASE + path`, the canonical (true today, now pinned).
  - New check `icon`, page `/`: every `<link rel="icon" type="image/png">` on the home page has `sizes` `NxN` and `png_size` of the file it names is `(N, N)`, and at least one has N larger than 48 (Google: "larger than 48x48px").
  - A file `png_size` can't read (missing, or without the PNG signature) is a problem of the check that asked, worded `<path> is missing` or `<path> is not a PNG`, never an exception.

- [ ] **Step 2: Run the check to verify it fails.** Expected FAIL lines, and no others: `social` on all four pages (the four new tags appear 0 times) and `icon /`.

- [ ] **Step 3: Implement** in `layouts/_partials/head.html`, after the Twitter template: `og:image:width` and `og:image:height` from `images.Config` on `/static` plus the first entry of `site.Params.images`; `og:image:alt` and `twitter:image:alt` with `printf "%s, %s" site.Title (lower site.Params.role)`. Among the icon links, after the SVG one: `<link rel="icon" href="/icons/android-chrome-192x192.png" type="image/png" sizes="192x192">`. No share-image number is written into the template or config.

- [ ] **Step 4: Run the check to verify it passes.** Expected: no `FAIL` line, exit 0.

- [ ] **Step 5: Commit.**

  ```bash
  git add -- scripts/check-site.py layouts/_partials/head.html
  git commit -m "Add the share image's size and alt text and a 192 px PNG icon, checked against the files."
  ```

### Task 4: One JSON-LD block on the home page

**Does:** Puts the site name and the owner's profile into one JSON-LD block on the home page and makes the check compare it with what the page shows, while still failing on every other script.
**Depends on:** Task 2, Task 3
**Adds:** `[params] alternatename`; `Page` fields `h1`, `scripts`, `ld` and each anchor's `cls` in `scripts/check-site.py`; check `data`
**Size:** ~95

**Files:**
- Modify: `scripts/check-site.py`
- Modify: `hugo.toml`
- Modify: `layouts/_partials/head.html`
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: `BASE` (Task 1); `lastmods(out)` (Task 2); `Page.role` (Task 3).
- Produces: nothing later tasks use.

- [ ] **Step 1: Write the failing checks.**
  - Scripts: `Page` records each `<script>`'s `type` (`scripts`) and the text of each `application/ld+json` one (`ld`). `links` fails a page when a script's type is anything but `application/ld+json`, when the number of `<script` in the raw HTML (case-insensitive) differs from the scripts the parser saw, or when the page holds more JSON-LD blocks than allowed: one on `/`, none on the other pages. `404` fails on any `<script` in `404.html`.
  - New check `data`, page `/`: the block parses with `json.loads`; `@context` is `https://schema.org`; `@graph` holds exactly one `WebSite` and one `ProfilePage` node and nothing else. `WebSite`: `name` = `p.h1` (the text inside the home `<h1>`), `url` = `BASE + "/"`. `ProfilePage`: `url` = `BASE + "/"`, `name` = the page's `<title>`, `dateModified` the same instant as `lastmods(out)[BASE + "/"]` (both read with `datetime.fromisoformat`: a `+00:00` commit is written `Z` in one and `+00:00` in the other), `mainEntity` with `@type` `Person`. `Person`: `name` = `p.h1`; `alternateName` = `[params.alternatename from hugo.toml (read with tomllib), the text of the anchor whose cls holds "mark"]`; `url` = `BASE + "/"`; `image` = `BASE` plus the home `<img>`'s `src`; `jobTitle.lower()` = `p.role`; `sameAs` = the bar's `href`s that start with `https://`, in order. Each mismatch is one problem naming the key, the found and the expected value. A home page without a block, a block `json.loads` rejects and a missing lastmod for `/` are each a problem, never an exception.

- [ ] **Step 2: Run the check to verify it fails.** Expected FAIL lines, and no others: `data /` (no JSON-LD block on the home page).

- [ ] **Step 3: Implement.** `hugo.toml` `[params]`: `alternatename = "Manuel Schuelein"`. `layouts/_partials/head.html`, inside `if .IsHome`, before the stylesheet: one `<script type="application/ld+json">` that prints a `dict` (not `jsonify | safeJS`: the template escapes a `dict` itself, as the Hugo docs' `safe.JS` page advises) of `@context` `https://schema.org` and an `@graph` slice of two dicts: `WebSite` (`name` `site.Title`, `url` `.Permalink`) and `ProfilePage` (`url` `.Permalink`, `name` `.Title`, `dateModified` `.Lastmod`, `mainEntity` a `Person` dict: `name` `site.Title`, `alternateName` `slice site.Params.alternatename site.Params.handle`, `url` `.Permalink`, `image` `absURL site.Params.avatarurl`, `jobTitle` `site.Params.role`, `sameAs` the `.URL` of each `site.Menus.main` entry that has the prefix `https://`).

- [ ] **Step 4: Run the check to verify it passes.** Expected: no `FAIL` line, exit 0. Read the built home page's `<script type=application/ld+json>` once and compare it with the shape in this plan's measurements.

- [ ] **Step 5: Update `CLAUDE.md`:** the no-JavaScript gotcha names the one exception (the home page's `<script type="application/ld+json">` block, data and not code, built in `layouts/_partials/head.html` from `hugo.toml` and the menu; `check-site.py` fails on any other `<script` and compares the block with the built home page); the structure's `head.html` line adds "JSON-LD (home page)"; the `[params]` list adds `alternatename` (the name without the umlaut; with `handle`, the alternate names in the JSON-LD); the `[[menu.main]]` line says every `url` entry that starts with `https://` also becomes a `sameAs` identity claim in the JSON-LD, so only the owner's own profiles belong there; the Configuration line on Git dates adds the JSON-LD's `dateModified`; the `check-site.py` command's comment lists what it checks now (pages, metadata, links, bar, host, sitemap, dates, icon, JSON-LD, motion).

- [ ] **Step 6: Commit.**

  ```bash
  git add -- scripts/check-site.py hugo.toml layouts/_partials/head.html CLAUDE.md
  git commit -m "Add the site name and the owner's profile as one JSON-LD block on the home page and check it against the page."
  ```

- [ ] **Step 7: Hostile text (Review Focus 1).** In a throwaway clone of the branch in `$SCRATCH`, set `title = "Manuel \"Q\" <b> & </script> Schülein"` in `hugo.toml` (the `<h1>`, the footer and the two `name`s read it) and the same text as the `title` in `content/_index.md` (the `<title>` and the ProfilePage's `name` read that one), and run that clone's `scripts/check-site.py`. Expected: `data /` and `links /` PASS (the block parses, its names equal the page, and the raw HTML holds exactly one `<script`); FAIL lines from other checks caused by the odd title are allowed and are listed in the report. Delete the clone.

- [ ] **Step 8: A second script (Review Focus 2).** In a new throwaway clone, add `<script>1</script>` to `layouts/404.html` and run the clone's check; then restore it, add a second `<script type="application/ld+json">{}</script>` to `layouts/home.html` and run it again. Expected: `404 /404.html` FAIL the first time and `links /` FAIL the second. Delete the clone.

- [ ] **Step 9: A date in UTC (Review Focus 3).** In a new throwaway clone, change one line in `content/_index.md` and one in `content/now.md` and commit both with `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` set to `2026-11-15T10:00:00+00:00`, then run the clone's check. Expected: no `FAIL` line. Delete the clone.

- [ ] **Step 10: Both Hugo versions (Review Focus 4).** Run the check with Hugo 0.166.0 first on PATH, then with the installed 0.169.0 first on PATH. Expected: no `FAIL` line in either run.

### Task 5: Decide's picks in the check

**Does:** Makes the check print a FAIL line, not a traceback, on a list-valued `@type`. It also ends its false FAILs on a link to the site's repository, a raw `ü` in a profile URL, config keys in another case and a mail address on a subdomain (Parking-lot lines K, M, N, S, T in flow.md, picked at Decide on 2026-11-15).
**Depends on:** Task 4 and the review fixes (`docs/audits/2026-11-15-review-branch.md`)
**Adds:** the constant `OLD_HOST` in `scripts/check-site.py`; `check_data` and `check_host` take the parsed `hugo.toml`
**Size:** ~15

**Files:**
- Modify: `scripts/check-site.py`

- [ ] **Step 1: Write the probes** in `$SCRATCH/probes5.sh <label> <check-site.py>`. Each probe runs in a fresh clone of the branch with that check copied in:
  - K: the `WebSite` node's `@type` as `(slice "WebSite")` in `layouts/_partials/head.html`;
  - M: a now row linking `https://github.com/deadmade/deadmade.github.io`. Control: a row linking `https://deadmade.github.io/`;
  - N: the LinkedIn URL in `hugo.toml` with a raw `ü` in place of `%C3%BC`;
  - S: `baseurl = …` in lowercase, and `[Params]` capitalized. Control: `baseurl = "https://example.org/"`;
  - T: a now row with `a@sub.manuelschuelein.de`. Controls: `https://www.manuelschuelein.de/` and `https://x@manuelschuelein.de/` in `layouts/home.html`;
  - fix 2's and fix 3's probes again, to show no regression.
- [ ] **Step 2: Run them on the current check.** Expected:
  - K: a `TypeError` traceback;
  - M: `FAIL host` and `FAIL seams`;
  - N: `FAIL data`;
  - S: `FAIL host` for `baseurl`, `FAIL data` for `[Params]`;
  - T: `FAIL seams`;
  - the controls fail;
  - fix 2 passes, and fix 3 fails `seams`.
- [ ] **Step 3: Implement** in `scripts/check-site.py`:
  - `check_data` keys `nodes` by `str(n.get("@type"))`;
  - add `OLD_HOST = r"(?<![^/]/)deadmade\.github\.io"`, the old host but not as a path segment. `check_host` and `seams` both use it;
  - `seams` removes mail addresses before it looks for a host, with `(?<![\w.+/-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+`, so a URL with user info still counts. This replaces the `(?<!@)` lookbehind;
  - `sameAs` is compared after `urllib.parse.unquote` on both sides;
  - `main` parses `hugo.toml` once, after a good build, with its keys lowercased, and passes it to `check_data` (which lowercases the param keys) and `check_host` (which reads `baseurl`).
- [ ] **Step 4: Run the probes on the fixed check.** Expected:
  - K: a `FAIL data /` line naming the graph, and no traceback;
  - M, N, S and T: no FAIL;
  - the controls fail;
  - fixes 2 and 3 keep their results;
  - the clean tree: 32 PASS.
- [ ] **Step 5: Commit at Decide**, with the review fixes in the same file.

### Task 6: The CLAUDE.md corrections

**Does:** Says in `CLAUDE.md` that the check fails on a shallow checkout, and that a mail address on the domain and the repository path `github.com/deadmade/deadmade.github.io` don't count as the host (Parking-lot line U).
**Depends on:** Task 5
**Size:** ~2

**Files:**
- Modify: `CLAUDE.md` (two phrases; the owner's uncommitted `[params]` edit stays out of the commit)

- [ ] **Step 1: Edit the two lines** in the working tree: the Configuration line on `enableGitInfo` and the Gotchas line on the host.
- [ ] **Step 2: Stage at Decide.** Stage HEAD's `CLAUDE.md` plus only these two edits: apply them to `git show HEAD:CLAUDE.md` in `$SCRATCH`, then `git update-index --cacheinfo 100644,<blob>,CLAUDE.md`. Expected: `git diff --cached CLAUDE.md` shows only the two edits, and `git diff CLAUDE.md` shows only the owner's line.
