#!/usr/bin/env python
"""
Test script to show repository owner mapping
"""
import sys
from pathlib import Path
from collections import defaultdict

sys.path.append('/Users/namsangboy/workspace/prompt-share')
from claude_sync import ClaudeSyncManager, get_project_path_from_sessions, decode_project_path

def main():
    claude_dir = Path.home() / '.claude'
    projects_dir = claude_dir / 'projects'
    
    if not projects_dir.exists():
        print("No projects directory found")
        return
    
    manager = ClaudeSyncManager()
    owner_to_repos = defaultdict(set)
    repo_to_owner = {}
    
    print("Analyzing repository ownership...")
    print("=" * 60)
    
    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue
        
        try:
            project_path = get_project_path_from_sessions(project_dir)
            if not project_path:
                project_path = decode_project_path(project_dir.name)
            
            owner, repo = manager.extract_repo_info(project_path)
            
            if owner and repo:
                owner_to_repos[owner].add(repo)
                if repo not in repo_to_owner or owner != 'None':
                    repo_to_owner[repo] = owner
        except Exception:
            continue
    
    # Display results
    print("\nRepository Owners and their Repositories:")
    print("-" * 60)
    
    for owner in sorted(owner_to_repos.keys()):
        repos = sorted(owner_to_repos[owner])
        print(f"\n{owner}:")
        for repo in repos:
            print(f"  - {repo}")
    
    # Show repos without owners
    no_owner_repos = [repo for repo, owner in repo_to_owner.items() if owner is None]
    if no_owner_repos:
        print("\nRepositories without identified owners:")
        for repo in sorted(no_owner_repos):
            print(f"  - {repo}")

if __name__ == "__main__":
    main()