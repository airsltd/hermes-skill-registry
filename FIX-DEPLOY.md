# 🚨 Cloudflare Pages 部署修复说明

## 问题诊断

从构建日志看到两个问题：

### ❌ 问题 1: 技能源路径不存在
```
⚠️ 源不存在：/userdata/hermes/profiles/skill-test/skills
⚠️ 源不存在：/userdata/hermes/profiles/skill-dev/projects/notebook-system
```

**原因**: 这些是本机路径，Cloudflare Pages 环境中不存在。

**解决**: 已更新为从 GitHub 同步:
```json
{
  "source_skills": [
    {
      "type": "github",
      "org": "NousResearch",
      "repo": "hermes-agent",
      "skill_path": "skills/"
    }
  ]
}
```

### ❌ 问题 2: 缺少 build-site.py
```
can't open file '/opt/buildhome/repo/scripts/build-site.py': [Errno 2] No such file or directory
```

**原因**: 文件未被推送到 GitHub。

**解决**: 已创建 `scripts/build-site.py`。

---

## ✅ 修复进度

- [x] 创建 `scripts/build-site.py`
- [x] 更新 `site-config.json` 使用 GitHub 源
- [x] 修复 `wrangler.toml` 配置
- [ ] 推送到 GitHub **← 需要手动执行**

---

## 📝 手动推送步骤

由于本地 Git 没有配置 SSH 密钥，请手动执行：

### 方案 A: 使用 HTTPS 推送（推荐）

```bash
# 1. 进入项目目录
cd /userdata/hermes/profiles/skill-dev/projects/skill-registry-site

# 2. 配置 Git 用户（首次）
git config user.email "dev@airs.ltd"
git config user.name "Hermes Skill Dev"

# 3. 添加并 commit
git add scripts/build-site.py site-config.json
git commit -m "Fix: Add build-site.py and update config for Cloudflare"

# 4. 推送到 GitHub
git push origin main
```

系统会提示输入 GitHub 用户名和密码（或个人访问令牌）。

### 方案 B: 重新克隆（如果 HTTPS 失败）

```bash
# 1. 备份本地更改
cd /userdata/hermes/profiles/skill-dev/projects/skill-registry-site
cp scripts/build-site.py /tmp/backup-build-site.py
cp site-config.json /tmp/backup-site-config.json

# 2. 删除并重新克隆
cd /userdata/hermes/profiles/skill-dev/projects/
rm -rf skill-registry-site
git clone https://github.com/airsltd/hermes-skill-registry.git

# 3. 恢复修改
cd skill-registry-site
cp /tmp/backup-build-site.py scripts/
cp /tmp/backup-site-config.json .

# 4. 推送
git add scripts/build-site.py site-config.json
git commit -m "Fix: Add build-site.py and update config"
git push origin main
```

---

## 🔄 Cloudflare Pages 自动重新构建

推送到 GitHub 后，Cloudflare Pages 会自动：

1. 检测到新的 commit
2. 运行构建命令: `python scripts/sync-skills.py && python scripts/build-site.py`
3. 从 GitHub 同步 NousResearch 的技能
4. 生成静态网站
5. 自动部署

预期构建输出：
```
✓ Sync: 89 skills from NousResearch/hermes-agent
✓ Build: Generated 89 skill pages
✓ Deploy: Published to skills.airs.ltd
```

---

## 🎯 验证部署

推送后，检查：

1. **GitHub Actions**: 
   - 访问 https://github.com/airsltd/hermes-skill-registry/actions
   - 查看 "Deploy to Cloudflare Pages" workflow 是否成功

2. **Cloudflare Pages**:
   - 访问 https://dash.cloudflare.com
   - Pages → hermes-skill-registry → Deployments
   - 查看最新部署状态

3. **在线网站**:
   - 访问 https://hermes-skill-registry.pages.dev
   - 或 https://skills.airs.ltd

---

## 📊 预期结果

部署成功后，网站应该显示：

- ✅ **89 个技能** (从 NousResearch/hermes-agent 同步)
- ✅ **分类筛选** (productivity, research, creative 等)
- ✅ **搜索功能**
- ✅ **技能详情页**

---

## 🆘 如果还有问题

### 构建仍然失败

查看 Cloudflare Pages 的构建日志：
1. Dash.cloudflare.com → Pages → hermes-skill-registry
2. 点击失败的部署
3. 查看 "View logs"

常见错误：
- **Python 版本**: 确保使用 3.11+
- **依赖缺失**: 检查是否使用了非标准库
- **路径错误**: 确保所有路径都是相对路径

### 技能数量为 0

检查:
- `site-config.json` 中的 GitHub 源配置
- NousResearch/hermes-agent repo 是否公开
- 构建日志中的同步输出

---

*更新时间：2026-06-06 14:30*  
*状态：等待手动推送到 GitHub*