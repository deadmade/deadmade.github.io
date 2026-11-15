# Review: branch (SEO)

`branch: job-application-portfolio ← 15aa5a6, 8 files, +216 −35, 5 commits`. The owner picked this scope (2026-11-15): this run's commits only. Out of scope:
- the owner's uncommitted copy edits (`CLAUDE.md`, `hugo.toml`, `assets/css/path.css`, `content/*.md`);
- the run's notes in `docs/features/seo/`;
- the 23 earlier commits on the branch.

The intent is in `docs/features/seo/spec.md`, `plan.md` and the four `Picked:` lines in `flow.md`. This review ran inline from the build flow, so its tasks, rulings, Parking lot, Skipped and Run verdict are in `docs/features/seo/flow.md`.

Six lenses ran: correctness, lean, tests, docs, security and risk. Correctness used the neutral brief: the scope isn't the branch against main, and the tree holds uncommitted files, so the built-in code review didn't apply. That makes six lens agents and one verifier, and no lens saw another's findings. The owner skipped pstack `interrogate`.

Checks: on 4751c5b, in a clean clone, `check-site.py` with `PAGES_BASE_URL=https://manuelschuelein.de` on Hugo 0.166.0 gives 32 PASS and 0 FAIL. The CI deploy build `hugo --gc --minify --baseURL "https://manuelschuelein.de/"` on Hugo 0.166.0 exits 0.

Verdict: ready. The built site is correct today, and every finding below is either a gap in the check or a false FAIL that a future edit would hit.

## Findings

<!-- Every verified finding, most severe first, `confirmed` or `plausible` in the evidence; `bucket` is
`fix before merge` or `worth doing`, so `all fix` resolves from this table. Then the dropped count. After the gate:
`Picks: <finding numbers> | none`, then one line `Fixed <date>: <number>` per pick once its check passes. -->

| #   | severity | where | finding | evidence | fix (recommended) | bucket |
| --- | -------- | ----- | ------- | -------- | ----------------- | ------ |
| 1   | med | `scripts/check-site.py:301-326`, `:263-267` | A checkout without full history ships the head commit's date as every page's lastmod, `dateModified` and `article:modified_time`, and the check passes, because the date checks only compare Hugo's outputs with each other. Only `fetch-depth: 0` (`hugo.yml:28`) guards it. Spec G7 says the check fails when G3 breaks. | confirmed (ran): in a `--depth 1` clone, `git rev-parse --is-shallow-repository` prints `true` and the check exits 0. All four lastmods are `2026-11-15T01:07:12+01:00`; with full history, three of them are 2026-11-10. The final review found the same. | `dates` fails when `git rev-parse --is-shallow-repository` prints `true` | worth doing |
| 2   | low | `scripts/check-site.py:361` | The `seams` host rule also matches the mail domain. An address such as `info@manuelschuelein.de` in page text stops the deploy with a "site host" message. Before this diff the rule matched only `deadmade.github.io`. | confirmed (ran): a now row with `[info@manuelschuelein.de](mailto:info@manuelschuelein.de)` gives `FAIL seams -: site host in content\now.md`, exit 1. The old rule was `"deadmade.github.io" in text` (`15aa5a6:scripts/check-site.py:206`). | `(?<!@)(?:deadmade\.github\.io\|manuelschuelein\.de)`. A bare `(?<!@)` in front still matches (ran). | worth doing |
| 3   | low | `scripts/check-site.py:361` | The `seams` rule types the host as a literal instead of reading `BASE`. After a move done the way `CLAUDE.md` says (three places), a hard-coded new host in `layouts/`, `content/` or `static/` passes. | confirmed (ran): with `BASE`, `baseURL` and `PAGES_BASE_URL` set to `https://example.dev` and `https://example.dev/now/` in `layouts/home.html`, there is no FAIL and the exit is 0. The control with `manuelschuelein.de` fails `seams`. | build the host part of the pattern from `urlparse(BASE).netloc` (the same line as 2) | worth doing |
| 4   | low | `scripts/check-site.py:243, 253`; `layouts/_partials/head.html:29` | A missing or empty `params.alternatename` ships `"alternateName":[null,"deadmade"]` (or `""`), and `data` passes: the expected value comes from the same key the template reads. The key spelled `alternateName` gives a false FAIL, because Hugo lowercases param keys but `tomllib` doesn't. | confirmed (ran), both cases. With the key deleted: `[null,"deadmade"]`, exit 0. Spelled `alternateName`: `FAIL data /: Person alternateName is ['Manuel Schuelein', 'deadmade'], expected [None, 'deadmade']`. The final review found the first case. | one problem when the value is empty; reading the keys lowercased is optional | worth doing |
| 5   | low | `scripts/check-site.py:325`, `:313-316` | `check_dates` parses the lastmod without a guard. A non-ISO lastmod, which only a custom `layouts/sitemap.xml` can produce, raises `ValueError`, and the run prints no PASS or FAIL lines. The RFC 3339 pattern at `:313-316` can't fail with Hugo's built-in sitemap. | confirmed (ran): an override with `"Jan 2, 2006"` gives `ValueError: Invalid isoformat string: 'Nov 15, 2026'`, exit 1, no lines. Hugo 0.166.0's embedded sitemap formats lastmod as `2006-01-02T15:04:05-07:00`, and the tree has no override. | guard `fromisoformat` in `check_dates`, so a bad lastmod is a FAIL line. Keep the pattern: the plan asked for it, and it is the only format check under an override. | worth doing |
| 6   | low | `scripts/check-site.py:255` | `jobTitle` is lowercased on one side only, though G7 says "ignoring case". A footer that shows the role as typed fails `data` while the block and the page agree. | confirmed (ran): with the footer as `{{ site.Params.role }}`, `FAIL data /: Person jobTitle, lowercased is 'backend developer', expected 'Backend developer'`. `social` then fails on all four pages as well, because the alt check follows the footer. | `(p.role or "").lower()` | worth doing |
| 7   | low | `scripts/check-site.py:248-262` | The key sets from 4751c5b are a second list next to the value comparisons. Adding a key to the template and to its set passes `data`, though nothing compares the key with the page. | confirmed (ran): `"email"` in `head.html:29` gives FAIL; adding `"email"` to the set at `:261` as well gives `PASS data /`. | one table of expected values per node, compared over the union of keys (about 5 lines shorter) | worth doing |
| 8   | low | `scripts/check-site.py:5` | The docstring names `docs/features/seo/plan.md`, which isn't in the tree. | confirmed (ran): `git cat-file -e 4751c5b:docs/features/seo/plan.md` fails, and `git status` shows `?? docs/features/seo/`. | commit `docs/features/seo/` at Decide (no code change) | worth doing |
| 9   | low | `scripts/check-site.py:41, 60-61` | `Page.images` holds the same two values as `Page.content`, and `check_pages` reads both for the same kind of lookup. `images` predates this diff; the diff added `content` next to it. | confirmed (ran): they are equal on all five built pages, also with two `og:image` tags. | delete `images`, and read the two keys from `content` at `:190-191` and `:275` (an explicit two-key lookup, not `.values()`) | worth doing |

Dropped: 1. The tests lens said a new `https://` menu entry would become a `sameAs` claim and pass. It doesn't pass: the bar is pinned by `BAR`, so `nav` fails on all four pages (ran).

Picks: 1, 2, 3, 4, 5, 6, 7, 8, 9 (the owner, 2026-11-15: "All 9").

Fixed 2026-11-15: 1
Fixed 2026-11-15: 2
Fixed 2026-11-15: 3
Fixed 2026-11-15: 4
Fixed 2026-11-15: 5
Fixed 2026-11-15: 6
Fixed 2026-11-15: 7
Fixed 2026-11-15: 9

The fixes are in `scripts/check-site.py` (+30 −27). Each fix's probe ran on the old check and then on the fixed one, in clean clones (see `docs/features/seo/flow.md`, Tasks). Fixes 7 and 9 are refactors whose old behaviour still holds. The clean tree gives 32 PASS before and after. A fresh fix-check agent (sonnet) found 8 of 8 PASS and no regressions. Number 8 needs no code change: it resolves when `docs/features/seo/` is committed.
