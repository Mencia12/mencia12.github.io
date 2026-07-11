"""
Dong.azw3 排版优化脚本
基于 kindle.md 中的排版规则，对 E:/Else/Dong.azw3 进行正则替换优化

工作流程：
1. 使用 calibre 的 ebook-convert 将 AZW3 转为 EPUB
2. 解压 EPUB，对 HTML 文件执行正则替换
3. 合并 CSS 样式
4. 重新打包 EPUB
5. 转换回 AZW3
"""

import os
import re
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path

# ============ 配置 ============
CALIBRE_PATH = r"D:\Soft\Calibre2"
SOURCE_AZW3 = r"E:\Else\Dong.azw3"
WORK_DIR = r"E:\Else\Dong_optimize"
TEMP_EPUB = os.path.join(WORK_DIR, "Dong_temp.epub")
EXTRACT_DIR = os.path.join(WORK_DIR, "epub_extracted")
OUTPUT_AZW3 = r"E:\Else\Dong_optimized.azw3"

# ============ CSS 样式 ============
CSS_STYLES = """
/* ===== 字体 ===== */
@page {
  margin-bottom: 5pt;
  margin-top: 5pt;
}
@font-face {
  font-family: "fzlt";
  src: url("../fzltHT.ttf");
}
@font-face {
  font-family: "syst";
  src: url("../systB.ttf");
}
@font-face {
  font-family: "hysf";
  src: url("../hysfFS.ttf");
}
@font-face {
  font-family: "fzys";
  src: url("../fzyanST.TTF");
}
@font-face {
  font-family: "stdgt";
  src: url("../stdgt.ttf");
}
@font-face {
  font-family: "zqfs";
  src: url("../zqfs.ttf");
}

/* ===== 文本 ===== */
.hd {
  display: block;
  line-height: 1.4;
}
.txt {
  display: block;
  line-height: 1.4;
  text-align: justify;
  text-indent: 2em;
}
.txtend {
  display: block;
  font-family: "stdgt";
  line-height: 1.4;
  text-align: center;
  margin: 10% auto;
}
.txtr {
  display: block;
  font-family: STKai, serif;
  line-height: 1.4;
  text-align: right;
}
.txth {
  display: block;
  line-height: 1.4;
  font-family: "hysf";
  text-align: justify;
  text-indent: 2em;
}
.txthc {
  display: block;
  font-family: "hysf";
  line-height: 1.4;
  text-align: center;
}
.txtbc {
  display: block;
  font-family: "stdgt";
  line-height: 1.4;
  text-align: center;
}
.txtsub {
  display: block;
  line-height: 1.4;
  font-size: smaller;
  text-align: right;
  vertical-align: sub;
}

/* ===== 章标题 ===== */
.chapter-sequence-number {
  font-family: "fzlt";
  font-size: 1rem;
  padding: 2px 4px;
}
.chapter-title {
  display: block;
  font-family: "syst";
  font-size: 1.2em;
  line-height: 1.4;
  text-align: center;
  margin: 10% auto;
}
.chapter-subtitle {
  font-size: 0.7em;
}
.hd1 {
  display: block;
  margin: 0.1em auto;
}

/* ===== 卷标题 横排 ===== */
.volume-title {
  display: block;
  font-family: "fzys";
  font-size: 1.2em;
  line-height: 1.4;
  text-align: center;
  margin: 30% auto;
}
.volume-subtitle {
  display: block;
  font-family: "syst";
  font-size: 1.2em;
  text-align: center;
}

/* ===== 卷标题下方文字 ===== */
.vtxt {
  display: block;
  font-family: "楷体", "STKai", serif;
  line-height: 1.4;
  text-align: justify;
  text-indent: 2em;
  margin-top: -20%;
  padding-top: 0;
  max-width: 60%;
  margin-left: auto;
  margin-right: auto;
}

/* ===== 封面图 ===== */
.pic {
  height: auto;
  line-height: 1.4;
  width: auto;
}
.cover {
  display: block;
  line-height: 1.4;
  margin-bottom: 1em;
  margin-top: 1em;
  text-align: center;
  width: 100%;
}

/* ===== 插图 ===== */
.imgg {
  text-align: center;
  margin: 1em 0;
}
.imgg1 {
  max-width: 100%;
  width: auto;
  height: auto;
}

/* ===== 注释 ===== */
.zhusi {
  display: block;
  font-family: "楷体", "STKai", serif;
  font-size: 1em;
  line-height: 1.5;
  text-indent: 2em;
}
.fenge {
  color: gray;
  display: block;
  height: 2px;
  line-height: 1.4;
  margin: 0.5em auto;
  border: currentColor inset 1px;
}
.math-super {
  font-family: "楷体", "STKai", serif;
  font-size: 0.75em;
  vertical-align: super;
}
.zs {
  line-height: 1.4;
  text-decoration: none;
}

/* ===== 分割线 ===== */
.fg {
  text-align: center;
  margin: 2em 0 2em;
}
"""


def apply_regex_replacements(text):
    """对 HTML 文本应用所有正则替换规则"""
    
    # =============================================
    # 1. body 标签替换
    # =============================================
    text = re.sub(
        r'<body class="calibre1">',
        '<body class="hd">',
        text
    )

    # =============================================
    # 2. 正文段落替换
    # =============================================
    text = re.sub(
        r'<p class="a">　　',
        '<p class="txt">',
        text
    )
    text = re.sub(
        r'<p class="calibre\d*">　　',
        '<p class="txt">',
        text
    )

    # =============================================
    # 3. 章标题替换 → chapter-title 格式
    # =============================================
    # 3.1 三段结构：章节号 + 标题 +（副标题）
    text = re.sub(
        r'<h2[^>]*class="titletoc"[^>]*>(.*?) (.*?)（(.*?)）</h2>',
        (
            '<h2 class="chapter-title">\n'
            '<span class="chapter-sequence-number">\1</span>\n'
            '<br class="hd1"/> \2\n'
            '<span class="chapter-subtitle">（\3）</span></h2>'
        ),
        text
    )

    # 3.2 两段结构：章节号 + 标题
    text = re.sub(
        r'<h2[^>]*class="titletoc"[^>]*>(.*?) (.*?)</h2>',
        (
            '<h2 class="chapter-title">\n'
            '<span class="chapter-sequence-number">\1</span>\n'
            '<br class="hd1"/> \2</h2>'
        ),
        text
    )

    # 3.3 单独标题
    text = re.sub(
        r'<h2[^>]*class="titletoc"[^>]*>(.*?)</h2>',
        r'<h2 class="chapter-title">\1</h2>',
        text
    )

    # 3.4 通用 h2 标题替换（非 titletoc 类）
    text = re.sub(
        r'<h2[^>]*class="calibre\d*"[^>]*>(\d+)\s+(.*?)</h2>',
        (
            '<h2 class="chapter-title">\n'
            '<span class="chapter-sequence-number">\1</span>\n'
            '<br class="hd1"/> \2</h2>'
        ),
        text
    )

    # 3.5 中文数字章节标题
    text = re.sub(
        r'<h[23][^>]*>(第[一二三四五六七八九十百千\d]+[章节回部卷集])\s+(.*?)</h[23]>',
        (
            '<h2 class="chapter-title">\n'
            '<span class="chapter-sequence-number">\1</span>\n'
            '<br class="hd1"/> \2</h2>'
        ),
        text
    )

    # 3.6 中文数字章节标题 + 副标题
    text = re.sub(
        r'<h[23][^>]*>(第[一二三四五六七八九十百千\d]+[章节回部卷集])\s+(.*?)（(.*?)）</h[23]>',
        (
            '<h2 class="chapter-title">\n'
            '<span class="chapter-sequence-number">\1</span>\n'
            '<br class="hd1"/> \2\n'
            '<span class="chapter-subtitle">（\3）</span></h2>'
        ),
        text
    )

    # =============================================
    # 4. 卷标题替换 → volume-title 格式
    # =============================================
    text = re.sub(
        r'<h2[^>]*class="titlel2single"[^>]*>(.*?) (.*?)</h2>',
        (
            '<h1 id="title" class="volume-title">\1<br class="hd1"/>\n'
            '<span class="volume-subtitle"> \2</span></h1>'
        ),
        text
    )

    text = re.sub(
        r'<h1[^>]*>(第[一二三四五六七八九十百千\d]+[卷部篇])\s+(.*?)</h1>',
        (
            '<h1 id="title" class="volume-title">\1<br class="hd1"/>\n'
            '<span class="volume-subtitle"> \2</span></h1>'
        ),
        text
    )

    # =============================================
    # 5. 阿蒙读书特定清理
    # =============================================
    remove_patterns = [
        r'<div id="book-columns" class="calibre1">',
        r'<div id="book-inner" class="calibre1">',
        r'<span id="kobo\.\d+\.\d+">',
        r'<img[^>]+src="\.\./images/\d+\.png"[^>]*/?>\s*</span>\s*<br[^>]*>',
    ]
    for p in remove_patterns:
        text = re.sub(p, '', text, flags=re.DOTALL)

    # 阿蒙读书注释分隔线
    text = re.sub(
        r'<div\s+class="calibre1">\s*<hr\s+class="xian"\s*/>\s*</div>\s*<ol\s+class="duokan-footnote-content"\s*>',
        '<hr class="fenge"/>',
        text,
        flags=re.I | re.S
    )

    # 阿蒙读书正文注释标记
    text = re.sub(
        r'<a[^>]*class="duokan-footnote"[^>]*type="noteref"[^>]*href="([^#"]+)#B_(\d+)"[^>]*id="A_\2"[^>]*>.*?</a>',
        r'<sup class="math-super"><a class="zs" href="\1#m\2" id="w\2">\2</a></sup>',
        text,
        flags=re.I | re.S
    )

    # 阿蒙读书注脚内容
    text = re.sub(
        r'<li class="duokan-footnote-item" id="B_(\d+)">\s*<p class="footnote"><a href="(.*?).html#A_\1" class="duokan-footnote">.*?</a>',
        r'<p class="zhusi"><a href="\2.html#w\1" id="m\1">[\1]</a>',
        text,
        flags=re.DOTALL
    )

    # =============================================
    # 6. 诗句格式化
    # =============================================
    text = re.sub(
        r'<p[^>]*>([\u4e00-\u9fa5]{7}，[\u4e00-\u9fa5]{7}。)</p>',
        r'<p class="txthc">\1</p>',
        text
    )
    text = re.sub(
        r'<p[^>]*>([\u4e00-\u9fa5]{5}，[\u4e00-\u9fa5]{5}。)</p>',
        r'<p class="txthc">\1</p>',
        text
    )

    # =============================================
    # 7. 清理多余空行和占位符
    # =============================================
    text = re.sub(r'<p[^>]*>　+</p>', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text


def convert_azw3_to_epub(azw3_path, epub_path):
    """使用 calibre 的 ebook-convert 将 AZW3 转为 EPUB"""
    ebook_convert = os.path.join(CALIBRE_PATH, "ebook-convert.exe")
    if not os.path.exists(ebook_convert):
        print(f"错误：找不到 ebook-convert.exe，路径：{ebook_convert}")
        sys.exit(1)
    
    print(f"[1/5] 转换 AZW3 → EPUB: {azw3_path} → {epub_path}")
    result = subprocess.run(
        [ebook_convert, azw3_path, epub_path],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if result.returncode != 0:
        print(f"转换失败：{result.stderr}")
        sys.exit(1)
    print("  转换完成")


def extract_epub(epub_path, extract_dir):
    """解压 EPUB 文件"""
    print(f"[2/5] 解压 EPUB 到: {extract_dir}")
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir, exist_ok=True)
    
    with zipfile.ZipFile(epub_path, 'r') as zf:
        zf.extractall(extract_dir)
    print("  解压完成")


def find_content_files(extract_dir):
    """找到 EPUB 中的 HTML/XHTML 内容文件和 CSS 文件"""
    html_files = []
    css_files = []
    
    for root, dirs, files in os.walk(extract_dir):
        for f in files:
            full_path = os.path.join(root, f)
            if f.endswith(('.html', '.xhtml', '.htm')):
                html_files.append(full_path)
            elif f.endswith('.css'):
                css_files.append(full_path)
    
    return html_files, css_files


def process_html_files(html_files):
    """对所有 HTML 文件应用正则替换"""
    print(f"[3/5] 对 {len(html_files)} 个 HTML 文件应用正则替换...")
    total_replacements = 0
    
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8', errors='replace') as f:
            original = f.read()
        
        modified = apply_regex_replacements(original)
        
        if modified != original:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(modified)
            # 统计变更数量
            diff_count = sum(1 for a, b in zip(original.split('\n'), modified.split('\n')) if a != b)
            total_replacements += diff_count
            rel_path = os.path.relpath(html_file, WORK_DIR)
            print(f"  ✓ {rel_path} ({diff_count} 处变更)")
    
    print(f"  共 {total_replacements} 处替换")


def merge_css_styles(css_files):
    """将排版 CSS 样式合并到样式表文件中"""
    print(f"[4/5] 合并 CSS 样式到 {len(css_files)} 个样式表...")
    
    for css_file in css_files:
        with open(css_file, 'r', encoding='utf-8', errors='replace') as f:
            existing_css = f.read()
        
        # 检查是否已包含我们的样式（避免重复添加）
        if '.chapter-title' in existing_css:
            print(f"  跳过 {os.path.relpath(css_file, WORK_DIR)}（已包含排版样式）")
            continue
        
        # 追加我们的样式
        new_css = existing_css + "\n" + CSS_STYLES
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(new_css)
        
        print(f"  ✓ {os.path.relpath(css_file, WORK_DIR)}")


def repack_epub(extract_dir, epub_path):
    """重新打包 EPUB"""
    print(f"[4.5/5] 重新打包 EPUB: {epub_path}")
    
    # EPUB 的 mimetype 必须是第一个文件且不压缩
    mimetype_path = os.path.join(extract_dir, 'mimetype')
    
    with zipfile.ZipFile(epub_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 先写入 mimetype（不压缩）
        if os.path.exists(mimetype_path):
            zf.write(mimetype_path, 'mimetype', compress_type=zipfile.ZIP_STORED)
        
        # 写入其他文件
        for root, dirs, files in os.walk(extract_dir):
            for f in files:
                full_path = os.path.join(root, f)
                arcname = os.path.relpath(full_path, extract_dir)
                # 跳过 mimetype（已写入）
                if arcname == 'mimetype':
                    continue
                zf.write(full_path, arcname)
    
    print("  打包完成")


def convert_epub_to_azw3(epub_path, azw3_path):
    """使用 calibre 的 ebook-convert 将 EPUB 转回 AZW3"""
    ebook_convert = os.path.join(CALIBRE_PATH, "ebook-convert.exe")
    
    print(f"[5/5] 转换 EPUB → AZW3: {epub_path} → {azw3_path}")
    result = subprocess.run(
        [ebook_convert, epub_path, azw3_path],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if result.returncode != 0:
        print(f"转换失败：{result.stderr}")
        sys.exit(1)
    print("  转换完成")


def main():
    print("=" * 60)
    print("Dong.azw3 排版优化工具")
    print("基于 kindle.md 排版规则")
    print("=" * 60)
    
    # 检查源文件
    if not os.path.exists(SOURCE_AZW3):
        print(f"错误：源文件不存在：{SOURCE_AZW3}")
        sys.exit(1)
    
    # 创建工作目录
    os.makedirs(WORK_DIR, exist_ok=True)
    
    # Step 1: AZW3 → EPUB
    convert_azw3_to_epub(SOURCE_AZW3, TEMP_EPUB)
    
    # Step 2: 解压 EPUB
    extract_epub(TEMP_EPUB, EXTRACT_DIR)
    
    # Step 3: 找到内容文件
    html_files, css_files = find_content_files(EXTRACT_DIR)
    print(f"  找到 {len(html_files)} 个 HTML 文件, {len(css_files)} 个 CSS 文件")
    
    # Step 4: 应用正则替换
    process_html_files(html_files)
    
    # Step 5: 合并 CSS
    merge_css_styles(css_files)
    
    # Step 6: 重新打包 EPUB
    repack_epub(EXTRACT_DIR, TEMP_EPUB)
    
    # Step 7: EPUB → AZW3
    convert_epub_to_azw3(TEMP_EPUB, OUTPUT_AZW3)
    
    print("=" * 60)
    print(f"✅ 排版优化完成！")
    print(f"  原文件：{SOURCE_AZW3}")
    print(f"  优化后：{OUTPUT_AZW3}")
    print("=" * 60)


if __name__ == "__main__":
    main()