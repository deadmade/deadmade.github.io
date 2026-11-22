# Prior art: animating inline-SVG architecture diagrams without JavaScript

**Source check (2026-11-17, four opus checkers, one per section):** 37 [source] claims confirmed, 2 not supported, 0 couldn't open; 10 inferences follow, 3 don't; 17 lines cite nothing (mostly untagged Shape and Good-at lines that the cited pages bear out). Corrected below: A's chaining and the 0,0 claim, B's and C's and D's bad-fit lines, D's flag name and its fade. Corrections are marked *(checked)*.

**Gaps:** (1) Stack Overflow answered 403, so Safari `offset-path` on SVG children and SMIL inside a `display:none` SVG are unverified. (2) The specs I opened do not say how `non-scaling-stroke` scales dashes; I saw only search excerpts (svgwg issue 323, a Chromium issue title), not the pages. (3) No source on the CPU cost of endless SVG animation. (4) No hand-crafted animated architecture diagram on a known engineering site turned up; the nearest are tools (Mermaid, D2, React Flow) and one JS repo. (5) React Flow's `animated` edge CSS was not read. (6) D2's `/tour/animations/` returned 404; I used its style, exports and composition pages.

Tags: [source] = a page I opened says it; [inferred] = my reasoning.

## A. SMIL dot along the real path

- **Shape:** a dot parked at rest (translate to the path start, then `scale(0)`), one `<animateMotion path=...>` per stepped edge. *(checked)* Each dot loops on itself, `begin="<offset>s;<its own id>.end+<gap>s"` with offset `(step-1)*stepDuration`; dots are not chained to each other, the order comes from staggered offsets in one shared period.
- **Who:** Mermaid 12.3.0 step animation, one dot per edge, `begin=(step-1)*1s`, `fill="remove"`, gap `(count-1)*1s` ([docs, "Step-by-step flow animation"](https://mermaid.js.org/syntax/flowchart.html); [edgeStepAnimation.ts](https://raw.githubusercontent.com/mermaid-js/mermaid/develop/packages/mermaid/src/rendering-util/rendering-elements/edgeStepAnimation.ts)). React Flow moves any SVG element along an edge with `<animateMotion>` ([animated SVG edge](https://reactflow.dev/ui/components/animated-svg-edge)).
- **Good at:** the real order, round trips included; all timing is attribute values. Mermaid's `stepNumbers` badges give a static order fallback [source: docs].
- **Costs:** Mermaid hides the dot and its edge highlight with `@media (prefers-reduced-motion: reduce){...display:none}` [source: edgeStepAnimation.ts]; its `stepNumbers` badges are off by default [source: docs]; SMIL does not honour the preference by itself [source: [imagetosvg.com](https://imagetosvg.com/how-to/svg-reduced-motion), a blog, only]. `pauseAnimations()` is script-only [source: [SVG animations spec](https://svgwg.org/specs/animations/)], so CSS can only hide the element. The syncbase loop never ends [source: code]; *(checked)* SMIL itself can bound or stop a run in markup with `end`, `repeatDur`, `max` and event values such as `click` [source: SVG animations spec]. *(checked)* The motion offset is added to the element's own position, so the dot is drawn at 0,0 or reset with a transform [source: [CSS-Tricks](https://css-tricks.com/guide-svg-animations-smil/), a blog; SVG animations spec, supplemental transform]. The timeline starts at load, not on scroll [source: SVG animations spec, `timelinebegin`].
- **Bad fit:** the project rule that all motion lives in motion.css's `no-preference` block, because this motion is SVG markup [inferred]. Pixel-identical at rest holds only if the parked dot is invisible [inferred].

## B. CSS `offset-path` dot

- **Shape:** `offset-path: path("M...")` or `url(#arrow)` on a dot; keyframes animate `offset-distance` 0% to 100%.
- **Who:** the spec and MDN examples only; I found no production diagram using it.
- **Good at:** timing in CSS, so it fits the `no-preference` block [inferred]. Support [source: BCD, [offset-path](https://raw.githubusercontent.com/mdn/browser-compat-data/main/css/properties/offset-path.json)]: Chrome 55, Firefox 72, Safari 15.4; `path()` Safari 16; `url()` Chrome 116, Firefox 122, Safari 17. In SVG contexts every `<coord-box>` acts as `view-box`, and a `url()` target uses a 1px user space [source: [CSS Motion spec](https://drafts.csswg.org/motion/), `offset-path`]. So `path()` units are viewBox units [inferred]; Safari's behaviour on SVG children is unchecked.
- **Costs:** an offset path is a transform, so the usual stacking-context effects apply [source: same spec]. A path ending in `z` wraps around; an open one clamps [source: spec, "Calculating the computed distance"]. Keep `fill-mode: none` and hide the dot at rest, given the owner's Chrome measurement that a finished `both` fill changed anti-aliasing [inferred from the brief].
- **Bad fit:** *(checked)* dots whose travel windows differ in length within one shared loop (arrows of different lengths at constant speed), because CSS has nothing like SMIL's `id.end` and each window's keyframe percentages are computed by hand [inferred]. Dots with equal windows can share one `@keyframes` and be staggered with `animation-delay` [inferred].

## C. Dash flow on every arrow

- **Shape:** `stroke-dasharray` plus an infinite `@keyframes dashdraw { from { stroke-dashoffset: 0 } }`.
- **Who:** D2 `animated` connections: dash defaults to 5 when animated, `animation: dashdraw <gap*0.5>s linear infinite` ([d2target.go](https://raw.githubusercontent.com/terrastruct/d2/master/d2target/d2target.go)). Two-way arrows are split in half, one reversed, because "there is no pure CSS way" ([d2svg.go](https://raw.githubusercontent.com/terrastruct/d2/master/d2renderers/d2svg/d2svg.go)). Mermaid offers it through classDef ([docs, "Using classDef Statements for Animations"](https://mermaid.js.org/syntax/flowchart.html)).
- **Good at:** a few lines of CSS for any number of edges.
- **Costs:** the arrow is dashed whenever animated [source: d2target.go], so the rest look changes [inferred]. `pathLength` rescales dash values [source: [SVG 2 painting](https://www.w3.org/TR/SVG2/painting.html), "Dashing strokes"]; the `non-scaling-stroke` interaction is a gap.
- **Bad fit:** this brief. It tells no story [inferred]. *(checked)* That it repeats the rejected "signal on every arrow" experiment comes from this project's history (`docs/features/site-animations/flow.md`), not from the sources.

## D. Whole-board sequencing

- **Shape:** one drawn copy per step; opacity keyframes switch 0 to 1 to 0 across `frames * interval`. *(checked)* The switch is a 1 ms hard cut, not a fade (`transitionDurationMS = 1`).
- **Who:** D2's animated export (*(checked)* the cited code names only an `intervalMS` parameter; the CLI flag's name is not in the cited pages); layers, scenarios and steps export as one animated SVG ([d2animate.go](https://raw.githubusercontent.com/terrastruct/d2/master/d2renderers/d2animate/d2animate.go), infinite; [composition](https://d2lang.com/tour/composition/)).
- **Good at:** the story as discrete frames, with no path maths.
- **Costs:** every frame is a full copy [source], so the markup multiplies, doubled again by wide and upright variants [inferred].
- **Bad fit:** *(checked)* hairline diagrams that must stay identical at rest, if stacked copies re-rasterise; that is an unverified rendering assumption carried over from this site's Chrome measurement, not something the D2 sources say.

A JS counter-example: [abergs/animations](https://github.com/abergs/animations) drives packets with `gsap.timeline({ repeat: -1 })`. It cannot be used here.

## Standards

- WCAG 2.2.2: automatic movement over 5 seconds beside other content needs pause, stop or hide; hiding counts [source: [Understanding 2.2.2](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html)]. So a looping dot needs a stop; a one-shot under 5 s does not [inferred].
- WCAG 2.3.3 covers motion triggered by interaction; technique C39 (`prefers-reduced-motion`) is sufficient [source: [Understanding 2.3.3](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html)].
- `animation-timeline: view()`: Chrome 115, Firefox 159, Safari 26 [source: [BCD](https://raw.githubusercontent.com/mdn/browser-compat-data/main/css/properties/animation-timeline.json)].
- `animateMotion`: Chrome 19, Firefox 4, Safari 6 [source: BCD `svg/elements/animateMotion.json`].
