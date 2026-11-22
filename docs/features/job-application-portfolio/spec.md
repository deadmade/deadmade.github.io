# Spec: job application portfolio

Status: approved at Gate 1 (2026-11-07). Planning only: nothing here is built.

## Problem and point

The site is one hugo-coder homepage with a placeholder avatar, and none of its content helps a job application. This work replaces it with a short site of four pages (home, work, path, now) in the design the owner approved, built into the Hugo site with its own layouts and without the theme. The aim is twofold: a hiring engineer in Germany sees within a minute who the owner is, what they built and where they work, and every page has its own title and description for search engines.

Each claim in this spec carries a label that says how I know it:

- **owner** means the owner said it in this run;
- **measured** means I ran it on the studies;
- **verified** means a file or page I read says so;
- **inferred** means it is my reasoning.

The last section lists the choices I made without asking; the grill settles them.

## Reference design

`mockups/study-11/` is the visual and content reference. It takes `index.html` and `work.html` from study 06c and `path.html` and `now.html` from study 10a, and adds a "now" link to the top bar and to the home page's links. Its `style.css` is shared; `path.css` holds the path and now rules (scoped by `body.path`); `study.js` is a throwaway palette toggle and is not part of the product.

- **Home:** name, role, a two-sentence introduction, the picture cut by a diagonal with a lit line, and three links (work, path, now). It fits one screen without a scrollbar. (owner: "strong")
- **Work:** three projects as architecture drawings, each with a title block: fangtype (built alone) leads, followed by RustLogger and IsoPrüfi (team projects). Three independent agents validated the drawings against the repositories, and the drawings were redrawn; the reports are in `validation/`. (owner: "awesome", must not change)
- **Path:** one column. Four steps run newest first, each with its place and what was worked on: Oct 2026 Business Solution Developer; 2023 to 2026 dual study; 2022 to 2023 university entrance qualification; 2019 to 2022 apprenticeship. Then come the toolkit (C#, .NET, SQL large), languages and hobbies. The page uses one pink rule and two text colours.
- **Now:** the same rows: at work, learning, priorities, updated. Its text is the owner's removed November 2025 text and is provisional. (owner: "Will adjust the text down the line")

## Decisions already made (owner)

- English; Germany-focused; broad backend positioning, with C# and .NET in support.
- Night City colours (background `#1A1626`, text `#E6DCF7`, purple surfaces); IBM Plex Mono only; the handle is `deadmade`.
- The owner's own anime-still picture is on the site, in one swappable file; its rights are unverified.
- A short home page with separate work, path and now pages; "now" is in the top bar and on the home page.
- Build approach: own layouts, with hugo-coder dropped (the submodule and its Dependabot entry are removed).
- Accent colour: palette A, pink `#F08BB4`.
- Discord is dropped from the links; the top bar shows GitHub, LinkedIn and mail.
- Sharing preview: text only (title and description), no image.
- The work page keeps its "not to scale" caption.
- The design is settled for now; the owner adjusts the text later.

## Requirements

1. The site has four pages at `/`, `/work/`, `/path/` and `/now/`, each rendered from `content/` and `layouts/`. They share one top bar and one footer, and the current page's item carries `aria-current`. The top bar and the home page's links come from `[[menu.main]]` (verified: `hugo.toml` has no menu today).
2. The home page fits one screen without a scrollbar from 768 px wide and 640 px high (measured on study-11 in iframes). Below that size it scrolls, as `style.css` documents. On phones it scrolls.
3. No page overflows horizontally at any width from 320 to 2560 px. I measured the studies from 320 to 1892 px; 2560 px is not measured yet.
4. Text contrast is at least 4.5:1. Reading text on the path and now pages is 15 px or larger (measured). The smallest text in the work drawings is 10.2 px from 360 px wide and 8.8 px at 320 px (measured on study 06c): a known shortfall below 360 px.
5. No request leaves the site: fonts are self-hosted (`static/fonts`, verified present), and there is no CDN, no analytics and no embeds. No JavaScript ships.
6. Search:
   - each page has its own `<title>` and meta description, set in its front matter;
   - `<html lang="en">`;
   - one canonical URL per page;
   - `sitemap.xml` and the existing `robots.txt`;
   - Open Graph and Twitter tags;
   - descriptive link text;
   - alt text on the picture.

   Google's SEO Starter Guide recommends unique titles and useful descriptions and says Google does not use meta keywords (verified in the source check of the prior-art report), so the `keywords` parameter goes. Hugo's embedded templates can emit the social tags. Inspect the generated HTML before adding any tag by hand, so that none is doubled (prior-art report; the duplicate-tag risk is inferred).
7. The text the owner will edit (path steps, now rows, hobbies, home introduction, project descriptions) lives in `content/` or front matter; the layouts and the SVG partials hold structure only. The work drawings keep their wide and upright versions.
8. Build and deploy stay the same in kind: the GitHub Pages workflow builds with Hugo 0.166.0 and `--minify`. The workflow's submodule checkout and the Dependabot `gitsubmodule` entry are removed. `CLAUDE.md` is updated after the work, because it still describes the theme.
9. Nothing is committed or pushed without the owner asking.

## Seams

- accent colour: resolved in the CSS token file (one `--accent` line, palette A pink or B red); never seen by templates or content.
- profile picture: resolved in `params.avatarurl` and one file under `static/images/`; never seen by any template except the home page's.
- navigation: resolved in `[[menu.main]]` in `hugo.toml` (name, weight, and a description for the home page's links); never seen by the page templates, which do not list their siblings.
- page text: resolved in `content/*.md` and front matter; never seen by the layouts or the SVG partials.
- per-page search metadata (title, description, canonical, sharing preview): resolved in one head partial from front matter, with site defaults; never seen by the page templates.
- fonts: resolved in the CSS font file, with the files in `static/fonts`; no page references a font URL.

## Out of scope

A blog, per-project detail pages, analytics, a contact form, a language switch (a German version), a light colour scheme, a print stylesheet, and any new project write-ups. The brief's "search optimization" is limited to requirement 6. The prior-art report found no research showing that any of its approaches raises hiring outcomes.

## Facts the owner must confirm before the site goes public

Planning does not need these:

- the employer, titles and dates on the path page;
- "Studienarbeit" and "independently" for fangtype (the repository says neither);
- RustLogger's text;
- the picture's rights;
- the hobbies and the now-page text;
- the public email address;
- the tracked env files in the public IsoPrüfi (`secrets.env`, `backup/*.env`) and RustLogger (`.env`) repositories. I never opened them, and the owner should check them before linking those repositories from a job-application site.

## Choices I made without asking, to settle at Gate 1

- One dark colour scheme only; the theme's light and dark toggle goes.
- Favicons and the web manifest are regenerated with `scripts/generate-favicons.py` to match the palette (`hugo.toml` has `mask_icon_color = "#1565c0"`, blue).
- No structured data (JSON-LD `Person`): the prior-art sources do not cover it, so it stays out until someone shows it is worth having.
- A simple 404 page in the same style.
- The real name leads and the handle sits in the top bar, as in the studies.
- I read "types" in RustLogger as the two log kinds and redrew the diagram on that reading; the owner has not confirmed it.
