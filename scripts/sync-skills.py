#!/usr/bin/env python3
"""
Sync Skills - 从 GitHub 同步技能元数据
扫描指定的 GitHub repo，提取 SKILL.md frontmatter，生成 JSON 索引
"""

import os
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(__file__).parent.parent
CORE_DIR = PROJECT_DIR / "core"
SKILLS_DIR = CORE_DIR / "skills"
TEMP_GITHUB_DIR = PROJECT_DIR / ".github-temp"

# 确保输出目录存在
SKILLS_DIR.mkdir(parents=True, exist_ok=True)

def extract_frontmatter(content):
    """提取 YAML frontmatter"""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
    if not match:
        return None
    
    data = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if value.startswith('[') and value.endswith(']'):
                items = value[1:-1].split(',')
                data[key] = [item.strip().strip('"\'') for item in items if item.strip()]
            elif value.lower() == 'true':
                data[key] = True
            elif value.lower() == 'false':
                data[key] = False
            elif value.isdigit():
                data[key] = int(value)
            else:
                data[key] = value.strip('"\'')
    
    return data

def scan_skill_directory(skill_path):
    """扫描单个技能目录"""
    skill_file = skill_path / "SKILL.md"
    if not skill_file.exists():
        return None
    
    try:
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter = extract_frontmatter(content)
        if not frontmatter:
            return None
        
        skill_meta = {
            "name": frontmatter.get('name', skill_path.name),
            "display_name": frontmatter.get('display_name', frontmatter.get('name', skill_path.name)),
            "version": frontmatter.get('version', '1.0.0'),
            "category": frontmatter.get('category', 'uncategorized'),
            "description": frontmatter.get('description', ''),
            "trigger": frontmatter.get('trigger', ''),
            "tags": frontmatter.get('tags', []),
            "author": frontmatter.get('author', 'Unknown'),
            "synced_at": datetime.now().isoformat()
        }
        
        return skill_meta
    except:
        return None

def clone_github_repo(org, repo, skill_path):
    """克隆 GitHub repo 到临时目录"""
    if TEMP_GITHUB_DIR.exists():
        subprocess.run(["rm", "-rf", str(TEMP_GITHUB_DIR)], check=True)
    
    url = f"https://github.com/{org}/{repo}.git"
    print(f"  📥 克隆 {org}/{repo}...")
    
    result = subprocess.run(
        ["git", "clone", "--depth=1", "--filter=blob:none", "--sparse", url, str(TEMP_GITHUB_DIR)],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"  ✗ 克隆失败：{result.stderr}")
        return None
    
    # 只 checkout skills 目录
    subprocess.run(
        ["git", "-C", str(TEMP_GITHUB_DIR), "sparse-checkout", "set", skill_path],
        capture_output=True
    )
    
    return TEMP_GITHUB_DIR / skill_path

def scan_level(base_path, depth, max_depth):
    """递归扫描目录"""
    if depth > max_depth:
        return []
    
    skills = []
    for item in base_path.iterdir():
        if not item.is_dir() or item.name.startswith('.'):
            continue
        
        skill_meta = scan_skill_directory(item)
        if skill_meta:
            skills.append(skill_meta)
        
        skills.extend(scan_level(item, depth + 1, max_depth))
    
    return skills

def sync_all_skills():
    """同步所有技能源"""
    config_file = PROJECT_DIR / "site-config.json"
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("🔍 开始同步技能...\n")
    all_skills = []
    
    for source in config.get('source_skills', []):
        source_type = source.get('type', 'local')
        
        if source_type == 'github':
            org = source.get('org')
            repo = source.get('repo')
            skill_path = source.get('path', 'skills/')
            
            if not org or not repo:
                print(f"⚠️  GitHub 源配置不完整：{source}")
                continue
            
            # 克隆 repo
            github_dir = clone_github_repo(org, repo, skill_path)
            if not github_dir:
                continue
            
            # 扫描技能
            print(f"  📂 扫描：{skill_path}")
            skills_found = scan_level(github_dir, 0, 2)
            
            for skill_meta in skills_found:
                all_skills.append(skill_meta)
                output_file = SKILLS_DIR / f"{skill_meta['name']}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(skill_meta, f, indent=2, ensure_ascii=False)
                print(f"    ✓ {skill_meta['name']} ({skill_meta['category']})")
            
            # 清理临时目录
            subprocess.run(["rm", "-rf", str(TEMP_GITHUB_DIR)], check=True)
        
        elif source_type == 'local':
            source_path = Path(source['path'])
            if not source_path.exists():
                print(f"⚠️  本地源不存在：{source_path}")
                continue
            
            print(f"📂 扫描本地源：{source_path}")
            skills_found = scan_level(source_path, 0, 3)
            
            for skill_meta in skills_found:
                all_skills.append(skill_meta)
                output_file = SKILLS_DIR / f"{skill_meta['name']}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(skill_meta, f, indent=2, ensure_ascii=False)
                print(f"  ✓ {skill_meta['name']} ({skill_meta['category']})")
    
    # 生成索引
    index_data = {
        "generated_at": datetime.now().isoformat(),
        "total_skills": len(all_skills),
        "categories": {},
        "skills": {}
    }
    
    for skill in all_skills:
        cat = skill['category']
        if cat not in index_data['categories']:
            index_data['categories'][cat] = []
        index_data['categories'][cat].append(skill['name'])
        index_data['skills'][skill['name']] = skill
    
    with open(SKILLS_DIR / "index.json", 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"✅ 同步完成！共 {len(all_skills)} 个技能，{len(index_data['categories'])} 个分类")
    
    if index_data['categories']:
        print(f"\n分类统计:")
        for cat, names in sorted(index_data['categories'].items()):
            print(f"  {cat}: {len(names)} 个")
    
    return all_skills

if __name__ == "__main__":
    sync_all_skills()