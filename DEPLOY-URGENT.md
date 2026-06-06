# 🚨 紧急修复 - 手动部署步骤

## 问题状态

**Cloudflare Pages 构建失败** - 原因是 `sync-skills.py` 不支持 GitHub 源配置。

**已修复**：
- ✅ 更新 `scripts/sync-skills.py` 支持从 GitHub 克隆
- ✅ 更新 `site-config.json` 配置为 GitHub 源
- ✅ 代码已 commit 但未推送

---

## 📝 立即执行（在本地终端）

### 方案 A: 如果你能访问机器

SSH 到机器或使用本地终端：

```bash
# 1. 进入项目目录
cd /userdata/hermes/profiles/skill-dev/projects/skill-registry-site

# 2. 查看当前状态
git status
# 应该看到：2 files changed (scripts/sync-skills.py, site-config.json)

# 3. 推送到 GitHub
git push origin main

# 如果遇到 SSH 错误，使用 HTTPS:
git remote set-url origin https://github.com/airsltd/hermes-skill-registry.git
git push origin main
# 输入 GitHub 用户名和密码（或个人访问令牌）
```

### 方案 B: 从本机重新克隆

如果无法 SSH 到机器，在本地电脑执行：

```bash
# 1. 克隆 repo
git clone https://github.com/airsltd/hermes-skill-registry.git
cd hermes-skill-registry

# 2. 创建修复文件

# 2.1 更新 site-config.json
cat > site-config.json << 'EOF'
{
  "name": "Hermes Skill Registry",
  "description": "发现和安装优质的 Hermes Agent 技能",
  "domain": "skills.airs.ltd",
  "source_skills": [
    {
      "type": "github",
      "org": "NousResearch",
      "repo": "hermes-agent",
      "path": "skills/"
    }
  ],
  "output": {
    "web_dir": "./web",
    "core_dir": "./core"
  },
  "auto_sync": {
    "enabled": true,
    "interval_hours": 6
  }
}
EOF

# 2.2 创建 scripts/sync-skills.py
# (完整文件内容见下方 - 太长不便粘贴，请访问机器复制)

# 3. 推送
git add .
git commit -m "Fix: Support GitHub source in sync-skills.py"
git push origin main
```

---

## 🔄 Cloudflare 自动重新构建

推送后，Cloudflare Pages 会：

1. 检测到新的 commit
2. 运行：`python scripts/sync-skills.py && python scripts/build-site.py`
3. 从 NousResearch/hermes-agent 克隆技能
4. 生成网站
5. 部署到 `https://skills.airs.ltd`

**预期输出**:
```
📥 克隆 NousResearch/hermes-agent...
📂 扫描：skills/
  ✓ arxiv (research)
  ✓ llm-wiki (research)
  ✓ blogwatcher (research)
  ...
✅ 同步完成！共 89 个技能
```

---

## 📊 验证清单

推送后检查：

### 1. GitHub Actions
访问：https://github.com/airsltd/hermes-skill-registry/actions
- 查看最新的 "Deploy to Cloudflare Pages"
- 状态应该是绿色 ✅

### 2. Cloudflare Pages
访问：https://dash.cloudflare.com
- Pages → hermes-skill-registry
- Deployments → 最新部署
- 状态应该是 "Ready"

### 3. 在线网站
访问：
- https://hermes-skill-registry.pages.dev
- https://skills.airs.ltd (已绑定域名)

应该看到：
- ✅ 搜索框
- ✅ 分类筛选
- ✅ 89 个技能卡片
- ✅ 技能详情页可点击

---

## 🆘 故障排查

### 构建仍然失败

**检查构建日志**:
1. Cloudflare Dashboard → Pages → hermes-skill-registry
2. 点击最新部署 → "View logs"

**常见错误**:

**错误 1**: `KeyError: 'path'`
- 原因：`site-config.json` 缺少 `path` 字段
- 解决：确保配置包含 `"path": "skills/"`

**错误 2**: `git clone failed`
- 原因：网络问题或 repo 不存在
- 解决：检查 `org` 和 `repo` 是否正确
- 确认 repo 是公开的

**错误 3**: `No skills found`
- 原因：`path` 配置错误
- 解决：确认 NousResearch/hermes-agent 的 skills 目录路径

### 网站空白

**可能**:
- 构建输出目录配置错误
- 应该是 `web` 而不是 `./web` 或 `web/`

检查 `wrangler.toml`:
```toml
[build]
publish = "web"
```

---

## 📎 附录：完整配置文件

### site-config.json
```json
{
  "name": "Hermes Skill Registry",
  "description": "发现和安装优质的 Hermes Agent 技能",
  "domain": "skills.airs.ltd",
  "source_skills": [
    {
      "type": "github",
      "org": "NousResearch",
      "repo": "hermes-agent",
      "path": "skills/"
    }
  ],
  "output": {
    "web_dir": "./web",
    "core_dir": "./core"
  },
  "auto_sync": {
    "enabled": true,
    "interval_hours": 6
  }
}
```

### wrangler.toml
```toml
[build]
command = "python scripts/sync-skills.py && python scripts/build-site.py"
publish = "web"

[build.environment]
PYTHON_VERSION = "3.11"
```

---

## ⏰ 时间线

- **13:22** - 网站生成完成（本地）
- **13:28** - 首次部署到 Cloudflare
- **13:30** - 构建失败（缺少 build-site.py）
- **13:35** - 创建 build-site.py
- **14:32** - 第二次部署
- **14:33** - 构建失败（KeyError: 'path'）
- **14:35** - 修复完成，**等待手动推送** ← 当前位置
- **?** - 推送后自动部署 ✅

---

**立即推送代码到 GitHub，完成后访问 `https://skills.airs.ltd`！** 🚀

*创建时间：2026-06-06 14:35*