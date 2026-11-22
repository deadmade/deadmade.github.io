# Browser and tool facts for the diagram animation

Source check (one fresh opus agent, 2026-11-17, all 24 cited URLs opened): 22 [source] claims confirmed, 1 not supported (the M152 merge, corrected below), 2 went further than their source (corrected), 0 couldn't open; of the [inferred] claims a verdict rests on, 3 did not follow (§1 Safari, §2 `-0.996`, §5 resume) and are corrected *(checked)*. One claim measured since: §6.

Gaps: nothing was rendered or built (no Safari, Firefox or Hugo on this machine). No WebKit or Gecko source states that a round-cap zero-length dash draws a dot. Offscreen throttling has blog sources only. The Hugo docs I read do not say `site.Data` works inside `ExecuteAsTemplate`. Chromium 730008 was access denied, WebKit 72401 showed attachments only, Stack Overflow returned 403.

Tags: [source] = a fetched page says it; [inferred] = my reasoning across sources.

## 1. Zero-length dash with round caps as a dot

- [source] SVG 2 stroke dashing and line caps (13.5.4, 13.5.6): each dash gets its cap shape at both ends, so a zero-length dash with round caps is a circle; a dash list that sums to zero is solid. https://www.w3.org/TR/SVG2/painting.html
- [source] The CSS Fill and Stroke 3 draft says "If all values are zero, it is treated as none"; the issue asking what a single zero does was open when fetched. In it an editor replies that "a zero-length dash is drawn as just the line caps", covered in the draft's stroke-geometry notes, and a 2017 test there says Chrome and Firefox on Mac treated zero-length dashes like zero-length segments (caps drawn; square caps wrongly oriented). https://github.com/w3c/fxtf-drafts/issues/235 *(checked)*
- [source] WebKit 174417: `0 <circumference>` on a circle left a hairline in Safari that Chrome and Firefox did not draw. Closed CONFIGURATION CHANGED after a macOS Ventura update, though one comment says it still affects Monterey. https://bugs.webkit.org/show_bug.cgi?id=174417
- [source, blog] `stroke-dasharray="0 20"` with round caps is the documented recipe for dots; it names no engine. https://perfectvector.com/blog/svg-dotted-outlines
- [inferred] Firefox drew caps on zero-length dashes in 2017 (item above), so a round-cap dot is likely there. No source says Safari draws the caps: WebKit 174417 is a hairline bug, not evidence of caps. *(checked)*

Verdict: risk. Specified for SVG 2, unconfirmed in Safari and Firefox. Check a real Safari and Firefox before shipping. [inferred] A fallback is a tiny non-zero dash such as `0.001 2`.

## 2. pathLength with dashes and non-scaling-stroke

- [source] pathLength scaling of dasharray and dashoffset is specified (SVG 2 13.5.6, URL above). BCD: `path` `pathLength` Chrome 50, Firefox 6, Safari 14. https://raw.githubusercontent.com/mdn/browser-compat-data/main/svg/elements/path.json
- [source] Firefox once ignored pathLength for dashoffset; fixed in Firefox 39. https://bugzilla.mozilla.org/show_bug.cgi?id=1137859
- [source] SVG 2 13.6: with `vector-effect: non-scaling-stroke` the stroke is computed in host coordinate space. https://svgwg.org/svg2-draft/painting.html
- [source] Whether dash values and pathLength follow host space is unclear in the spec; the issue is open. https://github.com/w3c/svgwg/issues/323
- [source] Chromium 151 and 152, devicePixelRatio 2: non-scaling-stroke strokes drew at half width, breaking an arrow built from `pathLength="1"`, dasharray 1, animated dashoffset and non-scaling-stroke. The same arrow rendered correctly in Safari 26.5. The fix was verified in M153 and merged to M152 (verified in 152.0.7977.57) and M151 (151.0.7922.172). *(checked)* https://issues.chromium.org/issues/541684117 and https://issues.chromium.org/issues/544748096 (duplicate)
- [source] Chromium 40727576: the UA's path-length measurement and the painted path differ slightly, so a dash at offset exactly equal to pathLength can leave a sliver at the start. https://issues.chromium.org/issues/40727576
- [inferred] The design ends at `-0.996`, short of `-1`; no source says how big the measurement difference is, so whether 0.004 is enough is measured only in Chrome (the spike), not elsewhere. *(checked)* Removing non-scaling-stroke fixed the arrow in 544748096 [source]; the spike's dot paths do not use it (only the outlines do, without dashes).

Verdict: risk. Test at DPR 2 in Chrome (151.0.7922.172, 152.0.7977.57, 153 or later have the fix), Safari and Firefox. Keep non-scaling-stroke off the dashed dot paths.

## 3. Keyframes on stroke-dashoffset and opacity

- [source] BCD: `@keyframes` Chrome 43, Firefox 16, Safari 9; `stroke-dasharray` and `stroke-dashoffset` Chrome 1, Firefox 1.5, Safari 4; `opacity` Chrome 1, Firefox 1, Safari 2. https://raw.githubusercontent.com/mdn/browser-compat-data/main/css/at-rules/keyframes.json, https://raw.githubusercontent.com/mdn/browser-compat-data/main/css/properties/stroke-dashoffset.json, https://raw.githubusercontent.com/mdn/browser-compat-data/main/css/properties/opacity.json
- [source] The Safari 26.5 observation in item 2 is an animated dashoffset (the report does not say whether by CSS or SMIL) rendering correctly.
- [source] Firefox rejects unitless `calc()` in dash properties (closed INVALID). https://bugzilla.mozilla.org/show_bug.cgi?id=1884525
- [inferred] BCD has no per-property "animatable" flag, so animation support rests on the spec (stroke-dashoffset animates "by computed value"), the Safari report, and Firefox bug 1137859, which is about an animated stroke-dashoffset (fixed in Firefox 39). *(checked)*

Verdict: works. Write plain numbers in the keyframes, no `calc()`.

## 4. :has()

- [source] BCD: Chrome 105, Firefox 121, Safari 15.4. https://raw.githubusercontent.com/mdn/browser-compat-data/main/css/selectors/has.json (MDN: https://developer.mozilla.org/en-US/docs/Web/CSS/:has)
- [inferred] A browser without `:has()` drops the whole rule, so the stop checkbox would not hide the run layer there; the animation would still run.

Verdict: works. Firefox 121 is the latest of the three minimum versions.

## 5. Offscreen and background-tab throttling

- [source, blog] Hidden tabs produce no animation frames; animations that are only scrolled out of view may still tick. https://www.css-animation.com/performance-budgeting-gpu-architecture/main-thread-scheduling-and-long-animation-frames/pausing-offscreen-and-background-tab-animations/ and https://dev.to/hyperiux-immersion-labs/how-to-pause-offscreen-animations-without-breaking-the-experience-581h
- Nothing official found from Chromium, WebKit or Gecko.
- [source, blog] Main-thread animations offscreen "still run style every frame" (css-animation.com, above). Neither page says how a CSS animation's time behaves while frames are skipped. *(checked)*

Verdict: unknown for power (offscreen loops likely keep costing style work); correctness after a background tab unverified.

## 6. Hugo 0.166: ExecuteAsTemplate and Concat

- [source] `resources.ExecuteAsTemplate TARGETPATH CONTEXT RESOURCE` renders an `assets/` resource as a Go template; the example reads `site.Params`. https://gohugo.io/functions/resources/executeastemplate/
- [source] `resources.Concat TARGETPATH SLICE` joins resources of one media type. https://gohugo.io/functions/resources/concat/
- [source] `site.Data` reads the project's `data/` directory. https://gohugo.io/content-management/data-sources/ (the repo has no `data/` today).
- [source] v0.170.0 (2026-11-13) accepts an `[]any` "containing only resources" in Concat. https://github.com/gohugoio/hugo/releases/tag/v0.170.0 and https://github.com/gohugoio/hugo/issues/15546. *(checked)* The existing `head.html` already passes `slice` of `resources.Get` to Concat on 0.166.
- [inferred] Give the template a `.css` TARGETPATH so the media type stays `text/css`, then put its result in the same `slice` before `| minify | fingerprint`. `site.Data` inside the template follows from the `site.Params` example; I did not see it stated.

Verdict: works. Measured 2026-11-17 in a scratch copy on Hugo 0.166.0: `motion.css` through `ExecuteAsTemplate` inside the existing Concat slice computed hop timings from `data/runs.toml`, and `check-site.py` passed. `site.Data` is deprecated since 0.156 and fails the check's build; `hugo.Data` works.
