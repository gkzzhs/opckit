# OPCKit — 一人公司 AI 操作系统

> 第一个「行业配置化 + 统一数据总线」的 OPC AI Skill 套件

OPCKit 是一套运行在 [OpenClaw](https://github.com/anthropics/openclaw) 上的 Skill Bundle，为一人公司创业者提供三个 AI 部门：**市场部、销售部、运营部**。三个部门共享同一个本地数据库，像一个真正的公司一样协同工作。

## 特性

- **行业配置化** — 选择你的职业（设计师/开发者/咨询师/创作者），系统自动配置报价模板、内容平台、跟进周期
- **统一数据总线** — 三个 Skill 共享一个 SQLite 数据库，市场部的内容记录、销售部的客户数据、运营部的财务报表互通
- **本地数据主权** — 所有数据存在你自己的机器上（`~/.opckit/`），不上传任何云端
- **对话式交互** — 通过微信/企微自然对话驱动，不需要打开任何 App

## 三个部门

| 部门 | Skill 名称 | 职责 |
|------|-----------|------|
| 📢 市场部 | `opckit-mkt` | 热点分析、内容创作、一稿多用、内容日历 |
| 🤝 销售部 | `opckit-sales` | 客户建档、需求拆解、智能报价、跟进提醒 |
| 📊 运营部 | `opckit-ops` | 记账、经营报告、晨报晚报、催款管理 |

## 安装

### 前提条件

- 已安装 [OpenClaw](https://github.com/anthropics/openclaw)
- Python 3.10+
- uv（Python 包管理器）

### 一键安装

```bash
git clone https://github.com/yourname/opckit.git
cd opckit
chmod +x install.sh
./install.sh
```

安装完成后，对 Agent 说 **「我是一个设计师」** 即可开始使用。

## 使用示例

### 市场部
```
你: 最近小红书上什么设计类内容比较火？
AI: [搜索分析] 这是本周 3 个热门选题方向...

你: 帮我写一篇小红书笔记，主题是 Logo 设计的 5 个避坑指南
AI: [生成完整图文] ...

你: 改写成公众号版本
AI: [一稿多用] ...
```

### 销售部
```
你: 有个新客户张总，做餐饮的，想要品牌 VI，预算 2 万
AI: 确认录入：姓名张总，行业餐饮... 确认？

你: 帮我出个报价单
AI: [三档报价] 基础版 ¥12,000 / 标准版 ¥18,000 / 高级版 ¥25,000 ...

你: 谁该跟进了？
AI: 张总 3 天没联系了，建议发条消息...
```

### 运营部
```
你: 收了张总 1 万首款
AI: 确认记录：收入 ¥10,000，来自张总... ✅

你: 这个月怎么样？
AI: [经营报告] 收入 ¥15,000 / 支出 ¥3,200 / 净利润 ¥11,800 ...

你: 开启每日晨报
AI: ✅ 已设置每天早上 8 点推送经营晨报
```

## 目录结构

```
opckit/
├── src/db.py                  # 共享数据库 CLI（唯一的代码文件）
├── install.sh                 # 一键安装
├── opckit-mkt/SKILL.md        # 市场部
├── opckit-sales/SKILL.md      # 销售部
├── opckit-ops/SKILL.md        # 运营部
└── config/templates/          # 行业配置模板
    ├── designer.json
    ├── developer.json
    ├── consultant.json
    └── creator.json
```

## 自定义行业模板

创建你自己的行业配置：

```bash
cp config/templates/designer.json config/templates/myindustry.json
# 编辑 myindustry.json，修改平台/报价/跟进周期等
# 重新运行 install.sh
```

然后对 Agent 说「初始化为 myindustry」即可加载。

## 技术架构

- **数据层：** SQLite（`~/.opckit/data/opckit.db`），三张表：clients / ledger / content_log
- **配置层：** JSON 模板（`~/.opckit/config/`），首次使用时选择行业自动加载
- **交互层：** OpenClaw SKILL.md（纯 Prompt 工程），通过 `uv run db.py` 调用数据操作
- **通道层：** 企业微信机器人 / 微信 ClawBot

## 许可证

MIT
