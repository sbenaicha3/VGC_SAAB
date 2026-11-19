"""Build the offline guide from repository Markdown and embed the current source.

No third-party Markdown renderer is required. Supports the subset used in these
guides: headings, paragraphs, fenced code, lists, tables and inline links/code.
"""
from html import escape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def slug(text):
    return re.sub(r'[^a-z0-9 -]', '', text.lower()).replace(' ', '-')


def inline(text):
    text = escape(text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)

    def link(match):
        label, url = match.groups()
        if url == 'CODE_GUIDE.md':
            url = '#navigation-and-reading-path'
        elif url == 'PARAMETERS.md':
            url = '#param-world-parameters'
        source = re.match(r'\.\./vgc_sd/(\w+)\.py#L(\d+)', url)
        if source:
            url = f'#source-{source[1]}-{source[2]}'
        return f'<a href="{url}">{label}</a>'
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, text)


def markdown_sections(path, prefix=''):
    lines = path.read_text(encoding='utf-8').splitlines()
    output, navigation = [], []
    i, section = 0, False
    while i < len(lines):
        line = lines[i]
        if line.startswith('## '):
            if section:
                output.append('</section>')
            title = line[3:]
            anchor = prefix + slug(title)
            output.append(f'<section class="guide-section" id="{anchor}"><h2>{inline(title)}</h2>')
            navigation.append((title, anchor))
            section = True
            i += 1
        elif line.startswith('# '):
            i += 1
        elif line.startswith('```'):
            language = line[3:]
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                block.append(lines[i])
                i += 1
            if language == 'mermaid':
                output.append('<p class="note">The class diagram below is Mermaid source, rendered as a diagram on GitHub. The ownership tree and diagram above cover the same relationships offline.</p>')
            output.append('<pre><code>' + escape('\n'.join(block)) + '</code></pre>')
            i += 1
        elif line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                cells = [v.strip() for v in lines[i].strip('|').split('|')]
                if not all(re.match(r'^:?-+:?$', v) for v in cells):
                    rows.append(cells)
                i += 1
            output.append('<div class="table-scroll"><table>')
            for index, row in enumerate(rows):
                tag = 'th' if index == 0 else 'td'
                output.append('<tr>' + ''.join(f'<{tag}>{inline(v)}</{tag}>' for v in row) + '</tr>')
            output.append('</table></div>')
        elif re.match(r'^\d+\. ', line):
            output.append('<ol>')
            while i < len(lines) and re.match(r'^\d+\. ', lines[i]):
                output.append('<li>' + inline(re.sub(r'^\d+\. ', '', lines[i])) + '</li>')
                i += 1
            output.append('</ol>')
        elif not line.strip():
            i += 1
        else:
            output.append('<p>' + inline(line) + '</p>')
            i += 1
    if section:
        output.append('</section>')
    return '\n'.join(output), navigation


def main():
    content, nav = markdown_sections(ROOT/'docs/CODE_GUIDE.md')
    parameters, param_nav = markdown_sections(ROOT/'docs/PARAMETERS.md', 'param-')
    sources = []
    source_nav = []
    for name in ('model', 'experiment', 'server', '__main__'):
        anchor = 'source-' + name
        source_nav.append((name + '.py', anchor))
        lines = (ROOT/f'vgc_sd/{name}.py').read_text(encoding='utf-8').splitlines()
        numbered = '\n'.join(f'<span id="source-{name}-{i}"><a class="ln" href="#source-{name}-{i}">{i:3}</a> {escape(line)}</span>' for i, line in enumerate(lines, 1))
        sources.append(f'<section class="guide-section source" id="{anchor}"><h2>{name}.py — source browser</h2><pre><code>{numbered}</code></pre></section>')
    navigation = '<h3>Code and model</h3>' + ''.join(f'<a href="#{a}">{escape(t)}</a>' for t,a in nav)
    navigation += '<h3>Parameters</h3>' + ''.join(f'<a href="#{a}">{escape(t)}</a>' for t,a in param_nav)
    navigation += '<h3>Source browser</h3>' + ''.join(f'<a href="#{a}">{escape(t)}</a>' for t,a in source_nav)
    diagram = '''<section class="guide-section" id="object-map"><h2>Object interaction map</h2>
<svg viewBox="0 0 960 360" role="img" aria-label="Browser sends a request through Handler and experiment to World; World references Parameters, consumes Actions and owns mutable State">
<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" fill="currentColor"/></marker></defs>
<g class="boxes"><rect x="10" y="20" width="210" height="65"/><rect x="370" y="20" width="210" height="65"/><rect x="730" y="20" width="210" height="65"/><rect x="10" y="190" width="210" height="65"/><rect x="370" y="190" width="210" height="65"/><rect x="730" y="190" width="210" height="65"/></g>
<g class="labels"><text x="115" y="49">Browser / app.html</text><text x="115" y="70">inputs and results</text><text x="475" y="49">Handler / server.py</text><text x="475" y="70">HTTP to Python</text><text x="835" y="49">experiment()</text><text x="835" y="70">sampling and policy memory</text><text x="115" y="220">Parameters</text><text x="115" y="240">frozen configuration</text><text x="475" y="220">Action</text><text x="475" y="240">hire / protect / exit</text><text x="835" y="220">World</text><text x="835" y="240">owns mutable State</text></g>
<g class="edges"><path d="M220 45H370"/><path d="M580 45H730"/><path d="M835 85V190"/><path d="M580 222H730"/><path d="M115 255V308H805V255"/><path d="M940 215H952V108H870V85" stroke-dasharray="4 4"/></g>
<text x="260" y="36">request JSON</text><text x="615" y="36">call</text><text x="700" y="142">create / step</text><text x="625" y="210">consume</text><text x="250" y="301">World references configuration</text><text x="610" y="105">observe() snapshot to policy loop</text>
<text x="12" y="345">Returned rows travel back through the server to the browser. Each policy and audit branch has its own state.</text>
</svg></section>'''
    page = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>VGC · Code and model guide</title>
<style>
:root{color-scheme:light;--bg:#f7f9fb;--text:#182b3c;--muted:#526677;--line:#ccd7e0;--panel:#fff;--code:#edf2f6;--accent:#08665d}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.65 system-ui,sans-serif}aside{position:fixed;inset:0 auto 0 0;width:290px;overflow:auto;background:var(--panel);border-right:1px solid var(--line);padding:24px}aside a{display:block;padding:4px 0;font-size:13px}aside h3{font-size:14px;margin:20px 0 6px}main{margin-left:290px;max-width:1500px;padding:35px 48px}h1{font-size:34px;line-height:1.2}h2{font-size:25px;line-height:1.3;margin:0 0 20px}h3{font-size:18px}p{max-width:1000px}a{color:var(--accent)}input{width:100%;padding:10px;font:inherit;border:1px solid var(--line);border-radius:5px}.guide-section{padding:32px 0;border-bottom:1px solid var(--line);scroll-margin-top:20px}.note{color:var(--muted);font-size:14px}code{font:13px/1.65 ui-monospace,Consolas,monospace;background:var(--code);padding:2px 4px}pre{overflow:auto;background:var(--code);padding:20px;border-radius:6px}pre code{padding:0;background:none;white-space:pre}table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;vertical-align:top;border-bottom:1px solid var(--line);padding:12px}th{background:var(--code)}.table-scroll{overflow:auto}.source pre{max-height:650px}.source span:target{background:#ffeaa4}.ln{color:var(--muted);text-decoration:none}svg{width:100%;height:auto;max-height:400px;font:12px system-ui}.boxes rect{fill:var(--panel);stroke:var(--line);rx:7}.labels{text-anchor:middle;fill:var(--text)}.edges path{fill:none;stroke:var(--accent);marker-end:url(#arrow)}svg text{fill:var(--text)}button{font:inherit;background:var(--panel);border:1px solid var(--line);border-radius:5px;padding:8px 12px;cursor:pointer}[hidden]{display:none!important}@media(max-width:900px){aside{position:static;width:auto;max-height:300px;border-bottom:1px solid var(--line)}main{margin:0;padding:25px 18px}}@media print{aside,button{display:none}main{margin:0;padding:0}.source{display:none}pre{white-space:pre-wrap}pre code{white-space:pre-wrap}.guide-section{break-inside:auto}}
</style></head><body><aside><strong>VGC documentation</strong><p class="note">Read the model, trace the code.</p><label for="search">Find a concept</label><input id="search" type="search" placeholder="e.g. hiring, certification, exit"><p id="matches" class="note"></p><nav>__NAV__</nav></aside><main><header><p class="note">IMPLEMENTATION GUIDE · 19 NOVEMBER 2026</p><h1>How the VGC model works</h1><p>Stock equations, assumptions, code flow and object ownership, traced from the current source. Start with the one-minute model, then explore individual stocks or the embedded source.</p><p><a href="CODE_GUIDE.md">GitHub Markdown guide</a> · <a href="PARAMETERS.md">Parameter reference</a> · <a href="../README.md">Setup and use</a></p><button onclick="window.print()">Print / save PDF</button></header>__DIAGRAM____CONTENT____PARAMETERS____SOURCES__</main>
<script>
const search=document.getElementById('search'),sections=[...document.querySelectorAll('.guide-section')];
function filter(){const term=search.value.trim().toLowerCase();let count=0;sections.forEach(section=>{const show=!term||section.textContent.toLowerCase().includes(term);section.hidden=!show;if(show)count++;});document.getElementById('matches').textContent=term?count+' matching sections':'';}
search.addEventListener('input',filter);
function revealHash(){search.value='';filter();const node=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(node)node.scrollIntoView({block:'start'});}
window.addEventListener('hashchange',revealHash);if(location.hash)revealHash();
</script></body></html>'''
    page = page.replace('__NAV__', '<a href="#object-map">Object interaction map</a>'+navigation).replace('__DIAGRAM__', diagram).replace('__CONTENT__', content).replace('__PARAMETERS__', parameters).replace('__SOURCES__', '\n'.join(sources))
    dest=ROOT/'docs/index.html'
    dest.write_text(page,encoding='utf-8')
    print(f'Built {dest}')


if __name__ == '__main__':
    main()
