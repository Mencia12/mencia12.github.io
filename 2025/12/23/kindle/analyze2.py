"""分析所有HTML中的class使用情况"""
import os, re

d = r'E:\Else\Dong_optimize\epub_extracted\text'
files = sorted([f for f in os.listdir(d) if f.endswith('.html')])

h_classes = set()
p_classes = set()
div_classes = set()

for f in files:
    path = os.path.join(d, f)
    content = open(path, 'r', encoding='utf-8', errors='replace').read()
    h_classes.update(re.findall(r'<h[12][^>]*class="([^"]+)"', content))
    p_classes.update(re.findall(r'<p[^>]*class="([^"]+)"', content))
    div_classes.update(re.findall(r'<div[^>]*class="([^"]+)"', content))

print('H classes:', sorted(h_classes))
print('P classes:', sorted(p_classes))
print('Div classes:', sorted(div_classes))

# Also check for consecutive pages where one has only h2 and next has content
h2_only = []
for i, f in enumerate(files):
    path = os.path.join(d, f)
    content = open(path, 'r', encoding='utf-8', errors='replace').read()
    body = re.search(r'<body[^>]*>(.*?)</body>', content, re.S)
    if body:
        b = body.group(1).strip()
        # Check if page has h2 but body text is very short
        h2_m = re.search(r'<h2[^>]*>(.*?)</h2>', b, re.S)
        if h2_m:
            # Remove h2, then check remaining content
            remaining = re.sub(r'<h2[^>]*>.*?</h2>', '', b, flags=re.S).strip()
            # Remove empty tags
            remaining = re.sub(r'<[^>]+>\s*</[^>]+>', '', remaining).strip()
            remaining = re.sub(r'<br[^>]*/?\s*>', '', remaining).strip()
            remaining = re.sub(r'\s+', '', remaining)
            if len(remaining) < 20:
                h2_only.append((f, h2_m.group(1).strip()[:50], len(remaining)))

print(f'\nH2-only pages (content < 20 chars): {len(h2_only)}')
for f, title, length in h2_only[:20]:
    print(f'  {f}: "{title}" (remaining: {length} chars)')