#!/usr/bin/env python3
"""Independent fidelity check: everything in the KSS docs HTML must appear in the
generated markdown. Reports every miss."""
import re
import os
import glob
import sys
import json
from bs4 import BeautifulSoup

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kss-docs-index.html')
OUT = '/Users/budtags/Desktop/budtags-claude-plugin/budtags/skills/kss'

soup = BeautifulSoup(open(SRC), 'html.parser')
md_corpus = ''
for path in glob.glob(OUT + '/patterns/*.md') + glob.glob(OUT + '/categories/*.md'):
    md_corpus += open(path).read() + '\n'

misses = []

# 1. Every endpoint method + path
for ep in soup.find_all('div', class_='endpoint'):
    method = ep.find(class_='method-badge').get_text(strip=True)
    path = re.sub(r'\s+', '', ep.find(class_='endpoint-path').get_text())
    if f'## {method} {path}' not in md_corpus:
        misses.append(f'ENDPOINT HEADING missing: {method} {path}')

# 2. Every param-name (backticked in md)
for pn in soup.find_all(class_='param-name'):
    name = pn.get_text(strip=True)
    if f'`{name}`' not in md_corpus:
        misses.append(f'PARAM missing: {name}')

# 3. Every param type
for pt in soup.find_all(class_='param-type'):
    t = pt.get_text(strip=True)
    if f'`{t}`' not in md_corpus:
        misses.append(f'TYPE missing: {t}')

# 4. Every enum chip value + label
for chip in soup.find_all(class_='enum-chip'):
    v = chip.find(class_='enum-chip-value').get_text(strip=True)
    l = chip.find(class_='enum-chip-label').get_text(strip=True)
    if f'`{v}` = {l}' not in md_corpus:
        misses.append(f'ENUM missing: {v} = {l}')

# 5. Every code block, exact text
for cb in soup.find_all('div', class_='code-block'):
    body = cb.find('code').get_text().rstrip('\n')
    if body not in md_corpus:
        misses.append(f'CODE BLOCK missing (first 80 chars): {body[:80]!r}')

# 6. Every JSON example must still be the exact same character stream:
#    compare each hljs-attr key against corpus (redundant with 5, kept as belt+braces)
attrs = set()
for a in soup.find_all('span', class_='hljs-attr'):
    attrs.add(a.get_text(strip=True).strip('"'))
for key in sorted(attrs):
    if f'"{key}"' not in md_corpus:
        misses.append(f'JSON FIELD missing: {key}')

# 7. Prose/token containment over the whole content area (minus UI chrome)
main = soup.find('section', class_='section').parent
for btn in main.find_all('button'):
    btn.decompose()
text = main.get_text(' ')
tokens = set(re.findall(r'[A-Za-z0-9][A-Za-z0-9_.\-]{2,}', text))
corpus_tokens = set(re.findall(r'[A-Za-z0-9][A-Za-z0-9_.\-]{2,}', md_corpus))
for tok in sorted(tokens - corpus_tokens):
    misses.append(f'TOKEN missing from markdown: {tok!r}')

# 8. Counts summary
def c(sel, **kw):
    return len(soup.find_all(sel, **kw))
print(f"endpoints html={c('div', class_='endpoint')} md={md_corpus.count('Doc anchor:')}")
print(f"code blocks html={c('div', class_='code-block')} md={md_corpus.count('```json') + md_corpus.count('```bash')}")
print(f"pagination notes html={c('p', class_='pagination-note')} md={md_corpus.count('**Pagination:**')}")
print(f"callouts html={len(soup.find_all('div', class_='callout'))} md={len(re.findall(r'^>', md_corpus, re.M))}")

if misses:
    print(f'\n=== {len(misses)} FIDELITY MISSES ===')
    for m in misses:
        print(' -', m)
    sys.exit(1)
print('\nFIDELITY OK: every endpoint, param, type, enum, code block, JSON field, and prose token from the docs is present in the markdown.')
