#!/usr/bin/env python3
"""查询论文的期刊指标与作者信息,只用标准库。

用法:
  python lookup.py journal --issn 0956-540X        # 也可 --name "Geophysical Journal International"
  python lookup.py paper   --doi 10.1093/gji/ggu180 [--years 5] [--authors 1,2,3,-1]
  python lookup.py paper   --title "Spectral induced polarization porosimetry"

journal: 从 LetPub 读 CiteScore(Scopus 分区、排名、百分位)、中科院分区表、新锐分区表、
         LetPub 实时影响因子。LetPub 在分区单元格里混入 display:none 的干扰值,脚本会先剔除。
         官方 IF 和 JCR 分区在 LetPub 上需要登录,脚本只标出"需另查"。
paper:   从 OpenAlex 读论文元数据、作者顺序、单位,以及指定作者的发文统计、研究主题、
         近 N 年高被引论文。OpenAlex 的通讯作者标记常缺失,通讯作者以论文原文为准。

输出为 Markdown 文本,数据都标了来源和版本,供智能体核对后写报告。
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date

UA = "Mozilla/5.0 (paper-background-check skill)"
OPENALEX = "https://api.openalex.org"
LETPUB = "https://www.letpub.com.cn/index.php"


def get(url, retries=2):
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode("utf-8", errors="ignore")
        except Exception as e:  # noqa: BLE001
            if i == retries:
                raise RuntimeError(f"请求失败:{url}\n{e}") from e
            time.sleep(2)


def get_json(url):
    return json.loads(get(url))


# ---------------------------------------------------------------- journal

def _strip_hidden(s):
    """删掉 display:none 的干扰元素(LetPub 用它在分区单元格里混入假值)。"""
    pat = re.compile(r"<(span|div|font|i|b)\b[^>]*display\s*:\s*none[^>]*>.*?</\1>", re.S | re.I)
    prev = None
    while prev != s:
        prev, s = s, pat.sub("", s)
    return s


def _text(fragment):
    t = re.sub(r"<br\s*/?>", " / ", fragment, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def _flat(s):
    s = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", " ", s)
    t = re.sub(r"<[^>]+>", " | ", s)
    t = re.sub(r"\s+", " ", html.unescape(t))
    return re.sub(r"(\s*\|\s*)+", " | ", t)


def letpub_find(issn=None, name=None):
    q = {"page": "journalapp", "view": "search", "searchname": name or "",
         "searchissn": issn or "", "searchsort": "relevance"}
    page = get(LETPUB + "?" + urllib.parse.urlencode(q))
    ids = re.findall(r"journalid=(\d+)&page=journalapp&view=detail", page)
    ids = [i for i in dict.fromkeys(ids) if i != "0"]
    names = re.findall(r"journalid=(\d+)&page=journalapp&view=detail[^>]*>([^<]+)<", page)
    return ids, {i: n.strip() for i, n in names}


def _partition_tables(h):
    """按页面顺序解析所有分区表,返回 [(版本标签, 是否新锐, 内容)]。

    每张表以"大类学科"表头开始;版本标签取表格之前最近的"(……版/……发布)"字样。
    新锐分区表在 HTML 里排在其标签说明之后、趋势图链接之后,所以不能按"标签之后第一张表"找。
    """
    out = []
    head = re.compile(r"<table width=\"100%\"><tr><th[^>]*>大类学科</th>")
    lab = re.compile(r"（\s*(?:<font[^>]*>)?\s*([^<（）]{4,24}?(?:升级版|发布|最新版))\s*(?:</font>)?\s*）")
    for m in head.finditer(h):
        start = m.start()
        before = h[max(0, start - 8000):start]
        labels = list(lab.finditer(before))
        label = labels[-1].group(1).strip() if labels else "版本未知"
        ctx = before[labels[-1].start() - 400:labels[-1].start()] if labels else before[-400:]
        xinrui = "新锐" in ctx
        seg = h[m.end():m.end() + 8000]
        big = re.search(r"<td[^>]*>(.*?)</td>", seg, re.S)
        inner_s = seg.find('<table width="99%">')
        inner_e = seg.find("</table>", inner_s)
        inner = seg[inner_s:inner_e] if inner_s >= 0 else ""
        subs = re.findall(r"<td[^>]*>(.*?)</td>\s*<td width=\"100\"[^>]*>(.*?)</td>", inner, re.S)
        rest = seg[inner_e + len("</table>"):] if inner_e >= 0 else ""
        tail = re.findall(r"<td[^>]*>\s*(.*?)\s*</td>", rest.split("</tr>")[0], re.S)
        big_txt = _text(big.group(1)) if big and inner_s != -1 and big.start() < inner_s else ""
        out.append((label, xinrui, {
            "大类": big_txt,
            "小类": [f"{_text(x)}:{_text(y)}" for x, y in subs],
            "Top期刊": _text(tail[0]) if len(tail) > 0 else "?",
            "综述期刊": _text(tail[1]) if len(tail) > 1 else "?",
        }))
    return out


def cmd_journal(a):
    ids, names = letpub_find(a.issn, a.name)
    if not ids:
        print("LetPub 未找到该期刊。换用 ISSN / E-ISSN / 全称再试,或改用网页搜索。")
        return
    if len(ids) > 1:
        print("LetPub 匹配到多本期刊,取第一本;如不对请用 ISSN 精确查询:")
        for i in ids[:5]:
            print(f"  - journalid={i} {names.get(i, '')}")
    jid = ids[0]
    url = f"{LETPUB}?journalid={jid}&page=journalapp&view=detail"
    raw = get(url)
    h = _strip_hidden(raw)
    t = _flat(h)

    def grab(pat, default="未找到"):
        m = re.search(pat, t)
        return m.group(1).strip() if m else default

    print(f"## 期刊指标(来源:LetPub,{url})\n")
    print(f"- 期刊:{grab(r'期刊名字 \| ([^|]+)')}")
    print(f"- ISSN:{grab(r'期刊ISSN \| ([^|]+)')};E-ISSN:{grab(r'E-ISSN \| ([^|]+)')}")
    if "登录 | 后，查看IF" in t or "后，查看IF" in t:
        print("- 官方影响因子(JCR):LetPub 需登录才显示 → 需另查(期刊官网 / 出版社页面 / JCR)")
    rt = re.search(r"截止(\d{4}年\d{1,2}月\d{1,2}日)：([\d.]+)", t)
    if rt:
        print(f"- LetPub 实时影响因子(非官方,按公式估算):{rt.group(2)}(截至 {rt.group(1)})")
    print(f"- 五年 IF(LetPub 网友提供,仅供参考):{grab(r'五年IF \| （数据来源于网友提供） \| ([\d.]+)')}")
    if "查看WOS分区等级" in t:
        print("- JCR 分区:LetPub 需登录才显示 → 需另查")

    cs_ver = grab(r"（ \| (\d{4}年\d{1,2}月最新版) \| ） \| CiteScore \| SJR", "版本未知")
    cs = re.search(r"CiteScore \| SJR \| SNIP \| CiteScore排名 \| ([\d.]+) \| ([\d.]+) \| ([\d.]+)", t)
    print(f"\n### Scopus / CiteScore({cs_ver})\n")
    if cs:
        print(f"- CiteScore {cs.group(1)};SJR {cs.group(2)};SNIP {cs.group(3)}")
    rows = re.findall(
        r"大类：(.*?)<br>\s*小类：(.*?)</td>\s*<td[^>]*>\s*(Q\d)\s*</td>.*?>(\d+\s*/\s*\d+)</span>"
        r".*?lay-percent=\"(\d+)%\"", h, re.S)
    if rows:
        print("\n| 大类 | 小类 | 分区 | 排名 | 百分位 |\n|---|---|---|---|---|")
        for big, small, q, rank, pct in rows:
            print(f"| {_text(big)} | {_text(small)} | {q} | {rank.replace(' ', '')} | {pct}% |")
    else:
        print("- 未解析到 CiteScore 学科排名")

    tables = _partition_tables(h)
    if not tables:
        print("\n### 分区表\n\n- 未解析到")
    for label, xinrui, p in tables:
        name = "新锐期刊分区表(原中科院分区表团队研制)" if xinrui else "中科院分区表"
        print(f"\n### {name}({label})\n")
        print(f"- 大类:{p['大类'] or '未解析到'}")
        for x in p["小类"]:
            print(f"- 小类:{x}")
        print(f"- Top 期刊:{p['Top期刊']};综述期刊:{p['综述期刊']}")
    warn = re.findall(r"(20\d\d年\d\d月发布的[^|]*?版)：(不?在预警名单中)", t)
    if warn:
        print("\n### 预警名单\n")
        for v, s in warn[:3]:
            print(f"- {v}:{s}")


# ---------------------------------------------------------------- paper

def _oa(path, **params):
    q = urllib.parse.urlencode(params) if params else ""
    return get_json(f"{OPENALEX}{path}{'?' + q if q else ''}")


def find_work(doi=None, title=None):
    if doi:
        doi = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", doi.strip(), flags=re.I)
        return _oa(f"/works/doi:{doi}")
    res = _oa("/works", search=title, **{"per-page": 5})["results"]
    if not res:
        sys.exit("OpenAlex 按标题未找到,请提供 DOI。")
    if len(res) > 1:
        print("按标题匹配到多条,取第一条;请核对标题和年份:")
        for w in res[:5]:
            print(f"  - {w['publication_year']} {w['title']} ({w.get('doi')})")
        print()
    return res[0]


def author_profile(aid, years, topic_words):
    a = _oa(f"/authors/{aid.split('/')[-1]}")
    this_year = date.today().year
    start = this_year - years + 1
    by_year = {c["year"]: c["works_count"] for c in a.get("counts_by_year", [])}
    works = _oa("/works", filter=f"author.id:{aid.split('/')[-1]},from_publication_date:{start}-01-01",
                sort="cited_by_count:desc", **{"per-page": 25},
                select="title,publication_year,primary_location,cited_by_count,doi,authorships")
    out = {
        "name": a["display_name"],
        "orcid": a.get("orcid"),
        "works_count": a.get("works_count"),
        "cited_by_count": a.get("cited_by_count"),
        "h_index": (a.get("summary_stats") or {}).get("h_index"),
        "last_known": [i["display_name"] for i in a.get("last_known_institutions") or []],
        "topics": [t["display_name"] for t in (a.get("topics") or [])[:6]],
        "per_year": [(y, by_year.get(y, 0)) for y in range(start, this_year + 1)],
        "recent": [],
    }
    for w in works.get("results", []):
        src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name", "")
        pos = next((x["author_position"] for x in w.get("authorships", [])
                    if (x["author"].get("id") or "").endswith(aid.split("/")[-1])), "")
        title = w.get("title") or ""
        hit = sum(1 for k in topic_words if k in title.lower())
        out["recent"].append((hit, w["publication_year"], title, src, w.get("cited_by_count", 0),
                              w.get("doi"), pos))
    return out


def cmd_paper(a):
    w = find_work(a.doi, a.title)
    src = (w.get("primary_location") or {}).get("source") or {}
    auths = w.get("authorships", [])
    print(f"## 论文(来源:OpenAlex,{w['id']})\n")
    print(f"- 题目:{w.get('title')}")
    print(f"- 期刊:{src.get('display_name')};ISSN:{', '.join(src.get('issn') or [])}")
    print(f"- 年份:{w.get('publication_year')};DOI:{w.get('doi')}")
    corr = set(w.get("corresponding_author_ids") or [])
    print(f"- OpenAlex 通讯作者标记:{'有' if corr else '无(以论文原文为准)'}\n")
    print("### 作者列表(按署名顺序)\n")
    for k, x in enumerate(auths, 1):
        mark = " [OpenAlex 标为通讯]" if x["author"]["id"] in corr or x.get("is_corresponding") else ""
        inst = "; ".join(i["display_name"] for i in x.get("institutions", [])) or "无"
        raw = " || ".join(x.get("raw_affiliation_strings") or [])
        print(f"{k}. {x['author']['display_name']}{mark}  (OpenAlex {x['author']['id'].split('/')[-1]})")
        print(f"   - 机构(规范化):{inst}")
        if raw:
            print(f"   - 原文单位:{raw}")
    n = len(auths)
    pick = []
    for s in a.authors.split(","):
        i = int(s)
        i = n + i + 1 if i < 0 else i
        if 1 <= i <= n and i not in pick:
            pick.append(i)
    stop = {"the", "and", "of", "for", "with", "from", "into", "using", "based", "a", "an", "in", "on",
            "by", "to", "its", "their", "via", "under"}
    topic_words = [t for t in re.findall(r"[a-z]{4,}", (w.get("title") or "").lower()) if t not in stop]
    print(f"\n### 作者档案(OpenAlex,近 {a.years} 年;同名作者可能被误合并,需与单位主页核对)\n")
    for i in pick:
        x = auths[i - 1]
        try:
            p = author_profile(x["author"]["id"], a.years, topic_words)
        except RuntimeError as e:
            print(f"#### 第 {i} 作者 {x['author']['display_name']}:查询失败 {e}\n")
            continue
        print(f"#### 第 {i} 作者:{p['name']}")
        print(f"- ORCID:{p['orcid'] or '无'}")
        print(f"- 最近单位(OpenAlex):{'; '.join(p['last_known']) or '无'}")
        print(f"- 总发文 {p['works_count']};总被引 {p['cited_by_count']};h 指数 {p['h_index']}")
        print(f"- 主要研究主题:{'; '.join(p['topics']) or '无'}")
        print(f"- 近 {a.years} 年每年发文数:" + ", ".join(f"{y}: {c}" for y, c in p["per_year"]))
        rec = sorted(p["recent"], key=lambda r: (-r[0], -r[4]))[:8]
        if rec:
            print("- 近年论文(先按与本文题目的关键词重合度,再按被引数排序;作者位次见括号):")
            for hit, y, t, s, c, d, pos in rec:
                print(f"  - {y} | {t} | {s} | 被引 {c} | {pos} | {d or ''}")
        print()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("journal")
    j.add_argument("--issn")
    j.add_argument("--name")
    j.set_defaults(fn=cmd_journal)
    p = sub.add_parser("paper")
    p.add_argument("--doi")
    p.add_argument("--title")
    p.add_argument("--years", type=int, default=5)
    p.add_argument("--authors", default="1,2,3,-1",
                   help="要查档案的作者序号,逗号分隔;-1 表示末位作者。默认前三位和末位。")
    p.set_defaults(fn=cmd_paper)
    a = ap.parse_args()
    if a.cmd == "journal" and not (a.issn or a.name):
        ap.error("journal 需要 --issn 或 --name")
    if a.cmd == "paper" and not (a.doi or a.title):
        ap.error("paper 需要 --doi 或 --title")
    a.fn(a)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
