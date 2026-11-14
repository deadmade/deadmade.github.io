#!/usr/bin/env python3
"""Build the site as CI does and check the output: python3 scripts/check-site.py

Prints PASS/FAIL <check> <page>[: reason] per check and page; exits 1 on any FAIL.
The checks are listed in docs/features/job-application-portfolio/plan.md, Task 1, and docs/features/seo/plan.md.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from collections import Counter
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://manuelschuelein.de"
PAGES = {"/": "index.html", "/projects/": "projects/index.html", "/path/": "path/index.html", "/now/": "now/index.html"}
OG_IMAGE = "/images/og.png"  # params.images in hugo.toml; the file is static/images/og.png, drawn by scripts/generate-og-image.py
BAR = ["projects", "path", "now", "github", "linkedin", "mail"]
results = []


def check(name, page, problems):
    results.append((name, page, "; ".join(problems)))


class Page(HTMLParser):
    """Collects what the checks read from one page."""

    def __init__(self):
        super().__init__()
        self.lang, self.a, self.robots = None, None, None
        self.titles, self.desc, self.links, self.srcs, self.imgs = [], [], [], [], []
        self.anchors, self.nav, self.go, self.current = [], [], [], []
        self.meta, self.images, self.content = Counter(), {}, {}
        self.foot, self.name, self.role = None, "", ""  # the footer's first span: "<name> · <role>"
        self.h1, self.scripts, self.ld = None, [], []  # ld: the text of each application/ld+json script
        self.in_head = self.in_title = self.in_nav = self.in_go = self.in_foot = self.in_foot_span = False
        self.in_h1 = self.in_ld = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        elif tag in ("head", "body"):
            self.in_head = tag == "head"
        elif tag == "title" and self.in_head:  # the drawings' SVG titles sit in the body
            self.in_title = True
            self.titles.append("")
        elif tag == "meta":
            key = a.get("name") or a.get("property")
            self.meta[key] += 1
            self.content[key] = a.get("content")
            if key in ("og:image", "twitter:image"):
                self.images[key] = a.get("content")
            if key == "robots":
                self.robots = a.get("content") or ""
            if key == "description":
                self.desc.append((a.get("content") or "").strip())
        elif tag == "link":
            self.links.append(a)
        elif tag == "img":
            self.imgs.append(a)
        elif tag == "nav":
            self.in_nav = True
        elif tag == "ul":
            self.in_go = "go" in (a.get("class") or "").split()
        elif tag == "footer":
            self.in_foot = True
        elif tag == "span" and self.in_foot and self.foot is None:
            self.foot, self.in_foot_span = "", True
        elif tag == "h1":
            self.h1, self.in_h1 = "", True
        elif tag == "script":
            self.scripts.append((a.get("type") or "").strip().lower())
            if self.scripts[-1] == "application/ld+json":
                self.ld.append("")
                self.in_ld = True
        elif tag == "a":
            self.a = {"href": a.get("href"), "label": (a.get("aria-label") or "").strip(), "text": "",
                      "cls": (a.get("class") or "").split()}
        if "src" in a:
            self.srcs.append(a["src"])
        if a.get("aria-current") == "page":
            self.current.append(a.get("href"))

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False
        elif tag == "title":
            self.in_title = False
        elif tag == "nav":
            self.in_nav = False
        elif tag == "ul":
            self.in_go = False
        elif tag == "footer":
            self.in_foot = False
        elif tag == "span" and self.in_foot_span:
            self.in_foot_span = False
            name, _, role = self.foot.partition(" · ")
            self.name, self.role = name.strip(), role.strip()
        elif tag == "h1" and self.in_h1:
            self.in_h1 = False
            self.h1 = " ".join(self.h1.split())
        elif tag == "script":
            self.in_ld = False
        elif tag == "a" and self.a is not None:
            self.anchors.append(self.a)
            if self.in_nav:
                self.nav.append(self.a)
            if self.in_go:
                self.go.append(self.a)
            self.a = None

    def handle_data(self, data):
        if self.in_title:
            self.titles[-1] += data
        if self.a is not None:
            self.a["text"] += data
        if self.in_foot_span:
            self.foot += data
        if self.in_h1:
            self.h1 += data
        if self.in_ld:
            self.ld[-1] += data


def png_size(path):
    """(width, height) from a PNG's IHDR chunk; ValueError when the file is missing or not a PNG."""
    if not path.is_file():
        raise ValueError("is missing")
    with path.open("rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        raise ValueError("is not a PNG")
    return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")


def classify(ref):
    """'empty', 'skip' (fragment, mailto, data), 'external', 'relative' (no leading slash), or the site path."""
    ref = (ref or "").strip()
    if not ref:
        return "empty"
    if ref.startswith("#"):
        return "skip"
    if ref.startswith(BASE + "/") or (ref.startswith("/") and not ref.startswith("//")):
        return urlparse(ref).path
    scheme = urlparse(ref).scheme
    return "external" if ref.startswith("//") or scheme in ("http", "https") else "skip" if scheme else "relative"


def ref_problem(out, kind, ref):
    """What is wrong with one reference; kind 'a' may leave the site, the others may not."""
    where = classify(ref)
    if where == "empty":
        return f"empty {kind} reference"
    if where == "relative":
        return f"{kind} {ref} is document-relative"
    if where == "external":
        return None if kind == "a" else f"{kind} {ref} leaves the site"
    rel = where.lstrip("/")
    if where != "skip" and not (out / (rel + "index.html" if rel == "" or rel.endswith("/") else rel)).is_file():
        return f"{kind} {ref} names no file"


def check_pages(out, pages):
    try:
        og_size, og_problems = [str(n) for n in png_size(out / OG_IMAGE.lstrip("/"))], []
    except ValueError as e:
        og_size, og_problems = [], [f"{OG_IMAGE} {e}"]
    for path, p in pages.items():
        title = [t.strip() for t in p.titles]
        canonical = [x.get("href") for x in p.links if x.get("rel") == "canonical"]
        problems = [f"lang is {p.lang!r}"] if p.lang != "en" else []
        problems += [f"{len(title)} <title> in <head>, or empty"] if len(title) != 1 or not title[0] else []
        problems += [f"{len(p.desc)} meta descriptions, or empty"] if len(p.desc) != 1 or not p.desc[0] else []
        problems += [f"canonical is {canonical}"] if canonical != [BASE + path] else []
        check("head", path, problems + ["meta keywords present"] * bool(p.meta["keywords"])
              + [f"robots meta {p.robots!r} present"] * (p.robots is not None))
        want = ["og:title", "og:description", "og:url", "og:image", "og:image:width", "og:image:height", "og:image:alt",
                "twitter:card", "twitter:image", "twitter:image:alt"]
        alt = f"{p.name}, {p.role}"  # what the share image shows: the name over the role
        check("social", path, [f"{k} appears {p.meta[k]} times" for k in want if p.meta[k] != 1]
              + [f"{k} is {p.images.get(k)!r}, expected {BASE}{OG_IMAGE}" for k in ("og:image", "twitter:image")
                 if p.images.get(k) != BASE + OG_IMAGE]
              + [f"og:url is {p.content.get('og:url')!r}, expected {BASE + path}"] * (p.content.get("og:url") != BASE + path)
              + (og_problems or [f"{k} is {p.content.get(k)!r}, the file says {v}"
                                 for k, v in zip(("og:image:width", "og:image:height"), og_size) if p.content.get(k) != v])
              + [f"{k} is {p.content.get(k)!r}, expected {alt!r}" for k in ("og:image:alt", "twitter:image:alt")
                 if p.content.get(k) != alt])
        bar = [a["text"].strip() for a in p.nav]
        problems = [f"bar reads {bar}"] if bar != BAR else []
        problems += [f"aria-current=page on {p.current}"] if [urlparse(h or "").path for h in p.current] != [path] else []
        if path == "/" and [urlparse(a["href"] or "").path for a in p.go] != ["/projects/", "/path/", "/now/"]:
            problems.append(f"home links are {[a['href'] for a in p.go]}")
        check("nav", path, problems)
        check("a11y", path, [f"img without alt: {i.get('src')}" for i in p.imgs if not (i.get("alt") or "").strip()]
              + [f"link without text: {a['href']}" for a in p.anchors if not (a["text"].strip() or a["label"])])
    for label, values in (("title", [t.strip() for p in pages.values() for t in p.titles]),
                          ("description", [d for p in pages.values() for d in p.desc])):
        check("head", "-", [f"{label} repeats: {v!r}" for v, n in Counter(values).items() if n > 1])


def check_icon(out, p):
    """Google shows a PNG icon (not the SVG), larger than 48x48; every PNG icon link's sizes must match its file."""
    problems, sides = [], []
    for link in p.links:
        if link.get("rel") == "icon" and link.get("type") == "image/png":
            href, sizes = link.get("href") or "", link.get("sizes") or ""
            try:
                size = png_size(out / urlparse(href).path.lstrip("/"))
            except ValueError as e:
                problems.append(f"{href} {e}")
                continue
            if sizes != f"{size[0]}x{size[1]}" or size[0] != size[1]:
                problems.append(f"{href} says sizes={sizes!r}, the file is {size[0]}x{size[1]}")
            else:
                sides.append(size[0])
    check("icon", "/", problems + ["no PNG icon larger than 48x48"] * (not any(n > 48 for n in sides)))


def check_data(out, p):
    """The home page's JSON-LD says only what the page shows (Google's structured-data rule)."""
    try:
        doc = json.loads(p.ld[0]) if p.ld else None
    except ValueError as e:
        return check("data", "/", [f"the JSON-LD block is not JSON: {e}"])
    if not isinstance(doc, dict):
        return check("data", "/", ["no JSON-LD block on the home page" if doc is None else "the JSON-LD block is not an object"])
    graph = doc.get("@graph") if isinstance(doc.get("@graph"), list) else []
    nodes = {n.get("@type"): n for n in graph if isinstance(n, dict)}
    site, page = nodes.get("WebSite", {}), nodes.get("ProfilePage", {})
    person = page.get("mainEntity") if isinstance(page.get("mainEntity"), dict) else {}
    home, mod, title = BASE + "/", lastmods(out).get(BASE + "/"), (p.titles or [""])[0].strip()
    mark = next((a["text"].strip() for a in p.anchors if "mark" in a["cls"]), "")
    img = (p.imgs or [{}])[0].get("src") or ""
    alternate = tomllib.loads((ROOT / "hugo.toml").read_text(encoding="utf-8")).get("params", {}).get("alternatename")
    job = person.get("jobTitle")
    problems = [f"the home page shows no {k}" for k, v in (("<h1>", p.h1), ("<title>", title), ("mark", mark), ("<img>", img), ("role", p.role)) if not v]
    problems += [f"@graph holds {sorted(map(str, nodes))} in {len(graph)} nodes, expected one WebSite and one ProfilePage"] * (
        len(graph) != 2 or set(nodes) != {"WebSite", "ProfilePage"})
    problems += [f"{key} is {found!r}, expected {want!r}" for key, found, want in (
        ("@context", doc.get("@context"), "https://schema.org"),
        ("WebSite name", site.get("name"), p.h1), ("WebSite url", site.get("url"), home),
        ("ProfilePage url", page.get("url"), home), ("ProfilePage name", page.get("name"), title),
        ("mainEntity @type", person.get("@type"), "Person"), ("Person name", person.get("name"), p.h1),
        ("Person alternateName", person.get("alternateName"), [alternate, mark]), ("Person url", person.get("url"), home),
        ("Person image", person.get("image"), BASE + img),
        ("Person jobTitle, lowercased", job.lower() if isinstance(job, str) else job, p.role),
        ("Person sameAs", person.get("sameAs"), [a["href"] for a in p.nav if (a["href"] or "").startswith("https://")]),
    ) if found != want]
    try:  # the same instant: a +00:00 commit is written Z in the JSON-LD and +00:00 in the sitemap
        same = datetime.fromisoformat(page.get("dateModified")) == datetime.fromisoformat(mod)
    except (TypeError, ValueError):
        same = False
    check("data", "/", problems + [f"ProfilePage dateModified is {page.get('dateModified')!r}, the sitemap lastmod for / is {mod}"] * (not same))


def check_links(out, pages):
    sheets = set()
    for path, p in pages.items():
        raw = (out / PAGES[path]).read_text(encoding="utf-8")
        refs = [("src", s) for s in p.srcs] + [("link", x.get("href")) for x in p.links] + [("a", a["href"]) for a in p.anchors]
        refs += [("meta", v) for v in p.images.values()]
        problems = [m for kind, ref in refs if (m := ref_problem(out, kind, ref))]
        scripts, allowed = raw.lower().count("<script"), 1 if path == "/" else 0  # the one JSON-LD block sits on the home page
        problems += [f"<script type={t!r}> present" for t in p.scripts if t != "application/ld+json"]
        problems += [f"{scripts} '<script' in the HTML, the parser saw {len(p.scripts)} scripts"] * (scripts != len(p.scripts))
        problems += [f"{len(p.ld)} JSON-LD blocks, at most {allowed} allowed"] * (len(p.ld) > allowed)
        check("links", path, problems + ["names a font file"] * (".woff2" in raw))
        sheets |= {urlparse(x["href"]).path for x in p.links if x.get("rel") == "stylesheet" and (x.get("href") or "").startswith("/")}
    for sheet in sorted(sheets):
        css = (out / sheet.lstrip("/")).read_text(encoding="utf-8")
        refs = re.findall(r"url\(\s*['\"]?([^'\")\s]+)['\"]?\s*\)", css) + re.findall(r"@import\s+['\"]([^'\"]+)", css)
        check("links", sheet, [m for ref in refs if (m := ref_problem(out, "css", ref))])


def check_404(out):
    """The 404 page is served at any missing path: it must not be indexed, and its references must work from anywhere."""
    p = Page()
    raw = (out / "404.html").read_text(encoding="utf-8")
    p.feed(raw)
    problems = [f"robots meta is {p.robots!r}, expected 'noindex'"] if p.robots != "noindex" else []
    problems += ["<script> present"] * ("<script" in raw.lower())
    problems += ["canonical present"] * any(x.get("rel") == "canonical" for x in p.links)
    refs = [("src", s) for s in p.srcs] + [("link", x.get("href")) for x in p.links] + [("a", a["href"]) for a in p.anchors]
    check("404", "/404.html", problems + [m for kind, ref in refs if (m := ref_problem(out, kind, ref))])


def lastmods(out):
    """Each sitemap <loc> mapped to its <lastmod>, or None when the URL has none."""
    sitemap = out / "sitemap.xml"
    text = sitemap.read_text(encoding="utf-8") if sitemap.is_file() else ""
    return {loc.group(1): (mod.group(1) if (mod := re.search(r"<lastmod>([^<]+)</lastmod>", url)) else None)
            for url in re.findall(r"<url>(.*?)</url>", text, re.S) if (loc := re.search(r"<loc>([^<]+)</loc>", url))}


def check_sitemap(out):
    robots, dates = out / "robots.txt", lastmods(out)
    want = {BASE + p for p in PAGES}
    lines = robots.read_text(encoding="utf-8").splitlines() if robots.is_file() else []
    stamp = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})"  # RFC 3339, as Google reads lastmod
    check("sitemap", "-", ([f"sitemap lists {sorted(dates)}, expected {sorted(want)}"] if set(dates) != want else [])
          + [f"no lastmod for {url}" if mod is None else f"lastmod {mod} for {url} is not RFC 3339"
             for url, mod in sorted(dates.items()) if mod is None or not re.fullmatch(stamp, mod)]
          + ([f"robots.txt lacks 'Sitemap: {BASE}/sitemap.xml'"] if f"Sitemap: {BASE}/sitemap.xml" not in lines else [])
          + [f"robots.txt says {line!r}" for line in lines if re.match(r"\s*disallow\s*:\s*\S", line, re.I)])


def check_dates(out):
    """The now page's "updated" month is the month of its Git date, as the sitemap gives it."""
    mod, page = lastmods(out).get(BASE + "/now/"), out / PAGES["/now/"]
    said = re.findall(r"updated ([A-Za-z]+ \d{4})", page.read_text(encoding="utf-8") if page.is_file() else "")
    want = datetime.fromisoformat(mod).strftime("%B %Y") if mod else None  # %B is English: Python keeps the C locale for dates
    check("dates", "/now/", [] if want and said == [want] else [f"now page says updated {said}, its sitemap lastmod is {mod}"])


def check_host(out):
    """The build, hugo.toml and (in CI) the Pages address all name BASE; the check builds with --baseURL, so it reads the other two itself."""
    problems = [f"old host in {f.relative_to(out).as_posix()}" for f in sorted(out.rglob("*")) if f.is_file() and b"deadmade.github.io" in f.read_bytes()]
    base_url = tomllib.loads((ROOT / "hugo.toml").read_text(encoding="utf-8")).get("baseURL")
    problems += [f"hugo.toml baseURL is {base_url}, expected {BASE}/"] * (base_url != BASE + "/")
    pages = os.environ.get("PAGES_BASE_URL")  # set by CI to the address the deploy build uses
    problems += [f"Pages address {pages} is not {BASE}"] * (pages is not None and pages.rstrip("/") != BASE)
    check("host", "-", problems)


def check_seams(out):
    declared = sum(f.read_text(encoding="utf-8").count("--accent:") for f in out.rglob("*.css"))
    problems = [f"--accent: is declared {declared} times in the built CSS, expected 1"] if declared != 1 else []
    for sheet in sorted(out.rglob("*.css")):  # all motion sits in the one no-preference block, which ends the sheet
        css = sheet.read_text(encoding="utf-8")
        gate = re.search(r"@media\s*\(\s*prefers-reduced-motion\s*:\s*no-preference\s*\)(?=\s*\{)", css)  # a query list ("..., all") never matches
        hit = re.search(r"animation|transition|@keyframes|view-transition|(?<![\w-])scroll-behavior", css[:gate.start()] if gate else css)
        if hit:
            problems.append(f"{hit.group(0)} in {sheet.name} before the no-preference block")
        if gate:
            depth = 0
            for i in range(css.index("{", gate.end()), len(css)):
                depth += (css[i] == "{") - (css[i] == "}")
                if depth == 0:
                    problems += [f"text after the no-preference block in {sheet.name}"] * bool(css[i + 1:].strip())
                    break
            else:
                problems.append(f"the no-preference block in {sheet.name} never closes")
    for source in [ROOT / "hugo.toml", *sorted(f for d in ("layouts", "content", "static") for f in (ROOT / d).rglob("*") if f.is_file())]:
        text, name = source.read_text(encoding="utf-8", errors="ignore"), source.relative_to(ROOT)
        if name.parts[0] != "static":  # static/icons/favicon.svg carries the accent on purpose (scripts/generate-favicons.py)
            problems += [f"accent colour in {name}"] * bool(re.search(r"F08BB4|FF544A", text, re.I))
        problems += [f"site host in {name}"] * (source.name != "hugo.toml" and bool(re.search(r"deadmade\.github\.io|manuelschuelein\.de", text)))
    check("seams", "-", problems)


def main():
    out = Path(tempfile.mkdtemp(prefix="check-site-"))
    try:
        done = subprocess.run(["hugo", "-s", str(ROOT), "--minify", "--panicOnWarning", "--baseURL", BASE + "/", "-d", str(out)],
                              capture_output=True, text=True)
        check("build", "-", [f"hugo exited {done.returncode}: {(done.stdout + done.stderr).strip()[-600:]}"] if done.returncode else [])
        if done.returncode == 0:
            files, want = {p.relative_to(out).as_posix() for p in out.rglob("*.html")}, {*PAGES.values(), "404.html"}
            check("files", "-", [f"html files are {sorted(files)}, expected {sorted(want)}"] if files != want else [])
            pages = {}
            for path, name in PAGES.items():
                if (out / name).is_file():
                    pages[path] = Page()
                    pages[path].feed((out / name).read_text(encoding="utf-8"))
            check_pages(out, pages)
            if "/" in pages:
                check_icon(out, pages["/"])
                check_data(out, pages["/"])
            check_links(out, pages)
            check_404(out)
            check_sitemap(out)
            check_dates(out)
            check_host(out)
            check_seams(out)
    finally:
        shutil.rmtree(out, ignore_errors=True)
    for name, page, reason in results:
        print(f"{'FAIL' if reason else 'PASS'} {name} {page}" + (f": {reason}" if reason else ""))
    return int(any(reason for *_, reason in results))


if __name__ == "__main__":
    sys.exit(main())
