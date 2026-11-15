---
flow: feature
phase: done
now: Done: pushed job-application-portfolio to origin, with no PR; main, which deploys the site, is unchanged.
---

# SEO: flow

## Request

Hey, could we drasticly enhance sso so its the best of the best :D

Read as SEO (search engine optimization): the site is static, with no sign-in anywhere, so single sign-on has nothing to attach to (inferred; the user's answer below treats it as search).

The why, in the user's words (2026-11-14): "well first of all it should just be easily shown when someone searches for my name and also for ai agent that for example look at my application"

## Artifacts

- Prior art: [prior-art.md](prior-art.md)

- Spec: [spec.md](spec.md). Builder check (one fresh agent on sonnet, 2026-11-14): 6 questions. Answered from measurements and docs: which host CI builds with (the live canonical is `manuelschuelein.de`), where the custom domain is held (the Pages settings; an Actions deploy ignores `CNAME`). Settled as my calls: Git dates move only with a content file's commit; the check compares the JSON-LD with what the built home page shows. Left for the grill: the now page's date, the extra person facts.
- Plan: [plan.md](plan.md). Self-review (2026-11-15) added: the check fails on a robots.txt Disallow and on a stale baseURL in hugo.toml, compares the JSON-LD date with the sitemap as instants (a `+00:00` commit is `Z` in one and `+00:00` in the other, measured), and puts the hostile title in `content/_index.md` too; "another working directory" left the Review Focus for the UTC date.
- ADRs:
- Glossary:

## Gates

- Gate 1, spec approved: 2026-11-15. Reopened 2026-11-15: G1 gains a CI check of the Pages address (plan review round 1, item 4; the user picked it). Approved again 2026-11-15.
- Gate 2, plan approved: 2026-11-15, execution: native
- Gate 3, review-code: report: 2026-11-15 (picks: all 9)
- Gate 4, Decide (round 1): 2026-11-15. Rulings A–I confirmed. Parking lot: K, M, N, S, T and U done now (plan Tasks 5 and 6); O and R are follow-ups; J, L, P and Q were resolved by the review. Both Skipped rows accepted. Round 2: 2026-11-15. The new rulings V and W confirmed, with Tasks 5 and 6 and the round-2 checks. Ready.

## Skipped

- Todo list: this session has no task tools; progress is kept in this file. Accepted by the user at Decide (2026-11-15).
- pstack `interrogate`, offered before /review-code's lenses because execution ran without per-task reviews: the user skipped it (2026-11-15). Accepted at Decide (2026-11-15).

## Grounding

My own reading, before the `how` explainer lands (measured = from a local build with Hugo 0.169.0, `--gc --panicOnWarning --baseURL https://deadmade.github.io/`; verified = the file says it):

- `layouts/_partials/head.html:1-21` writes the charset, viewport, `<title>` from `.Title`, the meta description (`.Description`, else `params.description`), the canonical link (on the 404: `noindex` instead), Hugo's embedded `_internal/opengraph.html` and `_internal/twitter_cards.html`, four icon links, the manifest and one fingerprinted stylesheet. Verified.
- Built head, measured: `og:url`, `og:site_name`, `og:title`, `og:description`, `og:locale` (`en_US`), `og:type` (`website` on the home page, `article` on the other three), `og:image` (`https://deadmade.github.io/images/og.png`, no width, height or alt); `twitter:card` `summary_large_image`, `twitter:image`, `twitter:title`, `twitter:description`; a `generator` meta on the home page only.
- `sitemap.xml` lists the four pages, no `lastmod` (measured). `static/robots.txt` allows everything and names the sitemap (verified, lines 1-5).
- No structured data. The earlier run left JSON-LD `Person` out "until someone shows it is worth having" (`docs/features/job-application-portfolio/spec.md:90`).
- `scripts/check-site.py`: `links` fails on any `<script` and on `.woff2` in a page (`:158`); `files` wants exactly the four pages and `404.html` (`:217-218`); `head` wants one title, one description, the canonical, no keywords, no robots meta (`:124-133`), and no repeated title or description across pages (`:146-148`); `social` wants each of six tags once and the share image URL (`:134-137`); `sitemap` wants exactly the four URLs and the robots line (`:176-182`); `seams` forbids the host name outside `hugo.toml` in `layouts/` and `content/` (`:203-206`). Verified.
- Constraints in `CLAUDE.md`: no JavaScript and no external requests; page text lives in `content/` front matter; the projects page's design is frozen (`layouts/projects.html`, the drawing partials and their CSS); the projects, path and now pages have visually hidden `<h1>`s (`projects`, `path`, `now`). Verified.
- CI checks out with `fetch-depth: 0` (`.github/workflows/hugo.yml:27-29`), so Git dates are available to Hugo there (inferred). Hugo is not on PATH here (winget's Hugo 0.169.0 at `%LOCALAPPDATA%\Microsoft\WinGet\Packages\Hugo.Hugo.Extended_Microsoft.Winget.Source_8wekyb3d8bbwe\hugo.exe`), nor is Python (`%LOCALAPPDATA%\Programs\Python\Python313\python.exe`); `check-site.py` calls `hugo` by name. Measured.
- No `GLOSSARY.md`, no `docs/adr/`.

From the `how` explainer (one Explore agent on fable; it did not run `check-site.py`, so pass/fail claims below are inferred from the script's source):

- Measured sizes: `static/images/og.png` is 1200×630 (`scripts/generate-og-image.py:14`); icons are 16, 32, 180 (apple-touch), 192 and 512 px, `favicon.ico` holds 16 and 32, plus `favicon.svg`. No linked PNG is a multiple of 48 px (the 192 px one is only in the manifest), and there is no root `/favicon.ico`.
- The 404 page's title is `404 Page not found`, with the site default description and `og:url …/404.html` (measured).
- Each page has one `<h1>`; the six project drawings are `role="img"` SVGs whose `<title>` is the `summary` from `content/projects.md` (measured). The only `<img>` is the avatar. Visible text comes from front matter, except the fixed labels in `layouts/path.html:9,22,29` and the 404 text (verified).
- Collisions, inferred from `check-site.py`: JSON-LD's `<script type="application/ld+json">` fails `links` (`:158`) and the no-JavaScript rule; microdata avoids that, but a `<link itemprop="sameAs" href="https://github.com/…">` fails `links` as leaving the site (`:58-59`, `:118`), and only `baseof.html`, `home.html`, `path.html` and `now.html` are open to markup (projects page frozen); a verification `<meta>` passes `head` but also lands on the 404 page; an HTML verification file fails `files` (`:217-218`); sitemap `lastmod` is unpinned (the check reads only `<loc>`, `:178`), would probably add `article:*_time` tags on the three `article` pages, sits beside the hand-written `updated: "November 2026"` (`content/now.md:16`), and Git dates miss text that lives in `hugo.toml` (menu descriptions); `og:image:width/height/alt` must be written by hand in `head.html` (the embedded template emits none), the alt text belongs in `[params]`, and `social` would not catch a doubled tag.
- Not pinned by any check: headings, SVG titles, visible text, `og:url` matching the canonical.
- Only Hugo 0.169 was measured; CI's 0.166 pin may differ in the embedded templates' output.

The live site, measured with curl on 2026-11-14 after the user said the site is "already published on manuelschuelein.de":

- `https://manuelschuelein.de/` answers 200 from GitHub Pages; `www.manuelschuelein.de`, `http://manuelschuelein.de/`, `deadmade.github.io/` and `deadmade.github.io/projects/` answer 301 to the same path on `https://manuelschuelein.de/`.
- It serves `main`'s build, the old hugo-coder home page: `lang=de`, title `Manuel Schülein`, description `Manuel Schüleins Website`, a `keywords` meta, `og:locale de_DE`, canonical `https://manuelschuelein.de/`. This branch is 23 commits ahead of `main` and 0 behind (`git log`), so the redesign and this SEO work go live together when the branch is merged (inferred).
- The live `robots.txt` says `Sitemap: https://deadmade.github.io/sitemap.xml`, the old host (that URL redirects). The live `sitemap.xml` lists `/`, `/categories/` and `/tags/` on `manuelschuelein.de`; the redesign drops the last two (`disableKinds` in `hugo.toml:5`).
- Production URLs come from CI, not `hugo.toml`: CI builds with `--baseURL "${{ steps.pages.outputs.base_url }}/"` (`.github/workflows/hugo.yml:68`), which gave the live canonical. The branch still names `deadmade.github.io` in `hugo.toml:1`, `static/robots.txt:5` and `scripts/check-site.py:18`, so the check passes for a host the site no longer uses, and the static `robots.txt` keeps the old host in production.
- `gh` is not installed here, so the Pages settings were not read through the API.

## Prior art

[prior-art.md](prior-art.md), one agent on sonnet. Source check (one fresh agent on opus, 2026-11-14): 43 claims tied to a page: 32 confirmed, 7 partly supported, 4 not supported, 0 couldn't open; 3 inferred claims behind the approaches did not follow (microdata "must wrap visible text" and "harder to keep one node"; "one JSON-LD block" for PaperMod). I corrected the report and put the counts at its top. Hugo's `opengraph.html` and `sitemap.xml` are byte-identical at v0.166.0, v0.169.0 and `master`. Not supported and fixed: ProfilePage's `name` is required, not recommended; `og:type` is `article` only for regular pages; a shallow clone "may be" inaccurate, not "wrong for every file". Added from the check: Google's favicon formats exclude SVG and WebP; ProfilePage needs a page whose primary focus is one person; Google's two AI pages disagree on whether a Search Console setting is needed.

- Implementations read: jekyll-seo-tag (one JSON-LD block, verification tags from config, og image width/height/alt as fields), PaperMod and Blowfish (JSON-LD; home page `Person`/`Organization` or `WebSite` with `sameAs`), Hugo's embedded `opengraph.html` (no image width/height/alt; non-home pages are `article`) and `schema.html` (head microdata for a generic page).
- Approaches: A meta tags only (as now); B one JSON-LD block (needs the `<script` check to allow `application/ld+json`); C microdata in the visible HTML (no script; Google accepts it for site names and ProfilePage); D Hugo's `schema.html` (does not describe `WebSite` or `Person`).
- Gaps the report names: Hugo docs read at the current version, not 0.166; no source on site names for github.io hosts beyond Google's page; LinkedIn's own docs unreachable (its image rules come from a blog); jekyll-seo-tag's JSON-LD builder, Congo and Bing's AI-crawler docs not read.

## Findings

## Options

### Address

Picked: `manuelschuelein.de`, where the site already lives (the user, 2026-11-14; measured). Offered: move to `manuelschuelein.de` (recommended), stay on `deadmade.github.io`, decide later. The user's answer: "its already published on manuelschuelein.de".

### How the site tells machines who the owner is

Picked: one JSON-LD block on the home page (the site name, and a profile of the owner as a person: name, job title, picture, GitHub and LinkedIn), built from `hugo.toml` and the page text, with `check-site.py` allowing exactly `<script type="application/ld+json">` (the user, 2026-11-14). Offered on top of the same groundwork (one host with a generated robots.txt, Git dates in the sitemap, share-image size and alt, a 192 px PNG icon, the owner's Search Console steps): A groundwork only (the smallest that would work; the site name rests on the title and `og:site_name`); B JSON-LD (recommended: Google's recommended format, one block, facts from one place); C microdata (no script element, but `check-site.py` still changes for a `<link itemprop="sameAs">` and the markup spreads over `home.html` and `baseof.html`). Seams offered with it: the host only in `hugo.toml` (CI: the Pages address); the owner's facts only in `hugo.toml` and the page text; dates only from Git.

### The now page's date (grill round 1, Q1)

Picked: the visible "updated" month comes from the now page's Git date, and `updated` leaves `content/now.md` (the user, 2026-11-14). Offered: from Git (recommended: it can't go stale or disagree with the sitemap); keep typing it.

### The profile's facts (grill round 1, Q2)

Picked: name, URL, picture, job title, GitHub and LinkedIn, plus "Manuel Schuelein" and "deadmade" as alternate names (the user, 2026-11-14: "add Manuel Schuelein and deadmade"). Offered: stop at the first six (recommended); add the region; add the email; add "Manuel Schuelein". Where the new spelling lives (a new `[params]` value) is my call. Left out: llms.txt, IndexNow, blocking AI crawlers, new pages. My calls the user did not object to: every crawler stays allowed; the facts stay in the visible text; no new pages; `/categories/` and `/tags/` return 404 after the merge; Search Console is verified by a DNS record, so the site gets no verification tag.

## Plan review

### Plan review round 1 (2026-11-15)

Three fresh reviewers: correctness (fable), fit (opus, with pstack `blast-radius`), simpler (sonnet, with ponytail `ponytail-review`). The correctness and fit reviewers ran the plan in throwaway clones with Hugo 0.169.0 (not 0.166.0); every measurement in the plan held. 0 blocking, 2 should-fix, 11 consider, 0 dropped.

Should-fix:

1. Task 1 can't go green: widening `seams` to `static/` also widens its accent-colour rule (`scripts/check-site.py:203-206`), which fires on `static/icons/favicon.svg:3` (`fill="#F08BB4"`, written by `generate-favicons.py` on purpose). Measured by fit (`FAIL seams -: accent colour in static\icons\favicon.svg` after Step 4); I verified the file line.
2. Tasks 2 and 3 are drawn as parallel (each depends only on Task 1) but both rewrite parts of `scripts/check-site.py` (imports, `main()`, `check_sitemap`, `social`): run concurrently, one task's commit stages the other's edits and its "no other FAIL lines" step breaks. Correctness: should-fix; fit: consider (in sequence both red lists matched, measured).

Consider:

3. `enableGitInfo` makes a Git checkout a build requirement: a copy without `.git` fails with `failed to load Git data: fatal: not a git repository` (measured by correctness and fit).
4. The deployed host comes from the Pages settings (`hugo.yml` passes `--baseURL` from `steps.pages.outputs.base_url`), not from `hugo.toml` or the check's `BASE`; and Task 1 Step 6's CLAUDE.md wording ("the host is written only in `hugo.toml`") contradicts Step 2, which writes it into `BASE` (correctness, fit; read, not run in CI).
5. Crash paths: `png_size` on a non-PNG or missing file, a missing lastmod for `/`, a JSON-LD block that doesn't parse would raise and hide every PASS/FAIL line; the deploy still stops (correctness; read, not run).
6. Partly pinned: the `icon` check checks one PNG link, not the 16 and 32 px links' `sizes`; `og:url` isn't compared with the canonical, though G1 lists it (correctness; read).
7. `sameAs` takes every `https://` menu entry; a future project link in the bar would be published as an identity claim and the check passes by construction (fit; built).
8. Stale CLAUDE.md lines: `:21` (what the check covers), `:13` (the check needs Python 3.11+ for `tomllib` and `fromisoformat` with `Z`), and Task 2's Git-date list lacks Task 4's `dateModified` (fit; Python docs fetched).
9. Simpler: the build-output host scan is redundant with `seams`.
10. Simpler: the `dateModified` and now-page comparisons compare Hugo with itself.
11. Simpler: Steps 7 and 9 re-test Hugo's escaping and date formatting through hand-built clones.
12. Simpler: the Hugo 0.166.0 download is heavy; CI already runs the check with 0.166.0.
13. Simpler: fewer JSON-LD equalities (drop `name`, `jobTitle`, `dateModified`, the footer parsing).

Decisions (the user, 2026-11-15) and what changed:

- 1: the host rule alone scans `static/`; the accent rule keeps `hugo.toml`, `layouts/`, `content/` (recommended). Plan Task 1 Step 2.
- 2: Task 3 depends on Task 2, order 1→2→3→4 (recommended). Plan Task 3 header.
- 3, 4 (wording), 7, 8: CLAUDE.md fixes (recommended). Plan Task 1 Step 6 (three host places, Python 3.11+), Task 2 Step 5 (Git checkout needed), Task 4 Step 5 (`sameAs` from the menu, `dateModified` in the Git-date line, the check's coverage list).
- 4 (CI check): taken, though I recommended skipping it. Spec G1, G7, files map and test seam edited (reopens Gate 1 for G1); plan Task 1: `host` fails when `PAGES_BASE_URL` is set and differs from `BASE`, `hugo.yml`'s check step gets `PAGES_BASE_URL: ${{ steps.pages.outputs.base_url }}`, Step 5 runs the check with both addresses.
- 5: crash paths become problems (recommended). Plan Task 3 Step 1 (`png_size`), Task 4 Step 1 (no block, invalid JSON, missing lastmod).
- 6: every PNG icon link's `sizes` checked against its file, at least one larger than 48; `og:url` = `BASE + path` (recommended). Plan Task 3 Step 1.
- 9–13: declined, plan kept as is (recommended): each cut drops something G7 asks for, or a one-off test run that ships nothing; the 0.166.0 runs are the only test of CI's Hugo before the merge.

No fresh-eyes round: the run order 1→2→3→4 and the modules are unchanged; the graph lost its one parallel wave, and Task 1 gained one workflow line.

Fix check (one fresh agent on sonnet, 2026-11-15): finding 1 PASS (plan Task 1 Step 2 splits the two rules; Step 3's red list still right), finding 2 PASS (Task 3 depends on Task 2; the chain is serial). The other edits break no neighbouring task, except one FAIL it found that predates this round: Task 1 Step 7's `git add` named `static/robots.txt` after Step 4's `git rm`, which fails the whole command (`fatal: pathspec … did not match any files`; I reproduced it). Fixed: the path left the `git add` line.

## Tasks

Workspace: the owner chose to commit on the current branch `job-application-portfolio` (2026-11-15), no new branch and no worktree. Executor: `executing-plans` (native); its ledger is `.superpowers/sdd/plan/progress.md` (git-ignored).

- Task 1: base 15aa5a6; untracked at start: `docs/features/seo/` (flow.md, plan.md, prior-art.md, spec.md); files clean (6 files, size 56 of ~55, adds as listed)
- Task 2: base 2d8320c; untracked at start: `docs/features/seo/` only; files clean (5 files, size 33 of ~40, adds as listed); Review Focus 5 held (an uncommitted now.md edit: 30 PASS, the page kept its last-commit month)
- Task 3: base 911138e; untracked at start: `docs/features/seo/` only; files clean (2 files, size 76 of ~50, under twice N; adds as listed, plus the private parser state and `check_icon`, the `icon` check)
- Task 4: base 43e77ff; untracked at start: `docs/features/seo/` only; files clean (4 files, size 91 of ~95; adds as listed, plus the private parser state and `check_data`, the `data` check); Review Focus 1 to 4 held (the hostile title: exit 0, `data /` and `links /` pass; a 404 script and a second block each fail; a UTC-dated commit: 32 PASS; Hugo 0.166.0 and 0.169.0: 32 PASS each)
- Final review (executing-plans, 2026-11-15): one fresh reviewer on fable read the package `15aa5a6..f6a2b24`, the plan, the spec and the ledger, and ran the check in a separate worktree. Result: no Critical, 1 Important, 8 Minor; Review Focus 1–5 held in its own runs; "Ready to merge: With fixes". Re-graded by effect: the Important stands, and no Minor rises. Fixed in 4751c5b: `data` fails on a JSON-LD key it does not compare with the page (probes: an email on `Person`, a description on `WebSite`; RED exit 0 with `PASS data /` → GREEN one `FAIL data /` each; suite 32/32 in a clean clone). `CLAUDE.md`'s no-JavaScript gotcha says so. The 8 Minors are under **Parking lot**, its 8 declined-to-judge lines under **Rulings**. The workspace `.superpowers/sdd/plan/` is deleted after this line; the check command is in plan.md's Global Constraints.
- An uncommitted edit to `content/now.md` (its description in the first person, the priorities row gone, "AI Agents") appeared in this checkout during the final review. The build did not make it (inferred: the owner's own copy edit, still being saved at 01:03:59). It stays out of every commit, and the check passes with it, 32/32.
- Fix 1–7 and Fix 9 (review findings, the owner's picks at Gate 3): base 4751c5b. Untracked at start: `docs/audits/2026-11-15-review-branch.md` and `docs/features/seo/`. The owner's uncommitted edits at start (`CLAUDE.md`, `hugo.toml`, `assets/css/path.css`, `content/_index.md`, `now.md`, `path.md`, `projects.md`) stay out. Files: `scripts/check-site.py` only (+30 −27). Files clean. Each probe was run on the old check, then on the fixed one, in clean clones:
  - Fix 1, a `--depth 1` clone: exit 0 → `FAIL dates /now/: the Git checkout is shallow…`.
  - Fix 2, `info@manuelschuelein.de` in a now row: `FAIL seams` → exit 0.
  - Fix 3, a move to `example.dev` in the three places plus a hard-coded link in `layouts/home.html`: exit 0 → `FAIL seams -: site host in layouts\home.html`.
  - Fix 4, `alternatename` deleted or `""`: exit 0 → `FAIL data /: hugo.toml sets no params.alternatename`. Spelled `alternateName`: false FAIL → exit 0.
  - Fix 5, a custom sitemap with `Jan 2, 2006` dates: a `ValueError` traceback with no lines → three FAIL lines.
  - Fix 6, the role as typed in the footer and the alt text: false FAIL → exit 0.
  - Fix 7, a refactor: an extra key, a wrong name and a wrong date still FAIL. The old way to silence an extra key (adding it to a key set) no longer exists, and the probe now FAILs.
  - Fix 9, a refactor: a second `og:image` naming no file still fails `social` and `links`.
  - Clean tree: 32 PASS before and after.
- Fix 8: no code. It resolves when `docs/features/seo/` is committed at Decide.
- Final checks (2026-11-15, measured). The clean clone is 4751c5b plus the fixed `scripts/check-site.py` (blob 6176137, the same in the clone and the working tree); its `git status --short` lists only that file.
  - `PAGES_BASE_URL=https://manuelschuelein.de python scripts/check-site.py` on Hugo 0.166.0: 32 PASS, exit 0. On Hugo 0.169.0: 32 PASS.
  - The CI deploy build `hugo --gc --minify --baseURL "https://manuelschuelein.de/"` on 0.166.0: exit 0.
  - The working tree, with the owner's uncommitted edits: 32 PASS.
  - Since then only `docs/` has changed, which neither the build nor the check reads.
  - `shortcut:` lines: none in this run (`git diff 15aa5a6`, and the untracked files). The branch's two are from the 2026-11-07 runs and were confirmed there.

- Task 5 (the Decide picks K, M, N, S and T): base 4751c5b plus the uncommitted review fixes. Untracked at start: `docs/audits/2026-11-15-review-branch.md` and `docs/features/seo/`. The owner's edits stay out. Files: `scripts/check-site.py` only (+20 −17 on top of the review fixes; +43 −37 against 4751c5b). Files clean. Each probe ran on the check before the task, then after it, in clean clones (`probes5.sh`):
  - K, a list-valued `@type`: a `TypeError` traceback → one `FAIL data /` line naming the graph.
  - M, a now row linking `https://github.com/deadmade/deadmade.github.io`: `FAIL host` and `FAIL seams` → exit 0. The control, a link to `https://deadmade.github.io/`, fails both before and after.
  - N, a raw `ü` in the LinkedIn URL: `FAIL data` (the href has `%c3%bc`, the block a raw `ü`) → exit 0.
  - S: `baseurl` in lowercase gave `FAIL host` and `[Params]` gave `FAIL data` → exit 0 each. The control `baseurl = "https://example.org/"` fails `host`, and now names the value (before: `None`).
  - T, `a@sub.manuelschuelein.de` in a now row: `FAIL seams` → exit 0. The `www.` control fails both times. The user-info control, `https://x@manuelschuelein.de/`, passed before: a gap that fix 2's `(?<!@)` opened. It now fails `seams`.
  - The probes of fixes 2, 3, 4 and 7 rerun on the new check, unchanged.
  - The clean tree gives 32 PASS.
  - One wrong turn: my first green run failed `data` on every probe ("Person sameAs is True"), because the new name `same` already held the date comparison's flag. I renamed it and reran.
  - Ruling I's "hugo.toml parsed twice" no longer holds: `main` parses it once.
- Task 6 (the Decide pick U): `CLAUDE.md`, the two phrases, made in the working tree. The commit stages HEAD's `CLAUDE.md` plus only those two (`git update-index --cacheinfo`). Checked: HEAD → the staged version shows only the two lines; the staged version → the working tree shows only the owner's `[params]` line.
- The scratchpad's top-level files were deleted from outside this session at about 12:20: the check runner, Hugo 0.166.0 and the earlier probe logs. The repository was untouched. I downloaded Hugo 0.166.0 again; its SHA-256 matches the release's checksums file (`51e4512f…`), and it is the same build (`78400b4`).
- Final checks, round 2 (2026-11-15, measured). The clean clone is 4751c5b plus the current `scripts/check-site.py` (blob 254ea41, the same in the clone and the working tree).
  - `PAGES_BASE_URL=https://manuelschuelein.de python scripts/check-site.py` on Hugo 0.166.0: 32 PASS, exit 0. On 0.169.0: 32 PASS.
  - The CI deploy build on 0.166.0: exit 0.
  - The working tree, with the owner's edits: 32 PASS.
  - Since then, only `docs/` and the owner's files have changed.

## Rulings

- 2026-11-15, Task 3: `check_pages` now takes `out`, to read the share image's size once — its one caller is `main` — costs nothing if wrong. — A, confirmed 2026-11-15
- 2026-11-15, Final: `onclick=` attributes and `javascript:` links pass the no-JavaScript rule — this predates the branch, the spec names only `<script`, and the owner writes every layout by hand — an inline handler could ship unnoticed (parked). — B, confirmed 2026-11-15
- 2026-11-15, Final: a `<script>` inside a static SVG is not scanned — the icons come from `scripts/generate-favicons.py` and are served as images, where scripts don't run — none unless an SVG is edited by hand. — C, confirmed 2026-11-15
- 2026-11-15, Final: the `www.` and `http://` redirects and the live Pages setting are not checked — they need the network and the repository settings, and the spec records them as measured — a broken redirect shows only on a visit. — D, confirmed 2026-11-15
- 2026-11-15, Final: how Google reads the markup (no `@id` links, a WebP image, `og:type` `article` on the inner pages) is not checked — the spec leaves it to URL Inspection, and `og:type` is a non-goal — a missed rich result shows only in Search Console. — E, confirmed 2026-11-15
- 2026-11-15, Final: "Manuel Schuelein" in `alternateName` is not shown on the page — the owner chose it at Gate 1, a spelling of the visible name, which the spec accepts as low risk — Google may ignore that one name. — F, confirmed 2026-11-15
- 2026-11-15, Final: a doubled space in the title fails `data` (the `<h1>` text is normalized, the block is not; inferred) — it fails loudly and closed, and a name holds no doubled space — one confusing FAIL line if it happens. — G, confirmed 2026-11-15
- 2026-11-15, Final: whether each intermediate commit passes on its own — measured: each task's `task-done` ran the whole check at that task's commit — none. — H, confirmed 2026-11-15
- 2026-11-15, Final: `hugo.toml` parsed twice, and backslash paths in `seams` messages on Windows — the plan's "one caller gets no helper" rule, and CI runs on Linux — none. — I, confirmed 2026-11-15

- 2026-11-15, Task 5: `seams` removes mail addresses before it looks for a host. A lookbehind can't see a subdomain (`a@sub.<host>`), and Python's `re` takes no variable-width lookbehind. Cost if wrong: a mail-shaped string meant as a link passes; none exists today. — V, confirmed 2026-11-15
- 2026-11-15, Task 5: the path-segment exception covers only the old host, because the repository is named `deadmade.github.io`. No path names the current host. Cost if wrong: a link to a repository named `manuelschuelein.de` fails `seams`, which fails closed. — W, confirmed 2026-11-15

## Parking lot

From the final review (Minor, deferred; measured by the reviewer unless marked):

- `scripts/check-site.py`: fail `data` on a missing or empty `params.alternatename` (today the block then says `[null, "deadmade"]` and passes).. — J: resolved by review #4
- `scripts/check-site.py`: a list-valued `@type` in the JSON-LD gives a traceback (`TypeError: unhashable type`), not a FAIL line; the deploy still stops. This is the class plan review item 5 ("crash paths become problems") was about. — K: do now (Decide 2026-11-15) → done in Task 5
- `scripts/check-site.py`: fail on a shallow checkout (`git rev-parse --is-shallow-repository`); today a `--depth 1` clone passes with every lastmod set to the head commit's date, and only `fetch-depth: 0` in `hugo.yml` guards it.. — L: resolved by review #1
- `scripts/check-site.py`: match the old host as a host (`//deadmade.github.io`), so a link to the site's own repository `github.com/deadmade/deadmade.github.io` doesn't fail `host` and `seams` as "old host" (the `seams` half predates this branch). — M: do now (Decide 2026-11-15) → done in Task 5
- `scripts/check-site.py`: compare `sameAs` after `urllib.parse.unquote`, or note in `CLAUDE.md` that profile URLs in `hugo.toml` must be percent-encoded (a raw `ü` fails `data`). — N: do now (Decide 2026-11-15) → done in Task 5
- `scripts/check-site.py`: `sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")` in `main`, so a FAIL line with a character outside cp1252 isn't a traceback on a Windows console (predates this branch; CI is unaffected). — O: a follow-up (Decide 2026-11-15)
- `scripts/check-site.py`: guard `fromisoformat` in `check_dates` as `check_data` does (inferred; Hugo's sitemap can't produce a bad value).. — P: resolved by review #5
- `scripts/check-site.py`: the docstring names `docs/features/seo/plan.md`, untracked until the run documents are committed (resolved if they are, at Decide).. — Q: resolved by review #8

From the final review's declined list:

- `scripts/check-site.py`: catch `onclick=`-style attributes and `javascript:` links under the no-JavaScript rule (predates this branch). — R: a follow-up (Decide 2026-11-15)

From the review's lens notes and the fix check:

- `scripts/check-site.py`: parse `hugo.toml` once, with keys lowercased the way Hugo reads them. Today `check_host` reads `.get("baseURL")` (`:334`), so a `baseurl = …` that Hugo accepts gives a false `FAIL host`. Fix 4 hit the same mistake for `alternatename`. Inferred from reading `:334`, not run; the verifier's note. — S: do now (Decide 2026-11-15) → done in Task 5
- `scripts/check-site.py`: a mail address on a subdomain (`a@sub.manuelschuelein.de`) still fails `seams`, because the lookbehind sees `.`, not `@`. Found by the fix check. — T: do now (Decide 2026-11-15) → done in Task 5

From /learn:

- `CLAUDE.md`: two corrections after the review fixes, held back because `CLAUDE.md` holds the owner's uncommitted `[params]` edit: — U: do now (Decide 2026-11-15) → done in Task 6
  - in the Configuration line on `enableGitInfo`, after "CI checks out with `fetch-depth: 0` for this", add "and `scripts/check-site.py` fails on a shallow checkout" (fix 1);
  - in the Gotchas line on the host, make "on either host in `layouts/`, `content/` or `static/`" read "…, except after an `@` (a mail address)" (fix 2).
  Doing it now would mean staging only my hunk (`git apply --cached`), with the owner's line left unstaged.

## Deviations

## Walkthrough

| goal | plan task | file:line | test |
| ---- | --------- | --------- | ---- |
| G1 One host | Task 1 | `hugo.toml:1`, `layouts/robots.txt:5`, `.github/workflows/hugo.yml:64`, `scripts/check-site.py:332`, `:342` | `host -`, `sitemap -` (robots line), `seams -`, `social` (`og:url` = `BASE` + path); Task 1 Step 5 with both Pages addresses |
| G2 One JSON-LD block | Task 4 | `layouts/_partials/head.html:26-33`, `hugo.toml:12` | `data /` (`scripts/check-site.py:227`, one table of expected values since the review), `links` (`:268`), `404` (`:287`); Review Focus 1, 2 |
| G3 Dates from Git | Task 2 | `hugo.toml:7`, `layouts/now.html:9` | `sitemap -` (`:307`), `dates /now/` (`:319`, which also fails on a shallow checkout), `data /` (`dateModified`); Review Focus 3, 5 |
| G4 Share image details | Task 3 | `layouts/_partials/head.html:13-19` | `social` on every page (`:171`) |
| G5 A 192 px PNG icon | Task 3 | `layouts/_partials/head.html:21` | `icon /` (`:209`) |
| G6 Facts as text for AI agents | Task 1 (every crawler allowed) | `layouts/robots.txt:1-5`; the page text is unchanged (already true, no code) | `sitemap -` (fails on a `Disallow:` with a value) |
| G7 The check pins it all | Tasks 1–4, the final-review fix, review fixes 1–7 and 9, Task 5 | `scripts/check-site.py` | the whole check: 32 PASS on Hugo 0.166.0 and 0.169.0 (Review Focus 4) |
| G8 The docs match | Tasks 1, 2, 4, the final-review fix, Task 6 | `CLAUDE.md` | none (prose); read against the code by the final reviewer |

## Review

/review-code, inline (2026-11-15).

- Scope (the user's pick): `branch: job-application-portfolio ← 15aa5a6, 8 files, +216 −35, 5 commits`. Out of scope: the owner's uncommitted edits to `content/now.md` and `content/path.md`, the run's notes in `docs/features/seo/`, and the 23 earlier commits (the job-application-portfolio run, reviewed there, and standalone commits outside this request).
- Intent: the spec, the plan and the four `Picked:` lines under **Options**.
- Checks, the latest run (commit 4751c5b, a clean clone, `git status --short` empty): `check-site.py` with `PAGES_BASE_URL=https://manuelschuelein.de` on Hugo 0.166.0 gives 32 PASS, exit 0; the CI deploy build `hugo --gc --minify --baseURL "https://manuelschuelein.de/"` on 0.166.0 exits 0.
- Lenses: correctness (sonnet, neutral brief), lean (opus), tests (sonnet, `flows:pr-test-analyzer`), docs (sonnet), security (opus), risk (opus); none skipped. Correctness and security: no findings. Verifier (opus): 9 confirmed, 1 dropped.
- Verdict: ready (0 to fix before merge, 9 worth doing). Audit file: [docs/audits/2026-11-15-review-branch.md](../../audits/2026-11-15-review-branch.md).
- Fixed (Gate 3 picks: all 9): findings 1–7 and 9, in `scripts/check-site.py` (+30 −27), each red, then green, in clean clones (**Tasks**, Fix 1–7 and Fix 9). Number 8 resolves when this folder is committed at Decide. Fix check (one fresh agent on sonnet): 8 of 8 PASS, no regressions. Its probe log is byte-identical to my own green run (`cmp`, measured).
- Lens notes outside the findings:
  - The `baseURL` lookup is case-sensitive; and a subdomain mail address still fails `seams`. Both under **Parking lot**.
  - Repointing the GitHub menu entry to another profile passes. This is by design: the check can't know who owns a profile, and `CLAUDE.md` says only the owner's profiles belong there.
  - A squash merge would date all four pages with the merge commit. Hugo's Git info skips merge commits, so a merge or a fast-forward keeps each page's own date (inferred from Hugo's gitmap; not run). Owner info for Close.
  - CI's Python 3.12 was not run; only 3.13 is installed here.

## Learned

/learn, inline (2026-11-15). It read **Rulings**, plan review, Gate 1's reopening, the review and the run's commits. It wrote 3 memory notes (outside the repo, in this project's Claude memory folder):

- `local-toolchain.md` (reference): `hugo`, `python`, `gh` and `nix` are not on PATH here. It gives the paths of Hugo 0.169.0 and Python 3.13, and says CI's Hugo 0.166.0 needs a download (measured).
- `owner-edits-alongside.md` (user): the owner edits the same checkout during a session. Stage by path, and leave their files alone.
- `owner-closes-check-gaps.md` (user): the owner takes cheap gaps in the check even at low severity. Seen in the CI Pages-address check, which reopened Gate 1, and in all 9 picks at Gate 3.

It parked 1 line (the `CLAUDE.md` corrections, under **Parking lot**) and merged the `hugo.toml` key-case lesson into the review's `check_host` line. No solutions note, glossary entry or ADR: the code comments carry the date and key-case details, and no decision passes domain-modeling's three tests.

## Run verdict

- 2026-11-15, the owner: worked as a whole: yes; clean: no. Gate 1 was reopened, Decide took two rounds, and I took one wrong turn (a reused variable name in Task 5).
