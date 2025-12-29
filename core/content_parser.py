# -*- coding: utf-8 -*-
"""
Content Parser for Dana's Brain
Parses generated markdown content into structured posts
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class Post:
    """Represents a single social media post."""
    platform: str  # LinkedIn, Facebook, Instagram
    archetype: str  # Heart, Head, Hands
    number: int  # Post number (1-3 per platform)
    content: str  # Hebrew post text
    word_count: int  # Number of words


@dataclass
class ParsedContent:
    """Represents parsed generation output."""
    strategy_output: str  # Campaign Bible
    posts: List[Post]  # All 9 posts
    metadata: Dict[str, any]  # Product, persona, execution time, etc.


def parse_generated_content(combined_output: str, metadata: Dict[str, any]) -> ParsedContent:
    """
    Parse the combined markdown output into structured content.

    Args:
        combined_output: Full markdown output from crew execution
        metadata: Product, persona, execution time, etc.

    Returns:
        ParsedContent with strategy and parsed posts
    """

    # Extract strategy section (Campaign Bible)
    # Try multiple patterns for strategy
    strategy_match = re.search(
        r'## 🎯 תקציר אסטרטגי \(Campaign Bible\)(.*?)(?=---\n\n## ✍️ פוסטים למדיה חברתית|# תוכן סופי|$)',
        combined_output,
        re.DOTALL
    )

    if not strategy_match:
        # Fallback: Look for any content before "# תוכן סופי"
        strategy_match = re.search(
            r'^(.*?)(?=# תוכן סופי|$)',
            combined_output,
            re.DOTALL
        )

    strategy_output = strategy_match.group(1).strip() if strategy_match else ""

    # Extract posts section - try multiple patterns
    # Pattern 1: With "✍️ פוסטים למדיה חברתית" header
    posts_match = re.search(
        r'## ✍️ פוסטים למדיה חברתית\n\n# תוכן סופי(.*?)(?=---\n\n## 💡 הערות לשימוש|$)',
        combined_output,
        re.DOTALL
    )

    if not posts_match:
        # Pattern 2: Direct "# תוכן סופי" without prior header
        posts_match = re.search(
            r'# תוכן סופי(.*?)$',
            combined_output,
            re.DOTALL
        )

    if not posts_match:
        # Pattern 3: Start from first platform section
        posts_match = re.search(
            r'(## סדרת (?:LINKEDIN|FACEBOOK|INSTAGRAM).*?)$',
            combined_output,
            re.DOTALL
        )

    posts_text = posts_match.group(1).strip() if posts_match else ""

    # Parse individual posts
    posts = []

    # Define platform sections
    platforms = [
        ('LINKEDIN', 'LinkedIn'),
        ('FACEBOOK', 'Facebook'),
        ('INSTAGRAM', 'Instagram')
    ]

    for platform_marker, platform_name in platforms:
        # Find platform section
        platform_pattern = rf'## סדרת {platform_marker}(.*?)(?=## סדרת |$)'
        platform_match = re.search(platform_pattern, posts_text, re.DOTALL)

        if not platform_match:
            continue

        platform_text = platform_match.group(1).strip()

        # Find all posts in this platform (Heart, Head, Hands)
        # Try multiple patterns for maximum compatibility

        # Pattern 1: "### פוסט 1 (Heart...)"
        post_pattern = r'### פוסט (\d+) \((Heart|Head|Hands)[^\)]*\)(.*?)(?=### |## סדרת |$)'
        post_matches = list(re.finditer(post_pattern, platform_text, re.DOTALL))

        if not post_matches:
            # Pattern 2: "### 1 פוסט (Heart...)" or "### 1. פוסט (Heart...)"
            post_pattern = r'### (\d+)\.? פוסט \((Heart|Head|Hands)[^\)]*\)(.*?)(?=### |## סדרת |$)'
            post_matches = list(re.finditer(post_pattern, platform_text, re.DOTALL))

        if not post_matches:
            # Pattern 3 (NEW): "### 1. פוסט Heart (רגשי)" - archetype before parentheses
            post_pattern = r'### (\d+)\. פוסט (Heart|Head|Hands) \([^\)]*\)(.*?)(?=### |## סדרת |$)'
            post_matches = list(re.finditer(post_pattern, platform_text, re.DOTALL))

        for post_match in post_matches:
            post_number = int(post_match.group(1))
            archetype = post_match.group(2)
            content = post_match.group(3).strip()

            # Clean content (remove markdown artifacts)
            content = content.strip()

            # Count words (Hebrew + English)
            word_count = len(content.split())

            post = Post(
                platform=platform_name,
                archetype=archetype,
                number=post_number,
                content=content,
                word_count=word_count
            )

            posts.append(post)

    # Sort posts by platform order, then number
    platform_order = {'LinkedIn': 1, 'Facebook': 2, 'Instagram': 3}
    posts.sort(key=lambda p: (platform_order.get(p.platform, 99), p.number))

    return ParsedContent(
        strategy_output=strategy_output,
        posts=posts,
        metadata=metadata
    )


def get_posts_by_platform(parsed_content: ParsedContent, platform: str) -> List[Post]:
    """
    Get all posts for a specific platform.

    Args:
        parsed_content: Parsed content object
        platform: 'LinkedIn', 'Facebook', or 'Instagram'

    Returns:
        List of posts for that platform
    """
    return [p for p in parsed_content.posts if p.platform == platform]


def get_post_emoji(archetype: str) -> str:
    """Get emoji for archetype."""
    emojis = {
        'Heart': '💜',  # Emotional
        'Head': '🎯',   # Expert
        'Hands': '🎁'   # Sales
    }
    return emojis.get(archetype, '✨')


def get_archetype_description(archetype: str) -> str:
    """Get Hebrew description for archetype."""
    descriptions = {
        'Heart': 'רגשי - מחבר לרגש',
        'Head': 'מומחה - מבוסס נתונים',
        'Hands': 'מכירתי - קריאה לפעולה'
    }
    return descriptions.get(archetype, archetype)
