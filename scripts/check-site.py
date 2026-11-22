#!/usr/bin/env python3
"""Build the site as CI does and check the output: python3 scripts/check-site.py

Prints PASS/FAIL <check> <page>[: reason] per check and page; exits 1 on any FAIL.
The checks are listed in docs/features/job-application-portfolio/plan.md, Task 1, docs/features/seo/plan.md and
docs/features/diagram-animations/plan.md (Task 4); the runs check has grown since, and CLAUDE.md's Gotchas say what it
fails on.
"""
import html
import json
import math
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
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://manuelschuelein.de"
PAGES = {"/": "index.html", "/projects/": "projects/index.html", "/path/": "path/index.html", "/now/": "now/index.html"}
OG_IMAGE = "/images/og.png"  # params.images in hugo.toml; the file is static/images/og.png, drawn by scripts/generate-og-image.py
BAR = ["projects", "path", "now", "github", "linkedin", "mail"]
OLD_HOST = r"(?<![^/]/)deadmade\.github\.io"  # the old host; in github.com/deadmade/deadmade.github.io it is the repository's name
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
        self.meta, self.content = Counter(), {}
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
              + [f"{k} is {p.content.get(k)!r}, expected {BASE}{OG_IMAGE}" for k in ("og:image", "twitter:image")
                 if p.content.get(k) != BASE + OG_IMAGE]
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


def check_data(out, p, config):
    """The home page's JSON-LD says only what the page shows (Google's structured-data rule)."""
    try:
        doc = json.loads(p.ld[0]) if p.ld else None
    except ValueError as e:
        return check("data", "/", [f"the JSON-LD block is not JSON: {e}"])
    if not isinstance(doc, dict):
        return check("data", "/", ["no JSON-LD block on the home page" if doc is None else "the JSON-LD block is not an object"])
    graph = doc.get("@graph") if isinstance(doc.get("@graph"), list) else []
    nodes = {str(n.get("@type")): n for n in graph if isinstance(n, dict)}  # str: a list-valued @type is one more mismatch
    site, page = nodes.get("WebSite", {}), nodes.get("ProfilePage", {})
    person = page.get("mainEntity") if isinstance(page.get("mainEntity"), dict) else {}
    home, mod, title = BASE + "/", lastmods(out).get(BASE + "/"), (p.titles or [""])[0].strip()
    mark = next((a["text"].strip() for a in p.anchors if "mark" in a["cls"]), "")
    img = (p.imgs or [{}])[0].get("src") or ""
    alternate = {k.lower(): v for k, v in config.get("params", {}).items()}.get("alternatename")  # Hugo reads param keys in any case
    job, profiles = person.get("jobTitle"), person.get("sameAs")
    problems = [f"the home page shows no {k}" for k, v in (("<h1>", p.h1), ("<title>", title), ("mark", mark), ("<img>", img), ("role", p.role)) if not v]
    problems += ["hugo.toml sets no params.alternatename"] * (not alternate)
    problems += [f"@graph holds {sorted(nodes)} in {len(graph)} nodes, expected one WebSite and one ProfilePage"] * (
        len(graph) != 2 or set(nodes) != {"WebSite", "ProfilePage"})
    try:  # the same instant: a +00:00 commit is written Z in the JSON-LD and +00:00 in the sitemap
        same = datetime.fromisoformat(page.get("dateModified")) == datetime.fromisoformat(mod)
    except (TypeError, ValueError):
        same = False
    for name, node, want in (  # each node's keys, each with the value the page shows; any other key is a problem
        ("the block", doc, {"@context": "https://schema.org", "@graph": graph}),
        ("WebSite", site, {"@type": "WebSite", "name": p.h1, "url": home}),
        ("ProfilePage", page, {"@type": "ProfilePage", "url": home, "name": title, "mainEntity": person,
                               "dateModified": page.get("dateModified") if same else f"the instant of the sitemap lastmod for /, {mod}"}),
        ("Person", {**person, "jobTitle": job.lower() if isinstance(job, str) else job,  # the role ignoring case, as G7 says
                    "sameAs": [unquote(u) if isinstance(u, str) else u for u in profiles] if isinstance(profiles, list) else profiles},
         {"@type": "Person", "name": p.h1, "alternateName": [alternate, mark], "url": home, "image": BASE + img, "jobTitle": p.role.lower(),
          "sameAs": [unquote(a["href"]) for a in p.nav if (a["href"] or "").startswith("https://")]}),  # the href escapes a raw ü, the block doesn't
    ):
        problems += [f"{name} has {k!r}, a key the check does not compare with the page" if k not in want
                     else f"{name} {k} is {node.get(k)!r}, expected {want[k]!r}"
                     for k in sorted(node.keys() | want.keys()) if k not in want or node.get(k) != want[k]]
    check("data", "/", problems)


def check_links(out, pages):
    sheets = set()
    for path, p in pages.items():
        raw = (out / PAGES[path]).read_text(encoding="utf-8")
        refs = [("src", s) for s in p.srcs] + [("link", x.get("href")) for x in p.links] + [("a", a["href"]) for a in p.anchors]
        refs += [("meta", p.content[k]) for k in ("og:image", "twitter:image") if k in p.content]
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
    """The now page's "updated" month is the month of its Git date, as the sitemap gives it, from a checkout with its history."""
    mod, page = lastmods(out).get(BASE + "/now/"), out / PAGES["/now/"]
    said = re.findall(r"updated ([A-Za-z]+ \d{4})", page.read_text(encoding="utf-8") if page.is_file() else "")
    try:
        want = datetime.fromisoformat(mod).strftime("%B %Y")  # %B is English: Python keeps the C locale for dates
    except (TypeError, ValueError):  # no lastmod, or one that isn't ISO (only a custom sitemap template writes one)
        want = None
    shallow = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--is-shallow-repository"], capture_output=True, text=True).stdout.strip()
    check("dates", "/now/", ([] if want and said == [want] else [f"now page says updated {said}, its sitemap lastmod is {mod}"])
          + ["the Git checkout is shallow, so every page gets the last commit's date (CI checks out with fetch-depth: 0)"] * (shallow == "true"))


def check_host(out, config):
    """The build, hugo.toml and (in CI) the Pages address all name BASE; the check builds with --baseURL, so it reads the other two itself."""
    problems = [f"old host in {f.relative_to(out).as_posix()}" for f in sorted(out.rglob("*")) if f.is_file() and re.search(OLD_HOST.encode(), f.read_bytes())]
    base_url = config.get("baseurl")
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
    host = rf"{OLD_HOST}|{re.escape(urlparse(BASE).netloc)}"  # the old and the current host
    mail = r"(?<![\w.+/-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+"  # info@<host> is mail and is removed first; a URL's user@<host> follows a / and stays
    for source in [ROOT / "hugo.toml", *sorted(f for d in ("layouts", "content", "static", "data") for f in (ROOT / d).rglob("*") if f.is_file())]:
        text, name = source.read_text(encoding="utf-8", errors="ignore"), source.relative_to(ROOT)
        if name.parts[0] != "static":  # static/icons/favicon.svg carries the accent on purpose (scripts/generate-favicons.py)
            problems += [f"accent colour in {name}"] * bool(re.search(r"F08BB4|FF544A", text, re.I))
        problems += [f"site host in {name}"] * (source.name != "hugo.toml" and bool(re.search(host, re.sub(mail, "", text))))
    check("seams", "-", problems)


def scope_root(prelude):
    """The root selector of an @scope prelude, read to its matching parenthesis; * when it has none (or an unbalanced one),
    which reads it wide; None for any other at-rule."""
    if not prelude.startswith("@scope"):
        return None
    m = re.match(r"@scope\s*\(", prelude)
    depth, i = 1, m.end() if m else 0
    while m and i < len(prelude) and depth:
        depth += (prelude[i] == "(") - (prelude[i] == ")")
        i += 1
    return prelude[m.end():i - 1] if m and depth == 0 else "*"


def css_rules(css, around=()):
    """(prelude, body, the at-rules around it) of each rule in minified CSS, looking inside every at-rule that holds rules;
    @keyframes come whole."""
    i = 0
    while (j := css.find("{", i)) >= 0:
        prelude, depth, k = css[i:j].rsplit(";", 1)[-1].strip(), 1, j + 1
        while depth:
            depth += (css[k] == "{") - (css[k] == "}")
            k += 1
        if prelude.startswith("@") and "{" in css[j + 1:k - 1] and not re.match(r"@(-\w+-)?keyframes\b", prelude):
            if (root := scope_root(prelude)) and (own := own_declarations(css[j + 1:k - 1])):
                yield root, own, around  # an @scope's own declarations style its root
            yield from css_rules(css[j + 1:k - 1], around + (prelude,))
        elif root := scope_root(prelude):
            yield root, css[j + 1:k - 1], around  # an @scope's own declarations style its root
        else:
            yield prelude, css[j + 1:k - 1], around
        i = k


def own_declarations(body):
    """The declarations of a block that also holds rules: its text outside the nested blocks, less their preludes."""
    top, depth = [], 0
    for ch in body:
        depth += (ch == "{") - (ch == "}")
        top.append("\0" if ch == "{" and depth == 1 else ch if depth == 0 and ch != "}" else "")
    pieces = "".join(top).split("\0")
    return ";".join(x for x in [q.rsplit(";", 1)[0] if ";" in q else "" for q in pieces[:-1]] + pieces[-1:] if x.strip(" ;"))


def props(body):
    """The property names a rule body or keyframes block sets, without a vendor prefix."""
    return [re.sub(r"^-(?:webkit|moz|ms|o)-", "", k) for k in re.findall(r"(?:^|[;{])\s*([\w-]+)\s*:", body)]


ANIMATION = r"(?:^|;)\s*(?:-\w+-)?animation(?:-name)?\s*:\s*([^;]*)"


def animation_names(body):
    """Every word of the rule's animation and animation-name values (a keyframes name among them)."""
    values = re.findall(ANIMATION, body)
    return [t.strip("\"'") for v in values for t in re.sub(r"[\w-]+\([^)]*\)", " ", v).replace(",", " ").split()]


VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Elements(HTMLParser):
    """The built page's elements (tag, attributes, classes, id, parent, place among the parent's children, text inside);
    `all` lists them in order, `drawn` every svg.dwg and every element inside one."""

    def __init__(self):
        super().__init__()
        self.open, self.all, self.drawn = [None], [], []

    def handle_starttag(self, tag, attrs):
        a, parent = dict(attrs), self.open[-1]
        el = {"tag": tag, "a": a, "cls": set((a.get("class") or "").split()), "id": a.get("id"), "parent": parent, "kids": [], "text": ""}
        if parent:
            el["i"] = len(parent["kids"])
            parent["kids"].append(el)
        self.all.append(el)
        if (tag == "svg" and "dwg" in el["cls"]) or (parent and parent.get("drawn")):
            el["drawn"] = True
            self.drawn.append(el)
        if tag not in VOID:
            self.open.append(el)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.open.pop()

    def handle_data(self, data):
        for el in self.open[1:]:
            el["text"] += data

    def handle_endtag(self, tag):
        for i in range(len(self.open) - 1, 0, -1):
            if self.open[i]["tag"] == tag:
                del self.open[i:]
                break


def under(el):
    """Every element inside el, in order."""
    for kid in el["kids"]:
        yield kid
        yield from under(kid)


def picks(el, comps, ops, i):
    """Whether compound i of a selector (and the compounds and combinators before it) can match the element."""
    tag, cls, ids, nodwg = comps[i]
    if (tag and el["tag"] != tag) or not cls <= el["cls"] or (ids and ids != {el["id"]}):
        return False
    if nodwg and any(e["tag"] == "svg" and "dwg" in e["cls"] for e in under(el)):
        return False
    if i == 0:
        return True
    if ops[i] == ">":
        return el["parent"] is not None and picks(el["parent"], comps, ops, i - 1)
    if ops[i] == " ":
        up = el["parent"]
        while up is not None:
            if picks(up, comps, ops, i - 1):
                return True
            up = up["parent"]
        return False
    before = el["parent"]["kids"][:el["i"]] if el["parent"] else []
    return any(picks(s, comps, ops, i - 1) for s in (before[-1:] if ops[i] == "+" else before))


def reaches(selector, els):
    """True when a rule's selector can pick one of els (a drawing or something in it). A pseudo-class, :not(), :has() or
    attribute test counts as matching anything, which only widens what is picked, except :not(:has(.dwg)), the site's way to
    leave the projects page out, which is read as written; a selector that ends in a pseudo-element picks no element (an SVG
    element has no ::before or ::after; ::view-transition-* hang off the root)."""
    selector = selector.replace(":not(:has(.dwg))", "%nodwg")
    while (s := re.sub(r"(?<!:):[\w-]+\((?:[^()]|\([^()]*\))*\)", "*", selector)) != selector:
        selector = s
    selector = re.sub(r"\[[^\]]*\]|(?<!:):(?!:)[\w-]+", "*", selector)
    for sel in re.split(r",(?![^()]*\))", selector):
        comps, ops, op = [], [], None
        for comb, space, comp in re.findall(r"\s*([>+~])\s*|(\s+)|([^\s>+~]+)", sel.strip()):
            if comp:
                tag = re.match(r"[A-Za-z][\w-]*", comp)
                comps.append((tag[0].lower() if tag else None, set(re.findall(r"\.(-?[A-Za-z_][\w-]*)", comp)), set(re.findall(r"#([\w-]+)", comp)), "%nodwg" in comp))
                ops.append(op or " ")
                op = None
            else:
                op = comb or op or " "
        if comps and "::" not in sel and any(picks(el, comps, ops, len(comps) - 1) for el in els):
            return True
    return False


def reaches_in(p, around, els):
    """reaches() for a rule inside @scope (root) blocks: what it picks must also be, or sit inside, what each root picks.
    A rule that names :scope or & keeps the wide reading."""
    roots = [r for a in around if (r := scope_root(a))]
    if not roots or re.search(r":scope|&", p):
        return reaches(p, els)
    for el in (e for e in els if reaches(p, [e])):
        chain, up = [], el
        while up is not None:
            chain.append(up)
            up = up["parent"]
        if all(reaches(r, chain) for r in roots):
            return True
    return False


def svg_elements(svg):
    """(tag, attributes, text) of each path, polygon, rect and text in a drawing's source, in order."""
    return [(m[1], dict(re.findall(r'([\w-]+)="([^"]*)"', m[2])), (m[3] or "").strip())
            for m in re.finditer(r"<(path|polygon|rect|text)\b([^>]*?)/?>(?:([^<]*)</text>)?", svg)]


def arrow_points(d):
    """The vertices of an authored path.ln (absolute M, H and V only); None if it uses anything else."""
    tokens, pts = re.findall(r"[A-Za-z]|-?\d*\.?\d+", d), []
    while tokens:
        c = tokens.pop(0)
        try:
            if c == "M":
                pts.append((float(tokens.pop(0)), float(tokens.pop(0))))
            elif c in "HV" and pts:
                v = float(tokens.pop(0))
                pts.append((v, pts[-1][1]) if c == "H" else (pts[-1][0], v))
            else:
                return None
        except (IndexError, ValueError):
            return None
    return pts


def along(arrow, p):
    """How far along the arrow (an axis-parallel polyline) a point lies, or None if it is off it."""
    done = 0.0
    for (ax, ay), (bx, by) in zip(arrow, arrow[1:]):
        if min(ax, bx) - 1e-6 <= p[0] <= max(ax, bx) + 1e-6 and min(ay, by) - 1e-6 <= p[1] <= max(ay, by) + 1e-6 and (ax == bx or ay == by):
            return done + abs(p[0] - ax) + abs(p[1] - ay)
        done += abs(bx - ax) + abs(by - ay)
    return None


def on_arrow(arrow, pts):
    """A hop's points lie on the arrow, in its direction, and between two of them the arrow runs straight."""
    pos = [along(arrow, p) for p in pts]
    if None in pos or any(b <= a for a, b in zip(pos, pos[1:])):
        return False
    corners = list(zip(arrow, [along(arrow, v) for v in arrow]))
    return all(abs((v[0] - p[0]) * (q[1] - p[1]) - (v[1] - p[1]) * (q[0] - p[0])) < 1e-6
               for (p, a), (q, b) in zip(zip(pts, pos), zip(pts[1:], pos[1:])) for v, c in corners if a < c < b)


def bounds(shape):
    """The box (x0, y0, x1, y1) around a stop's rect or polygon, or None (also for a malformed one)."""
    try:
        if "rect" in shape:
            x, y, w, h = map(float, shape["rect"])
            return x, y, x + w, y + h
        p = [float(v) for v in re.findall(r"-?\d*\.?\d+", shape["polygon"])]
        return min(p[0::2]), min(p[1::2]), max(p[0::2]), max(p[1::2])
    except (KeyError, TypeError, ValueError):
        return None


def ring(p, d):
    """The polygon p (x and y in turn) grown by d units: each vertex where its two edges meet once moved d outward."""
    pts = list(zip(p[0::2], p[1::2]))
    edges = list(zip(pts, pts[1:] + pts[:1]))
    turn = 1 if sum(ax * by - bx * ay for (ax, ay), (bx, by) in edges) > 0 else -1
    lines = []
    for (ax, ay), (bx, by) in edges:
        n = (turn * (by - ay) / math.dist((ax, ay), (bx, by)), -turn * (bx - ax) / math.dist((ax, ay), (bx, by)))
        lines.append((*n, n[0] * ax + n[1] * ay + d))
    return [((c1 * y2 - c2 * y1) / (x1 * y2 - y1 * x2), (x1 * c2 - x2 * c1) / (x1 * y2 - y1 * x2))
            for (x1, y1, c1), (x2, y2, c2) in zip(lines[-1:] + lines[:-1], lines)]


SHAPE_FORMS = {"rect": "[x, y, width, height]", "polygon": '"x,y x,y x,y"', "path": 'a string, "M x y H x V y"', "text": '[x, y, "label"]'}


def malformed(shape):
    """How a stop's or span's shape in data/runs.toml is written in the wrong form, so the checks after it don't trip on it."""
    if not isinstance(shape, dict):
        return [f"its shape {shape!r} is not a table"]
    num = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)  # noqa: E731
    ok = {"rect": lambda v: isinstance(v, list) and len(v) == 4 and all(map(num, v)),
          "polygon": lambda v: isinstance(v, str) and len(re.findall(r"-?\d*\.?\d+", v)) in range(6, 10 ** 4, 2),
          "path": lambda v: isinstance(v, str),
          "text": lambda v: isinstance(v, list) and len(v) == 3 and num(v[0]) and num(v[1]) and isinstance(v[2], str)}
    return [f"its {k} = {v!r} is not written as {SHAPE_FORMS[k]}" for k, v in shape.items() if k in ok and not ok[k](v)]


def shape_matches(shape, els):
    def nums(s):
        return [float(x) for x in re.findall(r"-?\d*\.?\d+", s)]
    def has(tag, cls, ok):
        return any(t == tag and cls in a.get("class", "").split() and ok(a, txt) for t, a, txt in els)
    def grown(drawn, p):
        try:
            r = ring(drawn, 4)
        except ZeroDivisionError:  # a repeated or collinear vertex
            return False
        return len(p) == 2 * len(r) and all(any(abs(x - p[2 * j]) <= .1 and abs(y - p[2 * j + 1]) <= .1 for j in range(len(r))) for x, y in r)
    found = {"rect": lambda r: has("rect", "bx", lambda a, _: [float(a.get(k, "nan")) for k in ("x", "y", "width", "height")] == [float(v) for v in r]),
             "polygon": lambda p: has("polygon", "st", lambda a, _: nums(a.get("points", "")) == nums(p)) or has(
                 "polygon", "acc", lambda a, _: grown(nums(a.get("points", "")), nums(p))),
             "path": lambda d: has("path", "ln", lambda a, _: a.get("d") == d),
             "text": lambda t: any(tag == "text" and [float(a.get("x", "nan")), float(a.get("y", "nan"))] == [float(t[0]), float(t[1])]
                                   and html.unescape(txt) == t[2] for tag, a, txt in els)}
    return [f"its {k} {shape[k]} matches no {k} of the drawing" if k in found else f"unknown shape {k}" for k in shape
            if k not in found or not found[k](shape[k])]


def check_runs(out):
    """The runs (data/runs.toml): routes on their drawing's arrows from stop to stop, outlines on its components, every layer
    hidden from screen readers and wired to its keyframes, the layers and their switches behind the gate, one switch per
    drawing that says its words, nothing inside a drawing moved beyond fill and stroke opacity and dash offset, and nothing
    in a projects sheet or what holds it moved but the run layers."""
    problems = []
    data = tomllib.loads((ROOT / "data" / "runs.toml").read_text(encoding="utf-8"))
    for name, d in data.get("drawing", {}).items():
        partial = ROOT / "layouts" / "_partials" / f"drawing-{name}.html"
        svgs = {m[1]: m[0] for m in re.finditer(r'<svg class="dwg ([hv])"[\s\S]*?</svg>', partial.read_text(encoding="utf-8"))} if partial.is_file() else {}
        for o in ("h", "v"):
            if o not in svgs:
                problems.append(f"{name}: no {o} drawing in {partial.relative_to(ROOT)}")
                continue
            src = re.sub(r"\{\{-?\s*/\*.*?\*/\s*-?\}\}", "", svgs[o], flags=re.S)
            calls = [(a.get("name"), a.get("o")) for a in (dict(re.findall(r'"([\w-]+)"\s+"([^"]*)"', m))
                                                             for m in re.findall(r'partial\s+"run\.html"\s+\(dict\s+([^)]*)\)', src))]
            problems += [f"{name} {o}: its drawing draws the runs {calls}, expected [('{name}', '{o}')]" if calls and all(None not in c for c in calls) else
                         f"{name} {o}: its drawing has no run.html call the check can read; write it as "
                         f"{{{{ partial \"run.html\" (dict \"name\" \"{name}\" \"o\" \"{o}\") }}}}"] * (calls != [(name, o)])
            els = svg_elements(svgs[o])
            arrows = []
            for (tag, a, _), nxt in zip(els, els[1:]):
                if tag == "path" and "ln" in a.get("class", "").split():
                    pts = arrow_points(a.get("d", ""))
                    if pts is None:
                        problems.append(f"{name} {o}: cannot read path d=\"{a.get('d')}\"")
                    elif nxt[0] == "polygon" and "ah" in nxt[1].get("class", "").split():
                        tip = re.findall(r"-?\d*\.?\d+", nxt[1].get("points", ""))[2:4]
                        arrows.append(pts + [(float(tip[0]), float(tip[1]))])
            boxes = {}
            for s in d.get("stop", []):
                shape = s.get(o, {})
                bad = malformed(shape)
                problems += [f"{name} {o} stop {s.get('id')}: {p}" for p in bad or shape_matches(shape, els)]
                keys = sorted(shape) if isinstance(shape, dict) else []
                problems += [f"{name} {o} stop {s.get('id')}: its shape has {keys}, expected one rect or one polygon"] * (
                    len(keys) != 1 or not {"rect", "polygon"} >= set(keys))
                boxes[s.get("id")] = None if bad else bounds(shape)
            for i, s in enumerate(d.get("span", [])):
                shape, ends = s.get(o, {}), [boxes.get(s.get("first")), boxes.get(s.get("last"))]
                bad = malformed(shape)
                problems += [f"{name} {o} span {i} ({s.get('first')} to {s.get('last')}): {p}" for p in bad or shape_matches(shape, els)]
                if bad or None in ends:
                    continue  # the shape's or the stop's own message says what is wrong
                pts = (arrow_points(shape.get("path", "")) or []) + ([tuple(map(float, shape["text"][:2]))] if "text" in shape else [])
                far = [q for q in pts if not (min(b[0] for b in ends) - 48 <= q[0] <= max(b[2] for b in ends) + 48
                                              and min(b[1] for b in ends) - 48 <= q[1] <= max(b[3] for b in ends) + 48)]
                problems += [f"{name} {o} span {i}: its shape reaches {q}, more than 48 units from its stops' boxes {ends}" for q in far[:1]]
            for r, run in enumerate(d.get("run", []), 1):
                for n, hop in enumerate(run.get("hops", []), 1):
                    pts = [tuple(map(float, p)) for p in hop.get(o, [])]
                    if len(pts) < 2 or not any(on_arrow(a, pts) for a in arrows):
                        problems.append(f"{name} {o} run {r} hop {n} ({hop.get('from')} to {hop.get('to')}) is not on one of the drawing's arrows")
                    # it leaves its stop's edge and ends on the next one's; 3 units of slack, as some upright tips end 2 short
                    for word, end, stop in (("starts", pts[:1], hop.get("from")), ("ends", pts[-1:], hop.get("to"))):
                        b = boxes.get(stop)  # None: the stop's own message says what is wrong with its shape
                        if end and b and not (b[0] - 3 <= end[0][0] <= b[2] + 3 and b[1] - 3 <= end[0][1] <= b[3] + 3):
                            problems.append(f"{name} {o} run {r} hop {n} {word} at {end[0]}, off {stop}'s box {b}")
    built = out / PAGES["/projects/"]
    html_text = built.read_text(encoding="utf-8") if built.is_file() else ""
    tree = Elements()
    tree.feed(html_text)
    # what the stylesheet check below can't read: a style attribute in a drawing, a <style> block, an SVG animation tag
    problems += [f"a {el['tag']} on the projects page has a style attribute" for el in tree.all if "style" in el["a"]]
    problems += [f"the projects page has a <{el['tag']}> element" for el in tree.all if el["tag"] in ("style", "animate", "animatetransform", "animatemotion", "set")]
    css = "".join(f.read_text(encoding="utf-8") for f in sorted(out.rglob("*")) if f.is_file() and f.suffix.lower() == ".css")
    # CSS the reading below can't follow fails instead of passing unread
    bare, strings = re.sub(r'"[^"]*"|\'[^\']*\'', "", css), re.findall(r'"[^"]*"|\'[^\']*\'', css)
    unreadable = (["a backslash (a CSS escape)"] * ("\\" in css) + ["@import"] * ("@import" in css.lower()) + ["unbalanced braces"] * (
        bare.count("{") != bare.count("}")) + ["a quoted string with a brace in it"] * any("{" in q or "}" in q for q in strings))
    if unreadable:
        check("runs", "-", problems + [f"the stylesheet has {u}, which the check can't read" for u in unreadable])
        return
    rules = list(css_rules(css))
    problems += [f"{p} holds nested rules" for p, body, _ in rules if not p.startswith("@") and "{" in body]
    frames = {}
    for p, body, _ in rules:
        if name := re.match(r"@(?:-\w+-)?keyframes\s+(\S+)", p):
            frames[name[1].strip("\"'")] = frames.get(name[1].strip("\"'"), "") + body
    animated = [(p, animation_names(body)) for p, body, _ in rules if not p.startswith("@")]
    for p, body, around in rules:
        if not p.startswith("@") and reaches_in(p, around, tree.drawn):
            problems += [f"{p} sets {k}" for k in props(body) if k in ("transform", "translate", "rotate", "scale", "offset") or k.startswith(("offset-", "transition", "view-transition"))]
            for v in re.findall(ANIMATION, body):
                fns = sorted({f + "()" for f in re.findall(r"([\w-]+)\(", v) if f.lower() not in ("cubic-bezier", "steps", "linear")})
                kws = sorted({t for t in re.split(r"[\s,]+", v.lower()) if t in ("inherit", "unset", "revert", "revert-layer")})
                problems += [f"{p} uses {', '.join(fns + kws)} in its animation, which the check can't follow"] * bool(fns + kws)
                problems += [f"{p} sets an animation with !important, which the stop rule can't end"] * bool(re.search(r"!\s*important", v, re.I))
            for a in animation_names(body):
                # an opacity animation, even on the run layers alone, changed how Chrome painted the drawings at rest on HiDPI screens
                bad = [k for k in props(frames.get(a, "")) if k not in ("fill-opacity", "stroke-opacity", "stroke-dashoffset", "animation-timing-function")]
                problems += [f"{p} runs @keyframes {a}, which sets {', '.join(sorted(set(bad)))}"] * bool(bad)
    in_runs = {id(e) for g in tree.all if g["tag"] == "g" and "run" in g["cls"] for e in [g, *under(g)]}
    still = [e for a in tree.all if a["tag"] == "article" and "sheet" in a["cls"] for e in [a, *under(a)] if id(e) not in in_runs]
    for svg in (e for e in tree.drawn if e["tag"] == "svg"):
        up = svg["parent"]
        while up is not None:
            still += [up] * all(up is not a for a in still)
            up = up["parent"]
    for p, body, around in rules:
        if not p.startswith("@") and reaches_in(p, around, still):
            moves = sorted({k for k in props(body) if k.startswith(("transition", "view-transition"))})
            moves += ["animation"] * any(v.strip().lower() != "none" for v in re.findall(ANIMATION, body))
            problems += [f"{p} sets {', '.join(moves)} on a projects sheet or what holds it, where only the run layers move"] * bool(moves)
    # the runs and their switches show only on screen, with motion allowed and where :has() works, so a switch can always stop them
    gate = ("@media(prefers-reduced-motion:no-preference)", "@media screen", "@supports selector(:has(*))")
    for rule in (".dwg .run{display:inline}", ".runbar{display:flex}", ".fig:has(input:checked) .run{display:none}", ".fig:has(input:checked) .run *{animation:none}"):
        where = [around for p, body, around in rules if f"{p}{{{body}}}" == rule]
        problems += [f"{rule} is in the stylesheet {len(where)} times, expected once"] * (len(where) != 1)
        problems += [f"{rule} is not inside {''.join(g + '{' for g in gate)}"] * (len(where) == 1 and where[0] != gate)
    hide = ".dwg .run,.runbar{display:none}"
    for need in (hide, ".dwg .hl{fill-opacity:0;stroke-opacity:0}", ".dwg .pu{stroke-opacity:0}"):
        problems += [f"{need} (base.css) is not in the stylesheet once, outside every at-rule"] * ([a for p, b, a in rules if f"{p}{{{b}}}" == need] != [()])
    shown = [e for e in tree.all if "runbar" in e["cls"] or (e["tag"] == "g" and "run" in e["cls"])]
    for p, body, around in rules:
        decls = re.findall(r"(?:^|;)\s*([\w-]+)\s*:\s*([^;]*)", body)
        if not p.startswith("@") and reaches_in(p, around, shown) and any(k == "all" for k, _ in decls):
            problems.append(f"{p} sets all on a run layer or a switch, which can show it")
        if not p.startswith("@") and reaches_in(p, around, shown) and any(k == "display" and re.sub(r"!\s*important", "", v, flags=re.I).strip().lower() != "none" for k, v in decls):
            problems += [f"{p}{{{body}}} shows a run layer or a switch, which only the gate's two rules may"] * (f"{p}{{{body}}}" not in (".dwg .run{display:inline}", ".runbar{display:flex}") or around != gate)
    svgs = [el for el in tree.drawn if el["tag"] == "svg" and "dwg" in el["cls"]]
    problems += ["no drawings on the built projects page"] * (not svgs)
    for i, svg in enumerate(svgs):
        layers = [g for g in under(svg) if g["tag"] == "g" and "run" in g["cls"]]
        if len(layers) != 1:
            problems.append(f"drawing {i + 1} ({svg['a'].get('class')}) has {len(layers)} run layers, expected 1")
            continue
        layer = layers[0]
        run = next((c for c in sorted(layer["cls"]) if re.fullmatch(r"run-[\w-]+-[hv]", c)), f"drawing {i + 1}")
        problems += [f"{run} is not aria-hidden"] * (layer["a"].get("aria-hidden") != "true")
        groups = {kind: sorted(c for g in under(layer) if g["tag"] == "g" and kind in g["cls"] for c in g["cls"] if c.startswith(kind + "-"))
                  for kind in ("pu", "hl")}
        problems += [f"{run} has no {kind} groups" for kind, found in groups.items() if not found]
        want = {c: [f"{run}-pu{c[3:]}", f"{run}-po{c[3:]}"] for c in groups["pu"]} | {c: [f"{run}-{c[3:]}"] for c in groups["hl"]}
        for c, names in want.items():
            wired = {a for p, names_ in animated if re.search(rf"\.{re.escape(run)}\s+\.{re.escape(c)}(?![\w-])", p) for a in names_}
            problems += [f"{run} .{c} is not wired to @keyframes {a}" for a in names if a not in frames or a not in wired]
        problems += [f"@keyframes {a} animates nothing in {run}" for a in frames if a.startswith(run + "-") and a not in {x for v in want.values() for x in v}]
    # every drawing has its stop / play switch, named with the words it shows (WCAG 2.2.2 and 2.5.3), under a key that says something
    for i, svg in enumerate(svgs, 1):
        fig = svg["parent"]
        while fig is not None and fig["tag"] != "figure":
            fig = fig["parent"]
        problems += [f"drawing {i} is not inside a figure.fig, which holds its switch and which the stop rules read"] * (fig is None or "fig" not in fig["cls"])
    figs = [f for f in tree.all if f["tag"] == "figure" and "fig" in f["cls"] and any(e["tag"] == "svg" and "dwg" in e["cls"] for e in under(f))]
    for n, fig in enumerate(figs, 1):
        bars = [e for e in under(fig) if "runbar" in e["cls"]]
        boxes = [e for e in under(fig) if e["tag"] == "input" and e["a"].get("type") == "checkbox"]
        if len(bars) != 1 or len(boxes) != 1 or all(boxes[0] is not e for e in under(bars[0])):
            problems.append(f"figure {n} has {len(bars)} run bars and {len(boxes)} switches, expected one switch in its one run bar")
            continue
        chain, up = [], boxes[0]
        while up is not None:
            chain.append(up)
            up = up["parent"]
        marks = sorted({k for e in chain for k in ("disabled", "hidden", "inert") if k in e["a"]})
        problems += [f"figure {n}: its switch or what holds it is marked {', '.join(marks)}"] * bool(marks)
        holder = next((e for e in chain if e["tag"] == "label"), None)
        problems += [f"figure {n}: its switch is not inside a label, so its words don't toggle it"] * (holder is None)
        label = (boxes[0]["a"].get("aria-label") or "").lower()
        for kind in ("on", "off"):
            words = [e["text"].strip() for e in under(bars[0]) if kind in e["cls"]]
            problems += [f"figure {n}: its {kind} word sits outside the switch's label, so it doesn't toggle it"] * bool(
                holder and words and not any(kind in e["cls"] for e in under(holder)))
            problems += [f"figure {n}: the switch's name \"{label}\" does not contain its {kind} word {words}"] * (len(words) != 1 or not words[0] or words[0].lower() not in label)
        problems += [f"figure {n}: the run's key is empty"] * (not "".join(e["text"] for e in under(bars[0]) if "lg-run" in e["cls"]).strip())
    check("runs", "-", problems)


def main():
    out = Path(tempfile.mkdtemp(prefix="check-site-"))
    try:
        done = subprocess.run(["hugo", "-s", str(ROOT), "--minify", "--panicOnWarning", "--baseURL", BASE + "/", "-d", str(out)],
                              capture_output=True, text=True)
        log = (done.stdout + done.stderr).strip()
        errors = [line.strip() for line in log.splitlines() if line.lstrip().startswith("ERROR") and len(line) < 300]
        check("build", "-", [f"hugo exited {done.returncode}: {' '.join(errors)} ... {log[-600:]}"] if done.returncode else [])
        if done.returncode == 0:
            config = {k.lower(): v for k, v in tomllib.loads((ROOT / "hugo.toml").read_text(encoding="utf-8")).items()}  # Hugo reads keys in any case
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
                check_data(out, pages["/"], config)
            check_links(out, pages)
            check_404(out)
            check_sitemap(out)
            check_dates(out)
            check_host(out, config)
            check_seams(out)
            check_runs(out)
    finally:
        shutil.rmtree(out, ignore_errors=True)
    for name, page, reason in results:
        print(f"{'FAIL' if reason else 'PASS'} {name} {page}" + (f": {reason}" if reason else ""))
    return int(any(reason for *_, reason in results))


if __name__ == "__main__":
    sys.exit(main())
