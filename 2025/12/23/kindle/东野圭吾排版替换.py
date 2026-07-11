"""
东野圭吾作品集（69册）排版优化 - EasyPub 正则替换函数
基于 kindle.md 中的排版规则

使用方法：
1. 在 Calibre 中安装 EasyPub 插件
2. 选择要处理的书籍（可批量选择69册）
3. 在 EasyPub 的"替换"功能中：
   - 查找规则填入: (?s).*
   - 将下方 replace 函数粘贴到正则替换函数中
4. 执行替换
"""

import re

def replace(match, number, file_name, metadata, dictionaries, data, functions, *args, **kwargs):
    text = match.group(0)

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
    # <p class="a">　　→ <p class="txt">
    text = re.sub(
        r'<p class="a">　　',
        '<p class="txt">',
        text
    )
    # <p class="calibre\d*">　　→ <p class="txt">
    text = re.sub(
        r'<p class="calibre\d*">　　',
        '<p class="txt">',
        text
    )

    # =============================================
    # 3. 章标题替换 → chapter-title 格式
    # =============================================

    # 3.1 三段结构：章节号 + 标题 +（副标题）
    # 匹配: <h2 ... class="titletoc">第一章 标题（副标题）</h2>
    # 或: <h2 ...>1 标题（副标题）</h2>
    text = re.sub(
        r'<h2[^>]*class="titletoc"[^>]*>(.*?) (.*?)（(.*?)）</h2>',
        (
            '<h2 class="chapter-title">\n'
            '<span class="chapter-sequence-number">\\1</span>\n'
            '<br class="hd1"/> \\2\n'
            '<span class="chapter-subtitle">（\\3）</span></h2>'
        ),
        text
    )

    # 3.2 两段结构：章节号 + 标题
    # 匹配: <h2 ... class="titletoc">第一章 标题</h2>
    text = re.sub(
        r'<h2[^>]*class="titletoc"[^>]*>(.*?) (.*?)</h2>',
        (
            '<h2 class="chapter-title">\n'
            '<span class="chapter-sequence-number">\\1</span>\n'
            '<br class="hd1"/> \\2</h2>'
        ),
        text
    )

    # 3.3 单独标题
    # 匹配: <h2 ... class="titletoc">标题</h2>
    text = re.sub(
        r'<h2[^>]*class="titletoc"[^>]*>(.*?)</h2>',
        r'<h2 class="chapter-title">\1</h2>',
        text
    )

    # 3.4 通用 h2 标题替换（非 titletoc 类）
    # 匹配各种 calibre 生成的 h2 标题
    text = re.sub(
        r'<h2[^>]*class="calibre\d*"[^>]*>(\d+)\s+(.*?)</h2>',
        (
            '<h2 class="chapter-title">\n'
            '<span class="chapter-sequence-number">\\1</span>\n'
            '<br class="hd1"/> \\2</h2>'
        ),
        text
    )

    # 3.5 中文数字章节标题
    # 匹配: 第X章 标题 / 第X回 标题 / 第X节 标题
    text = re.sub(
        r'<h[23][^>]*>(第[一二三四五六七八九十百千\d]+[章节回部卷集])\s+(.*?)</h[23]>',
        (
            '<h2 class="chapter-title">\n'
            '<span class="chapter-sequence-number">\\1</span>\n'
            '<br class="hd1"/> \\2</h2>'
        ),
        text
    )

    # 3.6 中文数字章节标题 + 副标题
    # 匹配: 第X章 标题（副标题）
    text = re.sub(
        r'<h[23][^>]*>(第[一二三四五六七八九十百千\d]+[章节回部卷集])\s+(.*?)（(.*?)）</h[23]>',
        (
            '<h2 class="chapter-title">\n'
            '<span class="chapter-sequence-number">\\1</span>\n'
            '<br class="hd1"/> \\2\n'
            '<span class="chapter-subtitle">（\\3）</span></h2>'
        ),
        text
    )

    # =============================================
    # 4. 卷标题替换 → volume-title 格式
    # =============================================

    # 4.1 titlel2single 类的 h2 → volume-title
    text = re.sub(
        r'<h2[^>]*class="titlel2single"[^>]*>(.*?) (.*?)</h2>',
        (
            '<h1 id="title" class="volume-title">\\1<br class="hd1"/>\n'
            '<span class="volume-subtitle"> \\2</span></h1>'
        ),
        text
    )

    # 4.2 通用卷标题（含"卷"/"部"/"篇"关键字）
    text = re.sub(
        r'<h1[^>]*>(第[一二三四五六七八九十百千\d]+[卷部篇])\s+(.*?)</h1>',
        (
            '<h1 id="title" class="volume-title">\\1<br class="hd1"/>\n'
            '<span class="volume-subtitle"> \\2</span></h1>'
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
    # 七言诗句
    text = re.sub(
        r'<p[^>]*>([\u4e00-\u9fa5]{7}，[\u4e00-\u9fa5]{7}。)</p>',
        r'<p class="txthc">\1</p>',
        text
    )
    # 五言诗句
    text = re.sub(
        r'<p[^>]*>([\u4e00-\u9fa5]{5}，[\u4e00-\u9fa5]{5}。)</p>',
        r'<p class="txthc">\1</p>',
        text
    )

    # =============================================
    # 7. 封面图替换
    # =============================================
    text = re.sub(
        r'<img[^>]+src="([^"]*?)/([^/"]+?)\.jpeg"[^>]*/?\s*>',
        r'<div class="cover">\n\t<img alt="" class="pic" src="../images/\2.jpeg"/>\n</div>',
        text
    )

    # =============================================
    # 8. 插图替换
    # =============================================
    text = re.sub(
        r'<img[^>]+src="[^"]*?/([^/"]+?)\.jpeg"[^>]*/?\s*>',
        r'<div class="imgg">\n    <img src="../images/\1.jpeg" class="imgg1"/>\n  </div>',
        text
    )

    # =============================================
    # 9. 清理多余空行和占位符
    # =============================================
    # 替换全角空格占位符
    text = re.sub(r'<p[^>]*>　+</p>', '', text)
    # 清理连续空行
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text


# =============================================
# 附：需要添加到书籍样式表中的 CSS
# 将以下 CSS 添加到每本书的 stylesheet.css 中
# =============================================
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