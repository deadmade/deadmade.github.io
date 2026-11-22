# Prior art: restrained CSS-only motion

**Source check (fresh opus agent, 2026-11-07, every link opened; my tally of its table rows):** 32 confirmed, 8 follow from the cited pages (inferences), 7 not supported, overstated or not following (corrected below), 8 cite nothing (now labelled), 0 could not open. Corrections below are marked *(checked)*.

**Gaps:** webstatus.dev pages render blank and MDN compat tables did not load, so Baseline data comes from the [api.webstatus.dev](https://api.webstatus.dev/v1/features/view-transitions) JSON. I found no personal portfolio with verifiable source doing all four patterns; the comparables are docs and demo repos. Search engines timed out often; one CSS-Tricks blog article was seen as a search excerpt only. No source found for `#anchor` links versus cross-document transitions. The Hugo minify check is my own local run (0.166.0), not a cited page.

## Support, 2026-11-07
- `prefers-reduced-motion`: widely available ([MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion)). *(checked)* That page covers only the media query; the Baseline status of CSS animations and transitions was not checked.
- `@starting-style`: newly (since 2024-08-06) ([API](https://api.webstatus.dev/v1/features/starting-style)).
- Scroll-driven animations: newly, since 2026-10-27 when Firefox 159 shipped ([API](https://api.webstatus.dev/v1/features/scroll-driven-animations), [Chrome DevRel timeline](https://scroll-driven-animations.style/demos/baseline-newly-available/css/)). [inferred, no usage data] It shipped in Firefox 11 days before this report, so many Firefox users probably lack it for now.
- Cross-document view transitions: limited. Chrome/Edge 126, Safari 18.2, no Firefox ([API](https://api.webstatus.dev/v1/features/cross-document-view-transitions)). *(checked)* Same-document view transitions (the Gaps line's `view-transitions` link) are newly available, Firefox 144, 2025-10-14, but the site's pages are separate documents, so only the cross-document kind applies.

## Constraints that shape design
- Keep to `opacity` and `transform` to stay on the compositor ([web.dev](https://web.dev/articles/animations-guide#animate_at_the_composite_stage)). [inferred] The page says to avoid properties that trigger layout or paint other than those two but never names `stroke-dashoffset`; it probably paints, not verified.
- [WCAG 2.3.3](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html): the `prefers-reduced-motion` query (C39) is a sufficient technique; scroll-moved decoration is a named vestibular trigger.
- [WCAG 2.2.2](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html): movement that starts automatically, lasts more than 5 s in total and sits beside other content needs pause/stop/hide (an endless loop lasts more than 5 s; so does a finite one that runs longer); C39 is not a listed sufficient technique. Scrolling into view counts as starting automatically.
- View transitions: same-origin, both pages opt in, push/replace/traverse only (not URL bar, bookmark, reload), Chrome skips the transition if the navigation itself takes over 4 s (not the animation), `pageswap`/`pagereveal` are script events ([Chrome](https://developer.chrome.com/docs/web-platform/view-transitions/cross-document)). Parsers ignore unknown at-rules, so unsupported means a normal navigation ([spec](https://drafts.csswg.org/css-view-transitions-2/#view-transition-navigation-descriptor)).

## Approaches

**A. Load reveals (keyframes with `both`, or `@starting-style`)**
- Shape: `animation: rise .5s both` from `opacity:0; translateY(8px)`, or a transition with a nested `@starting-style` block placed after the base rule ([MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@starting-style)). [inferred] Keyframe animations start from `from` without it, so `@starting-style` only matters for transitions.
- Users: MDN documents the pattern; I found no site using it to cite. [uncited] Good at: zero JS, one-shot, transform/opacity only.
- [inferred] Cost: delays on staggered items hide text longer. Bad fit: heavy stagger above the fold.
- Decision: write the final state as the base style and gate the motion in `@media (prefers-reduced-motion: no-preference)`. [inferred] Then disabled or unsupported animation shows content, never hides it.

**B. Scroll-driven reveals**
- Shape: `animation: reveal linear both; animation-timeline: view(); animation-range: entry 25% cover 50%` ([Chrome](https://developer.chrome.com/docs/css-ui/scroll-driven-animations)).
- Users: Chrome DevRel's image-reveal demo. Good at: off-main-thread, no observer.
- Decisions: `animation-timeline` must follow the `animation` shorthand, which resets it ([MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/animation-timeline)). [inferred] An element already in view at load starts partway through its `entry` range, so end the range early (`entry 0% entry 60%`) or above-fold text loads translucent.
- Cost: Firefox gap; the Chrome docs snippet above has no reduced-motion gate, so add one. Bad fit: [design judgement, no source] a 4-page site with little below the fold.

**C. Cross-document view transitions**
- Shape: `@view-transition { navigation: auto; }` on every page, and the default 0.25 s cross-fade needs nothing else ([MDN demo CSS](https://raw.githubusercontent.com/mdn/dom-examples/main/view-transitions/mpa/styles.css), [spec UA sheet](https://drafts.csswg.org/css-view-transitions-2/#ua-styles)).
- Decisions: nest it in `@media (prefers-reduced-motion: no-preference)` ([CSS-Tricks almanac blog](https://css-tricks.com/almanac/rules/v/view-transition/), "Nesting `@view-transition`": nests in `@media`, `@container`, `@supports`). The MDN demo sets duration on `::view-transition-group(root)` ([MDN demo CSS](https://raw.githubusercontent.com/mdn/dom-examples/main/view-transitions/mpa/styles.css)). The spec's header example names the header so it moves separately from the root cross-fade ([spec](https://drafts.csswg.org/css-view-transitions-2/)); [inferred] naming the nav does the same.
- Cost: skip `<link rel="expect" blocking="render">` unless needed; Chrome says to be cautious about blocking render ([Chrome](https://developer.chrome.com/docs/web-platform/view-transitions/cross-document)). *(checked)* The Chrome DevRel team-members demo that MDN walks through removes script-set `view-transition-name`s after the snapshot because "page state persisting in BFCache" causes name conflicts ([MDN](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API/Using), "(this to deal with BFCache)" is Chrome's wording on the cross-document page); [inferred] a CSS-only setup with fixed names needs no such cleanup. *(checked)* The earlier claim that per-element morphs "need script" was dropped: a fixed element on both pages can be named in CSS alone (the spec's header example, MDN's figcaption example); script is needed only for names that depend on which list item was clicked ([Chrome](https://developer.chrome.com/docs/web-platform/view-transitions/cross-document)). So a morph of the nav, the wordmark or a page title is possible CSS-only.

**D. SVG line-draw and loops**
- Shape: `stroke-dasharray` plus animated `stroke-dashoffset` ([CSS-Tricks, 2014 blog](https://css-tricks.com/svg-line-animation-works/)). Script was only for measuring length; `pathLength="1"` removes it and works on circle, ellipse, line, polygon, polyline, rect and path ([MDN](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/pathLength)).
- Decisions: the blog's base style hides the shape (dash and offset set), which [inferred] fails if animation is off; set dashes only inside the animation keyframes and gate with the media query. Only stroked shapes draw ([CSS-Tricks](https://css-tricks.com/svg-line-animation-works/)); filled-only shapes do not (follows from "must have a stroke"); `<text>` is [uncited].
- [inferred] Cost: paint per frame. Bad fit: loops (an endless loop exceeds 5 s of motion, so WCAG 2.2.2 above applies). *(checked)* Safer rule: total motion of 5 s or less, then at rest.

## Combining
- [uncited] A + D: same clock and gate; works well. B on top of A: animate different elements.
- C + A: [inferred] MDN says the new snapshot is live, not that the page's own CSS animations run inside it; the stacking of load reveals on the cross-fade is untested. Pick one per element. [uncited]

## Hugo minify
The agent's own local test, Hugo 0.166.0 `| minify` (the source check did not reproduce it; I re-measure at build time): `@keyframes` selectors (`from`, `to`, `0%`, `33.33%`, `entry 0%`), `animation-timeline`, `animation-range`, `path-length` survive. `0.0s` becomes `0s`. `@view-transition` and `@starting-style` blocks pass through unminified but valid. The tdewolff/minify [issue list for "keyframes"](https://github.com/tdewolff/minify/issues?q=keyframes) has one result, closed in 2016 (time-unit stripping), unrelated to keyframe selectors.
