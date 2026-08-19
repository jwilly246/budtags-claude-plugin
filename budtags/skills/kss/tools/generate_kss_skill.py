#!/usr/bin/env python3
"""Deterministic 1:1 converter: KSS API docs HTML -> markdown skill reference files.

Walks every element in document order and dispatches by CSS class.
Any unrecognized element is collected and causes a nonzero exit, so nothing
can be silently dropped.
"""
import re
import sys
import os
from bs4 import BeautifulSoup, NavigableString, Tag

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kss-docs-index.html')
OUT = '/Users/budtags/Desktop/budtags-claude-plugin/budtags/skills/kss'
DOC_URL = 'https://kssdata.com/docs/v1'
RETRIEVED = '2026-08-19'

errors = []


def err(msg):
    errors.append(msg)


def norm_ws(text):
    return re.sub(r'\s+', ' ', text).strip()


def inline_md(el):
    """Convert inline content of a tag to markdown, preserving exact text."""
    parts = []
    for node in el.children:
        if isinstance(node, NavigableString):
            parts.append(str(node))
        elif node.name == 'code':
            parts.append('`' + node.get_text() + '`')
        elif node.name == 'strong':
            parts.append('**' + inline_md(node).strip() + '**')
        elif node.name == 'a':
            # in-page anchor links: keep the text only
            parts.append(inline_md(node))
        elif node.name == 'br':
            parts.append(' ')
        elif node.name == 'span':
            parts.append(inline_md(node))
        else:
            err(f'inline_md: unhandled tag <{node.name}> in {el.get("class")}: {norm_ws(node.get_text())[:80]}')
            parts.append(node.get_text())
    return norm_ws(''.join(parts))


def cell_md(text):
    """Escape a string for use inside a markdown table cell."""
    return text.replace('|', '\\|')


def render_code_block(div):
    header = div.find(class_='code-block-header')
    lang_label = ''
    if header:
        lang_span = header.find(class_='code-block-lang')
        if lang_span:
            # the copy button is nested inside the lang span in the source markup
            lang_label = norm_ws(''.join(
                str(c) for c in lang_span.children if isinstance(c, NavigableString)))
    code = div.find('code')
    fence_lang = 'text'
    for cls in code.get('class', []):
        if cls.startswith('language-'):
            fence_lang = cls[len('language-'):]
    body = code.get_text()
    out = []
    if lang_label:
        out.append(f'**{lang_label}**')
        out.append('')
    out.append(f'```{fence_lang}')
    out.append(body.rstrip('\n'))
    out.append('```')
    return '\n'.join(out)


def render_info_grid(div):
    cards = div.find_all(class_='info-card')
    has_value = any(c.find(class_='info-card-value') for c in cards)
    out = []
    if has_value:
        out.append('| Name | Value | Notes |')
        out.append('|---|---|---|')
        for c in cards:
            label = inline_md(c.find(class_='info-card-label'))
            value = c.find(class_='info-card-value')
            value = '`' + inline_md(value) + '`' if value else ''
            sub = c.find(class_='info-card-sub')
            sub = inline_md(sub) if sub else ''
            out.append(f'| **{cell_md(label)}** | {cell_md(value)} | {cell_md(sub)} |')
    else:
        out.append('| Name | Description |')
        out.append('|---|---|')
        for c in cards:
            label = inline_md(c.find(class_='info-card-label'))
            sub = c.find(class_='info-card-sub')
            sub = inline_md(sub) if sub else ''
            out.append(f'| **`{cell_md(label)}`** | {cell_md(sub)} |')
    return '\n'.join(out)


def render_callout(div):
    classes = div.get('class', [])
    icon = div.find(class_='callout-icon')
    header = div.find(class_='callout-header')
    body = div.find(class_='callout-body')
    prefix = ''
    if icon:
        prefix = norm_ws(icon.get_text().replace('⚠', '⚠️')) + ' '
    label = norm_ws(header.get_text()) if header else ''
    body_md = inline_md(body)
    if label:
        return f'> {prefix}**{label}** {body_md}'
    return f'> {prefix}{body_md}'


def render_enum_values(div):
    chips = []
    for chip in div.find_all(class_='enum-chip'):
        value = norm_ws(chip.find(class_='enum-chip-value').get_text())
        label = norm_ws(chip.find(class_='enum-chip-label').get_text())
        chips.append(f'`{value}` = {label}')
    return 'Values: ' + ', '.join(chips)


def render_params_table(table):
    ths = [norm_ws(th.get_text()) for th in table.find_all('th')]
    out = []
    if ths == ['Name', 'Type', 'Required', 'Description']:
        out.append('| Name | In | Type | Required | Description |')
        out.append('|---|---|---|---|---|')
        for tr in table.find('tbody').find_all('tr'):
            tds = tr.find_all('td')
            name = norm_ws(tds[0].find(class_='param-name').get_text())
            p_in = tds[0].find(class_='param-in')
            p_in = norm_ws(p_in.get_text()) if p_in else ''
            p_type = norm_ws(tds[1].get_text())
            p_req = norm_ws(tds[2].get_text())
            desc_div = tds[3].find(class_='param-desc')
            desc = inline_md(desc_div) if desc_div else ''
            enum_div = tds[3].find(class_='enum-values')
            if enum_div:
                desc = (desc + '<br>' if desc else '') + render_enum_values(enum_div)
            out.append(f'| `{cell_md(name)}` | {cell_md(p_in)} | `{cell_md(p_type)}` | '
                       f'{cell_md(p_req)} | {cell_md(desc)} |')
    else:
        # generic table (e.g. get-inventory's response Field | Description table)
        out.append('| ' + ' | '.join(cell_md(h) for h in ths) + ' |')
        out.append('|' + '---|' * len(ths))
        for tr in table.find('tbody').find_all('tr'):
            cells = []
            for td in tr.find_all('td'):
                name_div = td.find(class_='param-name')
                desc_div = td.find(class_='param-desc')
                if name_div and not desc_div:
                    cells.append('`' + cell_md(norm_ws(name_div.get_text())) + '`')
                elif desc_div and not name_div:
                    cells.append(cell_md(inline_md(desc_div)))
                else:
                    cells.append(cell_md(inline_md(td)))
            out.append('| ' + ' | '.join(cells) + ' |')
    return '\n'.join(out)


def render_endpoint(ep):
    out = []
    anchor = ep.get('id')
    header = ep.find(class_='endpoint-header')
    method = norm_ws(header.find(class_='method-badge').get_text())
    path = norm_ws(header.find(class_='endpoint-path').get_text())
    out.append(f'## {method} {path}')
    out.append('')
    out.append(f'Doc anchor: [`#{anchor}`]({DOC_URL}#{anchor})')
    badges = [norm_ws(b.get_text()) for b in header.find_all(class_='badge')]
    if badges:
        out.append('')
        out.append('**Badges:** ' + ' · '.join(badges))
    # walk remaining children in document order
    for child in ep.children:
        if isinstance(child, NavigableString):
            if child.strip():
                err(f'endpoint {anchor}: stray text: {norm_ws(str(child))[:80]}')
            continue
        classes = child.get('class', [])
        if 'endpoint-header' in classes:
            continue
        elif 'endpoint-description' in classes:
            out.append('')
            out.append(inline_md(child))
        elif 'callout' in classes:
            out.append('')
            out.append(render_callout(child))
        elif 'params-label' in classes:
            out.append('')
            out.append(f'### {norm_ws(child.get_text())}')
        elif child.name == 'table' and 'params-table' in classes:
            out.append('')
            out.append(render_params_table(child))
        elif 'pagination-note' in classes:
            out.append('')
            out.append('**Pagination:** ' + inline_md(child))
        elif 'code-block' in classes:
            out.append('')
            out.append(render_code_block(child))
        elif child.name == 'p' and not classes:
            out.append('')
            out.append(inline_md(child))
        else:
            err(f'endpoint {anchor}: unhandled child <{child.name} class={classes}>: '
                f'{norm_ws(child.get_text())[:80]}')
    return '\n'.join(out)


def render_section_children(section):
    """Render intro-section children (prose, grids, callouts, code, subsections)."""
    out = []
    for child in section.children:
        if isinstance(child, NavigableString):
            if child.strip():
                err(f'section {section.get("id")}: stray text: {norm_ws(str(child))[:80]}')
            continue
        classes = child.get('class', [])
        if 'section-title' in classes:
            continue  # handled by the file title
        elif 'prose' in classes:
            for p in child.find_all('p'):
                out.append('')
                out.append(inline_md(p))
        elif 'info-grid' in classes:
            out.append('')
            out.append(render_info_grid(child))
        elif 'callout' in classes:
            out.append('')
            out.append(render_callout(child))
        elif 'code-block' in classes:
            out.append('')
            out.append(render_code_block(child))
        elif 'subsection-title' in classes:
            out.append('')
            out.append(f'### {norm_ws(child.get_text())}')
        else:
            err(f'section {section.get("id")}: unhandled child <{child.name} class={classes}>: '
                f'{norm_ws(child.get_text())[:80]}')
    return '\n'.join(out)


def file_header(title, anchor):
    return (f'# {title}\n\n'
            f'> Verbatim transcription of [{DOC_URL}#{anchor}]({DOC_URL}#{anchor}) '
            f'(retrieved {RETRIEVED}). Field names, parameters, enum values, and example '
            f'responses are copied exactly from the KSS docs. Do not edit by hand — '
            f'regenerate from source.\n')


def slugify(label):
    return re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-')


def main():
    soup = BeautifulSoup(open(SRC), 'html.parser')
    sections = soup.find_all('section', class_='section')
    intro_files = {
        'overview': ('getting-started', 'Getting Started'),
        'authentication': ('authentication', 'Authentication'),
        'rate-limiting': ('rate-limiting', 'Rate Limiting'),
        'pagination': ('pagination', 'Pagination'),
        'errors': ('errors', 'Errors'),
        'response-headers': ('response-headers', 'Response Headers'),
    }
    os.makedirs(os.path.join(OUT, 'patterns'), exist_ok=True)
    os.makedirs(os.path.join(OUT, 'categories'), exist_ok=True)

    endpoints_section = None
    for section in sections:
        sid = section.get('id')
        if sid == 'endpoints':
            endpoints_section = section
            continue
        if sid not in intro_files:
            err(f'unknown section id: {sid}')
            continue
        fname, title = intro_files[sid]
        body = render_section_children(section)
        path = os.path.join(OUT, 'patterns', fname + '.md')
        with open(path, 'w') as f:
            f.write(file_header(title, sid) + body + '\n')
        print(f'wrote {path}')

    # endpoints section: group-labels partition the endpoint divs
    groups = []  # (label, [endpoint_div])
    for child in endpoints_section.children:
        if isinstance(child, NavigableString):
            if child.strip():
                err(f'endpoints section: stray text: {norm_ws(str(child))[:80]}')
            continue
        classes = child.get('class', [])
        if 'section-title' in classes:
            continue
        elif 'group-label' in classes:
            groups.append((norm_ws(child.get_text()), []))
        elif 'endpoint' in classes:
            if not groups:
                err(f'endpoint {child.get("id")} appears before any group label')
                groups.append(('Ungrouped', []))
            groups[-1][1].append(child)
        else:
            err(f'endpoints section: unhandled child <{child.name} class={classes}>: '
                f'{norm_ws(child.get_text())[:80]}')

    for label, eps in groups:
        fname = slugify(label) + '.md'
        parts = [file_header(label, 'group-' + slugify(label).replace('-', ''))]
        # correct anchor: group ids are like group-customers / group-arAging etc.
        # recompute from the div itself instead:
        parts = []
        group_div = endpoints_section.find('div', class_='group-label', string=re.compile(re.escape(label)))
        anchor = group_div.get('id') if group_div else 'endpoints'
        parts.append(file_header(label, anchor))
        for ep in eps:
            parts.append('')
            parts.append(render_endpoint(ep))
            parts.append('')
            parts.append('---')
        path = os.path.join(OUT, 'categories', fname)
        with open(path, 'w') as f:
            f.write('\n'.join(parts).rstrip('-\n ') + '\n')
        print(f'wrote {path}  ({len(eps)} endpoints)')

    if errors:
        print('\n=== UNHANDLED / ERRORS ===')
        for e in errors:
            print(' -', e)
        sys.exit(1)
    print('\nOK: all elements handled.')


if __name__ == '__main__':
    main()
