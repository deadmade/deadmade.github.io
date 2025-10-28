# Manuel Schüleins Portfolio

Ein minimalistisches Portfolio und Blog erstellt mit [Hugo](https://gohugo.io/) und [TailwindCSS](https://tailwindcss.com/).

## 🚀 Features

- **Zero Node.js dependencies** - Nur Hugo und TailwindCSS CLI
- **Minimalistisches Design** - Klares, modernes Design mit TailwindCSS
- **Blog-System** - Vollständiges Blog mit Tags, Kategorien und Suche
- **Dunkler Modus** - Automatische und manuelle Umschaltung
- **Responsive Design** - Mobile-first Ansatz
- **Schnelle Ladezeiten** - Statische Site mit minimalem JavaScript
- **SEO-optimiert** - Meta-Tags, Open Graph, Sitemap
- **Suchfunktion** - Client-seitige Suche mit Fuse.js
- **RSS-Feed** - Automatisch generiert für Blog-Posts

## 📋 Voraussetzungen

- **Hugo Extended** Version 0.138.0 oder höher
- Git

### Hugo Installation

**Windows (Chocolatey):**
```powershell
choco install hugo-extended
```

**Windows (Scoop):**
```powershell
scoop install hugo-extended
```

**Windows (Winget):**
```powershell
winget install Hugo.Hugo.Extended
```

**macOS (Homebrew):**
```bash
brew install hugo
```

**Linux:**
```bash
# Download from GitHub releases
wget https://github.com/gohugoio/hugo/releases/download/v0.138.0/hugo_extended_0.138.0_linux-amd64.deb
sudo dpkg -i hugo_extended_0.138.0_linux-amd64.deb
```

## 🛠️ Entwicklung

### Lokale Entwicklung starten

```bash
# Repository klonen
git clone https://github.com/deadmade/deadmade.github.io.git
cd deadmade.github.io

# Entwicklungsserver starten
hugo server -D

# Server läuft auf http://localhost:1313
```

### Build für Produktion

```bash
hugo --minify
```

Die generierte Website befindet sich dann im `public/` Verzeichnis.

## 📝 Content Management

### Neuen Blog-Post erstellen

```bash
hugo new blog/mein-neuer-post.md
```

Dies erstellt eine neue Markdown-Datei in `content/blog/` mit vorausgefülltem Front Matter:

```yaml
---
title: "Mein Neuer Post"
date: 2025-01-15
draft: true
tags: []
categories: []
description: ""
---
```

### Draft-Status entfernen

Setze `draft: false` im Front Matter, um den Post zu veröffentlichen.

### Inhaltsstruktur

```
content/
├── _index.md          # Homepage
├── blog/              # Blog-Posts
├── projects/          # Projekte
├── experience.md      # Berufserfahrung
├── education.md       # Bildungsweg
├── hobbies.md         # Hobbies
├── reading.md         # Leseliste
├── contact.md         # Kontakt
└── search.md          # Suchseite
```

## 🎨 Theme-Anpassungen

### Farben ändern

Bearbeite `tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        // Deine Farben hier
      },
    },
  },
}
```

### Layout-Anpassungen

Die Layouts befinden sich in `themes/portfolio/layouts/`:

- `_default/baseof.html` - Basis-Template
- `_default/single.html` - Einzelseiten
- `blog/list.html` - Blog-Übersicht
- `blog/single.html` - Einzelner Blog-Post
- `index.html` - Homepage

### CSS anpassen

Bearbeite `assets/css/main.css` für custom Styles.

## 🚢 Deployment

### GitHub Pages (Automatisch)

Die Website wird automatisch via GitHub Actions deployed, wenn du pushst:

```bash
git add .
git commit -m "Update content"
git push origin main
```

Die GitHub Actions Workflow-Datei: `.github/workflows/hugo.yml`

### Manuelles Deployment

```bash
# Build erstellen
hugo --minify

# public/ Verzeichnis deployen
# (z.B. zu einem anderen Hosting-Provider)
```

## 📂 Projektstruktur

```
.
├── archetypes/           # Content-Templates
├── assets/               # CSS, JS, Bilder
│   └── css/
│       └── main.css      # TailwindCSS Hauptdatei
├── content/              # Alle Inhalte (Markdown)
├── themes/
│   └── portfolio/
│       └── layouts/      # HTML-Templates
│           ├── _default/
│           ├── blog/
│           └── partials/
├── .github/
│   └── workflows/
│       └── hugo.yml      # CI/CD Pipeline
├── hugo.toml             # Hugo-Konfiguration
├── tailwind.config.js    # TailwindCSS-Konfiguration
└── postcss.config.js     # PostCSS-Konfiguration
```

## 🔍 Suche verwenden

Die Suchfunktion ist verfügbar unter `/search`. Sie durchsucht alle Blog-Posts und Seiten in Echtzeit.

## 📱 Features im Detail

### Dark Mode

Der Dark Mode wird automatisch basierend auf den System-Einstellungen aktiviert. Benutzer können manuell zwischen Hell und Dunkel wechseln. Die Einstellung wird in localStorage gespeichert.

### Tags & Kategorien

Blog-Posts können mit Tags und Kategorien versehen werden:

```yaml
tags: ["hugo", "webdev", "tutorial"]
categories: ["entwicklung"]
```

Alle Tags/Kategorien sind unter `/tags/` und `/categories/` verfügbar.

### RSS Feed

Der RSS-Feed ist automatisch verfügbar unter `/index.xml`.

## 🤝 Migrationshinweise

Dies ist eine komplette Neuentwicklung, die folgende Verbesserungen bringt:

- ❌ **Entfernt:** React, Node.js, 50+ npm-Pakete, komplexes Build-System
- ✅ **Hinzugefügt:** Hugo (single binary), TailwindCSS, Blog mit Suche
- ⚡ **Performance:** 10-100x schnellere Builds
- 🎯 **Einfachheit:** Markdown statt React-Komponenten

## 📄 Lizenz

Dieses Projekt ist für den persönlichen Gebrauch von Manuel Schülein.

## 🔗 Links

- [Hugo Documentation](https://gohugo.io/documentation/)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [Live Website](https://deadmade.github.io)

## 📧 Kontakt

Manuel Schülein - [info@manuelschuelein.de](mailto:info@manuelschuelein.de)

GitHub: [@deadmade](https://github.com/deadmade)
