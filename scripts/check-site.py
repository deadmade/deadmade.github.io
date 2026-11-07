#!/usr/bin/env python3
"""Build the site as CI does and check the output: python3 scripts/check-site.py

Prints PASS/FAIL <check> <page>[: reason] per check and page; exits 1 on any FAIL.
The checks are listed in docs/features/job-application-portfolio/plan.md, Task 1.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://deadmade.github.io"
PAGES = {"/": "index.html", "/work/": "work/index.html", "/path/": "path/index.html", "/now/": "now/index.html"}
BAR = ["work", "path", "now", "github", "linkedin", "mail"]
results = []


def check(name, page, problems):
    results.append((name, page, "; ".join(problems)))


class Page(HTMLParser):
    """Collects what the checks read from one page."""

    def __init__(self):
        super().__init__()
        self.lang, self.a = None, None
        self.titles, self.desc, self.links, self.srcs, self.imgs = [], [], [], [], []
        self.anchors, self.nav, self.go, self.current = [], [], [], []
        self.meta = Counter()
        self.in_head = self.in_title = self.in_nav = self.in_go = False

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
        elif tag == "a":
            self.a = {"href": a.get("href"), "label": (a.get("aria-label") or "").strip(), "text": ""}
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


def check_pages(pages):
    for path, p in pages.items():
        title = [t.strip() for t in p.titles]
        canonical = [x.get("href") for x in p.links if x.get("rel") == "canonical"]
        problems = [f"lang is {p.lang!r}"] if p.lang != "en" else []
        problems += [f"{len(title)} <title> in <head>, or empty"] if len(title) != 1 or not title[0] else []
        problems += [f"{len(p.desc)} meta descriptions, or empty"] if len(p.desc) != 1 or not p.desc[0] else []
        problems += [f"canonical is {canonical}"] if canonical != [BASE + path] else []
        check("head", path, problems + ["meta keywords present"] * bool(p.meta["keywords"]))
        want = ["og:title", "og:description", "og:url", "twitter:card"]
        check("social", path, [f"{k} appears {p.meta[k]} times" for k in want if p.meta[k] != 1]
              + [f"{k} present" for k in ("og:image", "twitter:image") if p.meta[k]])
        bar = [a["text"].strip() for a in p.nav]
        problems = [f"bar reads {bar}"] if bar != BAR else []
        problems += [f"aria-current=page on {p.current}"] if [urlparse(h or "").path for h in p.current] != [path] else []
        if path == "/" and [urlparse(a["href"] or "").path for a in p.go] != ["/work/", "/path/", "/now/"]:
            problems.append(f"home links are {[a['href'] for a in p.go]}")
        check("nav", path, problems)
        check("a11y", path, [f"img without alt: {i.get('src')}" for i in p.imgs if not (i.get("alt") or "").strip()]
              + [f"link without text: {a['href']}" for a in p.anchors if not (a["text"].strip() or a["label"])])
    for label, values in (("title", [t.strip() for p in pages.values() for t in p.titles]),
                          ("description", [d for p in pages.values() for d in p.desc])):
        check("head", "-", [f"{label} repeats: {v!r}" for v, n in Counter(values).items() if n > 1])


def check_links(out, pages):
    sheets = set()
    for path, p in pages.items():
        raw = (out / PAGES[path]).read_text(encoding="utf-8")
        refs = [("src", s) for s in p.srcs] + [("link", x.get("href")) for x in p.links] + [("a", a["href"]) for a in p.anchors]
        problems = [m for kind, ref in refs if (m := ref_problem(out, kind, ref))]
        check("links", path, problems + ["<script> present"] * ("<script" in raw.lower()) + ["names a font file"] * (".woff2" in raw))
        sheets |= {urlparse(x["href"]).path for x in p.links if x.get("rel") == "stylesheet" and (x.get("href") or "").startswith("/")}
    for sheet in sorted(sheets):
        css = (out / sheet.lstrip("/")).read_text(encoding="utf-8")
        refs = re.findall(r"url\(\s*['\"]?([^'\")\s]+)['\"]?\s*\)", css) + re.findall(r"@import\s+['\"]([^'\"]+)", css)
        check("links", sheet, [m for ref in refs if (m := ref_problem(out, "css", ref))])


def check_sitemap(out):
    sitemap, robots = out / "sitemap.xml", out / "robots.txt"
    locs = set(re.findall(r"<loc>([^<]+)</loc>", sitemap.read_text(encoding="utf-8"))) if sitemap.is_file() else set()
    want = {BASE + p for p in PAGES}
    lines = robots.read_text(encoding="utf-8").splitlines() if robots.is_file() else []
    check("sitemap", "-", ([f"sitemap lists {sorted(locs)}, expected {sorted(want)}"] if locs != want else [])
          + ([f"robots.txt lacks 'Sitemap: {BASE}/sitemap.xml'"] if f"Sitemap: {BASE}/sitemap.xml" not in lines else []))


def check_seams(out):
    declared = sum(f.read_text(encoding="utf-8").count("--accent:") for f in out.rglob("*.css"))
    problems = [f"--accent: is declared {declared} times in the built CSS, expected 1"] if declared != 1 else []
    for source in [ROOT / "hugo.toml", *sorted(f for d in ("layouts", "content") for f in (ROOT / d).rglob("*") if f.is_file())]:
        text = source.read_text(encoding="utf-8", errors="ignore")
        problems += [f"accent colour in {source.relative_to(ROOT)}"] * bool(re.search(r"F08BB4|FF544A", text, re.I))
        problems += [f"site host in {source.relative_to(ROOT)}"] * (source.name != "hugo.toml" and "deadmade.github.io" in text)
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
            check_pages(pages)
            check_links(out, pages)
            check_sitemap(out)
            check_seams(out)
    finally:
        shutil.rmtree(out, ignore_errors=True)
    for name, page, reason in results:
        print(f"{'FAIL' if reason else 'PASS'} {name} {page}" + (f": {reason}" if reason else ""))
    return int(any(reason for *_, reason in results))


if __name__ == "__main__":
    sys.exit(main())
