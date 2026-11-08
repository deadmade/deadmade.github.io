# Checking motion in the browser tool: "no transition", animations that never start, screenshots that differ

- **Seen:** 2026-11-08, checking the site animations (docs/features/site-animations/flow.md, Task 6) in the headless Chrome 154 that the browser tool drives.
- **Cause:** four separate traps of the tool, found while measuring; the repo's CSS was not at fault in any of them.
  - A probe of the cross-document view transition (a scratch build with a small script, since the repo has no script) said `no transition` on every try on `http://127.0.0.1:<port>` (four tries, script and real clicks) and worked on `http://localhost:<port>`. Measured; the cause is not known.
  - The tool paints no frames until a screenshot is taken, so animation timelines do not advance by themselves. A click "0.3 s after load" cannot be made: by the time the page is looked at, the animations are either at their first state or finished.
  - Screenshots are JPEG. Two screenshots of the same unchanged page differ by up to 5 to 7 of 255 over some tens of pixels (measured: 62 px on the home page), so "no difference" by eye or by `cmp` never holds.
  - A tab keeps state between tests (a finished transition, scroll position, a paused animation). The window is 1892×956, so other widths need an iframe.
- **Fix:** nothing to fix in the repo. What worked:
  - Serve the build with `python3 -m http.server --bind 127.0.0.1` but open it as `http://localhost:<port>/`.
  - Use a fresh tab for each test.
  - To test a click during the intro, pause the intro animations at 300 ms (through `document.getAnimations()`), then click.
  - To tell a real change from noise, build the two variants into separate folders, take the screenshots at the same scroll position, and compare them with Pillow (the number of differing pixels and the largest difference); a variant is "the same" only when it is at or under the noise floor measured on two screenshots of one build. To find which of several CSS changes causes a difference, remove them one at a time and rebuild (this found the work page's raster change, commit 9498b30).
  - For widths other than the window's, load the page in iframes of the wanted size.
- **Spot it next time:** a probe that says "no transition" on `127.0.0.1` means try `localhost` before changing any CSS; a difference of 7 of 255 or less between two screenshots of one build is the tool, not the page.
