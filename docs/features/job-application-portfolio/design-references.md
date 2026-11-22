Gaps: (1) The browser tool cannot set a viewport or capture full pages: shots are first-screen only, desktop as a 1440x900 iframe and mobile as a 390x844 iframe inside a 1892x956 window (media queries respond; not device emulation), converted from JPEG to PNG. The browser prefers dark, so OS-aware sites render dark. (2) No design write-up praising these sites was found; "well regarded" rests on directory inclusion. (3) No neon or cyberpunk site by a working engineer survived the search (only templates and student portfolios); the dark examples here are restrained. (4) No author is a C#/.NET developer; I did not search for one. (5) xnacly.me and joshua.hu were opened but dropped for length.

Found via: Ask HN thread https://news.ycombinator.com/item?id=46618714 (directory criterion: "well received in past HN discussions") feeding https://hnpwd.github.io/ (hnpwd), plus https://webofdevs.com/.

## 1. tonsky.me — https://tonsky.me/
Opinionated text-first blog with a consulting hook. Author in Berlin [source: https://tonsky.me/about/]. In both lists [source].
- Stack: unknown (no generator tag; own style.css and script.js) [observed].
- Layout: nav, bordered intro note, year-grouped post list; nothing else above the fold [observed].
- Type/colour: IBM Plex Sans (your site uses Plex Mono) [observed]; one saturated yellow (253,219,41), black text, kept even under a dark OS preference; sun toggle [observed].
- Proof: writing, plus "I consult on all things Clojure" and a GitHub link in the note [observed].
- Personal: portrait tinted to the page yellow; stars beside some posts; a first-person offer instead of a tagline [observed].
- Criticism: no project list; black-on-yellow tires [inferred].

## 2. susam.net — https://susam.net/
Plain-HTML text-first. In hnpwd [source].
- Stack: unknown; zero scripts, one main.css, no webfonts [observed].
- Layout: title, tagline "On Technology, Mathematics, Etc.", "(78 pages)", then ~16 dated links [observed].
- Type/colour: Georgia/serif 18px; #111 background, #bbb text, pale-blue links; follows the OS light/dark setting [observed][source: https://susam.net/about.html].
- Proof: 78 pages [observed]; blogroll, open-source work since 2007 [source about page].
- Personal: page count and "© 2001–2026" are the only ornaments [observed].
- Criticism: nothing says what he does or how to hire him [observed].

## 3. antfu.me — https://antfu.me/
Modern minimal maintainer homepage. In webofdevs [source].
- Stack: Vue app mounted on #app [observed]; public repo, MIT code and CC BY-NC-SA text [source: https://github.com/antfu/antfu.me].
- Layout: narrow column: h1, one-line pitch, four chip rows (Working at, Creator of, Core team of, Maintaining), three paragraphs, socials [observed].
- Type/colour: Inter body, DM Mono loaded; near-black (5,5,5), grey text, white links, no accent; dark class on html, moon toggle [observed].
- Proof: credentials as logo chips (Vitest, Slidev, UnoCSS, Vue, Vite) [observed].
- Personal: handwritten "af" mark; "fanatical open sourceror"; hobby pages (photos, hardware) [observed].
- Criticism: assumes famous projects; icon-only nav [observed][inferred].

## 4. samwho.dev — https://samwho.dev/
Personality-led essay showcase, dark. In hnpwd [source].
- Stack: unknown; theme-color meta carries data-light and data-dark [observed].
- Layout: centred column: logo, five links, bio, photo; then ~12 essays (Big O, Bloom Filters…) under "I write." [observed].
- Type/colour: system stacks only (Seravek body, Iowan Old Style headings); warm near-black, grey text [observed].
- Proof: "visual, interactive essays", one to three months each; paid commissions [observed].
- Personal: SAMWHO keycap logo on a cable; bio mentions whisky and spiders [observed].
- Criticism: needs essays of that calibre; no CV or contact path above the fold [inferred].

## 5. cookie.engineer — https://cookie.engineer/
Playful dark homebrew; footer "Made with 💔 in Germany" [observed].
- Stack: unknown; own /design/index.css and index.mjs, joke generator meta ("peppermint tea and nightly VIM sessions") [observed]. In hnpwd [source].
- Layout: avatar plus bubble pitch ("Cyber Defense Engineer with AI, NetSec, WebSec, OSINT"), then project cards with art, date, tags; nav lists Conf Talks, CTF Writeups, Wiki [observed].
- Type/colour: custom webfont "crumble", vera-mono footer; muted slate (64,64,80), cyan links, thin rainbow scroll strip [observed].
- Proof: dated projects, talks, CTF writeups [observed].
- Personal: Cookie Monster avatar, hooded-monster project art; footer "All rights (and jokes) reserved under European Law" [observed].
- Criticism: at 390px titles truncate ("Qw…") and text is justified [observed]; mascot art may read as unserious to recruiters [inferred].

## 6. alexharri.com — https://alexharri.com/
Polished dark technical blog. In hnpwd [source].
- Stack: Next.js (/_next/ chunks) [observed]; public repo [source: https://alexharri.com/about].
- Layout: two nav links, three "Popular posts" cards (third fades at the edge), bio bubble; page ~1270px tall [observed].
- Type/colour: Fira Sans, MonoLisa credited in the footer; navy-black (9,13,19), pale-blue text (185,219,250), thin card borders [observed]. Google Fonts is loaded [observed].
- Proof: deep essays, employer history on /about [source about page].
- Personal: bio as speech bubble beside the photo; `/blog` and `/about` as inline code chips [observed].
- Criticism: no projects or CV on the home page [observed]; Google Fonts is a GDPR point for a German site [inferred].

## 7. maciejwalkowiak.com — https://maciejwalkowiak.com/
Freelance Java/Spring Boot consultant in Berlin [source: homepage]. In webofdevs [source].
- Stack: VitePress component classes (VPNav, VPNavBar) plus utility classes; no generator tag [observed].
- Layout: nav Home/Blog, h1, one-sentence pitch, round photo, then full blog excerpts with tag chips; ~7980px tall [observed].
- Type/colour: Inter variable; #1b1b1f, amber links (229,175,64), purple tag chips [observed].
- Proof: blog posts with code (Testcontainers, Flyway, JPA) [observed].
- Personal: the pitch gives city, stack and outcome in one sentence; amber-ringed photo [observed].
- Criticism: no contact or hire link in nav; long excerpt feed [observed].

## 8. jvt.me — https://www.jvt.me/
IndieWeb blog/feed; Nottingham [observed]. In hnpwd [source].
- Stack: Hugo v0.168.0 (generator tag); site and theme repos on GitLab linked from page [observed].
- Layout: nine-link nav (/now, Blog, Archives, Salary History, Open Source, Support Me, Hire Me…), photo, long bio, then a day-by-day feed; ~18,000px tall [observed].
- Type/colour: Atkinson Hyperlegible; brown-black (28,27,25), tan text, hot-pink links [observed]. /now names Srcery as his colourscheme [source: https://www.jvt.me/about/]; the site may follow it [inferred].
- Proof: Renovate project lead at Mend; maintainer of oapi-codegen and Renovate [observed].
- Personal: /now page; pronouns and ADHD note; public Salary History; partner, cat, dog linked [observed].
- Criticism: long and link-heavy; disclosures are a personal choice [inferred].

## 9. brittanychiang.com — https://brittanychiang.com/
Dark-navy single-page portfolio archetype (frontend). In webofdevs [source].
- Stack: footer: "Built with Next.js and Tailwind CSS, deployed with Vercel… set in Inter" [observed].
- Layout: sticky left column (name, role, tagline, three nav items, icons); right: About, dated Experience with tech pills, Projects; ~3860px [observed].
- Type/colour: Inter only, small tracked uppercase section labels; slate (15,23,42) background, slate-grey text, teal pills, blue glow top-left [observed].
- Proof: experience timeline, projects, GitHub/LinkedIn [observed].
- Personal: spare-time line ("Korok seeds"); accessibility as stated specialty [observed].
- Criticism: widely copied: the v4 repo README (older Gatsby version) asks forkers for credit [source: https://github.com/bchiang7/v4], so it can read as a template [inferred].

## Summary

| Site | Style | Stack | Density | Mode | Screenshots (in docs/features/job-application-portfolio/references/) |
|---|---|---|---|---|---|
| tonsky.me | text-first, opinionated | unknown | low | light (yellow) | tonsky-{desktop,mobile}.png |
| susam.net | plain-HTML text | unknown | low | OS-driven (seen dark) | susam-{desktop,mobile}.png |
| antfu.me | minimal maintainer page | Vue | low | dark (toggle) | antfu-{desktop,mobile}.png |
| samwho.dev | personality essays | unknown | low | dark (OS-driven) | samwho-{desktop,mobile}.png |
| cookie.engineer | playful dark homebrew | unknown | medium | dark | cookie-engineer-{desktop,mobile}.png |
| alexharri.com | polished dark blog | Next.js | low | dark | alexharri-{desktop,mobile}.png |
| maciejwalkowiak.com | consultant + blog | VitePress (class names) | medium | dark (toggle) | maciejwalkowiak-{desktop,mobile}.png |
| jvt.me | dense IndieWeb feed | Hugo | high | dark (warm) | jvt-me-{desktop,mobile}.png |
| brittanychiang.com | navy portfolio archetype | Next.js + Tailwind | medium | dark | brittanychiang-{desktop,mobile}.png |
