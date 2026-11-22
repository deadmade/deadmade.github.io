#!/usr/bin/env python3
"""Build the site as CI does and check the output: python3 scripts/check-site.py

Prints PASS/FAIL <check> <page>[: reason] per check and page; exits 1 on any FAIL.
The checks are listed in docs/features/job-application-portfolio/plan.md, Task 1, docs/features/seo/plan.md and
docs/features/diagram-animations/plan.md (Task 4).
"""
import html
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


class RunLayers(HTMLParser):
    """Each drawing (svg.dwg) of the built projects page, with its run layers (g.run) and their g.pu and g.hl classes."""

    def __init__(self):
        super().__init__()
        self.svgs, self.gs, self.in_dwg = [], [], False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        if tag == "svg" and "dwg" in cls:
            self.svgs.append({"cls": " ".join(cls), "runs": []})
            self.in_dwg, self.gs = True, []
        elif tag == "g" and self.in_dwg:
            self.gs.append(cls)
            if "run" in cls:
                self.svgs[-1]["runs"].append({"cls": " ".join(cls), "hidden": a.get("aria-hidden") == "true", "pu": [], "hl": []})
            for kind in ("pu", "hl"):
                if kind in cls and any("run" in g for g in self.gs[:-1]):
                    self.svgs[-1]["runs"][-1][kind] += [c for c in cls if c.startswith(kind + "-")]

    def handle_endtag(self, tag):
        if tag == "svg":
            self.in_dwg = False
        elif tag == "g" and self.in_dwg and self.gs:
            self.gs.pop()


def css_rules(css):
    """(prelude, body) of each rule in minified CSS, looking inside @media and @supports; @keyframes come whole."""
    i = 0
    while (j := css.find("{", i)) >= 0:
        prelude, depth, k = css[i:j].rsplit(";", 1)[-1].strip(), 1, j + 1
        while depth:
            depth += (css[k] == "{") - (css[k] == "}")
            k += 1
        if prelude.startswith(("@media", "@supports", "@layer", "@container")):
            yield from css_rules(css[j + 1:k - 1])
        else:
            yield prelude, css[j + 1:k - 1]
        i = k


def props(body):
    return re.findall(r"(?:^|[;{])\s*([\w-]+)\s*:", body)


ANIM_WORDS = {"none", "linear", "ease", "ease-in", "ease-out", "ease-in-out", "step-start", "step-end", "infinite", "normal", "reverse",
              "alternate", "alternate-reverse", "forwards", "backwards", "both", "running", "paused", "initial", "inherit", "unset"}


def animation_names(body):
    values = re.findall(r"(?:^|;)\s*animation(?:-name)?\s*:\s*([^;]*)", body)
    return [t for v in values for t in re.sub(r"[\w-]+\([^)]*\)", " ", v).replace(",", " ").split()
            if re.fullmatch(r"-?[A-Za-z_][\w-]*", t) and t.lower() not in ANIM_WORDS]


VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Elements(HTMLParser):
    """The built page's elements (tag, classes, id, parent, place among the parent's children); `drawn` lists every svg.dwg
    and every element inside one."""

    def __init__(self):
        super().__init__()
        self.open, self.drawn = [None], []

    def handle_starttag(self, tag, attrs):
        a, parent = dict(attrs), self.open[-1]
        el = {"tag": tag, "cls": set((a.get("class") or "").split()), "id": a.get("id"), "parent": parent, "kids": []}
        if parent:
            el["i"] = len(parent["kids"])
            parent["kids"].append(el)
        if (tag == "svg" and "dwg" in el["cls"]) or (parent and parent.get("drawn")):
            el["drawn"] = True
            self.drawn.append(el)
        if tag not in VOID:
            self.open.append(el)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.open.pop()

    def handle_endtag(self, tag):
        for i in range(len(self.open) - 1, 0, -1):
            if self.open[i]["tag"] == tag:
                del self.open[i:]
                break


def picks(el, comps, ops, i):
    """Whether compound i of a selector (and the compounds and combinators before it) can match the element."""
    tag, cls, ids = comps[i]
    if (tag and el["tag"] != tag) or not cls <= el["cls"] or (ids and ids != {el["id"]}):
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
    attribute test counts as matching anything, which only widens what is picked; a selector that ends in a pseudo-element
    picks no element (an SVG element has no ::before or ::after; ::view-transition-* hang off the root)."""
    while (s := re.sub(r"(?<!:):[\w-]+\((?:[^()]|\([^()]*\))*\)", "*", selector)) != selector:
        selector = s
    selector = re.sub(r"\[[^\]]*\]|(?<!:):(?!:)[\w-]+", "*", selector)
    for sel in re.split(r",(?![^()]*\))", selector):
        comps, ops, op = [], [], None
        for comb, space, comp in re.findall(r"\s*([>+~])\s*|(\s+)|([^\s>+~]+)", sel.strip()):
            if comp:
                tag = re.match(r"[A-Za-z][\w-]*", comp)
                comps.append((tag[0].lower() if tag else None, set(re.findall(r"\.(-?[A-Za-z_][\w-]*)", comp)), set(re.findall(r"#([\w-]+)", comp))))
                ops.append(op or " ")
                op = None
            else:
                op = comb or op or " "
        if comps and "::" not in sel and any(picks(el, comps, ops, len(comps) - 1) for el in els):
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


def shape_matches(shape, els):
    def nums(s):
        return [float(x) for x in re.findall(r"-?\d*\.?\d+", s)]
    def has(tag, cls, ok):
        return any(t == tag and cls in a.get("class", "").split() and ok(a, txt) for t, a, txt in els)
    def centroid(p):
        return sum(p[0::2]) / len(p[0::2]), sum(p[1::2]) / len(p[1::2])
    found = {"rect": lambda r: has("rect", "bx", lambda a, _: [float(a.get(k, "nan")) for k in ("x", "y", "width", "height")] == [float(v) for v in r]),
             "polygon": lambda p: has("polygon", "st", lambda a, _: nums(a.get("points", "")) == nums(p)) or has(
                 "polygon", "acc", lambda a, _: max(abs(u - v) for u, v in zip(centroid(nums(a.get("points", ""))), centroid(nums(p)))) <= 1),
             "path": lambda d: has("path", "ln", lambda a, _: a.get("d") == d),
             "text": lambda t: any(tag == "text" and [float(a.get("x", "nan")), float(a.get("y", "nan"))] == [float(t[0]), float(t[1])]
                                   and html.unescape(txt) == t[2] for tag, a, txt in els)}
    return [f"its {k} {shape[k]} matches no {k} of the drawing" if k in found else f"unknown shape {k}" for k in shape
            if k not in found or not found[k](shape[k])]


def check_runs(out):
    """The runs (data/runs.toml): routes on their drawing's arrows, outlines on its components, every layer hidden from screen
    readers and wired to its keyframes, and nothing inside a drawing animated beyond opacity and dash offset."""
    problems = []
    data = tomllib.loads((ROOT / "data" / "runs.toml").read_text(encoding="utf-8"))
    for name, d in data.get("drawing", {}).items():
        partial = ROOT / "layouts" / "_partials" / f"drawing-{name}.html"
        svgs = {m[1]: m[0] for m in re.finditer(r'<svg class="dwg ([hv])"[\s\S]*?</svg>', partial.read_text(encoding="utf-8"))} if partial.is_file() else {}
        for o in ("h", "v"):
            if o not in svgs:
                problems.append(f"{name}: no {o} drawing in {partial.relative_to(ROOT)}")
                continue
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
            for s in d.get("stop", []):
                problems += [f"{name} {o} stop {s.get('id')}: {p}" for p in shape_matches(s.get(o, {}), els)]
            for i, s in enumerate(d.get("span", [])):
                problems += [f"{name} {o} span {i} ({s.get('first')} to {s.get('last')}): {p}" for p in shape_matches(s.get(o, {}), els)]
            for r, run in enumerate(d.get("run", []), 1):
                for n, hop in enumerate(run.get("hops", []), 1):
                    pts = [tuple(map(float, p)) for p in hop.get(o, [])]
                    if len(pts) < 2 or not any(on_arrow(a, pts) for a in arrows):
                        problems.append(f"{name} {o} run {r} hop {n} ({hop.get('from')} to {hop.get('to')}) is not on one of the drawing's arrows")
    built = out / PAGES["/projects/"]
    html_text = built.read_text(encoding="utf-8") if built.is_file() else ""
    tree = Elements()
    tree.feed(html_text)
    css = "".join(f.read_text(encoding="utf-8") for f in sorted(out.rglob("*.css")))
    rules = list(css_rules(css))
    frames = {p.split()[1]: body for p, body in rules if p.startswith("@keyframes") and len(p.split()) > 1}
    animated = [(p, animation_names(body)) for p, body in rules if not p.startswith("@")]
    for p, body in rules:
        if not p.startswith("@") and reaches(p, tree.drawn):
            problems += [f"{p} sets {k}" for k in props(body) if k in ("transform", "translate", "rotate", "scale", "offset") or k.startswith("offset-")]
            for a in animation_names(body):
                bad = [k for k in props(frames.get(a, "")) if k not in ("opacity", "stroke-dashoffset", "animation-timing-function")]
                problems += [f"{p} runs @keyframes {a}, which sets {', '.join(sorted(set(bad)))}"] * bool(bad)
    page = RunLayers()
    page.feed(html_text)
    problems += ["no drawings on the built projects page"] * (not page.svgs)
    for i, svg in enumerate(page.svgs):
        if len(svg["runs"]) != 1:
            problems.append(f"drawing {i + 1} ({svg['cls']}) has {len(svg['runs'])} run layers, expected 1")
            continue
        layer = svg["runs"][0]
        run = (re.search(r"\brun-[\w-]+-[hv]\b", layer["cls"]) or [f"drawing {i + 1}"])[0]
        problems += [f"{run} is not aria-hidden"] * (not layer["hidden"])
        problems += [f"{run} has no {kind} groups" for kind in ("pu", "hl") if not layer[kind]]
        want = {c: [f"{run}-pu{c[3:]}", f"{run}-po{c[3:]}"] for c in layer["pu"]} | {c: [f"{run}-{c[3:]}"] for c in layer["hl"]}
        for c, names in want.items():
            wired = {a for p, names_ in animated if re.search(rf"\.{re.escape(run)}\s+\.{re.escape(c)}(?![\w-])", p) for a in names_}
            problems += [f"{run} .{c} is not wired to @keyframes {a}" for a in names if a not in frames or a not in wired]
        problems += [f"@keyframes {a} animates nothing in {run}" for a in frames if a.startswith(run + "-") and a not in {x for v in want.values() for x in v}]
    check("runs", "-", problems)


def main():
    out = Path(tempfile.mkdtemp(prefix="check-site-"))
    try:
        done = subprocess.run(["hugo", "-s", str(ROOT), "--minify", "--panicOnWarning", "--baseURL", BASE + "/", "-d", str(out)],
                              capture_output=True, text=True)
        check("build", "-", [f"hugo exited {done.returncode}: {(done.stdout + done.stderr).strip()[-600:]}"] if done.returncode else [])
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
