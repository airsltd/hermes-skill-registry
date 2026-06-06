# 🚀 Hermes Skill Registry

发现和安装优质的 Hermes Agent 技能

**在线预览**: [skills.airs.ltd](https://skills.airs.ltd) (部署后)

---

## 📊 当前统计

- **技能总数**: 91 个
- **分类**: 7 个
- **最后更新**: 自动同步（每 6 小时）

---

## 🛠️ 本地开发

### 1. 克隆项目

```bash
cd /userdata/hermes/profiles/skill-dev/projects/skill-registry-site
```

### 2. 同步技能

```bash
python scripts/sync-skills.py
```

这会从配置的技能源扫描 SKILL.md 文件，生成元数据索引。

### 3. 构建网站

```bash
python scripts/build-site.py
```

生成静态 HTML 文件到 `web/` 目录。

### 4. 本地预览

```bash
# Python 简易服务器
cd web && python -m http.server 8000

# 访问 http://localhost:8000
```

---

## ☁️ 部署到 Cloudflare Pages

### 方法 1: 通过 Cloudflare Dashboard（推荐）

1. **登录** [Cloudflare Dashboard](https://dash.cloudflare.com)

2. **进入 Pages** → **Create a project**

3. **选择连接方式**:
   - **Direct Upload** (直接上传) - 适合快速部署
   - **Git Provider** (GitHub/GitLab) - 适合持续集成

#### 直接上传步骤:

```bash
# 安装 Wrangler CLI
npm install -g wrangler

# 登录 Cloudflare
wrangler login

# 部署项目
cd /userdata/hermes/profiles/skill-dev/projects/skill-registry-site
wrangler pages deploy web --project-name=hermes-skill-registry
```

#### Git 集成步骤:

1. 将项目推送到 GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-user/hermes-skill-registry.git
git push -u origin main
```

2. 在 Cloudflare Dashboard:
   - 选择 **Git Provider**
   - 选择你的 GitHub repo
   - 设置:
     - **Production branch**: `main`
     - **Build command**: `python scripts/sync-skills.py && python scripts/build-site.py`
     - **Build output directory**: `web`
   - 点击 **Save and Deploy**

### 方法 2: 使用 GitHub Actions 自动部署

创建 `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloudflare Pages

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 */6 * * *'  # 每 6 小时自动同步

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Sync skills
        run: python scripts/sync-skills.py
      
      - name: Build site
        run: python scripts/build-site.py
      
      - name: Deploy to Cloudflare Pages
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          command: pages deploy web --project-name=hermes-skill-registry
```

---

## 📁 项目结构

```
skill-registry-site/
├── core/                    # 核心数据
│   └── skills/              # 技能元数据 JSON
│       ├── index.json       # 总索引
│       ├── arxiv.json
│       └── ...
│
├── web/                     # 生成的网站
│   ├── index.html           # 首页
│   ├── skills/              # 技能详情页
│   └── api/                 # API 端点（未来）
│
├── scripts/                 # 构建脚本
│   ├── sync-skills.py       # 同步技能元数据
│   └── build-site.py        # 生成静态网站
│
├── blog/                    # 开发博客（独立）
│   └── posts/
│
├── site-config.json         # 站点配置
├── wrangler.toml            # Cloudflare 配置
└── README.md                # 本文件
```

---

## 🔄 自动更新

### 本地定时任务

编辑 cron 任务，每 6 小时自动同步：

```bash
hermes cron create skill-registry-sync
# Schedule: 0 */6 * * *
# Prompt: 运行 sync-skills.py 和 build-site.py，然后部署
```

### GitHub Actions

使用上面的 workflow 文件，每次 push 或定时触发构建。

---

## 📈 功能特性

### ✅ 已实现
- [x] 扫描本地 SKILL.md 文件
- [x] 提取 frontmatter 元数据
- [x] 生成 JSON 索引
- [x] 静态网站生成
- [x] 搜索功能
- [x] 分类筛选
- [x] 技能详情页
- [x] 响应式设计

### 🔜 规划中
- [ ] 从 GitHub 自动同步
- [ ] 用户评分和评论
- [ ] 技能包（Bundles）
- [ ] 安装 API (`/api/v1/skills/<name>`)
- [ ] 下载统计
- [ ] 热门标签云
- [ ] 最近更新列表
- [ ] RSS 订阅

---

## 🤝 贡献

### 添加新技能源

编辑 `site-config.json`:

```json
{
  "source_skills": [
    {
      "type": "local",
      "path": "/path/to/your/skills"
    },
    {
      "type": "github",
      "org": "NousResearch",
      "repo": "hermes-agent"
    }
  ]
}
```

### 提交技能

1. 确保你的技能有完整的 `SKILL.md`
2. 包含 frontmatter（name, category, description）
3. 提交 PR 或手动添加到技能源目录

---

## 📝 许可证

MIT License - 开源项目

---

## 📞 联系方式

- **项目地址**: `/userdata/hermes/profiles/skill-dev/projects/skill-registry-site`
- **在线文档**: skills.airs.ltd (部署后)
- **问题反馈**: 在 Hermes Discord 社区提问

---

**构建时间**: 2026-06-06  
**版本**: 1.0.0