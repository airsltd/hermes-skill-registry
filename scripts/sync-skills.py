#!/usr/bin/env python3
"""
Sync Skills - 从源代码同步技能元数据到 core/skills/
递归扫描指定目录，提取 SKILL.md frontmatter，生成 JSON 索引
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(__file__).parent.parent
CORE_DIR = PROJECT_DIR / "core"
SKILLS_DIR = CORE_DIR / "skills"

# 确保输出目录存在
SKILLS_DIR.mkdir(parents=True, exist_ok=True)

def extract_frontmatter(content):
    """提取 YAML frontmatter (简化版)"""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
    if not match:
        return None
    
    data = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            # 处理数组
            if value.startswith('[') and value.endswith(']'):
                items = value[1:-1].split(',')
                data[key] = [item.strip().strip('"\'') for item in items if item.strip()]
            # 处理布尔值
            elif value.lower() == 'true':
                data[key] = True
            elif value.lower() == 'false':
                data[key] = False
            # 处理数字
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
        
        # 构建技能元数据
        skill_meta = {
            "name": frontmatter.get('name', skill_path.name),
            "display_name": frontmatter.get('display_name', frontmatter.get('name', skill_path.name)),
            "version": frontmatter.get('version', '1.0.0'),
            "category": frontmatter.get('category', 'uncategorized'),
            "description": frontmatter.get('description', ''),
            "trigger": frontmatter.get('trigger', ''),
            "tags": frontmatter.get('tags', []),
            "author": frontmatter.get('author', 'Unknown'),
            "created": frontmatter.get('created', datetime.now().strftime('%Y-%m-%d')),
            "source_path": str(skill_path.relative_to(PROJECT_DIR.parent.parent)),
            "synced_at": datetime.now().isoformat(),
            "readme_available": (skill_path / "README.md").exists(),
            "has_tests": (skill_path / "tests").exists(),
            "has_scripts": (skill_path / "scripts").exists()
        }
        
        return skill_meta
        
    except Exception as e:
        return None

def scan_directory_recursive(base_path, max_depth=3):
    """递归扫描目录查找技能"""
    skills = []
    
    def scan_level(current_path, depth):
        if depth > max_depth:
            return
        
        for item in current_path.iterdir():
            if not item.is_dir():
                continue
            
            if item.name.startswith('.') or item.name in ['__pycache__', 'node_modules']:
                continue
            
            # 尝试扫描当前目录作为技能
            skill_meta = scan_skill_directory(item)
            if skill_meta:
                skills.append(skill_meta)
            
            # 递归扫描子目录
            scan_level(item, depth + 1)
    
    scan_level(base_path, 0)
    return skills

def sync_all_skills():
    """同步所有技能源"""
    # 加载配置
    config_file = PROJECT_DIR / "site-config.json"
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("🔍 开始同步技能...")
    print(f"📂 输出目录：{SKILLS_DIR}")
    
    all_skills = []
    
    # 扫描所有配置的源
    for source in config.get('source_skills', []):
        source_path = Path(source['path'])
        
        if not source_path.exists():
            print(f"\n⚠️  源不存在：{source_path}")
            continue
        
        print(f"\n📂 扫描源：{source_path}")
        
        # 递归扫描技能（深度 3：skills/category/name/）
        skills_found = scan_directory_recursive(source_path, max_depth=3)
        
        for skill_meta in skills_found:
            all_skills.append(skill_meta)
            
            # 保存单个技能 JSON
            output_file = SKILLS_DIR / f"{skill_meta['name']}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(skill_meta, f, indent=2, ensure_ascii=False)
            
            print(f"  ✓ {skill_meta['name']} ({skill_meta['category']})")
    
    # 生成总索引
    index_file = SKILLS_DIR / "index.json"
    index_data = {
        "generated_at": datetime.now().isoformat(),
        "total_skills": len(all_skills),
        "categories": {},
        "skills": {}
    }
    
    # 按分类统计
    for skill in all_skills:
        cat = skill['category']
        if cat not in index_data['categories']:
            index_data['categories'][cat] = []
        index_data['categories'][cat].append(skill['name'])
        index_data['skills'][skill['name']] = skill
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"✅ 同步完成!")
    print(f"📊 总技能数：{len(all_skills)}")
    print(f"📂 分类数：{len(index_data['categories'])}")
    print(f"📁 索引文件：{index_file}")
    
    # 显示分类统计
    print(f"\n📂 分类统计:")
    for cat, skills in sorted(index_data['categories'].items()):
        print(f"  {cat}: {len(skills)} 个")
    
    return all_skills

if __name__ == "__main__":
    sync_all_skills()
