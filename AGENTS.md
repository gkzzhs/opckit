# OPCKit 项目说明

## 项目概览

这是一个运行在 OpenClaw / QClaw / WorkBuddy 上的 Skill Bundle。

- Python 代码入口只有一个：`src/db.py`
- 三个业务 Skill 分别位于 `opckit-mkt/`、`opckit-sales/`、`opckit-ops/`
- 行业模板位于 `config/templates/*.json`
- 安装脚本是 `install.sh`

项目核心设计是“Prompt 层 + 共享 SQLite CLI”：

- `SKILL.md` 负责定义对话行为和调用时机
- `src/db.py` 负责所有真实的数据读写
- `install.sh` 会把 `src/db.py` 复制到每个 Skill 的 `scripts/db.py`

## 目录结构

```text
src/db.py
  共享数据库 CLI，唯一 Python 源码入口

install.sh
  安装脚本；复制模板、分发 db.py、注册 3 个 Skill

opckit-mkt/SKILL.md
opckit-sales/SKILL.md
opckit-ops/SKILL.md
  Prompt 层定义。里面出现的 db.py 命令必须和 src/db.py 的 argparse 完全一致

config/templates/*.json
  行业模板，供 init 子命令复制到 ~/.opckit/config/industry.json
```

## 运行与数据约定

- 默认数据库路径：`~/.opckit/data/opckit.db`
- 可通过环境变量 `OPCKIT_DB_PATH` 覆盖数据库路径
- 配置目录：`~/.opckit/config`
- `init` 会从仓库内 `config/templates/` 读取模板；若该目录不存在，则回退到 `~/.opckit/config/templates`

当前 SQLite 表只有三张：

- `clients`
- `ledger`
- `content_log`

## 修改约定

### 修改 `src/db.py` 时

- 把它视为 CLI 真正的单一事实来源
- 新增、删除或改名任何子命令 / 参数后，必须同步检查 3 个 `SKILL.md`
- 保持输出约定不变：
  - 结构化结果走标准输出 JSON
  - 面向人的提示走标准错误输出
- 优先做小改动，不要把单文件脚本重构成多模块，除非任务明确要求
- 继续使用标准库，避免无必要的新依赖

### 修改 `SKILL.md` 时

- 所有 `python3 {baseDir}/scripts/db.py ...` 示例都必须能映射到 `src/db.py` 当前的 `argparse`
- `list` 类命令应显式带 `--limit`
- 不要在 `SKILL.md` 中发明 `src/db.py` 不支持的参数或子命令
- 如果改了调用方式，记得检查 `install.sh` 复制后的运行路径仍然成立

### 修改模板时

- 保持现有顶层结构：`industry`、`content`、`pricing`、`clients`
- 新增字段前先确认 3 个 `SKILL.md` 或 `src/db.py` 会实际读取它
- 尽量保持 4 份模板字段对齐，避免某一行业模板缺字段

### 修改 `install.sh` 时

- 保持“复制模板 -> 复制 `db.py` 到各 Skill -> 注册 Skill”的顺序清晰
- 优先兼容现有的 OpenClaw / QClaw / WorkBuddy 路径探测逻辑
- 改动后至少做 shell 语法检查

## 代码风格

- 遵循现有的单文件、函数式写法
- 保持命名直接清晰，和现有子命令名称一致
- 优先显式错误处理，尤其是参数缺失、模板不存在、空结果等情况
- 仅在逻辑不直观时加注释
- 继续使用 ASCII 为主；已有中文文案保持中文

## 测试与验证

当前仓库还没有内建的 `tests/` 目录或测试框架配置。做改动时，默认先做最快的本地验证。

### CLI 改动的最小验证

优先使用临时数据库，避免污染 `~/.opckit/data/opckit.db`：

```bash
TMP_DIR=$(mktemp -d)
OPCKIT_DB_PATH="$TMP_DIR/opckit.db" python3 src/db.py init
OPCKIT_DB_PATH="$TMP_DIR/opckit.db" python3 src/db.py client add --data '{"name":"张总"}'
OPCKIT_DB_PATH="$TMP_DIR/opckit.db" python3 src/db.py client list --limit 10
```

如果改动涉及财务、内容或仪表盘，补跑对应子命令：

```bash
OPCKIT_DB_PATH="$TMP_DIR/opckit.db" python3 src/db.py ledger income --amount 1000 --from "张总"
OPCKIT_DB_PATH="$TMP_DIR/opckit.db" python3 src/db.py content add --title "测试标题"
OPCKIT_DB_PATH="$TMP_DIR/opckit.db" python3 src/db.py dashboard
```

### Skill 文档改动的最小验证

- 全量搜索 `python3 {baseDir}/scripts/db.py`
- 逐条对照 `src/db.py` 的 `argparse` 定义
- 确认示例里的参数名、必填项、子命令都存在

### 安装脚本改动的最小验证

```bash
bash -n install.sh
```

### 如果后续补自动化测试

- 测试文件放在 `tests/`
- 默认使用 `pytest`
- 优先覆盖 `src/db.py` 的 CLI 行为，不要只测辅助细节
- 测试中统一用临时目录 + `OPCKIT_DB_PATH` 隔离数据库

## 给后续 Codex 的建议

- 先读 `src/db.py`，再看对应的 `SKILL.md`
- 遇到“文档命令和代码不一致”的问题时，以 `src/db.py` 为准
- 如果用户要求修改业务能力，通常会同时影响这几层：
  - `src/db.py`
  - 一个或多个 `SKILL.md`
  - 可能还有 `config/templates/*.json`
- 除非用户明确要求，否则不要改数据库位置、表名或安装目标目录
