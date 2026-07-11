"""
Dong.azw3 全面优化脚本 v2
基于实际HTML结构分析，执行以下操作：
1. 删除标题上logo格式的图片 (<div class="logo">)
2. 单独一页的二级标题(h2)移动到后面正文页，并删除原页
3. 统一各级标题格式 (h1→volume-title, h2→chapter-title)
4. 统一正文格式 (calibre2→txt)
5. 合并CSS，重打包EPUB，转回AZW3
"""
import os, re, shutil, subprocess

# ===== 路径配置 =====
CALIBRE = r'D:\Soft\Calibre2'
SOURCE_AZW3 = r'E:\Else\Dong.azw3'
WORK_DIR = r'E:\Else\Dong_optimize'
EPUB_DIR = os.path.join(WORK_DIR, 'epub_extracted')
TEXT_DIR = os.path.join(EPUB_DIR, 'text')
OUTPUT_AZW3 = r'E:\Else\Dong_optimized_v2.azw3'

# ===== CSS样式定义（来自page_styles.css） =====
EXTRA_CSS = """
/* ===== 字体 ===== */
@page {
  margin-bottom: 5pt;
  margin-top: 5pt;
}
@font-face {
  font-family: "fzlt";
  src: url(fonts/00126.ttf);
}
@font-face {
  font-family: "syst";
  src: url(fonts/00132.ttf);
}
@font-face {
  font-family: "hysf";
  src: url(fonts/00129.ttf);
}
@font-face {
  font-family: "fzys";
  src: url(fonts/00128.ttf);
}
@font-face {
  font-family: "stdgt";
  src: url(fonts/00131.ttf);
}
@font-face {
  font-family: "zqfs";
  src: url(fonts/00133.ttf);
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
  height: 1px;
  text-align: left;
  width: 60%;
  margin: 0.5em auto;
  border-top: gray solid 1px;
}
"""


def get_html_files():
    """获取排序后的HTML文件列表"""
    files = sorted([f for f in os.listdir(TEXT_DIR) if f.endswith('.html')])
    return files


def read_file(path):
    """读取文件内容"""
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()


def write_file(path, content):
    """写入文件内容"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def is_h2_only_page(content):
    """判断是否为仅含h2标题的独立页面"""
    body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.S)
    if not body_match:
        return False, None
    body = body_match.group(1).strip()
    h2_match = re.search(r'<h2[^>]*>(.*?)</h2>', body, re.S)
    if not h2_match:
        return False, None
    # 移除h2后检查剩余内容
    remaining = re.sub(r'<h2[^>]*>.*?</h2>', '', body, flags=re.S).strip()
    remaining = re.sub(r'<[^>]+>\s*</[^>]+>', '', remaining).strip()
    remaining = re.sub(r'<br[^>]*/?\s*>', '', remaining).strip()
    remaining = re.sub(r'\s+', '', remaining)
    if len(remaining) < 20:
        return True, h2_match.group(0)  # 返回完整的h2标签
    return False, None


def delete_logo_images(content):
    """删除 <div class="logo">...</div> 块（标题上logo格式的图片）"""
    # 匹配 <div class="logo" ...>...</div>
    content = re.sub(
        r'<div\s+class="logo"[^>]*>.*?</div>',
        '',
        content,
        flags=re.S
    )
    return content


def unify_headings(content):
    """统一各级标题格式"""
    # h1 class="calibre3" (属性可能在任意位置) → h1 class="volume-title"
    content = re.sub(
        r'<h1[^>]*class="calibre3"[^>]*>',
        '<h1 class="volume-title">',
        content
    )
    # h2 class="h2a1" → h2 class="chapter-title"
    content = re.sub(
        r'<h2[^>]*class="h2a1"[^>]*>',
        '<h2 class="chapter-title">',
        content
    )
    # h2 class="h2a" → h2 class="chapter-title" (如"作者简介")
    content = re.sub(
        r'<h2[^>]*class="h2a"[^>]*>',
        '<h2 class="chapter-title">',
        content
    )
    # h2 class="h2a2" → h2 class="chapter-title"
    content = re.sub(
        r'<h2[^>]*class="h2a2"[^>]*>',
        '<h2 class="chapter-title">',
        content
    )
    # h2 class="h" → h2 class="chapter-title" (独立页的章标题)
    content = re.sub(
        r'<h2[^>]*class="h"[^>]*>',
        '<h2 class="chapter-title">',
        content
    )
    # h3 class="h1" → h3 class="chapter-sequence-number" (节号如"01")
    content = re.sub(
        r'<h3[^>]*class="h1"[^>]*>',
        '<h3 class="chapter-sequence-number">',
        content
    )
    return content


def unify_text(content):
    """统一正文格式"""
    # p class="calibre2" → p class="txt"
    content = re.sub(
        r'<p\s+class="calibre2"[^>]*>',
        '<p class="txt">',
        content
    )
    return content


def clean_empty_lines(content):
    """清理多余的空行"""
    # 移除连续3个以上的空行
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    return content


def extract_azw3():
    """从原始AZW3重新解包，确保干净的起始状态"""
    print("===== 第零步：从原始AZW3重新解包 =====")
    # 清理旧目录
    if os.path.exists(WORK_DIR):
        print(f"清理旧工作目录: {WORK_DIR}")
        shutil.rmtree(WORK_DIR)
    os.makedirs(WORK_DIR, exist_ok=True)

    # AZW3 → EPUB
    print("转换 AZW3 → EPUB...")
    epub_path = os.path.join(WORK_DIR, 'Dong.epub')
    convert_cmd = os.path.join(CALIBRE, 'ebook-convert')
    result = subprocess.run(
        [convert_cmd, SOURCE_AZW3, epub_path],
        capture_output=True, text=True, timeout=300
    )
    if result.returncode != 0:
        print(f"EPUB转换失败: {result.stderr}")
        return False
    print(f"EPUB已生成: {epub_path}")

    # 解包EPUB
    import zipfile
    global EPUB_DIR, TEXT_DIR
    EPUB_DIR = os.path.join(WORK_DIR, 'epub_extracted')
    TEXT_DIR = os.path.join(EPUB_DIR, 'text')
    print(f"解包EPUB到: {EPUB_DIR}")
    with zipfile.ZipFile(epub_path, 'r') as zf:
        zf.extractall(EPUB_DIR)
    print(f"解包完成，text目录: {TEXT_DIR}")
    return True


def process_files():
    """主处理流程"""
    # 先重新解包
    if not extract_azw3():
        print("解包失败，退出")
        return

    files = get_html_files()
    print(f"总HTML文件数: {len(files)}")

    # ===== 第一步：识别h2独立页并移动标题到下一页 =====
    h2_only_pages = {}  # filename -> h2_tag
    for i, f in enumerate(files):
        path = os.path.join(TEXT_DIR, f)
        content = read_file(path)
        is_h2_only, h2_tag = is_h2_only_page(content)
        if is_h2_only:
            h2_only_pages[f] = h2_tag

    print(f"找到 {len(h2_only_pages)} 个h2独立页面")

    # 将h2标题移动到下一个非h2独立页
    # 为避免连续h2独立页导致标题丢失，需找到下一个非空内容页
    moved_count = 0
    h2_only_set = set(h2_only_pages.keys())
    
    for f, h2_tag in h2_only_pages.items():
        idx = files.index(f)
        # 找到下一个非h2独立页
        target_idx = None
        for j in range(idx + 1, len(files)):
            if files[j] not in h2_only_set:
                target_idx = j
                break
        
        if target_idx is not None:
            target_f = files[target_idx]
            target_path = os.path.join(TEXT_DIR, target_f)
            target_content = read_file(target_path)

            # 将h2标签改为chapter-title格式
            new_h2 = re.sub(
                r'<h2\s+class="[^"]*"[^>]*>',
                '<h2 class="chapter-title">',
                h2_tag
            )

            # 在body标签后插入h2
            body_match = re.search(r'(<body[^>]*>)', target_content, re.S)
            if body_match:
                insert_pos = body_match.end()
                target_content = target_content[:insert_pos] + '\n\n  ' + new_h2 + '\n' + target_content[insert_pos:]
                write_file(target_path, target_content)
                moved_count += 1

    print(f"已移动 {moved_count} 个h2标题到内容页")

    # ===== 第二步：删除h2独立页文件及OPF/NCX中的引用 =====
    deleted_count = 0
    h2_only_filenames = set(h2_only_pages.keys())
    
    # 删除HTML文件
    for f in h2_only_pages:
        path = os.path.join(TEXT_DIR, f)
        if os.path.exists(path):
            os.remove(path)
            deleted_count += 1
    print(f"已删除 {deleted_count} 个h2独立页HTML文件")

    # 从content.opf中移除引用（支持多种路径）
    opf_path = None
    for candidate in ['content.opf', 'OEBPS/content.opf', 'OEBPS/content.opf']:
        test_path = os.path.join(EPUB_DIR, candidate)
        if os.path.exists(test_path):
            opf_path = test_path
            break
    # 如果还没找到，搜索.opf文件
    if opf_path is None:
        for root, dirs, filenames in os.walk(EPUB_DIR):
            for fn in filenames:
                if fn.endswith('.opf'):
                    opf_path = os.path.join(root, fn)
                    break
            if opf_path:
                break
    
    if opf_path:
        print(f"找到OPF文件: {opf_path}")
        opf_content = read_file(opf_path)
        original_opf = opf_content
        
        # 先收集所有需要删除的item id
        item_ids_to_remove = []
        for f in h2_only_filenames:
            id_match = re.search(r'<item[^>]*id="([^"]*)"[^>]*href="text/' + re.escape(f) + '"', original_opf)
            if id_match:
                item_ids_to_remove.append(id_match.group(1))
        
        # 移除manifest中的item引用
        for f in h2_only_filenames:
            opf_content = re.sub(
                r'\s*<item[^>]*href="text/' + re.escape(f) + r'"[^>]*/?\s*>',
                '',
                opf_content,
                flags=re.S
            )
        
        # 移除spine中的itemref引用
        for item_id in item_ids_to_remove:
            opf_content = re.sub(
                r'\s*<itemref\s+idref="' + re.escape(item_id) + r'"[^>]*/?\s*>',
                '',
                opf_content
            )
        
        if opf_content != original_opf:
            write_file(opf_path, opf_content)
            print(f"已更新content.opf，移除 {len(h2_only_filenames)} 个文件引用和 {len(item_ids_to_remove)} 个spine项")
    else:
        print("警告：未找到content.opf")

    # 从toc.ncx中移除引用
    ncx_path = os.path.join(EPUB_DIR, 'toc.ncx')
    if os.path.exists(ncx_path):
        ncx_content = read_file(ncx_path)
        original_ncx = ncx_content
        
        for f in h2_only_filenames:
            # 移除navPoint中引用该文件的条目
            # 匹配整个navPoint块（可能嵌套）
            ncx_content = re.sub(
                r'\s*<navPoint[^>]*>\s*<navLabel[^>]*>.*?</navLabel>\s*<content\s+src="text/' + re.escape(f) + r'[^"]*"\s*/>\s*</navPoint>',
                '',
                ncx_content,
                flags=re.S
            )
        
        if ncx_content != original_ncx:
            write_file(ncx_path, ncx_content)
            print(f"已更新toc.ncx，移除相关导航条目")
    else:
        print("警告：未找到toc.ncx")

    # ===== 第三步：对所有文件执行统一格式替换 =====
    total_replacements = 0
    for f in files:
        # 跳过已删除的h2独立页文件
        if f in h2_only_set:
            continue
        path = os.path.join(TEXT_DIR, f)
        if not os.path.exists(path):
            continue
        content = read_file(path)
        original = content

        # 1. 删除logo图片
        content = delete_logo_images(content)

        # 2. 统一标题格式
        content = unify_headings(content)

        # 3. 统一正文格式
        content = unify_text(content)

        # 4. 清理空行
        content = clean_empty_lines(content)

        if content != original:
            write_file(path, content)
            # 统计替换数
            diffs = sum(1 for a, b in zip(original.split('\n'), content.split('\n')) if a != b)
            total_replacements += diffs

    print(f"格式替换完成，共修改 {total_replacements} 处")

    # ===== 第四步：合并CSS =====
    print("合并CSS样式...")
    # 将额外CSS追加到page_styles.css
    page_styles_path = os.path.join(EPUB_DIR, 'page_styles.css')
    existing_css = read_file(page_styles_path)
    # 检查是否已有volume-title等定义
    if 'volume-title' not in existing_css:
        write_file(page_styles_path, existing_css + '\n' + EXTRA_CSS)
        print("已追加CSS样式到page_styles.css")
    else:
        print("page_styles.css已包含所需样式，跳过")

    # ===== 第五步：重打包EPUB =====
    print("重打包EPUB...")
    epub_output = os.path.join(WORK_DIR, 'Dong_optimized.epub')

    # 使用ebook-convert重新打包
    # 先将解包的目录重新打包为EPUB
    # 方法：使用calibre的ebook-edit或手动重新创建EPUB

    # 使用zip重新打包EPUB（EPUB本质是zip）
    import zipfile
    epub_path = os.path.join(WORK_DIR, 'Dong_repacked.epub')

    # EPUB需要mimetype文件在首位且不压缩
    with zipfile.ZipFile(epub_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 先添加mimetype（必须不压缩）
        mimetype_path = os.path.join(EPUB_DIR, 'mimetype')
        if os.path.exists(mimetype_path):
            zf.write(mimetype_path, 'mimetype', compress_type=zipfile.ZIP_STORED)

        # 添加其他文件
        for root, dirs, filenames in os.walk(EPUB_DIR):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                arcname = os.path.relpath(file_path, EPUB_DIR)
                # 跳过mimetype（已添加）
                if arcname == 'mimetype':
                    continue
                zf.write(file_path, arcname)

    print(f"EPUB已重打包: {epub_path}")

    # ===== 第六步：转换回AZW3 =====
    print("转换回AZW3...")
    convert_cmd = os.path.join(CALIBRE, 'ebook-convert')
    result = subprocess.run(
        [convert_cmd, epub_path, OUTPUT_AZW3],
        capture_output=True, text=True, timeout=300
    )
    if result.returncode == 0:
        print(f"AZW3转换完成: {OUTPUT_AZW3}")
        # 检查文件大小
        size = os.path.getsize(OUTPUT_AZW3)
        print(f"输出文件大小: {size:,} 字节")
    else:
        print(f"AZW3转换失败: {result.stderr}")

    print("优化完成！")


if __name__ == '__main__':
    process_files()