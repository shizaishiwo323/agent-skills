#!/usr/bin/env python3
"""从论文 PDF 中截取图片和表格区域,供"图表梳理"使用。

依赖: PyMuPDF (pip install pymupdf)

用法:
  # 1) 自动识别图注/表注,按启发式裁出每个图和表,输出 PNG + manifest.json
  python extract_figures.py scan  paper.pdf out_dir [--dpi 200]

  # 2) 自动裁得不准时,渲染整页(带 50pt 坐标网格)查看坐标
  python extract_figures.py page  paper.pdf out_dir --pages 3,5 [--grid]

  # 3) 按页码和 PDF 坐标(单位 pt,原点左上)手动裁剪
  python extract_figures.py crop  paper.pdf PAGE X0 Y0 X1 Y1 out.png [--dpi 200]

  # 4) Word 文档:直接导出其中嵌入的图片
  python extract_figures.py docx  paper.docx out_dir

页码一律从 1 开始。自动结果只是初稿,必须逐张打开核对。
"""
import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

CAPTION_RE = re.compile(
    r"^\s*(?P<kind>Fig\.?|Figure|FIG\.?|FIGURE|Table|TABLE|图|表)\s*"
    r"(?P<num>S?\d+[a-z]?)\s*(?P<sep>[.:|：．]|\s+(?=[A-Z(（一-鿿])|$)"
)


def _fitz():
    try:
        import fitz  # PyMuPDF
    except ImportError:
        sys.exit("需要 PyMuPDF:pip install pymupdf")
    return fitz


def _kind(raw):
    return "table" if raw.lower().startswith("table") or raw == "表" else "figure"


def _overlap_x(a, b):
    return max(0.0, min(a[2], b[2]) - max(a[0], b[0]))


def _union(rects):
    return [min(r[0] for r in rects), min(r[1] for r in rects),
            max(r[2] for r in rects), max(r[3] for r in rects)]


def _content_x(page):
    """版心左右边界(按较宽的文本块估计),用于区分单栏/双栏。"""
    wide = [b for b in _text_blocks(page) if b[2] - b[0] > 100]
    if not wide:
        return 0.0, page.rect.width
    return min(b[0] for b in wide), max(b[2] for b in wide)


def _column_span(cap, left, right):
    """图注较窄时视为单栏图,限定在图注所在的半栏;否则通栏。"""
    if cap[2] - cap[0] > 0.6 * (right - left):
        return [left, 0, right, 0]
    mid = (left + right) / 2
    return [left, 0, mid, 0] if (cap[0] + cap[2]) / 2 < mid else [mid, 0, right, 0]


def _graphics(page):
    """页面上的位图和矢量图元外框。"""
    rects = []
    for info in page.get_image_info():
        b = info["bbox"]
        if (b[2] - b[0]) > 5 and (b[3] - b[1]) > 5:
            rects.append(list(b))
    for d in page.get_drawings():
        r = d["rect"]
        if (r.width > 2 or r.height > 2) and r.width < page.rect.width * 0.98:
            rects.append([r.x0, r.y0, r.x1, r.y1])
    return rects


def _text_blocks(page):
    return [b for b in page.get_text("blocks") if b[6] == 0 and b[4].strip()]


def _is_body(block, col):
    """正文段落:宽度接近栏宽且至少两行。"""
    w = block[2] - block[0]
    return w > 0.8 * (col[2] - col[0]) and block[4].count("\n") >= 2


def _figure_box(page, cap, prev_limit, col):
    gr = [g for g in _graphics(page)
          if g[3] <= cap[1] + 3 and g[1] >= prev_limit - 2 and _overlap_x(g, col) > 0]
    texts = _text_blocks(page)
    if gr:
        box = _union(gr)
        # 把落在图框附近的短文本(坐标轴标签、panel 字母)并进来
        for t in texts:
            tb = list(t[:4])
            if (tb[1] >= box[1] - 15 and tb[3] <= cap[1] + 1 and not _is_body(t, col)
                    and _overlap_x(tb, box) > 0):
                box = _union([box, tb])
        return box, "graphics"
    # 无图元(例如整页扫描件):取图注上方到最近正文段落之间
    top = prev_limit
    for t in texts:
        if t[3] <= cap[1] and _is_body(t, col) and _overlap_x(t, col) > 0:
            top = max(top, t[3])
    return [col[0] + 20, top + 2, col[2] - 20, cap[1] - 2], "fallback"


def _table_box(page, cap, next_limit, col):
    """表注在上。优先沿表格横线向下追踪表体;没有横线时取表注到下一段正文之间。"""
    texts = _text_blocks(page)
    rules = sorted((g for g in _graphics(page)
                    if g[1] >= cap[3] - 2 and g[3] <= next_limit and _overlap_x(g, col) > 0),
                   key=lambda g: g[1])
    if rules and rules[0][1] - cap[3] < 40:
        chain = [rules[0]]
        for g in rules[1:]:
            if g[1] - chain[-1][3] > 150:  # 横线之间断开太远,视为表格结束
                break
            chain.append(g)
        box = _union(chain)
        for t in texts:
            if t[1] >= box[1] - 2 and t[3] <= box[3] + 2 and _overlap_x(t, col) > 0:
                box = _union([box, list(t[:4])])
        return box, "graphics"
    bottom = next_limit
    for t in texts:
        if t[1] > cap[3] + 5 and _is_body(t, col) and _overlap_x(t, col) > 0:
            bottom = min(bottom, t[1])
    return [col[0], cap[3] + 1, col[2], bottom - 2], "fallback"


def _save_clip(page, box, out, dpi, pad=4):
    fitz = _fitz()
    r = fitz.Rect(box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad) & page.rect
    page.get_pixmap(clip=r, dpi=dpi).save(out)
    return [round(v, 1) for v in (r.x0, r.y0, r.x1, r.y1)]


def cmd_scan(a):
    fitz = _fitz()
    doc = fitz.open(a.pdf)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    seen, items = set(), []
    for pno, page in enumerate(doc, start=1):
        ph = page.rect.height
        left, right = _content_x(page)
        caps = []
        for b in _text_blocks(page):
            m = CAPTION_RE.match(b[4])
            if not m:
                continue
            kind = _kind(m.group("kind"))
            label = f"{'Table' if kind == 'table' else 'Fig'} {m.group('num')}"
            if label in seen:  # 续表、正文中的同名引用只取首次
                continue
            seen.add(label)
            caps.append((list(b[:4]), kind, label, " ".join(b[4].split())))
        caps.sort(key=lambda c: c[0][1])
        for i, (cap, kind, label, text) in enumerate(caps):
            col = _column_span(cap, left, right)
            col[3] = ph
            same_col = [c[0] for c in caps if _overlap_x(c[0], col) > 0]
            above = [c[3] for c in same_col if c[3] <= cap[1]]
            below = [c[1] for c in same_col if c[1] >= cap[3]]
            if kind == "figure":
                box, how = _figure_box(page, cap, max(above, default=0), col)
            else:
                box, how = _table_box(page, cap, min(below, default=ph - 30), col)
            name = re.sub(r"\s+", "_", label) + ".png"
            clip = _save_clip(page, box, out / name, a.dpi)
            items.append({"label": label, "kind": kind, "page": pno, "file": name,
                          "bbox_pt": clip, "method": how, "caption": text})
    (out / "manifest.json").write_text(json.dumps(items, ensure_ascii=False, indent=2),
                                       encoding="utf-8")
    for it in items:
        flag = "" if it["method"] == "graphics" else "  <- 未找到图元,请人工核对"
        print(f"p{it['page']:>3}  {it['label']:<10} {it['file']}{flag}")
    print(f"共 {len(items)} 项,清单见 {out / 'manifest.json'}")


def cmd_page(a):
    fitz = _fitz()
    doc = fitz.open(a.pdf)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    pages = [int(p) for p in a.pages.split(",")] if a.pages else range(1, len(doc) + 1)
    for p in pages:
        page = doc[p - 1]
        if a.grid:
            shape = page.new_shape()
            w, h = page.rect.width, page.rect.height
            for v in range(0, int(max(w, h)) + 1, 50):
                if v <= w:
                    shape.draw_line((v, 0), (v, h))
                if v <= h:
                    shape.draw_line((0, v), (w, v))
            shape.finish(color=(1, 0, 0), width=0.3)
            shape.commit()
            for v in range(0, int(max(w, h)) + 1, 50):
                if v <= w:
                    page.insert_text((v + 1, 8), str(v), fontsize=6, color=(1, 0, 0))
                if v <= h:
                    page.insert_text((1, v - 1), str(v), fontsize=6, color=(1, 0, 0))
        f = out / f"page_{p:03d}.png"
        page.get_pixmap(dpi=a.dpi).save(f)
        print(f"{f}  ({page.rect.width:.0f} x {page.rect.height:.0f} pt)")


def cmd_crop(a):
    fitz = _fitz()
    page = fitz.open(a.pdf)[a.page - 1]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    clip = _save_clip(page, [a.x0, a.y0, a.x1, a.y1], a.out, a.dpi, pad=0)
    print(f"{a.out}  bbox={clip}")


def cmd_docx(a):
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(a.docx) as z:
        media = sorted(n for n in z.namelist() if n.startswith("word/media/"))
        for n in media:
            (out / Path(n).name).write_bytes(z.read(n))
            print(out / Path(n).name)
    print(f"共 {len(media)} 张(顺序按文件名,需对照正文确认图号)")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan"); s.add_argument("pdf"); s.add_argument("out_dir")
    s.add_argument("--dpi", type=int, default=200); s.set_defaults(fn=cmd_scan)
    s = sub.add_parser("page"); s.add_argument("pdf"); s.add_argument("out_dir")
    s.add_argument("--pages"); s.add_argument("--grid", action="store_true")
    s.add_argument("--dpi", type=int, default=110); s.set_defaults(fn=cmd_page)
    s = sub.add_parser("crop"); s.add_argument("pdf"); s.add_argument("page", type=int)
    for k in ("x0", "y0", "x1", "y1"):
        s.add_argument(k, type=float)
    s.add_argument("out"); s.add_argument("--dpi", type=int, default=200)
    s.set_defaults(fn=cmd_crop)
    s = sub.add_parser("docx"); s.add_argument("docx"); s.add_argument("out_dir")
    s.set_defaults(fn=cmd_docx)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
