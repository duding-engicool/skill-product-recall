#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品召回报告生成器（混合式双版：MD + HTML）
读取召回信息 JSON（或内置小样本）→ 按一/二/三级矩阵分级 → 装配通知矩阵 + 时间线 + 演练推演 → 输出 MD + HTML。

JSON 字段：
{
  "meta": {"product":"产品","batch":"批次","company":"企业","date":"日期","owner":"负责人"},
  "recall": {"trigger":"触发原因","risk_level":"一级","estimated_units":8500,"affected_regions":"全国","root_cause":"根因"},
  "notifications": [{"channel":"监管机构","method":"限期上报","timing":"24h 内","owner":"合规"}],
  "timeline": [{"step":"触发与确认","deadline":"T+0","action":"确认风险，启动预案"}],
  "drill": [{"scenario":"模拟一级召回推演","participants":"质量+合规","duration":"2h","checkpoint":"30min 内完成上报决策"}]
}

用法：
  python build_report.py -i recall.json -o recall_report
  python build_report.py -o recall_report          # 使用内置小样本
"""

import argparse
import json
import os
import html

# 主色
MAIN = "#C8102E"

# 召回分级（通用参考，企业可覆盖）
GRADE = {
    "一级": {"scope": "全国范围", "launch": "立即启动", "notice": "媒体公告", "color": MAIN},
    "二级": {"scope": "限定区域", "launch": "限期启动", "notice": "定向通知", "color": "#E8A33D"},
    "三级": {"scope": "特定批次/渠道", "launch": "渠道内启动", "notice": "渠道回收", "color": "#2E9E5B"},
}


# 内置小样本（一级召回）
SAMPLE_DATA = {
    "meta": {"product": "XX 电动车充电器", "batch": "B-2606-009", "company": "待企业补充", "date": "2026-07-13", "owner": "质量总监"},
    "recall": {
        "trigger": "客户端批量过热投诉（安全相关）",
        "risk_level": "一级",
        "estimated_units": 8500,
        "affected_regions": "全国",
        "root_cause": "待企业补充（8D 结论）",
    },
    "notifications": [
        {"channel": "监管机构", "method": "限期上报", "timing": "24h 内", "owner": "合规"},
        {"channel": "客户/经销商", "method": "书面通知 + 回收指引", "timing": "公告后 48h", "owner": "销售 + 质量"},
        {"channel": "公众/媒体", "method": "官网公告", "timing": "同步", "owner": "公关"},
        {"channel": "内部", "method": "启动召回指挥组", "timing": "立即", "owner": "质量总监"},
    ],
    "timeline": [
        {"step": "触发与确认", "deadline": "T+0", "action": "确认风险，启动预案"},
        {"step": "影响评估", "deadline": "T+24h", "action": "量化批次与数量，定级"},
        {"step": "上报监管", "deadline": "T+24h", "action": "向监管提交报告"},
        {"step": "发布召回公告", "deadline": "T+48h", "action": "官网/媒体公告"},
        {"step": "回收与置换", "deadline": "T+7d", "action": "渠道回收、免费置换"},
        {"step": "整改验证", "deadline": "T+30d", "action": "根因整改、8D 闭环"},
        {"step": "闭环复盘", "deadline": "T+60d", "action": "演练复盘、预案更新"},
    ],
    "drill": [
        {"scenario": "模拟一级召回推演", "participants": "质量 + 合规 + 销售 + 公关", "duration": "2h", "checkpoint": "30min 内完成上报决策"},
        {"scenario": "媒体应对演练", "participants": "公关 + 法务", "duration": "1h", "checkpoint": "统一对外口径、零误报"},
        {"scenario": "渠道回收压力测试", "participants": "销售 + 物流", "duration": "1.5h", "checkpoint": "72h 内回收率 ≥ 90%"},
    ],
}


def grade_info(level):
    return GRADE.get(level, GRADE["三级"])


def fmt_num(v):
    try:
        return f"{int(v):,}"
    except Exception:
        return "—"


def generate_md(meta, recall, notifications, timeline, drill):
    level = recall.get("risk_level", "三级")
    gi = grade_info(level)
    lines = []
    lines.append(f"# 产品召回预案 · {meta.get('product','未命名产品')}")
    lines.append("")
    lines.append(f"- **产品**：{meta.get('product','待企业补充')} ｜ **批次**：{meta.get('batch','待企业补充')}")
    lines.append(f"- **企业**：{meta.get('company','待企业补充')} ｜ **日期**：{meta.get('date','—')} ｜ **负责人**：{meta.get('owner','待企业补充')}")
    lines.append(f"- **触发**：{recall.get('trigger','待企业补充')}")
    lines.append(f"- **召回分级**：**{level}**（范围：{gi['scope']}；启动：{gi['launch']}；公告：{gi['notice']}）")
    lines.append(f"- **预估数量**：{fmt_num(recall.get('estimated_units'))} 件 ｜ **影响区域**：{recall.get('affected_regions','待企业补充')}")
    lines.append(f"- **根因**：{recall.get('root_cause','待企业补充')}")
    lines.append("")

    # 一、通知矩阵
    lines.append("## 一、通知矩阵")
    lines.append("")
    lines.append("| 渠道 | 告知方式 | 时限 | 责任方 |")
    lines.append("|------|----------|------|--------|")
    for n in notifications:
        lines.append(f"| {n.get('channel','—')} | {n.get('method','—')} | {n.get('timing','—')} | {n.get('owner','待企业补充')} |")
    lines.append("")

    # 二、时间线
    lines.append("## 二、召回时间线")
    lines.append("")
    lines.append("| 里程碑 | 时限 | 动作 |")
    lines.append("|--------|------|------|")
    for t in timeline:
        lines.append(f"| {t.get('step','—')} | {t.get('deadline','—')} | {t.get('action','—')} |")
    lines.append("")
    lines.append("> 时限为通用参考，具体以企业制度与所在地法规为准；缺失项标「待企业补充」。")
    lines.append("")

    # 三、演练推演
    lines.append("## 三、模拟推演表")
    lines.append("")
    lines.append("| 场景 | 参与角色 | 时长 | 关键检查点 |")
    lines.append("|------|----------|------|------------|")
    for d in drill:
        lines.append(f"| {d.get('scenario','—')} | {d.get('participants','待企业补充')} | {d.get('duration','—')} | {d.get('checkpoint','—')} |")
    lines.append("")

    lines.append("---")
    lines.append("> 本预案由产品召回助手生成。法规条款号、监管时限、根因结论缺失处已标注「待企业补充」，分级默认参考通用矩阵，最终召回决策与报送以企业制度与所在地法规为准。")
    lines.append("")
    return "\n".join(lines)


def generate_html(meta, recall, notifications, timeline, drill):
    product = html.escape(str(meta.get("product", "未命名产品")))
    batch = html.escape(str(meta.get("batch", "待企业补充")))
    company = html.escape(str(meta.get("company", "待企业补充")))
    date = html.escape(str(meta.get("date", "—")))
    owner = html.escape(str(meta.get("owner", "待企业补充")))
    trigger = html.escape(str(recall.get("trigger", "待企业补充")))
    root = html.escape(str(recall.get("root_cause", "待企业补充")))

    level = recall.get("risk_level", "三级")
    gi = grade_info(level)
    gcolor = gi["color"]

    # 通知矩阵
    nrows = ""
    for n in notifications:
        nrows += f"<tr><td>{html.escape(str(n.get('channel','—')))}</td><td>{html.escape(str(n.get('method','—')))}</td><td>{html.escape(str(n.get('timing','—')))}</td><td>{html.escape(str(n.get('owner','待企业补充')))}</td></tr>"

    # 时间线
    trows = ""
    for i, t in enumerate(timeline):
        dot = MAIN if i in (0, len(timeline) - 1) else gcolor
        trows += f"""<div class="tl-item">
  <div class="tl-dot" style="background:{dot}"></div>
  <div class="tl-body"><b>{html.escape(str(t.get('step','—')))}</b> <span class="tl-dl">{html.escape(str(t.get('deadline','—')))}</span><div class="tl-act">{html.escape(str(t.get('action','—')))}</div></div>
</div>"""

    # 演练
    drows = ""
    for d in drill:
        drows += f"<tr><td>{html.escape(str(d.get('scenario','—')))}</td><td>{html.escape(str(d.get('participants','待企业补充')))}</td><td>{html.escape(str(d.get('duration','—')))}</td><td>{html.escape(str(d.get('checkpoint','—')))}</td></tr>"

    doc = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>产品召回预案 · {product}</title>
<style>
*{{box-sizing:border-box;font-family:-apple-system,'Segoe UI','Microsoft YaHei',sans-serif;margin:0;padding:0;color:#1f2329}}
body{{background:#f5f6f8;padding:24px}}
.wrap{{max-width:960px;margin:0 auto;background:#fff;border-radius:12px;padding:28px 32px;box-shadow:0 2px 12px rgba(0,0,0,.06)}}
h1{{font-size:22px;color:{MAIN};border-bottom:3px solid {MAIN};padding-bottom:10px}}
.meta{{color:#666;font-size:13px;margin:12px 0 18px;line-height:1.9}}
.grade{{display:inline-block;background:{gcolor};color:#fff;padding:4px 14px;border-radius:14px;font-weight:bold;font-size:14px}}
.section{{margin:22px 0}}
.section h2{{font-size:16px;color:{MAIN};border-left:4px solid {MAIN};padding-left:8px;margin-bottom:10px}}
table{{width:100%;border-collapse:collapse;font-size:13px;margin:6px 0}}
th,td{{border:1px solid #e8eaed;padding:8px 10px;text-align:left}}
th{{background:#fafbfc;color:#444}}
.tl{{position:relative;margin-left:8px;padding-left:20px;border-left:2px solid #e8eaed}}
.tl-item{{position:relative;margin:12px 0}}
.tl-dot{{position:absolute;left:-27px;top:4px;width:12px;height:12px;border-radius:50%;border:2px solid #fff;box-shadow:0 0 0 2px #e8eaed}}
.tl-body{{background:#fafbfc;border:1px solid #e8eaed;border-radius:8px;padding:10px 14px}}
.tl-dl{{color:#888;font-size:12px;margin-left:6px}}
.tl-act{{color:#555;font-size:13px;margin-top:4px}}
.foot{{color:#999;font-size:12px;margin-top:22px;border-top:1px dashed #ddd;padding-top:10px}}
</style></head>
<body><div class="wrap">
<h1>产品召回预案 · {product}</h1>
<div class="meta">
  产品：{product} ｜ 批次：{batch}<br>
  企业：{company} ｜ 日期：{date} ｜ 负责人：{owner}<br>
  触发：{trigger}<br>
  召回分级：<span class="grade">{html.escape(level)}</span> ｜ 范围：{html.escape(gi['scope'])} ｜ 启动：{html.escape(gi['launch'])} ｜ 公告：{html.escape(gi['notice'])}<br>
  预估数量：{fmt_num(recall.get('estimated_units'))} 件 ｜ 影响区域：{html.escape(str(recall.get('affected_regions','待企业补充')))}<br>
  根因：{root}
</div>

<div class="section"><h2>通知矩阵</h2>
<table><tr><th>渠道</th><th>告知方式</th><th>时限</th><th>责任方</th></tr>{nrows}</table></div>

<div class="section"><h2>召回时间线</h2>
<div class="tl">{trows}</div>
<p style="font-size:12px;color:#999">时限为通用参考，具体以企业制度与所在地法规为准。</p></div>

<div class="section"><h2>模拟推演表</h2>
<table><tr><th>场景</th><th>参与角色</th><th>时长</th><th>关键检查点</th></tr>{drows}</table></div>

<div class="foot">本预案由产品召回助手生成。法规条款号、监管时限、根因结论缺失处已标注「待企业补充」，分级默认参考通用矩阵，最终召回决策与报送以企业制度与所在地法规为准。</div>
</div></body></html>"""
    return doc


def main():
    ap = argparse.ArgumentParser(description="产品召回报告生成器（MD + HTML 双版）")
    ap.add_argument("-i", "--input", help="召回信息 JSON 路径（缺省使用内置小样本）")
    ap.add_argument("-o", "--output", default="recall_report", help="输出前缀（生成 .md 与 .html）")
    args = ap.parse_args()

    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            payload = json.load(f)
    else:
        payload = SAMPLE_DATA
        print("ℹ️ 未提供 -i，使用内置小样本数据。")

    meta = payload.get("meta", {}) or {}
    recall = payload.get("recall", {}) or {}
    notifications = payload.get("notifications", []) or []
    timeline = payload.get("timeline", []) or []
    drill = payload.get("drill", []) or []

    md = generate_md(meta, recall, notifications, timeline, drill)
    htm = generate_html(meta, recall, notifications, timeline, drill)

    out_dir = os.path.dirname(args.output)
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    md_path = args.output + ".md"
    html_path = args.output + ".html"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(htm)

    print(f"✅ 报告已生成：\n  MD : {md_path}\n  HTML: {html_path}")
    print(f"   召回分级={recall.get('risk_level','三级')}  预估数量={fmt_num(recall.get('estimated_units'))} 件")


if __name__ == "__main__":
    main()
