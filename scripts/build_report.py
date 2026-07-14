#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品召回报告生成器（纯文字版 .txt + Markdown .md）
读取召回信息 JSON（或内置小样本）→ 按一/二/三级矩阵分级 → 装配通知矩阵 + 时间线 + 演练推演 → 输出 .txt + .md。

JSON 字段：
{
  "meta": {"product":"产品","batch":"批次","company":"企业","date":"日期","owner":"负责人"},
  "recall": {"trigger":"触发原因","risk_level":"一级","estimated_units":8500,"affected_regions":"全国","root_cause":"根因"},
  "notifications": [{"channel":"监管机构","method":"限期上报","timing":"24h 内","owner":"合规"}],
  "timeline": [{"step":"触发与确认","deadline":"T+0","action":"确认风险，启动预案"}],
  "drill": [{"scenario":"模拟一级召回推演","participants":"质量+合规","duration":"2h","checkpoint":"30min 内完成上报决策"}]
}

用法：
  python build_report.py --input recall.json --out-dir ./out
  python build_report.py --out-dir ./out          # 使用内置小样本
"""

import argparse
import json
import os
from datetime import date

# 召回分级（通用参考，企业可覆盖）
GRADE = {
    "一级": {"scope": "全国范围", "launch": "立即启动", "notice": "媒体公告"},
    "二级": {"scope": "限定区域", "launch": "限期启动", "notice": "定向通知"},
    "三级": {"scope": "特定批次/渠道", "launch": "渠道内启动", "notice": "渠道回收"},
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


def generate_txt(meta, recall, notifications, timeline, drill):
    level = recall.get("risk_level", "三级")
    gi = grade_info(level)
    lines = []
    lines.append("=" * 72)
    lines.append(f"产品召回预案 · {meta.get('product','未命名产品')}")
    lines.append("=" * 72)
    lines.append("")
    lines.append(f"产品：{meta.get('product','待企业补充')} ｜ 批次：{meta.get('batch','待企业补充')}")
    lines.append(f"企业：{meta.get('company','待企业补充')} ｜ 日期：{meta.get('date','—')} ｜ 负责人：{meta.get('owner','待企业补充')}")
    lines.append(f"触发：{recall.get('trigger','待企业补充')}")
    lines.append(f"召回分级：{level}（范围：{gi['scope']}；启动：{gi['launch']}；公告：{gi['notice']}）")
    lines.append(f"预估数量：{fmt_num(recall.get('estimated_units'))} 件 ｜ 影响区域：{recall.get('affected_regions','待企业补充')}")
    lines.append(f"根因：{recall.get('root_cause','待企业补充')}")
    lines.append("")

    # 一、通知矩阵
    lines.append("-" * 72)
    lines.append("一、通知矩阵")
    lines.append("-" * 72)
    lines.append("  渠道 | 告知方式 | 时限 | 责任方")
    lines.append("  " + "-" * 68)
    for n in notifications:
        lines.append(f"  {n.get('channel','—')} | {n.get('method','—')} | {n.get('timing','—')} | {n.get('owner','待企业补充')}")
    lines.append("")

    # 二、时间线
    lines.append("-" * 72)
    lines.append("二、召回时间线")
    lines.append("-" * 72)
    lines.append("  里程碑 | 时限 | 动作")
    lines.append("  " + "-" * 68)
    for t in timeline:
        lines.append(f"  {t.get('step','—')} | {t.get('deadline','—')} | {t.get('action','—')}")
    lines.append("")
    lines.append("  时限为通用参考，具体以企业制度与所在地法规为准；缺失项标「待企业补充」。")
    lines.append("")

    # 三、演练推演
    lines.append("-" * 72)
    lines.append("三、模拟推演表")
    lines.append("-" * 72)
    lines.append("  场景 | 参与角色 | 时长 | 关键检查点")
    lines.append("  " + "-" * 68)
    for d in drill:
        lines.append(f"  {d.get('scenario','—')} | {d.get('participants','待企业补充')} | {d.get('duration','—')} | {d.get('checkpoint','—')}")
    lines.append("")

    lines.append("-" * 72)
    lines.append("本预案由产品召回助手生成。法规条款号、监管时限、根因结论缺失处已标注「待企业补充」，分级默认参考通用矩阵，最终召回决策与报送以企业制度与所在地法规为准。")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="产品召回报告生成器（txt + md）")
    ap.add_argument("--input", help="召回信息 JSON 路径（缺省使用内置小样本）")
    ap.add_argument("--out-dir", default=os.getcwd(), help="输出目录（默认当前工作目录）")
    ap.add_argument("--format", choices=["txt", "md", "all"], default="all",
                    help="输出格式：txt / md / all（默认 all = txt + md）")
    args = ap.parse_args()

    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            payload = json.load(f)
    else:
        payload = SAMPLE_DATA
        print("ℹ️ 未提供 --input，使用内置小样本数据。")

    meta = payload.get("meta", {}) or {}
    recall = payload.get("recall", {}) or {}
    notifications = payload.get("notifications", []) or []
    timeline = payload.get("timeline", []) or []
    drill = payload.get("drill", []) or []

    date_str = date.today().strftime("%Y%m%d")
    base = f"产品召回预案_{meta.get('product','未命名产品')}_{date_str}".replace("/", "-")
    os.makedirs(args.out_dir, exist_ok=True)

    if args.format in ("md", "all"):
        md = generate_md(meta, recall, notifications, timeline, drill)
        md_path = os.path.join(args.out_dir, base + ".md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"✅ MD : {md_path}")

    if args.format in ("txt", "all"):
        txt = generate_txt(meta, recall, notifications, timeline, drill)
        txt_path = os.path.join(args.out_dir, base + ".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(txt)
        print(f"✅ TXT: {txt_path}")

    print(f"   召回分级={recall.get('risk_level','三级')}  预估数量={fmt_num(recall.get('estimated_units'))} 件")


if __name__ == "__main__":
    main()
