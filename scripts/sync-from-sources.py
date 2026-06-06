#!/usr/bin/env python3
"""
从 GitHub 等源同步技能元数据
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "../site-config.json")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "../skills")

def load_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def sync_github_org(org_config):
    """同步 GitHub 组织的技能"""
    org = org_config["org"]
    repos = org_config.get("repos", [])
    skill_path = org_config.get("skill_path", "skills/")
    
    print(f"🔍 同步组织：{org}")
    print(f"   Repos: {', '.join(repos)}")
    print(f"   Skill Path: {skill_path}")
    
    skills = []
    
    for repo in repos:
        print(f"\n📦 扫描 Repo: {repo}")
        # TODO: 调用 GitHub API 扫描技能
        # 1. 获取 repo 内容
        # 2. 解析技能目录
        # 3. 提取 SKILL.md frontmatter
        # 4. 生成技能元数据
        
        # 示例：模拟数据
        mock_skill = {
            "skill_id": f"example-from-{repo}",
            "name": f"example-{repo}",
            "version": "1.0.0",
            "source": {
                "type": "github",
                "repo": f"{org}/{repo}",
                "path": skill_path
            }
        }
        skills.append(mock_skill)
    
    return skills

def validate_skill(skill_data):
    """验证技能是否符合质量标准"""
    # TODO: 实现验证逻辑
    # - 检查是否有 SKILL.md
    # - 检查文档完整性
    # - 检查代码质量
    # - 检查最后更新时间
    
    # 当前：全部通过
    return True

def save_skill(skill_data):
    """保存技能元数据"""
    category = skill_data.get("category", "uncategorized")
    category_dir = os.path.join(OUTPUT_DIR, category)
    os.makedirs(category_dir, exist_ok=True)
    
    skill_file = os.path.join(category_dir, f"{skill_data['skill_id']}.json")
    
    # 添加记录时间
    skill_data["indexed_at"] = datetime.now().isoformat()
    
    with open(skill_file, 'w', encoding='utf-8') as f:
        json.dump(skill_data, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ 保存：{skill_file}")

def build_index():
    """构建总索引"""
    print("\n📝 构建索引...")
    
    index = {
        "version": "1.0.0",
        "built_at": datetime.now().isoformat(),
        "total_skills": 0,
        "categories": {},
        "skills": []
    }
    
    # 扫描所有技能
    for root, dirs, files in os.walk(OUTPUT_DIR):
        for file in files:
            if file.endswith(".json"):
                skill_file = os.path.join(root, file)
                with open(skill_file, 'r', encoding='utf-8') as f:
                    skill = json.load(f)
                
                index["skills"].append(skill)
                
                # 统计分类
                category = skill.get("category", "uncategorized")
                if category not in index["categories"]:
                    index["categories"][category] = 0
                index["categories"][category] += 1
    
    index["total_skills"] = len(index["skills"])
    
    # 保存索引
    index_file = os.path.join(OUTPUT_DIR, "../index.json")
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 索引已保存：{index_file}")
    print(f"   总技能数：{index['total_skills']}")
    print(f"   分类数：{len(index['categories'])}")
    
    return index

def main():
    print("="*60)
    print("🚀 技能同步工具")
    print("="*60)
    
    config = load_config()
    
    all_skills = []
    
    # 同步每个源
    for source in config.get("content_sources", []):
        if source["type"] == "github":
            skills = sync_github_org(source)
            
            # 验证和保存
            for skill in skills:
                if validate_skill(skill):
                    save_skill(skill)
                    all_skills.append(skill)
                else:
                    print(f"  ⚠️  跳过：{skill['skill_id']} (验证失败)")
    
    # 构建索引
    if all_skills:
        build_index()
    else:
        print("\n⚠️  未找到技能")
    
    print("\n" + "="*60)
    print("✅ 同步完成!")
    print("="*60)

if __name__ == "__main__":
    main()
