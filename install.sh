#!/bin/bash
# OPCKit 一键安装脚本
# 兼容 OpenClaw / QClaw / WorkBuddy
# 用法: chmod +x install.sh && ./install.sh

set -e

OPCKIT_DIR="$HOME/.opckit"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 自动检测 Skill 目录（兼容多平台）
detect_skill_dir() {
    # 优先使用环境变量
    if [ -n "$OPENCLAW_SKILLS_DIR" ]; then
        echo "$OPENCLAW_SKILLS_DIR"; return
    fi

    # WorkBuddy (腾讯)
    if [ -d "$HOME/.workbuddy/skills" ]; then
        echo "$HOME/.workbuddy/skills"; return
    fi
    if [ -d "$HOME/Library/Application Support/WorkBuddy/skills" ]; then
        echo "$HOME/Library/Application Support/WorkBuddy/skills"; return
    fi

    # QClaw (腾讯电脑管家)
    if [ -d "$HOME/.qclaw/skills" ]; then
        echo "$HOME/.qclaw/skills"; return
    fi
    if [ -d "$HOME/Library/Application Support/QClaw/skills" ]; then
        echo "$HOME/Library/Application Support/QClaw/skills"; return
    fi

    # OpenClaw 标准路径
    if [ -d "$HOME/.openclaw/skills" ]; then
        echo "$HOME/.openclaw/skills"; return
    fi

    # 都没找到，用 OpenClaw 默认路径
    echo "$HOME/.openclaw/skills"
}

SKILL_DIR=$(detect_skill_dir)

echo "🚀 开始安装 OPCKit..."
echo ""

# 1. 创建数据目录
echo "📁 创建数据目录..."
mkdir -p "$OPCKIT_DIR/data"
mkdir -p "$OPCKIT_DIR/config/templates"

# 2. 复制行业配置模板
echo "📋 安装行业配置模板..."
cp "$SCRIPT_DIR/config/templates/"*.json "$OPCKIT_DIR/config/templates/" 2>/dev/null || true

# 3. 复制 db.py 到每个 Skill
echo "🔧 安装共享脚本..."
for skill in opckit-mkt opckit-sales opckit-ops; do
    mkdir -p "$SCRIPT_DIR/$skill/scripts"
    cp "$SCRIPT_DIR/src/db.py" "$SCRIPT_DIR/$skill/scripts/db.py"
done

# 4. 注册 Skill
echo "📦 注册 Skill 到: $SKILL_DIR"
mkdir -p "$SKILL_DIR"
for skill in opckit-mkt opckit-sales opckit-ops; do
    if [ -d "$SKILL_DIR/$skill" ]; then
        echo "   ⚠️  $skill 已存在，更新中..."
        rm -rf "$SKILL_DIR/$skill"
    fi
    cp -r "$SCRIPT_DIR/$skill" "$SKILL_DIR/$skill"
    echo "   ✅ $skill 已安装"
done

# 5. 检查 Python 环境
echo ""
echo "🐍 检查 Python 环境..."
if command -v python3 &>/dev/null; then
    PY_VER=$(python3 --version 2>&1)
    echo "   ✅ $PY_VER"
else
    echo "   ⚠️  未检测到 python3，请确保系统已安装 Python 3.10+"
    echo "   提示：macOS 可用 brew install python3"
fi

echo ""
echo "══════════════════════════════════════════"
echo "✅ OPCKit 安装完成！"
echo ""
echo "📂 数据目录:    $OPCKIT_DIR/"
echo "📂 Skill 目录:  $SKILL_DIR/"
echo "📂 检测到平台:  $(basename "$(dirname "$SKILL_DIR")")"
echo ""
echo "🎯 开始使用: 对 Agent 说 \"我是一个设计师\" 即可开始"
echo "══════════════════════════════════════════"
