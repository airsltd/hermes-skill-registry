# ☁️ Cloudflare Pages 部署指南

## 快速部署（5 分钟上线）

### 步骤 1: 安装 Wrangler

```bash
npm install -g wrangler
```

### 步骤 2: 登录 Cloudflare

```bash
wrangler login
```

### 步骤 3: 部署

```bash
cd /userdata/hermes/profiles/skill-dev/projects/skill-registry-site
wrangler pages deploy web --project-name=hermes-skill-registry
```

**完成！** 你会得到一个 URL:
`https://hermes-skill-registry.pages.dev`

---

## 绑定自定义域名

### 1. 在 Cloudflare 添加域名

如果 `airs.ltd` 还没在 Cloudflare:
1. 登录 https://dash.cloudflare.com
2. **Add a Site** → 输入 `airs.ltd`
3. 按照指引修改域名服务器

### 2. 配置 DNS

添加 CNAME 记录:
```
类型：CNAME
名称：skills
内容：hermes-skill-registry.pages.dev
代理：启用（橙色云）
```

### 3. 在 Pages 绑定

1. Pages → 选择项目
2. **Custom domains** → **Add custom domain**
3. 输入：`skills.airs.ltd`
4. 确认

等待几分钟，访问 `https://skills.airs.ltd` ✅

---

## Git 自动部署（推荐）

### 1. 推送到 GitHub

```bash
cd /userdata/hermes/profiles/skill-dev/projects/skill-registry-site

git init
git add .
git commit -m "Initial commit"

# 创建 GitHub repo 后
git remote add origin https://github.com/YOUR_USER/hermes-skill-registry.git
git push -u origin main
```

### 2. 连接 Cloudflare Pages

1. Pages → **Create a project**
2. 选择 **Git Provider** → **GitHub**
3. 选择你的 repo
4. 配置:
   - **Branch**: `main`
   - **Build command**: `python scripts/sync-skills.py && python scripts/build-site.py`
   - **Output directory**: `web`
5. **Save and Deploy**

### 3. 自动同步

GitHub Actions 已配置每 6 小时自动同步技能。

---

## 故障排查

**问题**: 部署失败  
**解决**: 查看日志 - Pages → Deployments → 点击部署 → View logs

**问题**: 技能数量为 0  
**解决**: 检查 `site-config.json` 中的路径是否正确

**问题**: 自定义域名不工作  
**解决**: 等待 DNS 传播（最多 24 小时），检查 SSL 证书状态

---

## 命令参考

```bash
# 本地预览
cd web && python -m http.server 8000

# 部署到 preview
wrangler pages deploy web --branch=preview

# 部署到 production
wrangler pages deploy web --branch=main

# 查看项目列表
wrangler pages project list

# 查看部署历史
wrangler pages deployment list
```

---

*详细文档：README.md*  
*创建时间：2026-06-06*