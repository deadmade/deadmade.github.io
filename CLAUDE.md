# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is Manuel Schülein's personal portfolio website built with Hugo and deployed to GitHub Pages. The site is a static website using the hugo-coder theme with custom extensions for timelines and dynamic project loading.

## Technology Stack

- **Hugo Extended** v0.152.2+ - Static Site Generator
- **hugo-coder theme** - Base theme (located in `themes/hugo-coder/`)
- **Dart Sass** - For SCSS compilation
- **Node.js** - For build scripts only (GitHub project fetching)
- **GitHub Actions** - CI/CD for automated deployment

## Development Commands

### Local Development
```bash
# Start development server with drafts
hugo server -D

# Start development server without drafts
hugo server

# Server runs at http://localhost:1313
```

### Building
```bash
# Build for production
hugo --minify

# Build with specific base URL
hugo --minify --baseURL "https://deadmade.github.io/"

# Output will be in public/ directory
```

### Content Management
```bash
# Create new blog post
hugo new blog/post-name.md

# Create new content page
hugo new content-name.md
```

### GitHub Project Sync
```bash
# Fetch GitHub pinned repositories (requires GITHUB_TOKEN)
GITHUB_TOKEN=your_token GITHUB_USERNAME=deadmade node scripts/fetch-projects.js

# Output: data/projects.json
```

## Project Structure

### Content Organization
```
content/
├── _index.md         # Homepage (empty, uses theme default)
├── blog/             # Blog posts (currently hidden in menu)
├── projects/         # Projects page (uses data/projects.json)
├── resume.md         # Professional resume (embedded PDF from GitHub)
└── freetime.md       # Hobbies and free time activities
```

### Custom Components

**Resume Page**
- Layout: `layouts/resume/single.html` (custom layout with PDF embed)
- Content: `content/resume.md` (minimal frontmatter only)
- PDF source: Local file (`static/pdfs/resume.pdf` → served at `/pdfs/resume.pdf`)
- Styled with `assets/scss/resume.scss`
- Features: Full-height PDF viewer, download button
- Updates when `static/pdfs/resume.pdf` is replaced and committed

**Projects System**
- Layout: `layouts/projects/list.html`
- Data source: `data/projects.json` (auto-generated via GitHub API)
- Script: `scripts/fetch-projects.js` (Node.js, fetches pinned repos)
- Styled with `assets/scss/projects.scss`

### Custom Styling

Main SCSS entry point: `assets/scss/custom.scss`
- Imports `projects.scss` and `resume.scss`
- Configured in `hugo.toml` as `customSCSS = ["scss/custom.scss"]`

Key design features:
- Resume page: Full-height PDF viewer with accent color blue (`#1565c0` / `#42a5f5` dark)
- Responsive design with mobile breakpoints at 768px
- Dark mode support via prefers-color-scheme
- Print-optimized styles for resume page

### Configuration

**hugo.toml** - Main configuration file
- Language: German (de-DE)
- Theme: hugo-coder
- Base URL: https://deadmade.github.io/
- Menu items: Lebenslauf, Projekte, Freizeit
- Social links: GitHub, LinkedIn, Email, Discord
- Custom SCSS: custom.scss

## GitHub Actions Workflow

File: `.github/workflows/hugo.yml`

**Build Process:**
1. Checkout with submodules (for theme)
2. Setup Go, Node.js, Dart Sass, and Hugo
3. Run `node scripts/fetch-projects.js` to sync GitHub projects
4. Build with `hugo --gc --minify`
5. Deploy to GitHub Pages

**Environment Variables:**
- `GITHUB_TOKEN` - Required for fetching pinned repositories
- `GITHUB_USERNAME` - Set to "deadmade"

## Important Implementation Details

### Resume Page
- Content file: `content/resume.md` (minimal frontmatter only)
- Layout: `layouts/resume/single.html` (custom PDF embed layout)
- PDF file: `static/pdfs/resume.pdf` (served at `/pdfs/resume.pdf`)
- No external dependencies or authentication tokens
- Update by replacing the PDF file in the repository

### Projects Page
- Projects are **not** manually maintained
- Auto-fetched from GitHub pinned repositories during build
- Edit `scripts/fetch-projects.js` to change fetching behavior
- Data stored in `data/projects.json` (gitignored, generated during build)

### Blog Section
- Blog infrastructure exists but is currently commented out in menu
- To enable: uncomment blog menu item in `hugo.toml` (lines 73-77)

### Static Assets
- Favicons: `/static/icons/` directory
- Company logos: `/images/logos/companies/`
- Theme assets: in `themes/hugo-coder/`

## Common Development Patterns

### Updating the Resume
1. Update your resume in your LaTeX repository
2. Compile LaTeX to PDF
3. Replace `static/pdfs/resume.pdf` in this repository with the new PDF
4. Commit and push changes
5. GitHub Actions will build and deploy the updated site

### Customizing Styles
1. Add styles to `assets/scss/custom.scss` or create new SCSS partial
2. Import new partials in `custom.scss`
3. Hugo will recompile on save

### Modifying the Theme
- **Do not** edit files in `themes/hugo-coder/` directly
- Override theme templates by creating same path in root `layouts/` directory
- Example: Override theme's projects list at `layouts/projects/list.html`

## Deployment

**Automatic:**
- Push to `main` branch triggers GitHub Actions
- Workflow builds and deploys to GitHub Pages automatically

**Manual (if needed):**
```bash
hugo --minify --baseURL "https://deadmade.github.io/"
# Then manually deploy public/ folder
```

## Language & Localization

- Default language: German (de-DE)
- Content is primarily in German
- Theme supports i18n (translations in `themes/hugo-coder/i18n/de.toml`)

## Notes

- Site uses Git submodules for theme management
- Blog posts support tags and categories (infrastructure ready)
- Dark mode automatically follows system preferences
- Site is fully responsive with mobile-first approach
