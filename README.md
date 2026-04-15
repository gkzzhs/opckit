<p align="center">
  <h1 align="center">🏢 OPCKit</h1>
  <p align="center">
    <strong>一人公司 AI 操作系统 — 让一个人像一家公司一样运转</strong><br>
    三个 AI 部门（市场部·销售部·运营部）共享同一个本地数据库，行业配置化，数据 100% 本地。
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/version-2.1.0-blue" alt="version">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="license">
    <img src="https://img.shields.io/badge/Python-3.10+-yellow" alt="python">
    <img src="https://img.shields.io/badge/code-~300%20lines-blueviolet" alt="code">
    <img src="https://img.shields.io/badge/data-100%25%20local-brightgreen" alt="local data">
  </p>
</p>

---

## 😩 它解决什么问题

你是一个人在接活、做项目、搞副业。AI 工具用了不少——ChatGPT 写文案、Claude 拆需求、Excel 记账、备忘录管客户。

但问题是：**这些工具互相不认识。**

你就是那个人肉数据总线——客户信息在微信聊天记录里，收支在备忘录里，内容计划在脑子里。工具越多，信息越碎；能力越强，管理越乱。

**OPCKit 不是再给你 3 个工具，而是给你 3 个能共享上下文的 AI 部门。**

## 🧭 Before / After

| | Before | After（OPCKit） |
|---|---|---|
| **客户管理** | 微信聊天记录翻半天 | 一句"查客户"看全部 |
| **记账** | 备忘录随手记，月底对不上 | "收了 5000"→ 自动归档，月报一键出 |
| **内容** | 凭感觉发，不知道什么火 | 热点分析 → 创作 → 一稿多用 → 排期 |
| **跟进** | 全靠记忆，经常忘 | 自动提醒谁该联系了，联系完自动更新 |
| **数据孤岛** | 每个工具各管各的 | 三部门共享一个数据库，数据自动流转 |

## ⚡ 三个部门

| 部门 | Skill | 核心能力 |
|------|-------|---------|
| 📢 **市场部** | `opckit-mkt` | 热点分析 · 内容创作（小红书/公众号/知乎/抖音）· 一稿多用 · 内容日历 · 效果追踪 |
| 🤝 **销售部** | `opckit-sales` | 客户建档 · 需求拆解 · 三档报价 · 跟进提醒 + 自动标记 · 成交收款 |
| 📊 **运营部** | `opckit-ops` | 记账 · 经营报告 · 月度报告 · 晨报/晚报（定时推送）· 催款管理 |

**关键设计：三个部门共享同一个 SQLite 数据库。** 市场部发了什么内容，销售部知道；销售部成交了，运营部自动记收入。数据在部门之间自动流转，不用你手动搬。

## 🎯 行业配置化

同一套框架，不同行业看到完全不同的报价模板和平台推荐：

| 行业 | 内容平台 | 报价参考 | 跟进周期 |
|------|---------|---------|---------|
| 🎨 设计师 | 小红书、Dribbble、站酷 | Logo ¥2k-5k | 3 天 |
| 💻 开发者 | 掘金、GitHub、知乎 | 官网 ¥5k-15k | 5 天 |
| 📋 咨询师 | 公众号、知乎、LinkedIn | 咨询 ¥500-2k/h | 7 天 |
| ✍️ 创作者 | 小红书、公众号、抖音 | 种草 ¥1k-5k/篇 | 3 天 |

首次使用时说一句"我是设计师"，自动加载对应配置。也可以自定义行业模板。

## 📊 真实经营数据

以下是作者本人使用 OPCKit 管理自己一人公司的真实数据：

```
📊 仪表盘: 客户 5 | 收入 ¥8,800 支出 ¥520 | 内容 3
```

| 数据 | 详情 |
|------|------|
| 客户 | 企业合作方（有劳务合同）、AI 社区、比赛等 |
| 收入 | 兼职月收入 + 比赛奖金 |
| 内容 | GitHub 开源项目 + 技术文章 |

**每一条都是真实经营记录，不是演示数据。**

## 🚀 快速开始

### 前提条件

- [OpenClaw](https://github.com/anthropics/openclaw) 已安装
- Python 3.10+

### 一键安装

```bash
git clone https://github.com/gkzzhs/opckit.git
cd opckit
chmod +x install.sh
./install.sh
```

安装完成后，对 Agent 说 **"我是一个设计师"** 即可开始使用。

## 💬 使用示例

### 市场部
```
你: 最近小红书上什么设计类内容比较火？
AI: [搜索分析] 这是本周 3 个热门选题方向...

你: 帮我写一篇小红书笔记，主题是 Logo 设计的 5 个避坑指南
AI: [生成完整图文] ...

你: 这篇发了，点赞 230 评论 45
AI: ✅ 状态已更新为"已发布"，互动数据已记录。
```

### 销售部
```
你: 有个新客户张总，做餐饮的，想要品牌 VI，预算 2 万
AI: 确认录入：姓名张总，行业餐饮... 确认？

你: 谁该跟进了？
AI: 张总 3 天没联系了，建议发条消息...
    联系完了告诉我，我帮你更新跟进时间。

你: 联系了
AI: ✅ 张总的跟进时间已更新到今天。
```

### 运营部
```
你: 收了张总 1 万首款
AI: 确认记录：收入 ¥10,000，来自张总... ✅

你: 这个月怎么样？
AI: [经营报告] 收入 ¥15,000 / 支出 ¥3,200 / 净利润 ¥11,800
    📌 张总已 5 天没联系，建议跟进。本月内容低于计划频率。

你: 开启每日晨报
AI: ✅ 已设置每天早上 8 点推送经营晨报
```

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────┐
│                 用户对话层                     │
│          OpenClaw / QClaw / WorkBuddy         │
└──────────┬──────────┬──────────┬─────────────┘
           │          │          │
    ┌──────▼──┐ ┌─────▼────┐ ┌──▼───────┐
    │ 市场部   │ │  销售部   │ │  运营部   │
    │ SKILL.md│ │ SKILL.md │ │ SKILL.md │
    └────┬────┘ └────┬─────┘ └────┬─────┘
         │           │            │
         └───────────┼────────────┘
                     │
              ┌──────▼──────┐
              │  db.py CLI   │
              │  (~300 行)   │
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │   SQLite     │
              │ opckit.db    │
              │ 3 张表共享    │
              └─────────────┘
```

- **数据层：** SQLite（`~/.opckit/data/opckit.db`），三张表：`clients` / `ledger` / `content_log`
- **配置层：** JSON 行业模板（`~/.opckit/config/`），首次使用时自动加载
- **交互层：** 纯 SKILL.md（零代码），通过 `python3 {baseDir}/scripts/db.py` 调用数据操作
- **安全设计：** 所有写入操作需用户二次确认；list 查询强制 limit；错误时立即停止并报告

## 📁 目录结构

```
opckit/
├── src/db.py                  # 共享数据库 CLI（唯一的代码文件，~300 行）
├── install.sh                 # 一键安装
├── AGENTS.md                  # Agent 总控配置
├── opckit-mkt/
│   ├── SKILL.md               # 市场部 Skill
│   └── scripts/db.py          # db.py 副本
├── opckit-sales/
│   ├── SKILL.md               # 销售部 Skill
│   └── scripts/db.py          # db.py 副本
├── opckit-ops/
│   ├── SKILL.md               # 运营部 Skill
│   └── scripts/db.py          # db.py 副本
└── config/templates/          # 行业配置模板
    ├── designer.json
    ├── developer.json
    ├── consultant.json
    └── creator.json
```

## 🔧 自定义行业模板

```bash
cp config/templates/designer.json config/templates/myindustry.json
# 编辑平台/报价/跟进周期等
```

然后对 Agent 说"初始化为 myindustry"即可加载。

## 🛡️ 设计原则

1. **AI 辅助，人类拍板** — 所有涉及金额、客户数据的操作必须用户确认
2. **数据不出本地** — SQLite 存在 `~/.opckit/`，不上传任何云端
3. **错误不静默** — db.py 报错时立即停止并展示原文，不自行猜测修复
4. **分类不自造** — 支出分类从固定枚举中选，保证报告聚合准确

## 📄 License

[MIT](LICENSE)

---

<p align="center">
  <strong>不是让 AI 帮你做一件事，而是让 AI 帮你跑一家公司。</strong>
</p>
