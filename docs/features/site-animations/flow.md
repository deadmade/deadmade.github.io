---
flow: feature
phase: execute
now: Waiting for you: pick how the branch ends.
---

# Site animations: flow

## Request

Hey, could we make a plan to enhance the site with cool but not over the top animations?

## Artifacts

- Prior art: [prior-art.md](prior-art.md) (source-checked and corrected)

- Spec: [spec.md](spec.md) (short design, small change; no builder check)
- Plan: [plan.md](plan.md) (6 tasks, ~107 lines of change; execution method asked at Gate 2)
- ADRs: none (no `docs/adr/`)
- Glossary: none (no `GLOSSARY.md`)

## Gates

- Gate 1, spec approved: 2026-11-08. Reopened 2026-11-08: the plan review widened decision 4 (the check also rejects text after the block), added decision 8 (the browser's group slide is off) and shortened the cursor blink to .9s in the motion table. Approved again 2026-11-08, by the owner's answers to those three findings.
- Gate 2, plan approved: 2026-11-08, execution: native
- Gate 3, review report (/review-code, inline): 2026-11-08; picks 1 to 7, finding 8 left out

## Skipped

- Todo list: this session has no task tools; the phase is tracked by `phase:` above. Accepted by the owner 2026-11-08.
- Review lenses security and risk: not run. The diff touches no input parsing, auth, network, files, processes, secrets or dependencies (security), and no migration, public interface, wire format or hot path (risk); the CSS concatenation line in `head.html` is the only config. Accepted by the owner 2026-11-08.
- pstack `interrogate`, which /review-code offers after a native execution without per-task reviews: not offered, because the resume instruction said not to ask further questions; the final lenses and verifier run instead. Accepted by the owner 2026-11-08.
- Task 6 step 7 click at 0.3 s: the intro animations were paused at 300 ms and the click made, because the harness paints no frames before a screenshot. Accepted by the owner 2026-11-08.
- Task 6, hover and focus (spec goal 4): not driven in a browser; Task 6 had no step for it. Accepted by the owner 2026-11-08.
- Not covered by any lens or by me: Firefox, Safari, a real reduced-motion setting, forced-colors mode, back and forward navigation (spec decision 7), touch hover, and how the arrival motion and the page transition feel together. Accepted by the owner 2026-11-08.
- `pstack-picks:how`: not run as a separate explainer agent. The site is 858 lines outside `docs/`, so I read the layouts, the CSS and the checker directly (cheaper and more exact than an agent's summary). Accepted by the owner 2026-11-08.

## Grounding

Measured/read in this session (verified by reading, not by running the site):

- **Base branch.** The own-layout site exists only on `job-application-portfolio` (10 commits ahead of `main`; branch kept unmerged by the last run, `cf03c61`). `main` still has the old hugo-coder site. Any animation work has to branch from `job-application-portfolio`, not `main`. (`git rev-list --count main..job-application-portfolio` = 10.)
- **Stack.** Hugo 0.166.0 extended, plain CSS concatenated and minified into one fingerprinted file (`layouts/_partials/head.html:14`: `tokens.css`, `fonts.css`, `base.css`, `path.css`). No Sass, no JavaScript.
- **Hard rule: no JavaScript, no external requests.** `scripts/check-site.py:150` fails a page that contains `<script` or `.woff2`; CLAUDE.md repeats it. So every motion option is CSS-only (or an inline SVG attribute).
- **Pages.** Home `layouts/home.html` (hero, picture `.pfp` with a pink diagonal `<line>` at `home.html:8`, name `h1` with one `span` per word, role line with a static `<span class="cursor">_</span>` at `home.html:14`, `.go` list of three links). Work `layouts/work.html` (three `.sheet` articles, each with a `.dwg` SVG drawing). Path `layouts/path.html` and Now `layouts/now.html` (shared `.p-wrap` / `.p-r` rows, a 2px pink rule over the first block, `assets/css/path.css`). 404.
- **Shared chrome.** `layouts/baseof.html:6-13` top bar (`.bar`, `.mark` with the hood triangle `.tri`, `nav` links), footer. The `.tri` hood triangle is "the one shape" (`base.css:11-13`).
- **Existing motion.** None, except `html{scroll-behavior:smooth}` (`base.css:4`) which has no `prefers-reduced-motion` guard (the last run logged this as a follow-up, `job-application-portfolio/flow.md` Parking lot: "inert today because the pages have no in-page anchors"). Hover is only a colour change (`base.css:7`, `base.css:41`). No `transition`, `animation`, `@keyframes` or `@media (prefers-reduced-motion)` anywhere in `assets/css/`.
- **Work page is frozen.** CLAUDE.md "Gotchas": "The work page's design is owner-approved and must not change ... leave `layouts/work.html`, the drawing partials and their CSS alone unless the owner asks for a redesign." Animating the drawings or sheets touches exactly those files/rules (`base.css:61-141`), so it needs the owner's yes. Drawing strokes use `vector-effect:non-scaling-stroke` (`base.css:91,93,94,95,96`), which affects how `stroke-dasharray` line-drawing behaves (inferred; the prior-art agent is checking).
- **Home fits one screen.** The home page is sized so it never scrolls from 768×640 up (`base.css:43-52`, measured by the last run). Any motion on home must use `transform`/`opacity` only so it can't change layout or add a scrollbar (inferred from how layout works; to be measured after building).
- **Previous run's taste notes.** `job-application-portfolio/design-tells.md` S4 lists "scroll-reveals" among the tells of AI-looking template sites (a blog listicle, S4, labelled as such there). The owner chose "dense, technical, drawing-sheet" as the look; motion should read as an engineer's instrument, not a landing-page template. Night-city palette: `--bg:#1A1626`, one accent pink `#F08BB4` (`assets/css/tokens.css`).
- **Checks available.** `python3 scripts/check-site.py` builds like CI and checks pages, metadata, links, bar, sitemap. There is no browser test; layout/motion claims need a rendered check (a browser via the web-mcp `browser` tool or `claude-in-chrome`).
- **No domain docs.** No `GLOSSARY.md`, no `docs/adr/`.

## Prior art

Report landed 2026-11-07 (sonnet agent, [prior-art.md](prior-art.md), 772 words). Source check by a fresh opus agent, every link opened: 32 confirmed, 8 follow from the cited pages, 7 not supported/overstated/not following, 8 cite nothing, 0 could not open (my tally of its rows). I corrected the report in place. Main corrections: the claim that per-element morphs need script was wrong for fixed elements (a nav, wordmark or title present on both pages can be named in CSS alone); the BFCache quote was misattributed; "animations/transitions widely available" was not covered by the page cited; the WCAG 2.2.2 rule is total motion over 5 s, so a finite animation over 5 s also counts. Not reproduced by the checker: the agent's own Hugo minify run (I re-measure at build time).

Report's four approaches (claims are the agent's until the source check lands): A load reveals (keyframes/`@starting-style`), B scroll-driven reveals (`animation-timeline: view()`), C cross-document view transitions (`@view-transition { navigation: auto; }`, no Firefox), D SVG line-draw (`pathLength`). Its gaps: no personal portfolio with verifiable source found that does all four (comparables are docs and demos); `#anchor` vs view-transition and `stroke-dashoffset` compositing are [inferred]; the Hugo minify result is the agent's own local run.

## Findings

### Spike: motion demo (throwaway, agreed by the user: "pls!")

Not building, not product code, never passes a gate; keeping any of it goes through the plan. Lives outside the repo in the session scratchpad (`.../scratchpad/spike/{before,after}-src` are copies of `hugo.toml`, `assets`, `layouts`, `content`, `static`; the repo is untouched). The only differences in `after-src`: a new `assets/css/motion.css` (one `@media (prefers-reduced-motion: no-preference)` block), one word added to the concat list in `layouts/_partials/head.html`, and `html{scroll-behavior:smooth}` moved from `base.css` into that block. Served locally: before http://localhost:8771/ and after http://localhost:8772/ (python `http.server`, two background tasks; stop them when the run ends).

Three layers: (1) cross-document view transitions with `.bar` and `main` named, so the bar stays and only the content fades and slides; (2) arrival: home name lines, role, lede and links rise in one after another, the picture fades, the pink line on the picture draws (`clip-path` on the SVG), the `_` cursor blinks four times; other pages: title and rows rise; (3) hover and focus: link colour eases, the home links' triangles nudge right, the top bar links get a sliding pink underline.

Measured (Chrome 154 via web-mcp browser, 1892×956): home: all 10 animations finished or running as designed, every element ends at opacity 1, scrollHeight = clientHeight (no scroll), scrollWidth = clientWidth. Home → path click: a real view transition ran (`pageswap` had `viewTransition`, navigation `push`; the UA groups `bar`, `content`, `root` and my `vt-in`/`vt-out` animations all finished); path page rows all at opacity 1. Work page: scrollWidth = clientWidth. Built CSS: no motion rule outside the media query (0 before it, 37 inside); Hugo's minifier kept `@view-transition`, all keyframes and the `clip-path` ranges (this reproduces the prior-art agent's minify claim for these rules). Before-site CSS has zero motion words.

Not measured: how it feels (timing and easing are my guesses); Firefox and Safari; real reduced-motion preference on (by construction only: nothing sits outside the query); phone widths; whether the load-reveals on path/work and the view-transition fade stack well (prior art called that untested; both play on those pages in this demo).

### Spike round 2 (throwaway)

User's feedback on round 1: "its to little. The animation on the start is nice but I would like to lean into the theme a bit more. Also it would be awesome if the svg would be a bit more live and not so static". My reading, said out loud and not yet confirmed: "the svg" = the three work-page drawings, and this lifts the CLAUDE.md freeze on that page for motion only (the look at rest must stay identical). Same URLs, rebuilt: after http://localhost:8772/, before http://localhost:8771/. Spike-only changes beyond round 1: `layouts/home.html` wraps the role text in `<span class="typed">`; `layouts/work.html` pipes each drawing partial through `replaceRE`/`safeHTML` so every arrow `<path class="ln">` gets a twin `<path class="sig" pathLength="1">` (the signal; hidden at rest); `assets/css/motion.css` rewritten. (Patch script: `scratchpad/spike/patch.py`.)

What round 2 adds, all my proposals: role line typed letter by letter (17 steps); name glitch once at 1.7 s (pink and violet split, skew, 0.6 s); a scanner line sweeps down the picture once; the cursor appears after typing and blinks four times; the pink rules over the first block on path/now and the sheet frames on work are plotted from the centre or left; page transitions reveal the new content top to bottom (clip-path, 0.5 s) with the bar fixed; the lead drawing is plotted on arrival (boxes, then lines, then labels and arrowheads) and a pink signal runs along each arrow once; the two lower drawings are plotted as they scroll into view (`animation-timeline: view()`, inside `@supports`); while the pointer is on any drawing the signals loop, and stop when it leaves; boxes turn pink on hover.

Measured (Chrome 154, 1892×956, own tab, animations seeked to fixed times for frames): glitch frame at 1.8 s (pink/violet fringe on "Manuel", scanner line on the picture); typing frame at 0.76 s ("Backend" typed, pink edge mid-draw); work page at 0.9 s (boxes drawn, lines half drawn) and at 2.35 s (pink dashes on the arrows); cursor opacity 0 until 1.2 s, then blinking, solid at the end; the two lower drawings are clipped until scrolled into view and complete once their bottom edge is on screen (a tall drawing is partly wiped until then: seen at scroll 900). **At rest the work page is pixel-identical to today's:** screenshots at three scroll positions, before vs after, 0 to 2 pixels of about 500,000 differ by more than 40/255 (max diff 57, JPEG noise), after waiting for the animations to finish. All 18 pulse twins in the two visible drawings end at opacity 0. Built CSS: 0 motion words outside the media query. Hover: tested by copying the hover rules with `:hover` swapped for a class (the browser tool cannot place a real pointer): 18 pulses loop, and after "leaving" 0 live and all at opacity 0. A first version replayed the arrival pulses after leaving (two stacked animations); I rewrote it as one animation (count 1 on arrival, endless on hover) and re-measured the fix.

Not measured: a real pointer; Firefox and Safari; phone widths (the upright drawings get the same twins); a real reduced-motion setting (by construction); how the top-to-bottom page transition looks mid-way (only that it runs); the plotted pink rule on path/now by eye; the `.dwg.v` (hidden) twins' animations stay pending, harmless. Open design cost: endless pulses while hovering are movement over 5 s, so WCAG 2.2.2 would want a pause control for them; mitigation here is that they only run while the pointer is on a drawing. A noted tool quirk: one browser tab kept navigating to `/work/` and `/path/` on its own (probably someone clicking in the shared window), and an unfocused tab stops rendering frames, so every animation test ran in a fresh tab.

## Options

### Motion on the work page's drawings and sheets

Picked: none. The three drawings, the sheets and their CSS stay exactly as they are, so CLAUDE.md's freeze on the work page stands. User, 2026-11-07, after trying round 2: "animations on the svg in work is horrible". Rejected: plot-in, travelling signals, hover loops, scroll-linked wipes on the drawings, and the plotted sheet frames (round-2 spike; the user's words cover "the svg"; the sheet frames were on the same page and I treat them as out too until told otherwise).

### Motion on the home page

Picked: keep round 2's home-page motion (typed role line, one-time name glitch, scanner over the picture, picture edge drawn, staggered arrival, cursor blinking four times). User, 2026-11-07: "animations on deadmade good". My reading, not yet confirmed: "deadmade" is the home page (the name or handle); it could also mean "the rest of the site", so page transitions and the other pages are still open.

### Approach

Picked: B, the home page's motion plus page-to-page transitions and the arrival of the other pages; the work page's content stays untouched. User, 2026-11-08: "B pls". Rejected: A, home page only (the smallest that would work). The two local demo servers (8771, 8772) died with the earlier session (the harness reported them stopped); the demo builds are still in the session scratchpad if the owner wants them served again.

### Grill, round 1 (2026-11-08)

Four questions asked with my recommended answers; the user answered "yes do all your recommendations!". Settled, and folded into the spec:

- **Work page and the page transition.** Picked: plain fade on the work page, top-to-bottom redraw on every other page. The work page is recognised by `html:has(.sheet)` so `layouts/work.html` gets no body class.
- **Link hover polish.** Picked: top bar and the three home links only; the work page's source links and the 404 link keep an instant colour change.
- **New check in `scripts/check-site.py`.** Picked: yes, no motion text in the built CSS before the no-preference block.
- **Home intro replays on every click-arrival.** Picked: accept it (CSS cannot tell a repeat visit; back and forward expected not to replay, inferred).

Checked afterwards (measured, demo only): the `html:has(.sheet)` selector picks the animation for both snapshots: home to work ran `vt-fade`, work to path ran `vt-in`. The frontier is empty. No glossary terms and no ADRs came out of the grill (nothing hard to reverse; the whole change is CSS that a revert undoes).

## Plan review

### Plan review round 1 (2026-11-08)

Three fresh reviewers, one angle each: correctness (fable), fit (opus), simpler (sonnet). 21 findings, 15 distinct (6 duplicates merged), none dropped, none blocking.

- **A. The browser's default group animation slides the bar and content on a scrolled page** (correctness; should-fix). Measured by the reviewer and reproduced by me in Chrome 154 on a scratch build of the plan's CSS: a click on `/work/` scrolled 1500px gave `-ua-view-transition-group-anim-bar` from -1500px to 0 and `-ua-view-transition-group-anim-content` from -1457px to +43px, 250ms. Picked: turn the slide off with `::view-transition-group(content),::view-transition-group(bar){animation-name:none}` (the reviewer's scratch build showed it removes both; cost: the old content image shows its own top edge for the 0.14s fade-out). Not picked: also hide the old content; animate the root instead. Spec decision 8; Task 2; Task 6 step 6.
- **B. The cursor blink ended at 5.2s against the spec's 5s anti-goal** (all three reviewers; should-fix). Arithmetic, and the correctness reviewer measured the end in Chrome. Picked: blink period .9s, ends at 4.8s. Not picked: three blinks; keep 5.2s and reword the anti-goal. Spec motion table; Task 3; Task 6 step 9 now asserts 5s or less.
- **C. The new check searched only before the block** (fit, correctness; should-fix). Read from the code, not run. Picked: it also rejects non-whitespace after the block's closing brace. Not picked: keep it as written. Spec decision 4; Task 1; proved in Task 2 step 4.
- **G. Task 6 had 11 steps and about 30 screenshots against the spec's five checks** (simpler; should-fix). Picked: trim: the block-off comparison covers `/` and `/work/` at the top only, the five-page screenshot comparison is gone, the cheap measurements stay.
- **D. Plain mistakes in my plan**, each seen by at least one reviewer who ran a build (grep for quoted attributes after a minified build, 28 not 29, the stylesheet path `css/main.min.<hash>.css`, a diff that included `head.html`, transition names read per pseudo-element). Picked: fixed. Task 4 now depends on Task 3 (both edit the end of `motion.css`).
- **Consider, six items** (rows beyond the sixth, the AGENTS.md step, `fade` defined once, the pink rule copied from `path.css`, the arrival and the transition running together, the default cross-fade as a smaller slice). Picked: apply the first five; keep the redraw transition as approved. The owner now judges how arrival and transition look together (spec, Verification).

The owner answered with "Turn off the slide (Recommended)", "Blink period 0.9 s (Recommended)", "Also reject anything after the block (Recommended)" and "Apply all (Recommended)".

**Fix check** (one fresh agent that made no edits; it built the edited plan and ran each item in Chrome 154): B, C and D PASS. A failed narrowly: the `animation:none` shorthand also zeroed the duration that the bar's old and new images inherit, so the old bar stayed drawn under the new one. I reproduced it on my scratch build (with the shorthand the bar's cross-fade entries are missing; with `animation-name:none` the 250ms entries are back and the group slide is still gone) and changed the rule to `animation-name:none` in the plan and spec decision 8. G failed on one point: Review Focus 4 promised the triangle nudge but Task 6 step 5 never hovers a link, so I reworded the line and added the 0.5 s sample at 375px. Other items fixed: a retry note for the flaky probe in step 6, the line count here, and two stale names in the spec (`vt-fade`, `pageswap`).

**Fresh eyes** (the third pass): skipped. No decision changed the plan's shape (no new task order, module or library); the edits narrowed or corrected existing tasks.

## Tasks

Workspace: the owner chose to build on the current branch `job-application-portfolio` ("pls build it on this branch"), no new branch and no worktree. Baseline before any change: `python3 scripts/check-site.py` passes. The uncommitted `flake.lock` change and the untracked folders that were present at the start stay out of every files check (the untracked list is saved in the session scratchpad as `untracked-start.txt`).

Task 1: base 6f096d1 (a stash snapshot of the `flake.lock` change); done, files clean (size 14 of ~12); 27 PASS, 0 FAIL; the stray-transition proof failed as planned; committed.

Task 2: base d508d38 (a stash snapshot of the `flake.lock` change); done, files clean (size 34 of ~41); 27 PASS, 0 FAIL; all five minifier strings kept; the after-the-block proof failed as planned; committed.

Task 3: base 6a28b96 (a stash snapshot of the `flake.lock` change); done, files clean (size 33 of ~27); 27 PASS, 0 FAIL; `--n:17` as is and `--n:28` with `HUGO_PARAMS_ROLE` set; committed.

Task 4: base d4f3096 (a stash snapshot of the `flake.lock` change); done, files clean (size 17 of ~21); 27 PASS, 0 FAIL; committed.

Task 5: base daa023b (a stash snapshot of the `flake.lock` change); done, files clean (size 5 of ~6); `AGENTS.md` does not exist, so nothing else to update; committed.

Task 6 (Chrome, scratch builds, no repo files planned): done, with one fix commit (9498b30, see Deviations). Results on the final build (byte-identical to the build tested, checked with `diff -rq`):
- Step 2, work page at rest vs the build from `cf03c61`: 0 differing pixels at scroll 0 and 1900; at 900 only the overlay scrollbar's thumb differs (before the fix: 329 px at scroll 0). After 6 s the work page has 0 animations in `document.getAnimations()`.
- Step 3, block-off build vs base on `/`: differs by up to 6/255 over 129 px, but two screenshots of the base home page also differ from each other by up to 5/255 (62 px), so that is the screenshot's noise floor. `/work/` was byte-identical earlier.
- Step 4, five pages after 6 s: no element or pseudo-element has an opacity other than 1, except the home scanner's `::after` at its intended 0; nothing is running.
- Step 5, 375×800 and 768×640 (iframes, samples at 0.3 to 6 s) and 1892×956 (at 6 s): no horizontal overflow on any of the five pages. Then the home page alone, in iframes at 768×640, 1280×720 and 1892×956, sampled ten times from 0.1 s to 6 s: no vertical and no horizontal overflow at any sample. The harness paints no frames before a screenshot, so the early samples show the animations at their first state (the worst case for the rise offsets); layout does not depend on painting.
- Step 6, transition names (Chrome 154, probe build, `localhost`): see Deviations for the lists. The probe said `no transition` on every try on `127.0.0.1` (four tries, JS and real clicks, also on the earlier build) and worked on `localhost`; I do not know why.
- Step 7, click during the intro: the harness cannot click at 0.3 s (no frames before a screenshot, and then the animations had already finished), so I paused the intro animations at 300 ms and clicked. `/work/` and `/path/` end with no element at an opacity other than 1, and the wordmark click from `/path/` replays the intro (`type` is in `document.getAnimations()`).
- Step 8: on `/now/` and `/404.html` the `h1` animation is `rise` (fill-mode `backwards`), `.p-r` delays are 0.08, 0.14, 0.2, 0.26 s.
- Step 9: home timeline ends at 4.8 s (the cursor blink); the longest single animation is the blink's 3.6 s.
- Step 10: no diff in `layouts/work.html` and the drawing partials against `cf03c61`; `base.css` differs only by the deleted `scroll-behavior` line; `motion.css` names `.sheet` once, in `main:not(:has(.sheet))`.
- `python3 scripts/check-site.py`: 27 PASS, 0 FAIL.

Decisions D to G are the audit file's four Rulings (Fix 1, Fix 3, Fix 7, Fix 5), confirmed 2026-11-08.

Fix 1 to Fix 7 (review picks, see `docs/audits/2026-11-08-review-branch.md`): base 9498b30; files clean (`scripts/check-site.py`, `CLAUDE.md`, `assets/css/motion.css`, all named by their findings); uncommitted until Decide; 27 PASS, 0 FAIL.

## Rulings

- 2026-11-08, Task 6: `assets/css/` was moved to `content/css/` by something other than my commands (both folders' change time is the same instant, 11:31:07 local, which was mid-Task 6; `git status` showed the five files deleted and `content/css/` untracked, and the folder held my uncommitted edit). I moved it back with `mv content/css assets/css` after checking that `assets/css` was absent and `content/css` complete; nothing was lost, the tree was clean again except for my fix, and the later commit contains only `assets/css/motion.css` and `CLAUDE.md`. I do not know the cause (maybe the owner, in a file manager or editor, at the same time) — if it was intended, `head.html` would have to change too. (A) confirmed 2026-11-08.

- 2026-11-08, Task 1: my first version built its message with `hit.group(0)` before the `* bool(hit)` guard and crashed on a clean sheet; I caught it on the clean run and used a plain `if hit:` — no behaviour change from the plan — if wrong, the check crashes instead of reporting. (B) confirmed 2026-11-08.
- 2026-11-08, before Task 1: the plan's Task 6 compared against the branch name `job-application-portfolio`, which stops meaning "before the change" once commits land on it; changed to the starting commit `cf03c61` in the plan's Global Constraints and Task 6 steps 1 and 10 — only wording, no behaviour — if wrong, Task 6 compares the wrong tree. (C) confirmed 2026-11-08.

## Parking lot

From /learn: nothing. The review's four lines are in `docs/audits/2026-11-08-review-branch.md` and were decided at Decide on 2026-11-08: (I) drop, (J) drop, (K) do now (the comment in `assets/css/motion.css` was reworded; done), (L) drop.

## Deviations

### The work page at rest was not pixel-identical with motion on (found in Task 6, step 2)

Status: decided 2026-11-08: (H) confirmed by the owner at Decide (applied earlier in commit 9498b30 without asking, because the resume instruction said not to ask; the change keeps the approved behaviour: the work page fades in plainly, its drawings do not move)

What I measured (Chrome 154, 1892×956, JPEG screenshots diffed with Pillow, scroll top): the work page as built differed from today's by 329 px (max 31/255) at rest although no rule targets its drawings. Bisect: the finished `rise` on `.page h1` and `.page .sub` (fill-mode `both` keeps a transform applied) plus `view-transition-name:content` on `main` (a named element is drawn as its own layer) together cause it; either one alone leaves 34 px (h1/.sub) or 329 px (main). With both removed: 0 px. Base, base and the block-off build were byte-identical to each other.

Options considered:
- Accept a hairline difference in the drawings' anti-aliasing: breaks the stated anti-goal (the work page's drawings stay as approved). Not chosen.
- Fill-mode `backwards` on the h1/.sub rise and leave `main` named on the work page: 34 px left. Not enough.
- (chosen) `backwards` on the rise and `main:not(:has(.sheet)){view-transition-name:content}`, and drop the explicit `html:has(.sheet)::view-transition-new(content){animation:fade .3s ease both}` rule, which has nothing to match once `main` is unnamed on the work page.

Result of the chosen fix (clean build, no probe script): 0 differing pixels against base at scroll 0 and 1900; at 900 only the overlay scrollbar's thumb differs (a timing artifact of the screenshot). The probe build differed by 47 px of 1–3/255 in one 8×8 JPEG block at scroll 0 (cause not found; the clean build is exact). Screenshots taken while the title rise still ran (first 0.7 s) differ by up to 23/255 over the whole page; that is the animation itself.

Transition names measured with the probe on the chosen build (`localhost:8785`): work to path: `vt-in@new(content)`, no `group-anim-content`, no `group-anim-bar`; path to home: `vt-in@new(content)` and `vt-out@old(content)`; home to work: `vt-out@old(content)` and the browser's `root` cross-fade, nothing on `new(content)`; a click from `/work/` scrolled to 1500 px: only `group-anim-root` (viewport-sized, no movement) and `vt-in@new(content)`.

Side effects to know: the work page's cross-fade is the browser's own 0.25 s on the whole page (spec said .3 s); when leaving the work page, its content leaves with the `root` fade instead of `vt-out` (0.14 s). Files changed: `assets/css/motion.css` (three places), the `CLAUDE.md` Gotchas line, the spec (decision 1, motion table, work-page mechanism, verification bullet) and the plan (Task 6 step 6 and the two `html:has(.sheet)` mentions). The plan's Task 2 and 3 code blocks still show the first version.

## Walkthrough

| goal | plan task | file:line | test |
| ---- | --------- | --------- | ---- |
| Goal 1: the home page arrives with the demo's motion | Task 3 | `assets/css/motion.css:46-61`, `layouts/home.html:14` | Task 6 steps 4, 7 and 9: every element ends at opacity 1; the intro replays on a wordmark click; the timeline ends at 4.8 s |
| Goal 2: page transitions; the work page fades plainly | Task 2, then fix `9498b30` | `assets/css/motion.css:13-22` | Task 6 step 6: the names on work, path, home and a click from `/work/` scrolled to 1500 px; no group slide |
| Goal 3: path, now and 404 arrive with a title rise; rows and rule on path and now | Task 4, then fix `9498b30` | `assets/css/motion.css:65-79` | Task 6 steps 4 and 8: `rise`, delays 0.08/0.14/0.2/0.26 s, nothing left at another opacity |
| Goal 4: hover and focus on the top bar and the home links | Task 2 | `assets/css/motion.css:25-30` | not driven in a browser (Task 6 has no step for it); the rules were read, and the build and `check-site.py` pass |
| Anti-goal: nothing hidden when motion is off or a rule is ignored | Task 1 and Task 2 | `scripts/check-site.py:170-183`, `assets/css/motion.css:4` | Task 1 and 2 proof runs failed as planned; Task 6 step 3: the block-off build equals the base within screenshot noise |
| Anti-goal: the work page looks different at rest | Task 4, then fix `9498b30` | `assets/css/motion.css:15`, `assets/css/motion.css:65-66` | Task 6 step 2: 0 differing pixels at scroll 0 and 1900; step 10: no diff in `layouts/work.html` or the drawing partials |
| Anti-goal: more than 5 s of motion on one trigger | Task 3 | `assets/css/motion.css:50` | Task 6 step 9: the latest end is 4.8 s, the longest single animation 3.6 s |
| Anti-goal: a scrollbar or layout shift on the home page | Task 3 | `assets/css/motion.css:46-61` | Task 6 step 5: no overflow in either direction on the home page at 768×640, 1280×720 and 1892×956, sampled from 0.1 s to 6 s; no horizontal overflow on the other pages at 375×800 and 768×640 |
| Constraint: `scroll-behavior` moves into the block | Task 2 | `assets/css/motion.css:6`, `assets/css/base.css:3` | Task 6 step 10: `base.css` differs only by the removed line |
| Doc: CLAUDE.md says where the motion lives | Task 5, then fix `9498b30` | `CLAUDE.md:63` | none (prose); read against the final CSS |

## Review

Inline /review-code on `branch` against `cf03c61`, stopped after its Phase 6. Latest run: `python3 scripts/check-site.py` on 9498b30, 27 PASS, 0 FAIL; the only tracked change was the older `flake.lock`. Execution ran natively (no per-task reviews). Lenses: correctness, lean and spec, tests, docs; one verifier; the audit file was copyedited (checked, applied). Audit file: `docs/audits/2026-11-08-review-branch.md`. Result: eight findings, none `fix before merge`, all `worth doing` (one medium: the check misses `scroll-behavior`); the lean lens found nothing. Gate 1 of the review is this run's Gate 3.

Review verdict: 0 to fix before merge, 8 worth doing. Gate 3: picks 1 to 7. Fixed 2026-11-08: 1 to 7 (the fixes to `scripts/check-site.py`, `CLAUDE.md` and the comments in `assets/css/motion.css`, uncommitted until Decide); a fresh fix checker passed all seven; `check-site.py` 27 PASS, 0 FAIL, built stylesheet unchanged. Left: 8 (motion text in `layouts/`, beyond spec decision 4). Four Parking-lot lines went into the audit file; they are decided at Decide.

## Learned

- 2026-11-08, `docs/solutions/checking-motion-in-the-browser-tool.md` (new): the browser tool's four traps when checking motion (the view-transition probe says "no transition" on `127.0.0.1` and works on `localhost`; no frames before a screenshot; JPEG noise up to 7 of 255; tab state), and how to measure a difference through them.
- 2026-11-08, `CLAUDE.md`, Gotchas (one line): points to that note before any motion check in a browser.
- Dropped as not worth keeping: the work page's rest-state difference (already the Gotchas bullet that Fix 2 rewrote), the `assets/css` move (cause unknown, nothing to act on), the Bash cwd drift, the tool-output filter on tables. Parked from /learn: nothing.

## Run verdict

worked as a whole: yes; clean: no (2026-11-08; one deviation during verification and seven review fixes)
