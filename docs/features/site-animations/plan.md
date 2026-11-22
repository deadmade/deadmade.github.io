# Site animations Implementation Plan

<!-- glance -->
```
Plan: Site animations · 6 tasks · ~107 lines · 8 files
 1  [1 Check that motion stays…]
 2  [2 motion.css with page tr… ←1]
 3  [3 Home arrival ←2]
 4  [4 Arrival of the other pa… ←2,3]
 5  [5 Update CLAUDE.md ←2,3,4]  [6 Verify in Chrome ←1,2,3,4]

#  does                                                          files  adds                            size
1  Makes `scripts/check-site.py` fail when the built styleshee…  1      nothing new                     ~12
2  Adds the stylesheet with the page-to-page transition (the w…  3      `assets/css/motion.css`, the …  ~41
3  Makes the home page arrive with the name rising and glitchi…  2      the keyframes `draw`, `type`,…  ~27
4  Makes the work, path, now and 404 pages arrive with a title…  1      the keyframes `plot-x`          ~21
5  Tells a future session that motion lives in `motion.css`, w…  1      nothing new                     ~6
6  Shows, by measurement on the real build, that the motion wo…  0      nothing new                     ~0
```
<!-- /glance -->

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the approved CSS-only motion (home intro, page-to-page transitions, arrival of the other pages, link hover) without changing the work page's drawings or sheets.

**Architecture:** One new stylesheet, `assets/css/motion.css`, goes last in the concatenated stylesheet. Everything that moves sits in its single `prefers-reduced-motion: no-preference` block, so the base styles stay the finished page. The rest of the change is small: one layout edit gives the home role text a hook, one check in `scripts/check-site.py` guards the block, and CLAUDE.md gets two lines. The home picture's pink edge is drawn with `clip-path`, which needs no markup change. The arrival motion (Tasks 3 and 4) and the page transition (Task 2) run on the same elements. The demo ran both and the owner approved them; nothing measures how they look together, so the owner judges that.

**Tech Stack:** Hugo Extended 0.166.0, plain CSS, Python 3 stdlib (`scripts/check-site.py`).

**Spec:** [spec.md](spec.md). The reference demo was a throwaway. Its rules for the work page's drawings and sheets (`.sig`, `.dwg`, `.sheet::before/::after`, `.ct`, `.om`) are not in this plan and must not be added.

## Global Constraints

- Seam lines (from the spec):
  - reduced motion: resolved in `assets/css/motion.css` (one `prefers-reduced-motion: no-preference` block); never seen by `layouts/*.html` (they carry no motion), `base.css`, `path.css`, `tokens.css`, the drawing partials.
  - which pages move: resolved in `motion.css` selectors (`body.home`, `.page`, `body.path`, `.bar`, `.go`); never seen by `layouts/work.html`, the drawing partials, the `.sheet` and `.dwg` rules.
  - which page is the work page (to leave its `main` unnamed): resolved in `motion.css` with `main:not(:has(.sheet))`; never seen by `layouts/work.html`, which gets no body class.
  - browser support for page transitions: resolved by the browser ignoring `@view-transition`; never seen by layouts or by any script (there is none).
- One implementation gets no interface; one caller gets no helper; no option nobody sets.
- CSS only: no JavaScript in the repo, no new dependency, no new colour (the `--accent` pink and the `--line` violet only), no request that leaves the site. Hugo runs with `--panicOnWarning`.
- The base styles are the finished page. Nothing outside the no-preference block hides, moves or times anything.
- `layouts/work.html`, `layouts/_partials/drawing-*.html` and the drawing CSS in `assets/css/base.css` are not edited. No rule in `motion.css` names `.sheet`, `.dwg`, `.fig`, `.sh` or `.tb`, except the one selector `main:not(:has(.sheet))`.
- Stack skill: none, because this is motion on an existing design and the owner did not name hallmark.
- Work on the branch `job-application-portfolio` itself (the owner chose that over a new branch), because the own-layout site exists only there. Its tip before Task 1 is commit `cf03c61`; Task 6 compares against that commit. Commit messages are one sentence with no co-author line. Do not push or merge.
- Timings, easing and keyframes come from the spec's motion table; the CSS below is that table written out.

## Test seams

- `python3 scripts/check-site.py` (builds like CI, reads the built CSS and pages): catches motion text outside the no-preference block, a missing or external reference, a `<script>` and a changed page set. It misses whether anything moves, whether it looks right, and whether content ends visible.
- The built site in Chrome, driven by the browser tool (Task 6 only): catches content stuck hidden, page scroll, whether the transition runs, which animation the work page gets, and any pixel change on a page at rest or with the block switched off. It misses Firefox, Safari, phones, a real reduced-motion setting and how the motion feels; the owner judges those.

## Review Focus

1. If the role text in `hugo.toml` changes, the typing must still step once per letter (Task 3, step 4).
2. For a browser or visitor that skips the block, the home and work pages must render exactly as today, with nothing hidden (Task 6, step 3).
3. After a click while the home intro still runs, the next page must still end fully visible (Task 6, step 7).
4. In a narrow window, the rise and the reveal clip must not add a horizontal scrollbar on any page, early or late in the animation (Task 6, step 5).
5. After a click on a page scrolled far down, the bar and the content must not slide (Task 6, step 6).

---

### Task 1: Check that motion stays inside the block

**Does:** Makes `scripts/check-site.py` fail when the built stylesheet has any motion text before the `prefers-reduced-motion: no-preference` block, or anything but whitespace after the block's end.
**Depends on:** none
**Adds:** nothing new
**Size:** ~12

**Files:**
- Modify: `scripts/check-site.py`

**Interfaces:**
- Consumes: the `problems` list and the `check("seams", "-", problems)` call inside `check_seams(out)`.
- Produces: two more problem lines in the `seams` check, `<word> in <sheet name> before the no-preference block` and `text after the no-preference block in <sheet name>`. Tasks 2 to 4 must pass it.

- [ ] **Step 1: Run the check as it is**

Run: `python3 scripts/check-site.py`
Expected: all lines `PASS`, including `PASS seams -`.

- [ ] **Step 2: Add the test to `check_seams`**

In `check_seams(out)`, before the `for source in ...` loop, add a loop over `sorted(out.rglob("*.css"))`. For each sheet, the loop finds the first `@media\s*\(\s*prefers-reduced-motion\s*:\s*no-preference\s*\)` match and searches the text before it (the whole sheet when there is no match) for `animation|transition|@keyframes|view-transition`. A hit adds `"<word> in <sheet name> before the no-preference block"` to `problems`. The loop does not search the block's own text. When there is a match, the loop also walks the braces from the first `{` after it to the matching `}` (the built CSS has no braces in strings); if anything but whitespace follows that `}`, it adds `"text after the no-preference block in <sheet name>"`.

- [ ] **Step 3: Prove the first half can fail**

Append `a{transition:color 1s}` to `assets/css/base.css`, then run `python3 scripts/check-site.py`.
Expected: `FAIL seams -: transition in main.min.<hash>.css before the no-preference block`, exit 1. Remove the line again. (Task 2, step 4 proves the second half, once a block exists.)

- [ ] **Step 4: Run it clean**

Run: `python3 scripts/check-site.py`
Expected: all `PASS`.

- [ ] **Step 5: Commit**

```bash
git add scripts/check-site.py
git commit -m "Check that motion CSS stays inside the no-preference block."
```

### Task 2: motion.css with page transitions and link hover

**Does:** Adds the stylesheet with the page-to-page transition (the work page gets a plain fade, and the browser's own slide of the named groups is off), the hover and focus rules for the top bar and home links, and smooth scrolling, all inside the one no-preference block.
**Depends on:** Task 1
**Adds:** `assets/css/motion.css`, the custom property `--ease` and the keyframes `rise`, `fade`, `vt-in`, `vt-out`
**Size:** ~41

**Files:**
- Create: `assets/css/motion.css`
- Modify: `layouts/_partials/head.html`
- Modify: `assets/css/base.css`

**Interfaces:**
- Consumes: the Task 1 check; the classes `.bar`, `.bar nav`, `.go`, `.desc`, `.tri` and `main` in the layouts.
- Produces: `--ease`, `@keyframes rise` (from `opacity:0` and `translateY(14px)`) and `@keyframes fade` (from `opacity:0`), which Tasks 3 and 4 use. The block's closing `}` is the last line of the file, and Tasks 3 and 4 add their rules above it.

- [ ] **Step 1: Create `assets/css/motion.css`** with exactly this content:

```css
/* Motion for the site. Every rule that moves sits inside the one no-preference query below, so the base styles stay
   the finished, visible page: with reduced motion, or in a browser that ignores a rule, nothing is hidden.
   scripts/check-site.py fails on motion text before this query. Nothing here touches the work page's drawings or sheets. */
@media (prefers-reduced-motion: no-preference){
  :root{--ease:cubic-bezier(.2,.7,.2,1)}
  html{scroll-behavior:smooth}
  @keyframes rise{from{opacity:0;transform:translateY(14px)}}
  @keyframes fade{from{opacity:0}}

  /* page to page (Chrome, Edge, Safari 18.2+; other browsers just load the page): the bar keeps its place and the page
     under it is redrawn top to bottom; the work page, recognised by its sheets, gets a plain fade instead */
  @view-transition{navigation:auto}
  .bar{view-transition-name:bar}
  main{view-transition-name:content}
  /* the browser's own slide of the two named groups is off: from a scrolled page it would move the bar and the content by hundreds of pixels.
     animation-name only: the shorthand would also zero the duration that the bar's own cross-fade inherits from its group */
  ::view-transition-group(content),::view-transition-group(bar){animation-name:none}
  ::view-transition-old(content){animation:vt-out .14s ease-in both}
  ::view-transition-new(content){animation:vt-in .5s var(--ease) both}
  html:has(.sheet)::view-transition-new(content){animation:fade .3s ease both}
  @keyframes vt-out{to{opacity:0}}
  @keyframes vt-in{from{opacity:0;clip-path:inset(-20px -20px 100% -20px);transform:translateY(8px)}to{opacity:1;clip-path:inset(-20px)}}

  /* hover and focus: the top bar and the three home links only */
  .bar a,.go a{transition:color .18s ease}
  .bar nav a{background:linear-gradient(var(--accent),var(--accent)) 0 100%/0 1px no-repeat;transition:background-size .24s var(--ease),color .18s ease}
  .bar nav a:hover,.bar nav a:focus-visible{background-size:100% 1px}
  .go .desc{transition:color .18s ease}
  .go .tri{transition:transform .24s var(--ease)}
  .go a:hover .tri,.go a:focus-visible .tri{transform:translateX(5px)}
}
```

- [ ] **Step 2: Add the file last to the stylesheet.** In `layouts/_partials/head.html`, append `(resources.Get "css/motion.css")` after `(resources.Get "css/path.css")` in the `resources.Concat` slice. It must stay last, so that the block ends the built file.

- [ ] **Step 3: Move smooth scrolling.** Delete the line `html{scroll-behavior:smooth}` (line 4) from `assets/css/base.css`.

- [ ] **Step 4: Build and check**

Run: `python3 scripts/check-site.py`
Expected: all `PASS`, including `PASS seams -`.

Then build into a scratch folder with the CI command from CLAUDE.md, and confirm that the built stylesheet keeps what the demo's minify run kept: `grep -o '@view-transition{[^}]*}\|@keyframes vt-in\|clip-path:inset(-20px)\|prefers-reduced-motion:no-preference\|::view-transition-group(content),::view-transition-group(bar){animation-name:none}' <folder>/css/main.min.*.css` prints all five. If the minifier drops or rewrites one, stop and report it.

Prove the second half of Task 1's check: append `a{color:red}` to the end of `assets/css/motion.css` and run `python3 scripts/check-site.py`.
Expected: `FAIL seams -: text after the no-preference block in main.min.<hash>.css`. Remove the line again and rerun: all `PASS`.

- [ ] **Step 5: Commit**

```bash
git add assets/css/motion.css layouts/_partials/head.html assets/css/base.css
git commit -m "Add motion.css with page transitions and link hover."
```

### Task 3: Home arrival

**Does:** Makes the home page arrive with the name rising and glitching once, the role typed, a cursor that blinks four times, the intro and links rising in turn, and the picture fading in with its pink edge drawn and a scanner sweep.
**Depends on:** Task 2
**Adds:** the keyframes `draw`, `type`, `caret`, `scan`, `glitch`; the class `typed`; the custom property `--n` (set inline in `layouts/home.html`)
**Size:** ~27

**Files:**
- Modify: `layouts/home.html`
- Modify: `assets/css/motion.css`

**Interfaces:**
- Consumes: `--ease`, `@keyframes rise` and `@keyframes fade` from Task 2; the classes `.home`, `.lede`, `.go`, `.pfp`, `.pfp-img`, `.role` and `.cursor` already in `home.html`.
- Produces: `<span class="typed" style="--n:N">` around the role text, where N is the role's letter count.

- [ ] **Step 1: Wrap the role text.** In `layouts/home.html`, replace the role line with:

```html
    <p class="role"><span class="typed" style="--n:{{ strings.RuneCount site.Params.role }}">{{ site.Params.role }}</span><span class="cursor">_</span></p>
```

- [ ] **Step 2: Add the home rules** to `assets/css/motion.css`, above the closing `}`:

```css
  /* ---- home ---- */
  @keyframes draw{from{clip-path:inset(-4px -4px 100% -4px)}to{clip-path:inset(-4px)}}
  @keyframes type{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0)}}
  @keyframes caret{0%,49%{opacity:1}50%,99%{opacity:0}100%{opacity:1}}
  @keyframes scan{0%{top:-36px;opacity:0}12%{opacity:1}88%{opacity:1}100%{top:100%;opacity:0}}
  /* a short signal glitch: the letters split into pink and violet and jump a few pixels, twice, then settle */
  @keyframes glitch{
    0%,100%{text-shadow:none;transform:none}
    8%{text-shadow:-5px 0 var(--accent),5px 0 var(--line);transform:translateX(3px)}
    16%{text-shadow:4px 0 var(--accent),-4px 0 var(--line);transform:translateX(-4px) skewX(-4deg)}
    24%{text-shadow:none;transform:none}
    52%{text-shadow:-3px 0 var(--accent),3px 0 var(--line);transform:translateX(2px)}
    60%{text-shadow:none;transform:none}
  }
  .home h1 span{animation:rise .7s var(--ease) both,glitch .6s linear 1.7s}
  .home h1 span + span{animation-delay:.09s,1.79s}
  /* the role is typed one letter per step (--n is its letter count), then the cursor blinks four times (ends at 4.8s) and stays */
  .typed{display:inline-block;animation:type .85s steps(var(--n)) .35s both}
  .cursor{opacity:0;animation:caret .9s steps(1) 1.2s 4 forwards}
  .home .lede{animation:rise .6s var(--ease) .5s both}
  .home .go li{animation:rise .5s var(--ease) both}
  .home .go li:nth-child(1){animation-delay:.62s}
  .home .go li:nth-child(2){animation-delay:.7s}
  .home .go li:nth-child(3){animation-delay:.78s}
  .home .pfp-img{animation:fade .9s ease .1s both}
  .home .pfp svg{animation:draw .7s cubic-bezier(.5,0,.2,1) .8s both}
  /* a scanner sweeps down the picture once, after the pink edge is drawn */
  .home .pfp-img::after{content:"";position:absolute;left:0;right:0;top:-36px;height:36px;opacity:0;pointer-events:none;
    background:linear-gradient(transparent,color-mix(in srgb,var(--accent) 38%,transparent) 88%,var(--accent));
    animation:scan 1.1s cubic-bezier(.5,0,.3,1) 1.5s both}
```

- [ ] **Step 3: Check**

Run: `python3 scripts/check-site.py`
Expected: all `PASS`.

- [ ] **Step 4: The step count follows the role.** Build the site into a scratch folder twice: once as it is, and once with `HUGO_PARAMS_ROLE="Backend developer, then more"` in the environment (Hugo honours it). On both builds, run `grep -o 'class="\?typed"\? style="\?--n:[0-9]*' <folder>/index.html` (the pattern allows for missing quotes, because a minified build strips them).
Expected: `--n:17` for "Backend developer" and `--n:28` for the longer text.

- [ ] **Step 5: Commit**

```bash
git add layouts/home.html assets/css/motion.css
git commit -m "Add the home page arrival motion."
```

### Task 4: Arrival of the other pages

**Does:** Makes the work, path, now and 404 pages arrive with a title rise, and makes the path and now rows rise in turn with the pink rule plotted from left to right.
**Depends on:** Tasks 2, 3
**Adds:** the keyframes `plot-x`
**Size:** ~21

**Files:**
- Modify: `assets/css/motion.css`

**Interfaces:**
- Consumes: `--ease` and `@keyframes rise` from Task 2; the classes `.page`, `.sub`, `body.path`, `.p-r`, `.p-steps` and `.p-now` in the layouts and `path.css`. This task depends on Task 3 only because both tasks add their rules above the block's closing `}`, so run them one after the other.
- Produces: nothing a later task uses.

- [ ] **Step 1: Add the rules** to `assets/css/motion.css`, above the closing `}`:

```css
  /* ---- work, path, now, 404: the title, then the rows one after another ---- */
  .page h1{animation:rise .6s var(--ease) both}
  .page .sub{animation:rise .6s var(--ease) .08s both}
  /* delays for the first six rows; a seventh row would rise without a delay */
  body.path .p-r{animation:rise .55s var(--ease) both}
  body.path .p-r:nth-child(1){animation-delay:.08s}
  body.path .p-r:nth-child(2){animation-delay:.14s}
  body.path .p-r:nth-child(3){animation-delay:.2s}
  body.path .p-r:nth-child(4){animation-delay:.26s}
  body.path .p-r:nth-child(5){animation-delay:.32s}
  body.path .p-r:nth-child(6){animation-delay:.38s}
  /* the pink rule over the first block is plotted from left to right (the border keeps its 2px of space);
     the 2px and the accent copy path.css, lines 12 and 38: change them together */
  @keyframes plot-x{from{transform:scaleX(0)}}
  body.path .p-steps,body.path .p-now{position:relative;border-top-color:transparent}
  body.path .p-steps::before,body.path .p-now::before{content:"";position:absolute;left:0;right:0;top:-2px;height:2px;background:var(--accent);transform-origin:left;animation:plot-x .9s var(--ease) .1s both}
```

On the path page, the three lower sections are children 2 to 4 of `.p-wrap`, so they share the delays of steps 2 to 4 (60 ms apart, as in the demo the owner saw). Leave it that way.

- [ ] **Step 2: Check**

Run: `python3 scripts/check-site.py`
Expected: all `PASS`.

- [ ] **Step 3: Commit**

```bash
git add assets/css/motion.css
git commit -m "Add the arrival motion for the work, path, now and 404 pages."
```

### Task 5: Update CLAUDE.md

**Does:** Tells a future session that motion lives in `motion.css`, what guards it and where the work page's line is.
**Depends on:** Tasks 2, 3, 4
**Adds:** nothing new
**Size:** ~6

**Files:**
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: the final shape of Tasks 1 to 4.
- Produces: nothing a later task uses.

- [ ] **Step 1: Edit three places.**
  - Commands (line 21): change the comment to `# builds like CI and checks pages, metadata, links, bar, sitemap, motion`.
  - Structure (line 37): change the `assets/css/` line to name `motion.css (all motion, last)` after `path.css`.
  - Gotchas: add one line saying that all motion lives in `assets/css/motion.css`, inside its one `prefers-reduced-motion: no-preference` block, last in the concatenation, and `scripts/check-site.py` fails on motion text before that block; page transitions work in Chrome, Edge and Safari 18.2+ only; the work page's drawings and sheets have no motion (the owner rejected it), and the work page gets only the plain page fade, picked by `html:has(.sheet)`.
- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "Record in CLAUDE.md where the site's motion lives."
```

### Task 6: Verify in Chrome

**Does:** Shows, by measurement on the real build, that the motion works and that the work page and the reduced-motion case are unchanged.
**Depends on:** Tasks 1, 2, 3, 4
**Adds:** nothing new
**Size:** ~0

**Files:** none. Everything lives in a scratch folder, and nothing is added to the repo.

Use the browser tool with a fresh tab per test, because an unfocused tab stops rendering frames and its animations never finish. Serve each build with `python3 -m http.server <port> -d <folder>`. Compare screenshots with Pillow: `ImageChops.difference(a, b).getbbox() is None` means they are identical. Scroll with `window.scrollTo({top: y, behavior: "instant"})`.

- [ ] **Step 1: Build three copies** into scratch folders with `--baseURL http://127.0.0.1:<port>/`:
  - `base`: the site at commit `cf03c61`, before Task 1 (`git archive cf03c61 | tar -x -C <folder>`, then build there);
  - `new`: this branch;
  - `off`: a copy of `new` whose built stylesheet has `no-preference` replaced by `never`, so the browser skips the block.
- [ ] **Step 2: Work page at rest.** At 1892×956, screenshot `/work/` of `base` and `new` at three scroll positions (top, middle and bottom of the page), waiting 6 s after load. Expected: identical at each position.
- [ ] **Step 3: Block off.** Screenshot `/` and `/work/` of `base` and `off` at 1892×956, at the top of the page. Expected: identical, and every element's computed `opacity` on both pages of `off` is `1`.
- [ ] **Step 4: End state with motion.** On `new`, 6 s after load, list the elements under `body` whose computed `opacity` is not `1` on each of the five pages (`/`, `/work/`, `/path/`, `/now/`, `/404.html`). Expected: none.
- [ ] **Step 5: No scroll.** On `new`, at 768×640 and 1892×956, at 0.5 s and at 6 s, `/` has `scrollHeight <= innerHeight` and `scrollWidth <= innerWidth`. At 375×800, all five pages have `scrollWidth <= innerWidth` at 0.5 s and at 6 s. Report a page that also scrolls on `base` separately from one that scrolls only on `new`.
- [ ] **Step 6: The transition.** In a scratch copy of the repo (not the repo itself), add this to `layouts/baseof.html` after the head partial, then build and serve it:

```html
<script>addEventListener('pagereveal',function(e){if(!e.viewTransition){sessionStorage.setItem('vtnames','no transition');return}e.viewTransition.ready.then(function(){sessionStorage.setItem('vtnames',JSON.stringify(document.getAnimations().filter(function(a){return a.effect&&a.effect.pseudoElement}).map(function(a){return a.animationName+'@'+a.effect.pseudoElement})))})})</script>
```

Click the links from home to work, path, now and back to home, and read `sessionStorage.vtnames` after each arrival. Expected: a transition ran each time; the entry for `::view-transition-new(content)` is `vt-in` on path, now and home and there is none on work (the work page's `main` is unnamed, so the browser cross-fades `root`); and the entry for `::view-transition-old(content)` is `vt-out` when leaving home, path or now and none when leaving work (the browser's own entries on `root` and `bar` are normal). Then open `/work/`, scroll to 1500px, click the `path` link and read the list again. Expected: no `-ua-view-transition-group-anim-content` and no `-ua-view-transition-group-anim-bar` entry. Chrome is the only browser to check. Open the pages as `localhost`, not `127.0.0.1` (four tries on `127.0.0.1`, with script and real clicks, all said `no transition`; `localhost` worked), arm the click with `setTimeout(…,50)` inside the eval, and read `vtnames` in a second eval; if `vtnames` is empty or says `no transition`, repeat in a new tab before reporting a failure.
- [ ] **Step 7: A click during the intro.** On `new`, open `/`, click the `work` link at about 0.3 s, wait 2 s, and list the elements on `/work/` whose `opacity` is not `1`. Repeat from `/` to `/path/`. Expected: none. Then, from `/path/`, click the wordmark and confirm that `document.getAnimations()` on the home page includes `type` (the intro replays; spec decision 7).
- [ ] **Step 8: The other pages.** On `new`'s `/404.html` and `/now/`, the `h1`'s computed `animation-name` is `rise`, and on `/now/` the `.p-r` rows' `animation-delay` values are 0.08 s, 0.14 s, 0.2 s and 0.26 s.
- [ ] **Step 9: The home timeline.** On `new`'s home page, read `document.getAnimations()` right after load, and report the latest end time of any animation and the longest single animation. Expected: the latest end is 4.8 s (the cursor's blink starts at 1.2 s and runs 4 × .9 s), and the longest single animation is 3.6 s. A latest end over 5 s breaks the spec's anti-goal.
- [ ] **Step 10: The diffs.**
  - `git diff cf03c61 --stat -- layouts/work.html 'layouts/_partials/drawing-*.html'` prints nothing.
  - `git diff cf03c61 -- assets/css/base.css` shows only the deleted `html{scroll-behavior:smooth}` line.
  - `grep -n '\.sheet\|\.dwg\|\.fig\|\.sh\b\|\.tb\b' assets/css/motion.css` prints only the `main:not(:has(.sheet))` rule and comment lines.
- [ ] **Step 11: Report** each step's result (the figures and the screenshot comparisons) in the task's hand-back. There is nothing to commit.
