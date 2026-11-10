---
flow: feature
phase: execute
now: Done; merged into job-application-portfolio.
---

# Home page hacker redesign: flow

## Request

From a session in dead-claude-skills, after a blind comparison of 54 generated pages (`docs/features/frontend-design-flow/` there): "could we make a plan to port the design I liked to deadmade.github.io?", then "could we take home-18 and add the hackerish style? remove the whitespace under the pfp".

The owner's blind notes on the home pages they liked: home-18 (5) "good, but a bit to much whitespace"; home-17 (5) "thats quite awesome with the rings in the background but I feel it could have leant more into the theme"; home-13 (4) "I really like the arrow and the picture looks like a hacker but a bit tp much whitespace and didnt lean enough into the hacker theme". Across the set, the notes return to the profile picture's placement and to too much whitespace.

## Artifacts

- Reference: [reference/home-18/](reference/home-18/) (the page as built, plain HTML and CSS) with [desktop](reference/home-18-desktop.png) and [phone](reference/home-18-phone.png) screenshots
- Prior art: [prior-art.md](prior-art.md) (source-checked)

- Spec: [spec.md](spec.md) (written from the approved spike)
- Plan:
- ADRs:
- Glossary:

## Gates

- Gate 1, spec approved: 2026-11-10, "Approve" (not copyedited: the owner removed the copyedit from flows on 2026-11-10)
- Gate 2, plan approved:

## Skipped

- Plan, plan review and Gate 2: the owner asked to build straight from the approved spec ("can we just implement it pls?").

- Copyedit before Gate 1: the owner removed the copyedit from flows on 2026-11-10 for low payoff; the installed flows 0.6.46 still lists it.

## Grounding

Read directly (the site is about 430 lines of layout and CSS, so pstack `how` and Explore agents weren't needed). Verified against the files on branch `job-application-portfolio`:

- **Where the site lives.** The current four-page site is on local branch `job-application-portfolio`, 19 commits ahead of `main` and never merged or pushed; `main` still has the old hugo-coder home page. Both earlier runs (`job-application-portfolio`, `site-animations`) are `done` and kept on that branch. Uncommitted there: `flake.lock`, `.superpowers/`, two mockups under `docs/features/job-application-portfolio/mockups/`.
- **Home page.** `layouts/home.html:1-26`: picture in `.side` (absolutely placed, right), `.intro` with the name split into spans, the typed role (`--n` = role length), the lede from `content/_index.md`, and `.go`, the three links from `[[menu.main]]` entries that have a `description` (`hugo.toml:14-33`).
- **Shared shell.** `layouts/baseof.html:6-19`: the top bar (handle with the triangle, then every menu entry) and the plain footer, on every page.
- **CSS.** `assets/css/` concatenated into one stylesheet: `tokens.css` (palette: bg `#1A1626`, accent `#F08BB4`, a commented red `#FF544A` from the picture), `fonts.css` (IBM Plex Mono 400/600/700), `base.css` (home rules `:21-51` and `:234-244`, the subpages' drawing sheet `:60-67`, footer `:223-227`), `motion.css` (all motion, one reduced-motion block, last).
- **One-screen rule.** `base.css:42-51`: the home page fits one desktop window; the name shrinks with the window height (`calc(52svh - 232px)`); phones scroll.
- **Constraints (CLAUDE.md).** No JavaScript and no external requests (`scripts/check-site.py` fails on them); all motion in `motion.css`'s one block, checked by `check-site.py`; the work page's design is owner-approved and must not change; text lives in `content/` and `hugo.toml`, not in layouts.
- **The reference, home-18** ([reference/home-18/](reference/home-18/)): built in the blind comparison from this site's home page. Same material as the site: IBM Plex Mono only, the same palette under other token names, the site's drawing-sheet frame (hairlines overshooting at the corners, centring marks) wrapped around the whole home page. Layout: name, role and lede left; the picture pinned in the frame's top-right cell; the three links as a register row across the bottom. The whitespace the owner means is the empty cell under the picture, between its bottom edge and the register (about 125 px at 1440×900). It is plain HTML and CSS with `#` links and its own token names, so porting it means rewriting it into `home.html`, `base.css` and `motion.css`.
- **Domain docs.** None: no `GLOSSARY.md`, `CONTEXT.md` or `docs/adr/`. No `graphify-out/`.

## Prior art

[prior-art.md](prior-art.md): five hacker-style implementations (panr's Terminal theme, Scanlines, the tionosulis redesign log, htunteza.com, Tokyo Terminal) in four approaches: accent plus prompt; full CRT emulation; a terminal frame with a readable core; a multi-pane live shell (needs JavaScript, so out). Constraints from MDN (reduced motion, `steps()`) and WCAG 2.2 (1.4.3 contrast, 2.3.1 flashes). Source check by a fresh GPT agent: 27 confirmed / 11 not supported / 0 couldn't open; the report was corrected. No source covers how recruiters read such pages.

## Findings

## Options

### What "hackerish" means here

Picked, then dropped: after seeing it in the spike, the owner said "lets remove the eye thing. Thought it would be better". The spike now keeps only the scan lines over the picture and the picture filling its cell (option A); the eye-callout version's screenshots are in [spike/eye-callout/](spike/eye-callout/). What hackerish means now is open.

First pick: home-13's eye callout ([reference/home-13/](reference/home-13/), `css/home.css:76-99`): a thin box drawn round the picture's red eye, a pink line with an arrowhead running from it to the name, the name's first line at the eye's height, and fine scan lines over the picture. The owner, asked what they picture as hackerish: "something with the eye or so you had in a different preview"; shown home-13 and home-14, they picked "home-13". Their blind note on it: "I really like the arrow and the picture looks like a hacker".

### The whitespace under the picture

Picked: A, the picture fills its cell down to the links, cropped as a portrait instead of a square; on a 1440×900 window that is about 560 px tall from the 460 px source, so it is upscaled a little, and the scan lines carry the softness. The owner: "lets try A".

### The introduction text

Picked: one heading, then one paragraph: "Backend developer in Bavaria. APIs and ERP integrations in C# by day, Rust and NixOS by night." with the blinking cursor at its end; the separate role line is gone (the owner: "coud we fold backend deleoper in the text? two headings feel strange"). My calls: "Based in Bavaria" folded into the first sentence, the two day/night sentences joined with a comma. `params.role` still feeds the footer and page metadata.

Earlier: Picked: "APIs and ERP integrations in C# by day. Rust and NixOS by night. Based in Bavaria.", option C of three written from scratch from the site's path, toolkit and hobbies (the owner: "Could we complelty create the text from scratch? not just move it around.", then "C"). The role line stays "Backend developer" (asked, not answered; my call: it reads clearer outside the company than the job title Business Solution Developer). The paragraph's lines are balanced, so the break falls after "by day."

Offered: A, the path ("From apprentice in 2019 to Business Solution Developer at 4SELLERS in Bavaria. I build the APIs that ERP systems talk through: C# and .NET at work, Rust at home.", my recommendation); B, what the owner does ("I write the code nobody sees: REST APIs, ERP integrations and tools for other developers. C# and .NET at work, Rust and NixOS at home. Bavaria, Germany.").

Before that: "I build the parts users never see: APIs, business systems and developer tools. C# and .NET at work, Rust at home. Based in Bavaria, Germany." The owner asked for Rust: "could we say rust at home or something"; it replaces "side projects out of curiosity". Type sizes evened out after the owner said "it feels so strange the big Manuel Schülein small Backend dev and other font with I work etc": the name from 172 px to 132 px, the role from 25 px to about 30 px, the paragraph from 16 px muted to about 20 px in full ink. The picture's cell is now about 458 px tall at 1440x900, so it is no longer upscaled.

Earlier proposal: "I build the parts users never see: APIs, business systems and developer tools. C# and .NET at work, side projects out of curiosity. Based in Bavaria, Germany." in place of today's lede (`content/_index.md:4`), and the paragraph widened from 46ch to 62ch so it runs in three lines across the column. The owner asked: "could we change the text to make it a bit better and also to remove the whitespace". The facts are today's; "build" replaces "work across", and "the parts users never see" is my wording for backend work.

### Size

Picked: bigger overall, so the sheet fills a laptop window again (the owner: "could we make it bigger overall? to much whitespace now"): the name up to 180 px, the paragraph up to 28 px with balanced lines, the link labels up to 39 px with 16 px descriptions and taller cells. At 1440x900 the sheet runs from the bar to the footer again. Wider than 1440 px the page keeps home-18's 1440 px container, so a 1920 px window still has wide margins.

### Spike

Approved: the bigger version (the owner: "thats great :D"); the spec is written from it.

Picked: a throwaway mockup, [spike/](spike/) (home-18's files plus an appended block at the end of `spike/css/home.css`), after the owner said "just suprise me and show it to me pls". It isn't building and doesn't pass Gate 2. My own calls in it: the surname's line (not the first name's) sits on the eye's height and the name is sized from the picture's height so it fits above; the box round the eye is four corner brackets; a faint red glow on the eye under the scan lines; on arrival the brackets lock onto the eye and the line draws towards the name (motion only without reduced motion); on phones the picture stacks on top with the brackets and no line. Measured: no horizontal overflow at 390, 1440 and 1920 px; one screen at 1440×900. Headless Chrome doesn't paint the end of the line's draw-in animation, so the screenshots are taken with reduced motion.

Offered: B, the text shrinks to the picture's height (a sharp square picture, the name about 110 px instead of 172 px); C, the links move up under the text only and the picture's column runs past them (no resizing, but the full-width link row is broken).

## Plan review

## Tasks

## Rulings

Grill round 1, all recommendations accepted (the owner: "yes to all"): the site's two sheet marks, not the spike's four; hover keeps the site's triangle slide and description colour, no new colour token; the sheet spans the site's `--pad` gutters, no 1440 px cap; the meta description as proposed; the branch is cut from `job-application-portfolio`; page text stays in `content/_index.md` and `hugo.toml`, and `CLAUDE.md`'s typed-role note is corrected.

## Parking lot

## Deviations

- Built on branch `home-hacker-redesign`, cut from `job-application-portfolio`. Changed: `layouts/home.html`, `assets/css/base.css` (home block and the phone block), `assets/css/motion.css`, `content/_index.md`, `CLAUDE.md`.
- `motion.css`: the view-transition rule recognised the work page by `.sheet`; the home page now has a sheet too, so it recognises the work page by its drawings (`.dwg`), keeping the home page's slide-in.
- Renamed "work" to "projects" (first "study projects", then the owner: "lets go with just projects"): the menu name in `hugo.toml`, the work page title and heading, the checker's bar list and the CLAUDE.md file note. The URL stays /work/. The work page's intro line is removed (the owner asked). Under 860 px the work title is 19vw instead of 22vw (`body.work`): "projects" at 22vw ran past the gutters.
- URL renamed from /work/ to /projects/ (the owner: "pls also the path!" meaning the URL): `content/projects.md`, `layouts/projects.html`, body class `projects`, the checker's page list and home links, motion.css comments and CLAUDE.md. No redirect from /work/: the branch was never published.
- Projects page header redesigned (the owner: "I just dont like the projects headline it just doesnt sit in right"). Mockups A (index row), B (title on the frame), C (quiet kicker) shown; the owner: "second looks great but i dont think it scales". D, built: no visible headline (`h1` visually hidden, the bar marks the page); each project's name and tag are lettered onto the rule above it; all names one size; the top centring tick removed from the projects sheets. Owner: "thats awesome". Screenshots 320 to 2560 px: no overflow; check-site 27 PASS.
- All three projects now use fangtype's sheet (the owner: "keep RustLogger and IsoPrüfi in the same design not different"): one sheet each, the pink triangle on every name, drawing beside the title block; the two-view pair sheet and its CSS are gone. Check-site 27 PASS; no overflow 320 to 2560 px.
- Path page redesigned from scratch (the owner: "could we also redesign the path from scratch?"). Mockups: A, a chart by year with ruled cells; B, one line through the steps, newest first. The owner picked B; the school year first drew as a side branch, moved onto the main line after the owner said "the bos donauwörth wasnt just a detour!"; then "that is it :D". Built: `layouts/path.html` (career and toolkit sheets, names lettered on the top edge), path.css (path-only rules replaced; the now page's shared rules kept), motion.css (the steps rise in turn; the pink-rule plot kept for /now/ only). Check-site 27 PASS; no overflow 320 to 2560 px; /now/ unchanged.
- Hobbies (the owner: "I like all of them just hobbies im just not sure"): first a short dotted list, then an "off the clock" row of five ruled cells under the toolkit cells, each hobby with a short note ("that looks good"). `content/path.md` hobbies are now name/note pairs; the notes "my whole setup, declared" and "to balance the desk" are my wording, accepted with the mockup. Check-site 27 PASS; no overflow 320 to 2560 px.
- WPF removed from the toolkit list (the owner: "lets remove WPF pls rest is great!").
- Now page redesigned from scratch (the owner: "could we also redesign the now page from scratch?"). Mockups A (three ruled cells) and B (the path's pink line) were turned down ("not happy with the design"); then C (no frame: a stamp line, each topic a full-width rule with its name lettered on it, the answer in large type, the first bright and the rest muted) and D (one status paragraph with pink markers and a cursor). The owner picked C. Built: `layouts/now.html`, path.css (the old row rules `.p-wrap`, `.p-r`, `.lab`, `.p-sec`, `.p-now` and `--lc` removed), motion.css (the stamp and topics rise in turn; the pink-rule plot removed). The text in `content/now.md` is unchanged and still says November 2025. Check-site 27 PASS; no overflow 320 to 2560 px; /path/ unchanged.
- Now text (the owner): at work "Working on the Gateway for Business Central."; a new "on the side" row for dead-agent-skills (its description is my wording); "learning" removed ("can you remove learning?"); updated November 2026. Then less space above the rows and the footer, and type that also follows the window height (the owner: "lets remove the head space a bit so we dont need to scrol"): fits one screen at 1440x900 and 1280x720.
- Path page whitespace closed the same way (the owner: "it does not need to be just close the whitespace"): less space above the sheets, between them, between the steps and above the footer, shared with the now page in path.css. 1220 to 930 px tall at 1440x900; a side-by-side layout that would fit one screen was offered and declined.
- Bug found while doing it: removing the empty 1199px media block had left a stray closing brace at the end of base.css, so browsers dropped the first rule of path.css (the path and now pages's space above the content). Removed; the path page now matches the mockup (930 px at 1440x900). Check-site 27 PASS; no overflow 320 to 2560 px on home, projects, path and now.
- Now page again (the owner: "It just doesnt feel like the other pages"): C was the only page without sheets. Mockups E (one sheet "now", the topics as ruled rows inside) and F (one sheet per topic, its name lettered on the top edge). The owner picked F ("F!"). Built: `layouts/now.html`, path.css (the C rules replaced by `.topic`), motion.css (the sheets rise in turn). Fits one screen at 1440x900 and 1280x720.
- Phones break at 700 px, the site's own breakpoint, not the spike's 40rem.
- `python3 scripts/check-site.py` (in `nix develop`): all PASS. Screenshots at 320, 390, 900, 1280x720, 1440x900, 1920x1080 and 2560x1440: no horizontal overflow; one screen at 1280x720 and 1440x900.

## Walkthrough

| goal | plan task | file:line | test |
| ---- | --------- | --------- | ---- |

## Review

## Learned

## Run verdict
