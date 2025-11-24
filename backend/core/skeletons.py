from typing import Dict, List
from pydantic import BaseModel


class ViralDNA(BaseModel):
    """Platform-specific content structure template"""
    name: str
    platform: str
    structure: str
    optimization_rules: Dict[str, str]
    algo_targets: Dict[str, str]
    examples: List[str] = []  # FIX: Add few-shot examples
    intent_tags: List[str] = []  # NEW: Intent compatibility tags


# Intent to DNA mapping
INTENT_TO_DNA_MAP = {
    'educational': ['linkedin', 'blog', 'twitter'],
    'inspirational': ['linkedin', 'blog', 'twitter'],
    'controversial': ['twitter', 'linkedin'],
    'story': ['linkedin', 'blog', 'twitter'],
    'data': ['linkedin', 'blog', 'twitter'],
    'list': ['twitter', 'linkedin'],
    'opinion': ['twitter', 'linkedin']
}


SKELETON_LIBRARY: Dict[str, ViralDNA] = {
    "linkedin": ViralDNA(
        name="The Scroll-Stopper",
        platform="linkedin",
        structure="""BLOCK_1_TRIGGER:
Line 1: {hook}
Line 2: [EMPTY_LINE]
Line 3: {re_hook}

BLOCK_2_MEAT:
{body}

BLOCK_3_TWIST:
{twist}

BLOCK_4_ENGAGEMENT:
{cta}
PS: {catchphrase}""",
        optimization_rules={
            "hook_max_lines": "2",  # FIX: Changed from max_chars to max_lines
            "hook_chars_per_line": "40",  # FIX: Mobile screen width reference
            "hook_max_words": "15",  # FIX: Added word count as secondary check
            "paragraph_max_lines": "2",
            "empty_line_after_hook": "mandatory",
            "bullet_emoji_required": "true",
            "readability_target": "grade_8"
        },
        algo_targets={
            "primary": "Trigger 'See More' click at Line 3",
            "secondary": "Increase Dwell Time via spaced content",
            "tertiary": "Drive comments via specific CTA question"
        },
        examples=[
            """I spent 6 months analyzing 1,000 viral LinkedIn posts.

Here's what actually works in 2025:

1. The hook must create a knowledge gap
2. Use "you" not "I" in the first 3 lines
3. White space = engagement

Most people get #2 wrong.

What's your biggest LinkedIn struggle?""",
            
            # Example 2: Controversial
            """Unpopular opinion: Your resume doesn't matter anymore.

I've hired 50+ people in the last 2 years.

Zero of them got the job because of their resume.

Here's what actually matters:
• Your network
• Your projects
• Your communication

The resume is just a formality.

Agree or disagree?""",
            
            # Example 3: Story
            """My startup failed. Lost $500k. Fired everyone.

That was 3 years ago.

Today, I run a $10M company.

The difference? I stopped making these 3 mistakes:

[Rest of content]"""
        ],
        intent_tags=['educational', 'controversial', 'story', 'data', 'list', 'opinion']
    ),
    
    "twitter": ViralDNA(
        name="The Velocity Thread",
        platform="twitter",
        structure="""TWEET_1_MYSTERY:
{hook}

{validation}

A thread 🧵

TWEET_2_TO_N_VALUE:
{body_point_1}

{body_point_2}

{body_point_3}

TWEET_FINAL_SUMMARY:
TL;DR:
{summary_bullets}

TWEET_CTA:
If this added value:
1. Follow @{handle}
2. RT the first tweet 🔁""",
        optimization_rules={
            "tweet_max_chars": "280",
            "one_idea_per_tweet": "mandatory",
            "thread_indicator": "🧵",
            "summary_required": "true",
            "cta_format": "numbered_list"
        },
        algo_targets={
            "primary": "Maximize replies on Tweet 1",
            "secondary": "Drive retweets via value density",
            "tertiary": "Encourage quote tweets via hot takes"
        },
        examples=[
            """I made $47k in 60 days using AI.

Here's the exact system I used (anyone can copy this):

A thread 🧵

1/ The problem: Most people use AI wrong...

[Rest of thread]""",
            
            """90% of productivity advice is garbage.

I tested 50 methods over 2 years.

Only 3 actually worked:

🧵

1/ The "2-Minute Rule"...

[Rest of thread]"""
        ],
        intent_tags=['educational', 'controversial', 'data', 'list']
    ),
    
    "blog": ViralDNA(
        name="The Search Engine Eater",
        platform="blog",
        structure="""H1: {seo_title}

INTRODUCTION:
{pas_framework}

H2: {core_concept_1}
{body_paragraphs_1}

H2: {core_concept_2}
{body_paragraphs_2}
{bullet_list}

H2: {core_concept_3}
{body_paragraphs_3}

CONCLUSION:
{key_takeaways}
{cta}""",
        optimization_rules={
            "h1_keyword_required": "true",
            "keyword_first_100_words": "mandatory",
            "readability_grade": "8",
            "header_hierarchy": "h1_h2_h3_strict",
            "paragraph_max_sentences": "4",
            "bullet_lists_for_scannability": "true",
            "keyword_density_min": "0.5",
            "keyword_density_max": "2.5"
        },
        algo_targets={
            "primary": "Google HCU compliance (Helpful Content)",
            "secondary": "Semantic keyword density",
            "tertiary": "User engagement metrics (Time on Page)"
        },
        examples=[
            """# Complete Guide to RAG Systems in 2025

Retrieval-Augmented Generation (RAG) is transforming how AI applications access and use information. But most implementations fail.

In this guide, you'll learn the proven architecture that powers production RAG systems.

## What is RAG?

RAG combines the power of large language models with external knowledge retrieval...

[Rest of article]"""
        ],
        intent_tags=['educational', 'data']
    )
}

UNIVERSAL_MASTER_KEY = ViralDNA(
    name="The Universal Master Key",
    platform="universal",
    structure="""OPENING:
{hook}

BODY:
{main_content}

CLOSING:
{cta}""",
    optimization_rules={
        "double_line_breaks": "after_paragraphs",
        "paragraph_max_lines": "3",
        "readability_grade": "8",
        "no_walls_of_text": "mandatory"
    },
    algo_targets={
        "primary": "Universal readability",
        "secondary": "Platform-agnostic engagement",
        "tertiary": "Flexible structure adaptation"
    },
    examples=[],
    intent_tags=[]
)


def get_skeleton_by_intent(platform: str, intent: str) -> ViralDNA:
    """NEW: Get skeleton based on platform AND intent compatibility"""
    
    # Get platform skeleton
    skeleton = SKELETON_LIBRARY.get(platform.lower())
    
    if not skeleton:
        return UNIVERSAL_MASTER_KEY
    
    # Check if intent is compatible with this platform's DNA
    if intent and intent.lower() in skeleton.intent_tags:
        return skeleton
    
    # Intent not compatible - need dynamic synthesis
    return UNIVERSAL_MASTER_KEY


def get_skeleton(platform: str) -> ViralDNA:
    """Original method - backward compatible"""
    skeleton = SKELETON_LIBRARY.get(platform.lower())
    return skeleton if skeleton else UNIVERSAL_MASTER_KEY