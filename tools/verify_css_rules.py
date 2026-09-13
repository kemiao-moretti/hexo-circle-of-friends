#!/usr/bin/env python3
"""校验 css_rules.yaml 中某条 link_page_rules 规则能否真实命中目标页面。

用法：
    python verify_css_rules.py <theme> <url>

例如：
    python verify_css_rules.py hugo-solitude https://blog.518339.xyz/links/

规则语义与 FCircle 保持一致：
  - 每个字段（author/link/avatar）是一个规则列表；
  - 由上到下依次尝试，命中第一个非空值即停止，不再尝试后续规则；
  - 输出每条规则各自命中的数量，便于判断兜底规则是否被触发。
"""
import sys
from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup

RULES_FILE = Path(__file__).resolve().parent.parent / "css_rules.yaml"
FIELDS = ("author", "link", "avatar")


def fetch_html(url: str) -> str:
    resp = requests.get(
        url,
        timeout=30,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0 Safari/537.36"
            )
        },
    )
    resp.raise_for_status()
    return resp.text


def extract(el, attr: str) -> str:
    """取属性值。attr 为 text 时取文本，否则取对应 HTML 属性。"""
    if attr == "text":
        return el.get_text(strip=True)
    return (el.get(attr) or "").strip()


def resolve(soup, rules: list) -> tuple:
    """按 FCircle 语义解析：逐条规则尝试，命中非空即停止。

    返回 (值, 命中的规则描述, 该规则命中数, 每条规则的命中数统计)。
    """
    stats = []
    for rule in rules:
        selector, attr = rule["selector"], rule["attr"]
        elements = soup.select(selector)
        values = [extract(e, attr) for e in elements]
        hit = [v for v in values if v]
        stats.append((selector, attr, len(elements), len(hit)))
        if hit:
            return hit[0], f'{selector} [attr={attr}]', len(hit), stats
    return "", "<未命中>", 0, stats


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2

    theme, url = sys.argv[1], sys.argv[2]

    with RULES_FILE.open(encoding="utf-8") as f:
        rules = yaml.safe_load(f)

    link_rules = rules.get("link_page_rules", {})
    if theme not in link_rules:
        print(f"✗ link_page_rules 中不存在主题：{theme}")
        print(f"  可用主题：{', '.join(link_rules)}")
        return 1

    print(f"主题规则：{theme}")
    print(f"目标页面：{url}")
    print("=" * 68)

    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    theme_rules = link_rules[theme]
    for field in FIELDS:
        if field not in theme_rules:
            print(f"✗ 缺少字段 {field}")
            return 1
        rules_list = theme_rules[field]
        value, matched_by, count, stats = resolve(soup, rules_list)

        print(f"\n[{field}] 命中 {count} 个")
        for selector, attr, found, hit in stats:
            flag = "✓" if hit else "·"
            print(f"  {flag} {selector}  attr={attr}  元素 {found} / 非空 {hit}")
        if value:
            shown = value if len(value) <= 80 else value[:77] + "..."
            print(f"  → 取值：{shown}")
            print(f"  → 来自：{matched_by}")
        else:
            print("  → 未取到任何值")

    print("\n" + "=" * 68)

    # 交叉校验：三个字段的命中数量应当一致（同一批友链条目）
    counts = {}
    for field in FIELDS:
        _, _, count, _ = resolve(soup, theme_rules[field])
        counts[field] = count

    print(f"各字段命中数量：{counts}")
    if len(set(counts.values())) != 1:
        print("✗ 失败：author/link/avatar 命中数量不一致，规则可能抓错了元素")
        return 1
    if counts["author"] == 0:
        print("✗ 失败：未命中任何友链条目")
        return 1

    print(f"✓ 通过：三个字段均命中 {counts['author']} 条友链")
    return 0


if __name__ == "__main__":
    sys.exit(main())
