#!/usr/bin/env python3
"""
Build Site - 从技能元数据生成静态网站
读取 core/skills/index.json，生成 HTML 页面
"""

import json
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(__file__).parent.parent
CORE_DIR = PROJECT_DIR / "core"
SKILLS_DIR = CORE_DIR / "skills"
WEB_DIR = PROJECT_DIR / "web"
WEB_SKILLS_DIR = WEB_DIR / "skills"

# 确保输出目录存在
WEB_SKILLS_DIR.mkdir(parents=True, exist_ok=True)

# 加载索引
index_file = SKILLS_DIR / "index.json"
if not index_file.exists():
    print("❌ 错误：未找到技能索引文件")
    print("请先运行：python scripts/sync-skills.py")
    exit(1)

with open(index_file, 'r', encoding='utf-8') as f:
    index_data = json.load(f)

print(f"📊 加载了 {index_data['total_skills']} 个技能")

def generate_homepage():
    """生成首页"""
    skills = index_data['skills']
    categories = index_data['categories']
    
    # 生成技能卡片 HTML
    skills_html = ""
    for name, skill in sorted(skills.items()):
        card = f"""
        <div class="skill-card" data-name="{skill['name'].lower()}" data-category="{skill['category']}">
            <h3><a href="skills/{skill['name']}.html">{skill['display_name']}</a></h3>
            <p class="description">{skill['description'][:120]}...</p>
            <div class="meta">
                <span class="category">{skill['category']}</span>
                <span class="version">v{skill['version']}</span>
            </div>
        </div>
        """
        skills_html += card
    
    # 生成分类标签
    categories_html = ""
    for cat, names in sorted(categories.items()):
        categories_html += f'<button class="category-btn" data-category="{cat}">{cat} ({len(names)})</button>'
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hermes Skill Registry - 发现和安装优质技能</title>
    <style>
        :root {{
            --bg-primary: #0f0f0f;
            --bg-secondary: #1a1a1a;
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
            --accent: #00d4ff;
            --border: #333;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        header {{
            background: var(--bg-secondary);
            padding: 40px 20px;
            border-bottom: 1px solid var(--border);
        }}
        h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .subtitle {{ color: var(--text-secondary); font-size: 1.1em; }}
        .stats {{
            display: flex;
            gap: 20px;
            margin-top: 20px;
        }}
        .stat {{
            background: var(--bg-primary);
            padding: 15px 25px;
            border-radius: 8px;
            border: 1px solid var(--border);
        }}
        .stat-value {{ font-size: 2em; font-weight: bold; color: var(--accent); }}
        .stat-label {{ color: var(--text-secondary); font-size: 0.9em; }}
        .search-section {{
            padding: 30px 20px;
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
        }}
        #search {{
            width: 100%;
            max-width: 600px;
            padding: 15px 20px;
            font-size: 1.1em;
            background: var(--bg-primary);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-primary);
        }}
        #search:focus {{ outline: 2px solid var(--accent); }}
        .categories {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 20px;
        }}
        .category-btn {{
            padding: 8px 16px;
            background: var(--bg-primary);
            border: 1px solid var(--border);
            border-radius: 20px;
            color: var(--text-primary);
            cursor: pointer;
            transition: all 0.2s;
        }}
        .category-btn:hover, .category-btn.active {{
            background: var(--accent);
            border-color: var(--accent);
            color: #000;
        }}
        .skills-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            padding: 30px 0;
        }}
        .skill-card {{
            background: var(--bg-secondary);
            padding: 25px;
            border-radius: 12px;
            border: 1px solid var(--border);
            transition: transform 0.2s, border-color 0.2s;
        }}
        .skill-card:hover {{
            transform: translateY(-3px);
            border-color: var(--accent);
        }}
        .skill-card h3 a {{
            color: var(--text-primary);
            text-decoration: none;
        }}
        .skill-card h3 a:hover {{ color: var(--accent); }}
        .description {{
            color: var(--text-secondary);
            margin: 15px 0;
            font-size: 0.95em;
        }}
        .meta {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .category, .version {{
            padding: 4px 12px;
            background: var(--bg-primary);
            border-radius: 12px;
            font-size: 0.85em;
            color: var(--text-secondary);
        }}
        footer {{
            text-align: center;
            padding: 40px 20px;
            border-top: 1px solid var(--border);
            color: var(--text-secondary);
        }}
        @media (max-width: 768px) {{
            .skills-grid {{ grid-template-columns: 1fr; }}
        }}
        .no-results {{
            text-align: center;
            padding: 60px 20px;
            color: var(--text-secondary);
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>🚀 Hermes Skill Registry</h1>
            <p class="subtitle">发现和安装优质的 Hermes Agent 技能</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{index_data['total_skills']}</div>
                    <div class="stat-label">总技能数</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{len(categories)}</div>
                    <div class="stat-label">分类</div>
                </div>
            </div>
        </div>
    </header>

    <div class="search-section">
        <div class="container">
            <input type="text" id="search" placeholder="🔍 搜索技能名称或描述...">
            <div class="categories" id="categories">
                <button class="category-btn active" data-category="all">全部 ({index_data['total_skills']})</button>
                {categories_html}
            </div>
        </div>
    </div>

    <main class="container">
        <div class="skills-grid" id="skills-grid">
            {skills_html}
        </div>
        <div class="no-results" id="no-results" style="display: none;">
            😕 未找到匹配的技能
        </div>
    </main>

    <footer>
        <p>Hermes Skill Registry &copy; 2026</p>
        <p>Powered by Cloudflare Pages</p>
    </footer>

    <script>
        // 搜索功能
        const searchInput = document.getElementById('search');
        const skillsGrid = document.getElementById('skills-grid');
        const noResults = document.getElementById('no-results');
        const cards = Array.from(document.querySelectorAll('.skill-card'));
        
        searchInput.addEventListener('input', (e) => {{
            const query = e.target.value.toLowerCase().trim();
            let visibleCount = 0;
            
            cards.forEach(card => {{
                const name = card.dataset.name;
                const desc = card.querySelector('.description').textContent.toLowerCase();
                const matches = name.includes(query) || desc.includes(query);
                card.style.display = matches ? 'block' : 'none';
                if (matches) visibleCount++;
            }});
            
            skillsGrid.style.display = visibleCount > 0 ? 'grid' : 'none';
            noResults.style.display = visibleCount > 0 ? 'none' : 'block';
        }});
        
        // 分类筛选
        const categoryBtns = document.querySelectorAll('.category-btn');
        categoryBtns.forEach(btn => {{
            btn.addEventListener('click', () => {{
                categoryBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                const category = btn.dataset.category;
                if (category === 'all') {{
                    cards.forEach(card => card.style.display = 'block');
                }} else {{
                    cards.forEach(card => {{
                        card.style.display = card.dataset.category === category ? 'block' : 'none';
                    }});
                }}
            }});
        }});
    </script>
</body>
</html>
"""
    
    output_file = WEB_DIR / "index.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ 生成首页：{output_file}")

def generate_skill_pages():
    """生成所有技能详情页"""
    skills = index_data['skills']
    
    for name, skill in skills.items():
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{skill['display_name']} - Hermes Skill Registry</title>
    <style>
        :root {{
            --bg-primary: #0f0f0f;
            --bg-secondary: #1a1a1a;
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
            --accent: #00d4ff;
            --border: #333;
            --success: #00ff88;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
        header {{
            background: var(--bg-secondary);
            padding: 30px 20px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 40px;
        }}
        h1 {{ font-size: 2em; margin-bottom: 10px; }}
        .version {{ color: var(--text-secondary); font-size: 0.9em; }}
        .breadcrumb {{
            color: var(--text-secondary);
            margin-bottom: 15px;
        }}
        .breadcrumb a {{ color: var(--accent); text-decoration: none; }}
        .content {{ background: var(--bg-secondary); padding: 30px; border-radius: 12px; border: 1px solid var(--border); }}
        .description {{ font-size: 1.1em; margin-bottom: 25px; }}
        .meta-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .meta-item {{
            background: var(--bg-primary);
            padding: 15px;
            border-radius: 8px;
            border: 1px solid var(--border);
        }}
        .meta-label {{ color: var(--text-secondary); font-size: 0.85em; margin-bottom: 5px; }}
        .meta-value {{ font-weight: 600; }}
        .install-section {{
            background: var(--bg-primary);
            padding: 20px;
            border-radius: 8px;
            border: 1px solid var(--border);
            margin-bottom: 25px;
        }}
        .install-command {{
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }}
        code {{
            background: #000;
            padding: 12px 15px;
            border-radius: 6px;
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 0.95em;
            color: var(--success);
            flex-grow: 1;
        }}
        .copy-btn {{
            padding: 10px 20px;
            background: var(--accent);
            border: none;
            border-radius: 6px;
            color: #000;
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.2s;
        }}
        .copy-btn:hover {{ opacity: 0.8; }}
        .tags {{ display: flex; gap: 8px; flex-wrap: wrap; }}
        .tag {{
            padding: 6px 14px;
            background: var(--bg-primary);
            border: 1px solid var(--border);
            border-radius: 16px;
            font-size: 0.9em;
            color: var(--text-secondary);
        }}
        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            color: var(--accent);
            text-decoration: none;
        }}
        .back-link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <a href="../index.html" class="back-link">← 返回首页</a>
        
        <header>
            <div class="breadcrumb">
                <a href="../index.html">首页</a> / 
                <a href="../index.html#category-{skill['category']}">{skill['category']}</a> / 
                {skill['display_name']}
            </div>
            <h1>{skill['display_name']}</h1>
            <p class="version">版本 {skill['version']} • 作者：{skill['author']}</p>
        </header>
        
        <div class="content">
            <p class="description">{skill['description']}</p>
            
            <div class="install-section">
                <h3>📥 安装命令</h3>
                <div class="install-command">
                    <code>hermes skill install {skill['name']}</code>
                    <button class="copy-btn" onclick="navigator.clipboard.writeText('hermes skill install {skill['name']}')">复制</button>
                </div>
            </div>
            
            <div class="meta-section">
                <div class="meta-item">
                    <div class="meta-label">分类</div>
                    <div class="meta-value">{skill['category']}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">版本</div>
                    <div class="meta-value">{skill['version']}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">作者</div>
                    <div class="meta-value">{skill['author']}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">同步时间</div>
                    <div class="meta-value">{skill['synced_at'][:10]}</div>
                </div>
            </div>
            
            <h3 style="margin-bottom: 15px;">🏷️ 标签</h3>
            <div class="tags">
                {"".join(f'<span class="tag">{tag}</span>' for tag in skill.get('tags', ['无标签']))}
            </div>
        </div>
    </div>
</body>
</html>
"""
        
        output_file = WEB_SKILLS_DIR / f"{name}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
    
    print(f"✓ 生成 {len(skills)} 个技能详情页")

# 执行构建
print("🏗️ 开始构建网站...")
generate_homepage()
generate_skill_pages()
print("\n✅ 网站构建完成!")
print(f"📁 输出目录：{WEB_DIR}")
