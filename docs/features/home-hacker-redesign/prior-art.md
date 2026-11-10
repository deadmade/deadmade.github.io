# Prior art: hacker-styled developer home page

Source check (a fresh GPT agent opened all 15 cited links): 27 confirmed / 11 not supported / 0 couldn't open, across 38 claims; the three claims marked [source] all held. Unsupported claims below are dropped or marked [unverified].

**Gaps:**
- panr's `layouts/index.html` returned 404, so I read its CSS, not its home markup. Scanlines' profile-mode markup and htunteza's `index.html` were not opened either (README only).
- MDN has no page on `text-shadow` or `filter` cost, and none on CSS typing animations. The `steps()` page describes the function but has no typing example. Glow-cost claims come from blogs.
- Several search engines timed out; the pitfalls section rests on four blog posts.
- I opened no recruiter-focused write-up, so nothing here shows how recruiters read these pages.

## Implementations

1. **panr/hugo-theme-terminal**. Two colours (`--background`, `--foreground`) plus one `--accent`, all-monospace, `--radius: 0`. [main.css](https://raw.githubusercontent.com/panr/hugo-theme-terminal/master/assets/css/main.css): images get an 8px accent border, blockquotes a `>` marker, lists accent-coloured bullets. [header.css](https://raw.githubusercontent.com/panr/hugo-theme-terminal/master/assets/css/header.css): the logo is an accent block, followed by a dashed rule from `repeating-linear-gradient`. The cited files are CSS; the theme was not checked for scripts, and `main.css` has an ungated `transition`.
2. **wthouse/scanlines** ([README](https://github.com/wthouse/scanlines), [_crt-effects.scss](https://raw.githubusercontent.com/wthouse/scanlines/main/assets/scss/_crt-effects.scss)). Full VT220 emulation: scanline overlay, vignette, glow, optional flicker, a "profile" home mode with name, subtitle, avatar, bio and buttons. Flicker is off by default and drops under `prefers-reduced-motion`. Scanlines and vignette are removed under `prefers-contrast: more`. The README admits the overlays lower delivered contrast below the stated ratios.
3. **tionosulis redesign log** (blog post, [source](https://tionosulis.github.io/posts/redesign-log-terminal-theme/)). A neofetch-style heavy box-drawing frame around the logo, made from `::before`/`::after` pseudo-elements (`┏━━━━━┓`). It chose amber over green because green-on-white fails for body text, and says "terminal vibe, not terminal replica".
4. **htunteza.com** ([repo](https://github.com/finerbrighterlighter/personal_web_hugo)). A three-column shell with live panels and a typed command header. Roboto Mono is subset to include the box-drawing range. Its README says scripts are needed for the typing and the panels, so it breaks your no-JS rule.
5. **rehan-hk Tokyo Terminal** ([listing](https://template0.com/item/hugo-theme-tokyo-terminal)). Home page is ASCII art, a configurable prompt (`rehan@dev:~$`), a blinking cursor and social links. I did not read its code.

## Official constraints

- [MDN prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion): `reduce` asks to remove or replace non-essential motion. Its example replaces scaling with a muted fade.
- [MDN animation-timing-function](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/animation-timing-function): `steps(n, jump-*)` holds n equal-length stops, which is what a typed or blinking effect needs.
- [WCAG 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html): 4.5:1 for normal text, 3:1 for large text. Logotypes are exempt, but a logo that is also a link is encouraged to meet contrast. The page says red on black is a problem for people with protanopia. Thin or unusual fonts can render fainter than their nominal ratio.
- [WCAG 2.3.1](https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html): no more than three flashes per second, unless below the flash thresholds. Saturated red flashes have their own test.

## Pitfalls

- Monospace body text. A blog post says not to use it for prose ([lambdaland](https://lambdaland.org/posts/2025-06-24_reading_blogs/), blog). Another puts long-form reading 5–10% slower and suggests monospace for frame text, metadata and code ([emptybird](http://emptybird.com/en/post/terminal-style-blog/), blog, unsourced figure).
- Maximum contrast. A blog post claims pure white on pure black causes halation and recommends 7:1–11:1 ([moltamp](https://moltamp.com/blog/terminal-themes-that-dont-suck/), blog, no citation).
- Glow cost. A blog says one `text-shadow` is cheap, and stacked shadows, large blurs and animating `text-shadow` are not ([csstoolkit](https://csstoolkit.net/blog/css-text-shadow-guide/), blog). Scanlines' default glow puts two shadows on most `p`, `li` and `a`, with metadata and the status line excluded.
- Fixed overlays. Scanlines' own comments say a full-viewport gradient overlay sized in `dvh` repainted on every mobile scroll frame and left an unstyled band; it switched to `lvh`.

## Approaches

**A. Accent-plus-prompt (panr, Tokyo Terminal, tionosulis).**
Dark base, one accent, mono type, prompt or accent-block framing, box-drawing or dashed rules.
- *Good at:* can be adapted in plain CSS with one accent, the pink triangle [inferred]; how fast it scans and what it costs are [unverified].
- *Cost:* may look like every terminal theme, leaving the hacker idea to the picture [unverified].
- *Bad fit if* the prompt text is faux commands the reader must decode. [inferred]

**B. Full CRT emulation (Scanlines).**
Scanlines, vignette, glow and phosphor palette over the whole page.
- *Good at:* a no-JS reference implementation with reduced-motion and contrast opt-outs [source: Scanlines README]; "strongest atmosphere" is [unverified].
- *Cost:* lowers contrast [source: Scanlines README]. Whether it fights the red-eye picture is [unverified].
- *Bad fit for* a sub-minute recruiter screen, where the effect may compete with the paragraph [unverified: no source examines recruiter screening].

**C. Terminal frame, readable core (tionosulis, emptybird).**
Mono for chrome (name, labels, links, rules); the paragraph stays at comfortable size and line height. You can't mix typefaces, so this means controlling size, weight and measure within Plex Mono.
- *Good at:* the "vibe, not replica" balance [source: tionosulis].
- *Cost:* needs careful measure and line-height [inferred].
- *Bad fit if* the owner wants the page to look like a literal shell. [inferred]

**D. Multi-pane live shell (htunteza).**
Columns, collapsible panels, typed commands.
- *Good at:* meant to behave like a working terminal [source: README]; density and how readers take it are [unverified].
- *Cost:* needs JS and API calls [source: README].
- *Bad fit here:* breaks no-JS and no-external-requests. [inferred]

## Fit to your rules (inferred)

Typing and blinking can run as `steps()` keyframes inside your one `no-preference` block. Scanlines can be a static `repeating-linear-gradient` at low opacity on one element, so it needs no motion block. Check pink text against 4.5:1 and keep any glow sparing [inferred].
