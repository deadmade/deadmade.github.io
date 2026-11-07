Gaps: Hugo documentation is rolling; Context7 lists v0.165.0, while this repository deploys v0.166.0. Exact-version theme documentation was fetched at commit `58d956f41c056a12e15d5b6ee27c54fc98cd6e49`. No research establishes a hiring conversion uplift, and no private employment results or project metrics were verified. Source check (2026-11-07, independent agent, all 7 cited pages opened): 11 confirmed / 1 not supported / 0 couldn't open. The one failure, `hugo.toml:29`, is corrected below. Claims that cite nothing: the Context7 version, the effort ratings, "needs no runtime API…", and C's premise. The Hugo docs links are not tied to v0.166.0, and the Chiang and Academic Pages links point at `main` / `master`, not a pinned commit.

# Prior art: job application portfolio

Repository facts: Hugo Extended 0.166.0 is pinned in `.github/workflows/hugo.yml:22`; `hugo.toml:4` selects hugo-coder, and `hugo.toml:25` starts its author/profile settings. The existing content surface is `content/_index.md`. This proposal needs no runtime API, authentication, retries, or asynchronous data loading.

## A — Expand the existing profile

Used by: [hugo-coder configuration example](https://github.com/luizdepra/hugo-coder/blob/58d956f41c056a12e15d5b6ee27c54fc98cd6e49/docs/configurations.md#complete-example).

Keep the author identity and social links; add a short professional introduction, selected work, and visible contact links in static content. Use the theme's menu configuration and custom SCSS extension.

- [source] The pinned theme documents headline, description, avatar, automatic color scheme, custom SCSS, weighted social links, and weighted menus in its [configuration reference](https://github.com/luizdepra/hugo-coder/blob/58d956f41c056a12e15d5b6ee27c54fc98cd6e49/docs/configurations.md#theme-parameters).
- [inferred] Good for a small portfolio: preserves the current stack and limits template maintenance. Costs little implementation work but cannot compensate for thin evidence. A bad fit when many projects need individual explanations. (The last two sentences are the report's reasoning; no cited page addresses them.)

Effort: S.

## B — Curated evidence with a project collection

Used by: [Brittany Chiang's project component](https://raw.githubusercontent.com/bchiang7/v4/main/src/components/sections/projects.js), [Academic Pages portfolio archive](https://raw.githubusercontent.com/academicpages/academicpages.github.io/master/_pages/portfolio.html).

Store projects as content and render a short selected list on the homepage, with detail pages when the evidence warrants them. Each entry should connect a problem, personal contribution, technical decision, and verifiable artifact; that editorial schema is [inferred], not prescribed by these examples.

- [source] Chiang queries Markdown project front matter for title, technologies, GitHub and external URLs; initially shows six projects and links an archive. Its animation code checks reduced-motion preferences.
- [source] Academic Pages uses a dedicated `site.portfolio` collection rendered through an archive-item include (`archive-single.html`), separating project content from its listing template.
- [inferred] Good for linking engineering claims to inspectable work and reusing one content source. Costs a content schema and project template. Bad fit if project ownership or results cannot be substantiated; omit unsupported outcomes rather than filling cards with claims.

Effort: M.

## C — Profile as an outbound evidence directory

Used by: [GitHub pinned repositories](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/pinning-items-to-your-profile).

Keep the site compact and send readers to a small set of strong repositories or gists. The website provides context; external artifacts carry technical detail.

- [source] GitHub explicitly positions pins as a way to show best work quickly and permits up to six repositories and gists combined.
- [inferred] Good when repository documentation is already strong; inexpensive to maintain locally. Costs reader context switching and depends on external availability. Bad fit for private work or repositories without usable explanations. (Costs and bad fit are the report's reasoning; the GitHub page does not discuss them.)

Effort: S.

## Constraints and pitfalls

- [source] [Hugo front matter](https://gohugo.io/content-management/front-matter/#fields) distinguishes descriptions from summaries, reserves field names, and places custom metadata under `params`. [Embedded templates](https://gohugo.io/templates/embedded/) provide social metadata; inspect generated HTML before adding duplicate tags. The duplicate-tag warning is [inferred].
- [source] Google's [SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide) recommends clear unique titles, useful descriptions, descriptive links, and relevant image alt text. It states Google does not use meta keywords and gives no indexing guarantee. [inferred] Improve truthful visible copy before expanding the current keyword list.

Recommendation: B with A's existing theme and C's artifact links. [inferred] This creates inspectable evidence for applications without introducing a new framework or live dependency. C's links to GitHub do depend on that outside service staying available.
