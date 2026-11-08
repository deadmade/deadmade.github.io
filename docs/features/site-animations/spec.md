# Site animations: design

Size: a small change (one new stylesheet, one small layout edit, one new check, a few doc lines). This short design is the spec.

## Intent

The site has no motion: every click is a hard cut, and the home page appears all at once. The owner wants it to feel smoother and more alive, in the site's own theme (a night-city terminal and drawing-sheet look), "cool but not over the top".

Owner's words, in order: "cool but not over the top animations"; "Would like to have a smoother more nicer way"; "its to little ... lean into the theme a bit more"; "animations on the svg in work is horrible, animations on deadmade good"; "B pls".

The owner tried a throwaway demo (two rounds, not kept) and picked what to keep. Every motion in the table below comes from that demo; its timings and easing are my guesses, not the owner's.

## Goals

1. The home page arrives with the demo's motion. The name rises line by line and glitches once; the role is typed; the cursor blinks four times and stays; the intro and the three links rise in turn; the picture fades in, its pink edge is drawn, and a scanner line sweeps down it once.
2. Moving between pages is smooth in browsers that support it: the top bar stays where it is, and the page under it is redrawn top to bottom (the work page fades in plainly instead). Other browsers load the page as they do today.
3. The path, now and 404 pages arrive with a title rise; path and now also stagger their rows and plot the pink rule from left to right. The work page gets the plain fade and a rise of its title and subtitle, and nothing else.
4. Links respond to hover and focus: the top-bar links get a sliding pink underline, and the three home links nudge their triangle to the right.

## Non-goals

- No motion at all on the work page's drawings, sheets or title block. The owner rejected it, so CLAUDE.md's rule that the work page's design must not change stands. Nobody edits `layouts/work.html`, the drawing partials or their CSS.
- No scroll-triggered reveals, no parallax, no looping motion, no JavaScript, no new dependency and no new colour (only the pink accent and the existing `--line` violet).

## Anti-goals (a failure even if it works)

- Content that stays hidden when motion is off or when a browser ignores a rule. The base styles are the finished page; motion is added on top of them.
- Any motion for visitors who ask for reduced motion.
- A scrollbar or layout shift on the home page (it must keep fitting one screen from 768×640 up).
- Motion that runs longer than 5 seconds in total on one trigger (WCAG 2.2.2).
- A work page that looks different at rest.

## Constraints

- CSS only. `scripts/check-site.py` fails on a `<script>` or an outside request, and Hugo runs with `--panicOnWarning`.
- Every rule that moves sits inside one `@media (prefers-reduced-motion: no-preference)` block. A browser that doesn't support the query, or a visitor who has turned motion off, therefore gets a static, fully visible page (source: prior-art report, checked; `prefers-reduced-motion` is widely available).
- Page transitions work only in Chrome and Edge 126+ and Safari 18.2+; Firefox has no cross-document view transitions (webstatus API, checked). Parsers ignore the unknown `@view-transition` rule, so Firefox just navigates (spec, checked).
- Scroll behaviour: `html{scroll-behavior:smooth}` (`assets/css/base.css:4`) has no reduced-motion guard today, a follow-up the last run logged. It moves into the same block.

## Approaches

- **A, home page only** (rejected by the owner): only the home motion and the link hover; navigation stays a hard cut. It is the smallest change, but it delivers only half of "smoother".
- **B, home page plus page transitions and the other pages** (picked): A, plus the view transition and the arrival of path, now, 404 and the work title. The work page's content is untouched.

## The motion (all my proposals except where the owner chose; timings are guesses)

| Where | Motion | Timing |
| --- | --- | --- |
| Home name | each line rises 14px and fades in; one-time glitch (pink and violet split, small skew) | rise .7s, second line +.09s; glitch .6s at 1.7s |
| Home role | typed one letter per step; cursor appears after, blinks four times, ends visible | type .85s from .35s; blink .9s ×4 from 1.2s (ends at 4.8s) |
| Home intro and links | rise in turn | .5s, then .62s, .70s, .78s |
| Home picture | fades in; pink edge drawn; scanner line sweeps down once | fade .9s from .1s; draw .7s from .8s; scan 1.1s from 1.5s |
| Path, now, 404, work title | title rises, subtitle .08s later | .6s |
| Path, now rows | rise in turn; the pink rule over the first block is plotted | .08s to .38s steps; rule .9s |
| Between pages | bar named so it stays; `main` named, old content fades out; new content revealed top to bottom with a small rise (home, path, now, 404) or, on the work page, which is not named, the browser's plain cross-fade of the whole page; the browser's own slide of the two named groups is switched off | out .14s; in .5s; the work page's cross-fade is the browser's own (.25s) |
| Hover and focus | top-bar links: sliding pink underline and colour ease; home links: triangle nudges 5px, description colour eases | .18s to .24s |

## Seams

- reduced motion: resolved in `assets/css/motion.css` (one `prefers-reduced-motion: no-preference` block); never seen by `layouts/*.html` (they carry no motion), `base.css`, `path.css`, `tokens.css`, the drawing partials.
- which pages move: resolved in `motion.css` selectors (`body.home`, `.page`, `body.path`, `.bar`, `.go`); never seen by `layouts/work.html`, the drawing partials, the `.sheet` and `.dwg` rules.
- which page is the work page (to leave its `main` unnamed): resolved in `motion.css` with `main:not(:has(.sheet))`; never seen by `layouts/work.html`, which gets no body class.
- browser support for page transitions: resolved by the browser ignoring `@view-transition`; never seen by layouts or by any script (there is none).

## Decisions

On 2026-11-08 the owner answered the grill with "yes do all your recommendations", so items 1 to 4 and 7 are the owner's decisions. Items 5 and 6 are decisions I made; the owner approves them with the spec. The plan review widened item 4, added item 8 and shortened the cursor blink in the motion table; the owner chose each of those three on 2026-11-08.

1. The work page takes part in the page transition, but with a plain fade; every other page gets the top-to-bottom redraw. The work page's drawings neither animate themselves nor get wiped; they fade with the page. `motion.css` recognises the work page by `main:not(:has(.sheet))`, so `layouts/work.html` stays untouched. (Changed during Task 6, see `flow.md`, Deviations: the first build named the work page's `main` too and gave it an explicit `fade .3s` on its new content; that, together with a finished `both` rise on its title, made the drawings raster differently at rest. Now the work page's `main` is unnamed, so it gets the browser's own cross-fade, and the title rise uses fill-mode `backwards`.) This was measured on the demo in Chrome 154, with a throwaway script that recorded the transition's animation names on arrival: going from home to work ran `vt-fade` (the demo's name for the build's `fade`) on the new content, and going from work to path ran the redraw (`vt-in`). The new page's selectors choose the animation for both snapshots. The builder repeats this measurement on the real build.
2. Outside the work page, the transition reveals the new page top to bottom with a small rise instead of a plain cross-fade. The demo's later version did it this way; the owner did not comment on the transition, and said yes to keeping it everywhere but work.
3. Link colour easing and the underline apply only to the top bar and the three home links. The work page's source links and the 404 link keep today's instant hover, so nothing in the work page's body changes.
4. `scripts/check-site.py` gets one new check: in the built CSS, no `animation`, `transition`, `@keyframes` or `view-transition` text appears before the no-preference block starts, and nothing but whitespace follows the block's end. It is the one test of the guarantee that matters most, and it goes with the existing seam test (`check_seams`).
5. `layouts/home.html` wraps the role text in `<span class="typed">`. The typing step count must follow the role text (17 letters today), so the builder either computes it from `params.role` in the layout or leaves a `shortcut:` comment.
6. CLAUDE.md gets the new file in its structure list and a Gotchas line (motion lives in `motion.css`, inside one query, and none of it touches the work page's drawings and sheets).
7. The home intro replays every time a click opens the home page, because CSS cannot tell a repeat visit and the site has no JavaScript. Back and forward restore the page from the browser's cache and are expected not to replay it (inferred, not tested).
8. The browser's own 0.25 s slide of the named bar and content groups is switched off (`::view-transition-group(content)` and `::view-transition-group(bar)` with `animation-name:none`). Measured on a scratch build in Chrome 154: a click on `/work/` scrolled down 1500px otherwise moved the bar from -1500px to 0 and the content from -1457px to +43px, so the bar did not stay where it is. The rule sets `animation-name` only: the `animation` shorthand would also zero the duration that the bar's old and new images inherit from their group, and the old bar would stay drawn under the new one for the whole transition (measured in Chrome 154: with `animation-name:none` the bar's 250ms cross-fade runs). The cost: from a scrolled page, the old content image shows its own top edge during the 0.14s fade-out.

## Verification (what the builder shows)

- `python3 scripts/check-site.py` passes, including the new check.
- In Chrome:
  - after the animations end, every element is at opacity 1;
  - the home page has no vertical or horizontal scroll at 768×640 and 1892×956;
  - clicking a link runs a view transition (`pagereveal` on the new page carries `viewTransition`), and arriving at the work page runs no `content` animation, only the browser's cross-fade of the whole page, not the redraw (read from the animation names during the transition), and the work page at rest is pixel-identical to today's;
  - a click on a link of `/work/` scrolled down about 1500px runs no `-ua-view-transition-group-anim-content` or `-ua-view-transition-group-anim-bar` animation, so the bar and the content do not slide;
  - the work page at rest is pixel-identical to today's (screenshot diff at three scroll positions, as in the demo).
- `git diff` shows `layouts/work.html`, the drawing partials and the drawing CSS unchanged.
- Not checkable by me: a real reduced-motion setting, Firefox, Safari, phones, and how it feels, including how the arrival motion and the page transition look together (the demo ran both on the same elements and nothing measures the stacking). The owner judges those.

## Left to the builder

The builder decides the exact keyframes and the file layout inside `motion.css`, and how to stagger (pure CSS `nth-child`, as in the demo, is fine). The builder also re-measures that Hugo's minifier keeps `@view-transition` and the keyframes (it did for the demo's rules).
