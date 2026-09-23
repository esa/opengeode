#!/usr/bin/env python3
"""Scan help/wiki markdown pages for broken anchors, page links, and images."""
import os
import re
from urllib.parse import unquote

WIKI_DIR = "help/wiki"

ANCHOR_RE = re.compile(r'<a\s+name="([^"]+)"', re.IGNORECASE)
GENERIC_ID_RE = re.compile(r'\bid="([^"]+)"', re.IGNORECASE)
# [text](target) — skip leading ! (images handled separately)
LINK_RE = re.compile(
    r'(?<![\!\[])'
    r'\['
    r'(?:[^\[\]]|\[[^\[\]]*\])*?'
    r'\]'
    r'\(\s*([^)\s]+)(?:\s+"[^"]*")?\s*\)',
    re.DOTALL)
# linked image: [![alt](img)](link)
LINKED_IMAGE_RE = re.compile(
    r'\[\s*!\[[^\[\]]*\]\(\s*([^)\s]+)(?:\s+"[^"]*")?\s*\)\s*\]'
    r'\(\s*([^)\s]+)(?:\s+"[^"]*")?\s*\)',
    re.DOTALL)
# standalone image: ![alt](img)
IMAGE_RE = re.compile(
    r'\!\[[^\[\]]*\]\(\s*([^)\s]+)(?:\s+"[^"]*")?\s*\)')


def norm_anchor(name):
    return unquote(name).strip().lower().replace(' ', '_')


def pageref0(target):
    """Page-part of a link target (no anchor, no query)."""
    return target.split('#')[0].split('?')[0].rstrip('/')


def main():
    pages = {f[:-3]: f for f in os.listdir(WIKI_DIR) if f.endswith('.md')}
    contents, anchors_by_page = {}, {}
    for name, fname in pages.items():
        with open(os.path.join(WIKI_DIR, fname), encoding='utf-8',
                  errors='replace') as f:
            text = f.read()
        contents[name] = text
        anchors = set()
        for m in ANCHOR_RE.finditer(text):
            anchors.add(norm_anchor(m.group(1)))
        for m in GENERIC_ID_RE.finditer(text):
            anchors.add(norm_anchor(m.group(1)))
        anchors_by_page[name] = anchors

    img_dirs = [WIKI_DIR, os.path.join(WIKI_DIR, 'img'),
                os.path.join(WIKI_DIR, 'uploads')]

    def find_image(path):
        if path.startswith(('http://', 'https://', 'mailto:')):
            return True
        clean = path.split('?')[0].split('#')[0]
        # resolve relative to wiki root (pages reference img/... or uploads/...)
        if os.path.isfile(os.path.join(WIKI_DIR, clean)):
            return True
        base = os.path.basename(clean)
        return any(os.path.isfile(os.path.join(d, base)) for d in img_dirs)

    broken_anchors, broken_pages, broken_images = [], [], []

    for name, text in contents.items():
        # positions of linked-image constructs [![alt](img)](link) — the
        # link target of such a construct is an image/file, not a page
        linked_img_spans = [m.span() for m in LINKED_IMAGE_RE.finditer(text)]
        # positions of standalone images ![alt](img)
        standalone_img_spans = [m.span() for m in IMAGE_RE.finditer(text)]

        def in_spans(pos):
            return any(a <= pos < b for a, b in linked_img_spans + standalone_img_spans)

        for m in LINK_RE.finditer(text):
            if in_spans(m.start()):
                continue
            target = unquote(m.group(1).strip())
            lineno = text.count('\n', 0, m.start()) + 1
            if target.startswith(('http://', 'https://', 'mailto:', '//',
                                  'tel:')):
                continue
            # target looks like a file reference (image, pdf, zip...)?
            if re.search(r'\.(png|jpg|jpeg|gif|svg|pdf|zip|tgz|mp3|mp4|PNG|JPG)$'
                         r'|^(img|uploads)/', pageref0(target)):
                if not find_image(target):
                    broken_images.append((name, target, lineno))
                continue
            if target.startswith('#'):
                a = norm_anchor(target[1:])
                if a and a not in anchors_by_page[name]:
                    broken_anchors.append((name, target, lineno))
            else:
                pageref = pageref0(target)
                anchor = target.split('#')[1] if '#' in target else None
                if not pageref or pageref.startswith(('http', 'mailto:')):
                    continue
                cand = pageref[:-3] if pageref.endswith('.md') else pageref
                if cand not in pages:
                    broken_pages.append((name, target, lineno))
                elif anchor:
                    if norm_anchor(anchor) not in anchors_by_page[cand]:
                        broken_anchors.append((name, target, lineno))
        for m in IMAGE_RE.finditer(text):
            lineno = text.count('\n', 0, m.start()) + 1
            if not find_image(unquote(m.group(1).strip())):
                broken_images.append((name, m.group(1), lineno))

    print("=" * 70)
    print(f"BROKEN ANCHORS ({len(broken_anchors)}):")
    for page, tgt, ln in broken_anchors:
        print(f"  {page}:{ln}: {tgt}")
    print()
    print(f"BROKEN PAGE LINKS ({len(broken_pages)}):")
    for page, tgt, ln in broken_pages:
        print(f"  {page}:{ln}: {tgt}")
    print()
    print(f"BROKEN IMAGES ({len(broken_images)}):")
    for page, img, ln in broken_images:
        print(f"  {page}:{ln}: {img}")
    print()
    print(f"pages scanned: {len(pages)}")


if __name__ == '__main__':
    main()
