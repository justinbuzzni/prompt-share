#!/usr/bin/env python
"""
Debug script to show what's being extracted from Git configs
"""
import sys
from pathlib import Path

sys.path.append('/Users/namsangboy/workspace/prompt-share')
from claude_sync import ClaudeSyncManager, get_project_path_from_sessions, decode_project_path

def main():
    claude_dir = Path.home() / '.claude'
    projects_dir = claude_dir / 'projects'
    
    if not projects_dir.exists():
        print("No projects directory found")
        return
    
    manager = ClaudeSyncManager()
    
    print("Debugging Git config extraction:")
    print("=" * 60)
    
    # Sample some project paths to see what's happening
    count = 0
    for project_dir in sorted(projects_dir.iterdir()):
        if not project_dir.is_dir() or count >= 20:
            continue
        
        try:
            project_path = get_project_path_from_sessions(project_dir)
            if not project_path:
                project_path = decode_project_path(project_dir.name)
            
            # Get both git config and fallback results
            git_owner, git_repo = manager.extract_repo_info_from_git_config(project_path)
            final_owner, final_repo = manager.extract_repo_info(project_path)
            
            print(f"\nPath: {project_path}")
            print(f"  Git config result: owner={git_owner}, repo={git_repo}")
            print(f"  Final result: owner={final_owner}, repo={final_repo}")
            
            # If there's a difference, explain why
            if git_owner != final_owner:
                print(f"  -> Using fallback extraction (no git config found)")
            
            count += 1
            
        except Exception as e:
            print(f"\nError processing {project_dir.name}: {e}")
            continue

if __name__ == "__main__":
    main()