# Review: branch (site animations)

The branch job-application-portfolio, compared with cf03c61 (the tip before this feature), changes 6 files (+99 −5) in 6 commits. The count leaves out flake.lock, which was already modified before the feature. The intent is in `docs/features/site-animations/spec.md` and `plan.md` (approach B). The last commit, 9498b30, is a fix made during verification (see flow.md, Deviations).

Four lenses ran: correctness (with a neutral brief, because the tree has uncommitted and untracked files); lean and spec; tests; and docs. The security and risk lenses were skipped (see Skipped). Four lens agents and one verifier did the review, and no lens saw another's findings.

Checks: `python3 scripts/check-site.py` on 9498b30 gives 27 PASS and 0 FAIL, and the only tracked change in the tree is the older `flake.lock` one.

## Findings

<!-- Every verified finding, most severe first, `confirmed` or `plausible` in the evidence; `bucket` is
`fix before merge` or `worth doing`, so `all fix` resolves from this table. Then the dropped count. After the gate:
`Picks: <finding numbers> | none`, then one line `Fixed <date>: <number>` per pick once its check passes. -->

| #   | severity | where | finding | evidence | fix (recommended) | bucket |
| --- | -------- | ----- | ------- | -------- | ----------------- | ------ |
| 1 | medium | `scripts/check-site.py:173` | The new check's word list does not include `scroll-behavior`, the one motion property that existed before this change and that the spec says moves into the block (spec.md:38). If `html{scroll-behavior:smooth}` goes back into `base.css`, the check passes, and visitors who asked for reduced motion get smooth scrolling. | confirmed: three lenses found it, and the verifier appended the line to `base.css` in a scratch copy and got `PASS seams -`. With the word added, the clean tree passes and the copy fails with `scroll-behavior in main.min.<hash>.css before the no-preference block` | Add `\|scroll-behavior` to the pattern (the check does not search the line inside the block). | worth doing |
| 2 | low | `CLAUDE.md:63` | The Gotchas bullet ends "the work page gets only the browser's plain page cross-fade", but the work page's title and subtitle also rise (`motion.css:65-66`, spec goal 3). A later session may take the rise for a leak and remove it or switch it to `both`. The bullet also runs 97 words without a break, and it does not explain "rastered". | confirmed: two lenses found it; the built `/work/` has `main.page` and `p.sub`; the word count is from `wc -w` on the bullet | Split it into two bullets: one on where motion lives and what guards it, one on the work-page rule. Say that the work page's transition is the plain cross-fade, that its title and subtitle still rise with fill-mode `backwards`, and that naming its `main` or leaving a finished `both` fill on the title paints its drawings differently. | worth doing |
| 3 | low | `scripts/check-site.py:172` | The gate pattern matches only the start of the media query. A header such as `@media (prefers-reduced-motion: no-preference),(min-width:0){` (a comma is an OR) or `…,all{` always applies, so all motion plays under reduced motion, and the check still passes. | confirmed: the verifier changed the header both ways in a scratch copy and got `PASS seams -` | End the pattern with a lookahead, `no-preference\s*\)(?=\s*\{)`. The tests lens proposed `\)\s*\{`, which is wrong: it moves `gate.end()` past the brace, so the clean build fails with `text after the no-preference block` (the verifier showed this). The lookahead passes the clean tree and fails both mutations. | worth doing |
| 4 | low | `scripts/check-site.py:177-183` | The fallback `end = len(css)` lets unbalanced braces pass the "text after the block" check: with a `{` inside a string in the block and `a{animation:x 1s}` after the block, the check gives `PASS`. | confirmed: the verifier built that case, with the tail `…both}}a{animation:x 1s}`, and got `PASS seams -` | Replace `end` with a `for`/`else`: at depth 0, check `css[i+1:].strip()` and stop; in the `else`, report "the no-preference block in X never closes". The clean tree passes and the mutation fails. | worth doing |
| 5 | low | `assets/css/motion.css:63-73` | The comments say "the rows one after another" and "delays for the first six rows", but `:nth-child` counts siblings inside each parent. On `/path/` the three sections (toolkit, languages, hobbies) are children 2 to 4 of `.p-wrap`, so they rise with steps 2 to 4 (.14, .2, .26 s), and no element uses the .38 s delay. The plan makes this deliberate (plan.md:281, "as in the demo the owner saw"), but no other file says so. | confirmed: the built `/path/index.html` has seven `.p-r` (four `li` in `ol.p-steps`, three `section` in `.p-wrap`), and the delays follow from the selectors | No behaviour change. Reword the comment to "delays by position inside the parent; on /path/ toolkit, languages and hobbies share the delays of steps 2 to 4 (as in the demo); a 7th child gets none". Optionally, change the spec's motion table to "up to .26 s on today's content". | worth doing |
| 6 | low | `assets/css/motion.css:74-79` | The plotted pink rule copies `2px` and the accent from `path.css`, and its comment points at them by line number (12 and 38), which goes stale. If the border in `path.css` becomes 3px or another colour, the plotted rule stays 2px pink over the new gap, while reduced motion shows the new border. | confirmed by reading, not rendered: `path.css:12` is `body.path .p-steps{…border-top:2px solid var(--accent)}`, and line 38 is the `.p-now` one | In the comment, name the selectors (`body.path .p-steps` and `body.path .p-now` in `path.css`: 2px, accent) instead of line numbers. | worth doing |
| 7 | low | `CLAUDE.md:49`, `layouts/home.html:14` | `[params] role` now also sets the typing step count (`--n` from `strings.RuneCount`), but CLAUDE.md lists it only as text. If the role wraps on a phone, the typing reveals columns across both lines instead of letters. | plausible: builds with `HUGO_PARAMS_ROLE` give `--n:41` for 41 characters. The wrap case is by reasoning (about 31 characters fit at 375 px, about 26 at 320 px), with no browser run. An empty role gives `--n:0` with an empty span, which shows nothing either way | Add one clause to CLAUDE.md: the role is also the typed line (the step count follows its length), so keep it to one line on a phone, about 25 characters. | worth doing |
| 8 | low | `scripts/check-site.py:184-187` | The check reads only `*.css`, so motion placed in a layout (`<style>`, `style="animation:…"`, an SVG `<animate>`) passes. Spec decision 4 promises only "in the built CSS", so the check does what was agreed; the seam lines ("layouts carry no motion") describe the design, not the check. | confirmed mechanically: the verifier put each of the three into a layout in scratch copies and got `PASS seams -` each time | Optional, because it goes beyond decision 4: add one line to the existing source loop, limited to `layouts/`, that matches `animat\|transition\|keyframes` (the clean tree has no match). | worth doing |

Dropped: none of the nine merged candidates. The verifier trimmed two parts (the empty-role case in 7, and the "(all motion, last)" wording in 2). The lean lens dropped five of its own candidates as matters of taste or as decisions already stated, and it returned no findings. No finding is `fix before merge`, because nothing here ships a wrong build.

Picks: 1, 2, 3, 4, 5, 6, 7 (2026-11-08; 8 left out)

Fixed 2026-11-08: 1, 2, 3, 4, 5, 6, 7 (a fresh fix checker passed all seven; the check is green with 27 PASS and the built stylesheet is unchanged). Finding 8 was not picked.

## Tasks

<!-- One line per task: `Fix <n>: base <sha>`, untracked at start: <files or none>, then `files clean` or
`deviation` (see Deviations). -->

- Fix 1, Fix 3, Fix 4: base 9498b30; untracked at start: the planning folders and mockups that were already there, `docs/features/site-animations/` and `docs/audits/`; files `scripts/check-site.py`; files clean. Failing proof first: a scratch export of HEAD with four mutations (`scroll-behavior` in `base.css`, the header `…no-preference),(min-width:0){`, the header `…no-preference),all{`, a `{` in a string plus text after the block) passed the old check; the fixed check fails all four, passes the clean tree and passes `overscroll-behavior` in `base.css`.
- Fix 2, Fix 7: base 9498b30; files `CLAUDE.md`; files clean.
- Fix 5, Fix 6: base 9498b30; files `assets/css/motion.css`; files clean (comments only; the built stylesheet is byte-identical, `main.min.2eb37f15…css`).

## Rulings

<!-- Calls the fixes made on their own (not deviation-class), one line each, as they are made. -->

- 2026-11-08, Fix 1: the pattern is `(?<![\w-])scroll-behavior`, not the bare word — so a future `overscroll-behavior` (not motion) does not fail the check — costs nothing if wrong beyond a missed `x-scroll-behavior`.
- 2026-11-08, Fix 3: a lookahead `(?=\s*\{)` after the query, not the tests lens's `\)\s*\{` — the verifier showed the latter fails the clean build — a query list now fails closed with the first motion word as its message, which names the wrong cause.
- 2026-11-08, Fix 7: the role limit "about 25 characters" comes from the verifier's estimate (about 31 characters fit at 375 px, about 26 at 320 px), not from a measurement — if wrong, the advice is a little off.
- 2026-11-08, Fix 5: the optional change to the spec's motion table ("up to .26 s on today's content") was not made; the CSS comment now says it.

## Parking lot

<!-- Cleanups and ideas outside a fix, one line each (`file`: what); not done. The user picks at Decide. -->

- `scripts/check-site.py`: when the gate header is not the bare form (a comma list, `screen and`), the check fails closed but names the first motion word instead of the real cause; say "the no-preference block is not a plain `@media (prefers-reduced-motion: no-preference)`" in that case. Decided 2026-11-08: drop.
- `scripts/check-site.py`: the brace scan is not string-aware, so a `{` in a string inside the block cancelled by a `}` in a string after it still passes (contrived, and the old code passed it too). Decided 2026-11-08: drop.
- `assets/css/motion.css`: the new comment says "as in the demo", but the demo was a throwaway that was not kept (spec.md:11); reword to "approved by the owner from the demo". Decided 2026-11-08: do now (done).
- `scripts/check-site.py`: finding 8 (motion text in `layouts/`) was not picked; revisit if layouts ever carry inline styles. Decided 2026-11-08: drop.

## Deviations

<!-- Decisions that go to the user, one per `### <deviation>` heading, then `Status: open` or
`Status: decided <date>: <what>`; below it, why the pick doesn't hold and the options with a recommendation. -->

## Skipped

<!-- Checks and lenses skipped, and why. -->

- Security lens: the diff touches no input parsing, auth, network, files, processes, secrets or dependencies.
- Risk lens: the diff has no migration, public interface, wire format or hot path; the CSS concatenation line in `head.html` is the only config it changes.
- pstack `interrogate` (offered after a native execution): not offered.
- Not covered by any lens or by me: Firefox, Safari, a real reduced-motion setting, forced-colors mode (the path and now rule is a transparent border plus a pseudo-element), back and forward navigation (spec decision 7), touch hover, and how the arrival motion and the page transition feel together.

All rows above accepted by the owner 2026-11-08, at Decide.

## Run verdict

<!-- The user's, at Decide: worked as a whole: yes | no; clean: yes | no. -->

worked as a whole: yes; clean: no (2026-11-08)
