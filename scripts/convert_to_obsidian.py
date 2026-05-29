#!/usr/bin/env python3
"""
Convert Claude data export to Obsidian vault structure.

Organizes data by type and relevance:
- User profile
- Memory/context
- Projects
- Conversations (grouped by topic/theme)
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List
from collections import defaultdict


def sanitize_filename(name: str, max_length: int = 100) -> str:
    """Convert a string into a safe filename."""
    # Remove or replace unsafe characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = re.sub(r'\s+', '-', name.strip())
    # Remove leading/trailing dashes
    name = name.strip('-')
    # Limit length
    if len(name) > max_length:
        name = name[:max_length].rstrip('-')
    return name or "untitled"


def format_date(date_str: str) -> str:
    """Format ISO date string to readable format."""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return date_str


def create_user_profile(data: List[Dict], vault_path: Path) -> None:
    """Create user profile markdown."""
    profile_dir = vault_path / "1-Profile"
    profile_dir.mkdir(parents=True, exist_ok=True)

    if not data:
        return

    user = data[0]
    content = f"""# User Profile

## Identity
- **Name**: {user.get('full_name', 'N/A')}
- **Email**: {user.get('email_address', 'N/A')}
- **Phone**: {user.get('verified_phone_number', 'N/A')}
- **UUID**: `{user.get('uuid', 'N/A')}`

## Quick Links
- [[../2-Memory/Context-Memory|Memory & Context]]
- [[../3-Projects/_Projects-Index|Projects Index]]
- [[../4-Conversations/_Conversations-Index|Conversations Index]]

---
*Generated from Claude data export on {datetime.now().strftime('%Y-%m-%d')}*
"""

    (profile_dir / "User-Profile.md").write_text(content, encoding='utf-8')


def create_memory_docs(data: List[Dict], vault_path: Path) -> None:
    """Create memory/context markdown files."""
    memory_dir = vault_path / "2-Memory"
    memory_dir.mkdir(parents=True, exist_ok=True)

    if not data:
        return

    memory = data[0]
    content = f"""# Context Memory

This is your comprehensive context and memory from Claude conversations.

## Work Context

{memory.get('work_context', 'No work context available.')}

## Personal Context

{memory.get('personal_context', 'No personal context available.')}

## Top of Mind

{memory.get('top_of_mind', 'Nothing currently top of mind.')}

## Brief History

{memory.get('brief_history', 'No history available.')}

## Full Memory Snapshot

{memory.get('conversations_memory', 'No detailed memory available.')}

---

## Quick Links
- [[../1-Profile/User-Profile|Back to Profile]]
- [[../3-Projects/_Projects-Index|View Projects]]
- [[../4-Conversations/_Conversations-Index|View Conversations]]

---
*Last updated from export: {datetime.now().strftime('%Y-%m-%d')}*
"""

    (memory_dir / "Context-Memory.md").write_text(content, encoding='utf-8')


def create_projects(data: List[Dict], vault_path: Path) -> None:
    """Create project markdown files."""
    projects_dir = vault_path / "3-Projects"
    projects_dir.mkdir(parents=True, exist_ok=True)

    # Create index
    index_content = """# Projects Index

All Claude AI projects organized by relevance and category.

## Projects

"""

    for project in data:
        name = project.get('name', 'Untitled Project')
        uuid = project.get('uuid', '')
        description = project.get('description', 'No description')
        is_starter = project.get('is_starter_project', False)
        created = format_date(project.get('created_at', ''))

        filename = sanitize_filename(name)
        index_content += f"- [[{filename}]] {'⭐ (Starter)' if is_starter else ''}\n"
        index_content += f"  - {description}\n"
        index_content += f"  - Created: {created}\n\n"

        # Create individual project file
        project_content = f"""# {name}

{'> ⭐ **Starter Project**' if is_starter else ''}

## Overview

**Description**: {description}

**Created**: {created}
**Updated**: {format_date(project.get('updated_at', ''))}
**UUID**: `{uuid}`
**Private**: {'Yes' if project.get('is_private') else 'No'}

"""

        # Add prompt template if exists
        if project.get('prompt_template'):
            project_content += f"""## Prompt Template

```
{project['prompt_template']}
```

"""

        # Add documentation
        docs = project.get('docs', [])
        if docs:
            project_content += "## Documentation\n\n"
            for doc in docs:
                doc_name = doc.get('filename', 'Untitled')
                doc_content = doc.get('content', '')
                project_content += f"### {doc_name}\n\n{doc_content}\n\n---\n\n"

        project_content += f"""
## Quick Links
- [[_Projects-Index|Back to Projects Index]]
- [[../1-Profile/User-Profile|Profile]]
- [[../2-Memory/Context-Memory|Memory]]

---
*Exported on {datetime.now().strftime('%Y-%m-%d')}*
"""

        (projects_dir / f"{filename}.md").write_text(project_content, encoding='utf-8')

    index_content += f"""
---
**Total Projects**: {len(data)}

[[../0-Index|Back to Main Index]]
"""

    (projects_dir / "_Projects-Index.md").write_text(index_content, encoding='utf-8')


def analyze_conversation_themes(conversations: List[Dict]) -> Dict[str, List[Dict]]:
    """Group conversations by detected themes/topics."""
    themes = defaultdict(list)

    for conv in conversations:
        name = conv.get('name', '').lower()
        summary = conv.get('summary', '').lower()

        # Categorize by keywords
        if any(kw in name or kw in summary for kw in ['workout', 'fitness', 'health', 'training']):
            themes['Health & Fitness'].append(conv)
        elif any(kw in name or kw in summary for kw in ['code', 'python', 'javascript', 'programming', 'web', 'app', 'dev']):
            themes['Development'].append(conv)
        elif any(kw in name or kw in summary for kw in ['write', 'essay', 'article', 'blog', 'content']):
            themes['Writing & Content'].append(conv)
        elif any(kw in name or kw in summary for kw in ['alpha', 'fraternity', 'greek', 'chapter']):
            themes['Greek Life'].append(conv)
        elif any(kw in name or kw in summary for kw in ['trading', 'stock', 'finance', 'market']):
            themes['Trading & Finance'].append(conv)
        elif any(kw in name or kw in summary for kw in ['photo', 'image', 'visual', 'camera']):
            themes['Photography'].append(conv)
        elif any(kw in name or kw in summary for kw in ['robot', 'robolearn', 'capstone', 'project']):
            themes['RoboLearn & Academic'].append(conv)
        else:
            themes['General & Miscellaneous'].append(conv)

    return dict(themes)


def create_conversations(data: List[Dict], vault_path: Path) -> None:
    """Create conversation markdown files organized by theme."""
    conversations_dir = vault_path / "4-Conversations"
    conversations_dir.mkdir(parents=True, exist_ok=True)

    # Filter out empty conversations
    conversations = [c for c in data if c.get('chat_messages')]

    # Group by themes
    themed_conversations = analyze_conversation_themes(conversations)

    # Create index
    index_content = f"""# Conversations Index

All Claude conversations organized by theme and topic.

**Total Conversations**: {len(conversations)}
**Conversations with Messages**: {len(conversations)}

## Themes

"""

    for theme, convs in sorted(themed_conversations.items()):
        index_content += f"\n### {theme} ({len(convs)} conversations)\n\n"

        # Create theme directory
        theme_dir = conversations_dir / sanitize_filename(theme)
        theme_dir.mkdir(exist_ok=True)

        for conv in convs[:50]:  # Limit to 50 per theme to avoid overwhelming
            name = conv.get('name', 'Untitled Conversation')
            if not name:
                name = 'Untitled Conversation'

            uuid = conv.get('uuid', '')
            created = format_date(conv.get('created_at', ''))
            updated = format_date(conv.get('updated_at', ''))
            messages = conv.get('chat_messages', [])

            filename = sanitize_filename(f"{name}_{created[:10]}")
            rel_path = f"{sanitize_filename(theme)}/{filename}"

            index_content += f"- [[{rel_path}|{name}]]\n"
            index_content += f"  - Created: {created} | Messages: {len(messages)}\n"

            # Create conversation file
            conv_content = f"""# {name}

**Created**: {created}
**Updated**: {updated}
**Messages**: {len(messages)}
**UUID**: `{uuid}`

---

## Conversation

"""

            for i, msg in enumerate(messages, 1):
                sender = msg.get('sender', 'unknown')
                text = msg.get('text', '')
                msg_created = format_date(msg.get('created_at', ''))

                sender_label = "👤 **You**" if sender == 'human' else "🤖 **Claude**"

                conv_content += f"""
### Message {i} - {sender_label}
*{msg_created}*

{text}

---

"""

            conv_content += f"""
## Navigation
- [[../_Conversations-Index|Back to Conversations Index]]
- [[../../3-Projects/_Projects-Index|Projects]]
- [[../../2-Memory/Context-Memory|Memory]]

---
*Exported on {datetime.now().strftime('%Y-%m-%d')}*
"""

            (theme_dir / f"{filename}.md").write_text(conv_content, encoding='utf-8')

    index_content += f"""
---

## Navigation
[[../0-Index|Back to Main Index]]

---
*Generated on {datetime.now().strftime('%Y-%m-%d')}*
"""

    (conversations_dir / "_Conversations-Index.md").write_text(index_content, encoding='utf-8')


def create_main_index(vault_path: Path, stats: Dict[str, int]) -> None:
    """Create main vault index/dashboard."""
    content = f"""# Second Brain - Claude Data Export

Welcome to your Obsidian second brain! This vault contains all your Claude conversations, projects, and context organized for easy navigation and knowledge management.

## Quick Navigation

### 📋 Core Sections

1. **[[1-Profile/User-Profile|Your Profile]]** - Personal information and identity
2. **[[2-Memory/Context-Memory|Memory & Context]]** - Your comprehensive context and background
3. **[[3-Projects/_Projects-Index|Projects]]** ({stats['projects']} total) - All Claude AI projects and documentation
4. **[[4-Conversations/_Conversations-Index|Conversations]]** ({stats['conversations']} total) - Organized conversation history

## Statistics

- **Projects**: {stats['projects']}
- **Conversations**: {stats['conversations']}
- **Total Messages**: {stats['messages']}
- **Export Date**: {datetime.now().strftime('%Y-%m-%d')}

## How to Use This Vault

### Navigation
- Use the links above to jump to different sections
- Each section has its own index with detailed navigation
- Use `Ctrl+O` (or `Cmd+O` on Mac) to quick-open any note
- Use `Ctrl+Shift+F` to search across all notes

### Search & Discovery
- Use tags and links to discover related content
- The graph view (`Ctrl+G`) shows connections between notes
- Search for keywords to find relevant conversations and projects

### Tips
- Bookmark frequently accessed notes
- Create your own MOCs (Maps of Content) to organize topics
- Add your own notes and link them to the imported content
- Use Obsidian's daily notes feature to journal alongside this data

---

## Recent Activity

Check the [[4-Conversations/_Conversations-Index|Conversations Index]] to see your most recent interactions organized by theme.

---

*This vault was automatically generated from your Claude data export.*
*Data current as of: 2026-04-02*
"""

    (vault_path / "0-Index.md").write_text(content, encoding='utf-8')


def create_obsidian_config(vault_path: Path) -> None:
    """Create basic Obsidian configuration."""
    obsidian_dir = vault_path / ".obsidian"
    obsidian_dir.mkdir(exist_ok=True)

    # Basic workspace config
    workspace = {
        "main": {
            "id": "main",
            "type": "split",
            "children": [
                {
                    "id": "index",
                    "type": "leaf",
                    "state": {
                        "type": "markdown",
                        "state": {
                            "file": "0-Index.md",
                            "mode": "source"
                        }
                    }
                }
            ]
        },
        "active": "index"
    }

    (obsidian_dir / "workspace.json").write_text(
        json.dumps(workspace, indent=2),
        encoding='utf-8'
    )

    # App config with useful defaults
    app_config = {
        "strictLineBreaks": False,
        "foldHeading": True,
        "foldIndent": True,
        "showLineNumber": False,
        "spellcheck": True,
        "useMarkdownLinks": True,
        "showFrontmatter": True
    }

    (obsidian_dir / "app.json").write_text(
        json.dumps(app_config, indent=2),
        encoding='utf-8'
    )


def main():
    """Main conversion function."""
    # Paths
    data_dir = Path("/Users/eyerise/Downloads/data-2026-04-02-00-45-47-batch-0000")
    vault_path = Path("/Users/eyerise/Documents/surf2026-pqc-smartgrid/obsidian")

    print("🧠 Creating Obsidian Second Brain...")
    print(f"Source: {data_dir}")
    print(f"Destination: {vault_path}")

    # Create vault directory
    vault_path.mkdir(exist_ok=True)

    # Load data
    print("\n📚 Loading data...")
    with open(data_dir / "users.json", encoding='utf-8') as f:
        users = json.load(f)

    with open(data_dir / "memories.json", encoding='utf-8') as f:
        memories = json.load(f)

    with open(data_dir / "projects.json", encoding='utf-8') as f:
        projects = json.load(f)

    with open(data_dir / "conversations.json", encoding='utf-8') as f:
        conversations = json.load(f)

    # Calculate stats
    total_messages = sum(
        len(c.get('chat_messages', []))
        for c in conversations
    )

    stats = {
        'projects': len(projects),
        'conversations': len([c for c in conversations if c.get('chat_messages')]),
        'messages': total_messages
    }

    print(f"  - Projects: {stats['projects']}")
    print(f"  - Conversations: {stats['conversations']}")
    print(f"  - Total Messages: {stats['messages']}")

    # Create content
    print("\n✨ Creating vault structure...")
    create_user_profile(users, vault_path)
    print("  ✓ User profile created")

    create_memory_docs(memories, vault_path)
    print("  ✓ Memory documents created")

    create_projects(projects, vault_path)
    print(f"  ✓ {len(projects)} projects created")

    create_conversations(conversations, vault_path)
    print(f"  ✓ Conversations organized by theme")

    create_main_index(vault_path, stats)
    print("  ✓ Main index created")

    create_obsidian_config(vault_path)
    print("  ✓ Obsidian configuration created")

    print(f"\n✅ Done! Your Obsidian vault is ready at:")
    print(f"   {vault_path}")
    print(f"\nTo use it:")
    print(f"  1. Open Obsidian")
    print(f"  2. Click 'Open folder as vault'")
    print(f"  3. Select: {vault_path}")
    print(f"  4. Start with 0-Index.md")


if __name__ == "__main__":
    main()
