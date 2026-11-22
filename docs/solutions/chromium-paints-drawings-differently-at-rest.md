# A drawing looks a few pixels different at rest in Chrome after its animation ran

- **Seen:** 2026-11-17 and 2026-11-22, /projects/, at-rest screenshots of the branch against the base build in Chromium 147
  (lossless clips of each drawing, between runs and with every switch stopped). With the run layers fading through
  `opacity`, RustLogger and IsoPrüfi differed by 157 and 43 px at a device pixel ratio of 2 and by 329 and 294 px at 3, up
  to 25/255; with `fill-opacity` and `stroke-opacity` fades, all three drawings differed by 4 to 51 px at a ratio of 1
  (by width and the moment of the shot), up to 26/255. Earlier, one `transform` animation inside a drawing changed 12,766 px.
- **Cause:** Chromium paints the static drawing differently depending on how the moving part beside it is painted
  (inferred from the measurements, not from Chromium's source). An `opacity` animation, or `will-change: opacity`, gives
  the run layer its own compositor layer, and at ratios of 2 and 3 the rest of the drawing is then rastered differently.
  `fill-opacity` and `stroke-opacity` fades stay in main-thread paint, which is clean at 1.25 to 3 but repaints the
  touched tiles at 1 with slightly different edge antialiasing. WebKit 26.4 and Firefox 148 were identical with both,
  and every variant was identical once the run layer was `display:none` (stopped).
- **Fix:** none is clean at every ratio. Eight variants were measured: each fade alone, with `will-change`, with
  `isolation:isolate`, and drawn in an overlay svg. The owner kept `fill-opacity` and `stroke-opacity` on 2026-11-22
  (assets/css/motion.css, the run block; assets/css/base.css, the run rules), and CLAUDE.md gives the remainder.
- **Spot it next time:** compare at-rest shots against the base build at ratios of 1 and 2 (3 for phones), both between
  runs and stopped, as lossless clips, with the drawing in view while it runs (scrolled in only for the shot, it
  shows 0 px). A single ratio hides it: the `opacity` fades differed only at 2 and 3, the
  `fill-opacity` and `stroke-opacity` fades only at 1 (both were clean at 1.25 and 1.5). Don't call it noise until the base build against itself gives 0 px. Below 760 px the
  upright drawings sit 32 px lower (the switch's row, assets/css/motion.css). That move alone changes 11 to 239 px at
  ratios 2 and 3 in Chromium (9 px at 1 in an 844 px tall window) and 103 px in WebKit at 1, between runs and stopped alike, so compare narrow widths against
  the base with that `padding-top` added.
