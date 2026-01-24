"""
🧠 SKILL LOADER
===============
Auto-discover and load skills from .agent/skills/

Features:
- Discovers all SKILL.md files
- Parses YAML frontmatter
- Indexes by name and category
- Provides search and filtering
"""

import os
import yaml
from pathlib import Path
from typing import List, Dict, Optional


class SkillLoader:
    """Auto-discover and load skills from .agent/skills/"""
    
    def __init__(self, skills_dir: str = ".agent/skills"):
        self.skills_dir = Path(skills_dir)
        self.skills: Dict[str, Dict] = {}
        self.categories: Dict[str, List[str]] = {}
    
    def discover_skills(self) -> List[Dict]:
        """Discover all SKILL.md files"""
        skills = []
        
        if not self.skills_dir.exists():
            print(f"⚠️  Skills directory not found: {self.skills_dir}")
            return skills
        
        for skill_path in self.skills_dir.rglob("SKILL.md"):
            skill_data = self._parse_skill(skill_path)
            if skill_data:
                skills.append(skill_data)
                self.skills[skill_data['name']] = skill_data
                
                # Index by category
                category = skill_data.get('category', 'uncategorized')
                if category not in self.categories:
                    self.categories[category] = []
                self.categories[category].append(skill_data['name'])
        
        return skills
    
    def _parse_skill(self, skill_path: Path) -> Optional[Dict]:
        """Parse SKILL.md frontmatter and content"""
        try:
            with open(skill_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse YAML frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    metadata = yaml.safe_load(parts[1])
                    body = parts[2].strip()
                    
                    return {
                        'name': metadata.get('name', skill_path.parent.name),
                        'description': metadata.get('description', ''),
                        'path': str(skill_path.parent),
                        'content': body,
                        'metadata': metadata,
                        'category': self._infer_category(skill_path.parent.name)
                    }
            
            # Fallback: no frontmatter
            return {
                'name': skill_path.parent.name,
                'description': content[:200],
                'path': str(skill_path.parent),
                'content': content,
                'metadata': {},
                'category': 'uncategorized'
            }
            
        except Exception as e:
            print(f"⚠️  Error parsing {skill_path}: {e}")
            return None
    
    def _infer_category(self, skill_name: str) -> str:
        """Infer category from skill name"""
        categories = {
            'ai-agents': ['langgraph', 'crewai', 'agent', 'autonomous', 'voice-agents'],
            'development': ['react', 'frontend', 'backend', 'fullstack', 'tdd', 'debug'],
            'security': ['pentest', 'security', 'exploit', 'vulnerability', 'hacking'],
            'design': ['ui-ux', 'design', 'canvas', 'art', 'theme'],
            'integrations': ['stripe', 'firebase', 'supabase', 'clerk', 'discord', 'slack'],
            'infrastructure': ['docker', 'aws', 'gcp', 'azure', 'serverless', 'devops'],
            'testing': ['test', 'playwright', 'qa', 'webapp-testing'],
            'workflow': ['plan', 'brainstorm', 'orchestrate', 'loki-mode'],
        }
        
        skill_lower = skill_name.lower()
        for category, keywords in categories.items():
            if any(keyword in skill_lower for keyword in keywords):
                return category
        
        return 'other'
    
    def get_skill(self, name: str) -> Optional[Dict]:
        """Get a specific skill by name"""
        return self.skills.get(name)
    
    def get_skills_by_category(self, category: str) -> List[Dict]:
        """Get all skills in a category"""
        skill_names = self.categories.get(category, [])
        return [self.skills[name] for name in skill_names if name in self.skills]
    
    def search_skills(self, query: str) -> List[Dict]:
        """Search skills by name or description"""
        query_lower = query.lower()
        results = []
        
        for skill in self.skills.values():
            if (query_lower in skill['name'].lower() or 
                query_lower in skill['description'].lower()):
                results.append(skill)
        
        return results
    
    def get_stats(self) -> Dict:
        """Get statistics about loaded skills"""
        return {
            'total_skills': len(self.skills),
            'categories': {cat: len(skills) for cat, skills in self.categories.items()},
            'top_categories': sorted(
                self.categories.items(), 
                key=lambda x: len(x[1]), 
                reverse=True
            )[:5]
        }
    
    def print_summary(self):
        """Print a summary of loaded skills"""
        stats = self.get_stats()
        
        print(f"\n{'='*60}")
        print(f"🧠 SKILL LOADER SUMMARY")
        print(f"{'='*60}")
        print(f"\n✅ Total Skills: {stats['total_skills']}")
        print(f"\n📊 Top Categories:")
        for category, skills in stats['top_categories']:
            print(f"   - {category}: {len(skills)} skills")
        print(f"\n{'='*60}\n")


if __name__ == "__main__":
    # Test the skill loader
    loader = SkillLoader()
    skills = loader.discover_skills()
    loader.print_summary()
    
    # Show some examples
    print("📚 Sample Skills:")
    for skill in list(loader.skills.values())[:10]:
        print(f"   - {skill['name']}: {skill['description'][:60]}...")
    
    # Test search
    print(f"\n🔍 Search for 'agent':")
    results = loader.search_skills('agent')
    for result in results[:5]:
        print(f"   - {result['name']}")
