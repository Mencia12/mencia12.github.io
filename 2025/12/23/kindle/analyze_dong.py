"""分析 Dong.azw3 的 HTML 结构"""
import os, re

d = r'E:\Else\Dong_optimize\epub_extracted\text'
files = sorted([f for f in os.listdir(d) if f.endswith('.html')])

h1_with_img = []
h2_only_pages = []
h2a1_count = 0
calibre2_count = 0
h2a1_titles = []

for f in files:
    path = os.path.join(d, f)
    content = open(path, 'r', encoding='utf-8', errors='replace').read()
    
    # Check for h1 with img (book title + logo)
    h1_match = re.search(r'<h1[^>]*>.*?</h1>', content, re.S)
    img_match = re.search(r'<img[^>]+>', content)
    if h1_match and img_match:
        h1_with_img.append((f, h1_match.group()[:120], img_match.group()[:120]))
    
    # Check for h2a1 class
    if 'class="h2a1"' in content:
        h2a1_count += 1
        h2_m = re.search(r'<h2[^>]*class="h2a1"[^>]*>(.*?)</h2>', content, re.S)
        if h2_m:
            h2a1_titles.append((f, h2_m.group(1).strip()[:50]))
    
    # Check for pages with only h2 and minimal content
    body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.S)
    if body_match:
        body = body_match.group(1).strip()
        h2_match = re.search(r'<h2[^>]*class="h2a1"[^>]*>(.*?)</h2>', body, re.S)
        if h2_match:
            remaining = re.sub(r'<h2[^>]*class="h2a1"[^>]*>.*?</h2>', '', body, flags=re.S).strip()
            remaining = re.sub(r'<[^>]+>\s*</[^>]+>', '', remaining).strip()
            remaining = re.sub(r'<br[^>]*/?>', '', remaining).strip()
            remaining = re.sub(r'\s+', '', remaining)
            if len(remaining) < 50:
                h2_title = h2_match.group(1).strip()[:40]
                h2_only_pages.append((f, h2_title, len(remaining)))

    if 'class="calibre2"' in content:
        calibre2_count += 1

print(f'Total HTML files: {len(files)}')
print(f'\nH1+IMG pages (book titles with logo): {len(h1_with_img)}')
for f, h1, img in h1_with_img[:10]:
    print(f'  {f}:')
    print(f'    h1: {h1}')
    print(f'    img: {img}')

print(f'\nh2a1 class usage: {h2a1_count}')
print(f'calibre2 class usage: {calibre2_count}')

print(f'\nShort h2-only pages (candidates for removal): {len(h2_only_pages)}')
for f, title, remaining_len in h2_only_pages[:30]:
    print(f'  {f}: [{title}] remaining={remaining_len}')

# Also check what h2a1 titles look like
print(f'\nSample h2a1 titles:')
for f, title in h2a1_titles[:30]:
    print(f'  {f}: {title}')