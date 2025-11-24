from typing import Dict, List, Any


class PromptBuilder:
    """Complete prompt construction with surgical rewrite (ENHANCED)"""
    
    @staticmethod
    def analyze_feedback_target(feedback: str) -> Dict[str, bool]:
        """FIX: Determine which sections need rewriting"""
        
        feedback_lower = feedback.lower()
        
        targets = {
            'hook': False,
            'body': False,
            'cta': False,
            'structure': False
        }
        
        # Check for hook-related feedback
        hook_indicators = ['hook', 'opening', 'first line', 'headline', 'attention']
        targets['hook'] = any(indicator in feedback_lower for indicator in hook_indicators)
        
        # Check for body-related feedback
        body_indicators = ['body', 'content', 'main section', 'bullet', 'paragraph']
        targets['body'] = any(indicator in feedback_lower for indicator in body_indicators)
        
        # Check for CTA-related feedback
        cta_indicators = ['cta', 'call to action', 'closing', 'ending']
        targets['cta'] = any(indicator in feedback_lower for indicator in cta_indicators)
        
        # Check for structural issues
        structure_indicators = ['structure', 'flow', 'organization', 'format']
        targets['structure'] = any(indicator in feedback_lower for indicator in structure_indicators)
        
        return targets
    
    @staticmethod
    def build_research_prompt(topic: str, avatar: Any) -> str:
        """Research query decomposition with avatar context"""
        return f"""You are a research strategist working with {avatar.name}.

OBJECTIVE: Decompose "{topic}" into 3 precise search queries.

STRATEGY:
Query 1: Technical/Factual (recent developments, statistics)
Query 2: Expert Opinion/Analysis (thought leadership)
Query 3: Case Study/Real-World (practical applications)

REQUIREMENTS:
- Each query: 3-7 words maximum
- Include year markers (2024, 2025) for recency
- Align with {avatar.name}'s expertise
- Avoid generic terms

OUTPUT FORMAT:
Query 1: [query]
Query 2: [query]
Query 3: [query]

Generate:"""
    
    @staticmethod
    def build_synthesis_prompt(search_results: List[str]) -> str:
        """Fact extraction with citation"""
        results_text = "\n\n".join([f"RESULT {i+1}:\n{r}" for i, r in enumerate(search_results)])
        
        return f"""Extract verifiable facts from these search results.

RESULTS:
{results_text}

EXTRACTION PROTOCOL:
1. Locate claims with numbers, dates, quotes, examples
2. Format: "Fact: [statement]. [Source: URL]"
3. Must be objective and verifiable
4. No opinions or speculation

TARGET: Extract 5-8 high-quality facts.

Extract now:"""
    
    @staticmethod
    def build_intent_analysis_with_keyword(topic: str, platform: str) -> str:
        """FIX: Intent analysis with intelligent keyword extraction"""
        return f"""Analyze the user's content intent and extract the primary SEO keyword.

TOPIC: {topic}
PLATFORM: {platform}

INTENT CATEGORIES:
1. Educational: Teaching concept/skill
2. Inspirational: Motivating
3. Controversial: Challenging beliefs
4. Story: Personal narrative
5. Data: Research/statistics
6. List: Actionable tips
7. Opinion: Hot take
8. Apology: Crisis management
9. Launch: Product announcement
10. Guide: Comprehensive tutorial

KEYWORD EXTRACTION RULES:
1. Identify the PRIMARY concept/entity (not generic words like "guide", "complete")
2. Consider multi-word phrases (e.g., "machine learning" not just "learning")
3. Focus on searchable terms users would type
4. Avoid stop words (the, for, to, etc.)

EXAMPLES:
- Topic: "Complete Guide to RAG Systems" → Keyword: "RAG systems"
- Topic: "Why AI Startups Fail" → Keyword: "AI startups"
- Topic: "10 Tips for SEO" → Keyword: "SEO tips"
- Topic: "Crisis Management Apology" → Keyword: "crisis management"

OUTPUT (JSON ONLY):
{{
  "primary_intent": "[category]",
  "confidence": "[high/medium/low]",
  "reasoning": "[brief explanation]",
  "primary_keyword": "[main searchable term]",
  "secondary_keywords": ["related term 1", "related term 2"]
}}

Analyze:"""

    
    @staticmethod
    def build_hook_prompt_json(avatar: Any, topic: str, platform: str, intent: str) -> str:
        """Hook generation with JSON output"""
        
        psychological_triggers = {
            'educational': 'Curiosity gap + Promise',
            'inspirational': 'Emotional resonance + Aspiration',
            'controversial': 'Challenge beliefs + Provocation',
            'story': 'Human connection + Relatability',
            'data': 'Surprising statistic + Credibility',
            'list': 'Clear benefit + Scannability',
            'opinion': 'Bold stance + Personality'
        }
        
        trigger = psychological_triggers.get(intent, 'Curiosity gap')
        max_chars = 60 if platform == 'linkedin' else 280
        
        return f"""You are {avatar.name}.

{avatar.system_instruction}

TASK: Generate 3 hook variations for "{topic}"

PSYCHOLOGICAL TRIGGER: {trigger}
MAX CHARS: {max_chars}

CONSTRAINTS:
- Hook 1: Max 8 words
- Hook 2: Max 10 words
- Hook 3: Max 12 words
- Create information gap
- Stay in character

OUTPUT (JSON ONLY):
{{
  "hook_1": "first variation",
  "hook_2": "second variation",
  "hook_3": "third variation",
  "best": 1,
  "reasoning": "why hook_1 is best"
}}

Generate JSON:"""
    
    @staticmethod
    def build_surgical_rewrite_prompt(
        avatar: Any,
        topic: str,
        current_hook: str,
        current_body: str,
        feedback: str,
        targets: Dict[str, bool]
    ) -> str:
        """FIX: Surgical rewrite - only fix flagged sections"""
        
        sections_to_preserve = []
        sections_to_rewrite = []
        
        if not targets['hook']:
            sections_to_preserve.append(f"HOOK (KEEP AS IS):\n{current_hook}")
        else:
            sections_to_rewrite.append("HOOK")
        
        if not targets['body']:
            sections_to_preserve.append(f"BODY (KEEP AS IS):\n{current_body}")
        else:
            sections_to_rewrite.append("BODY")
        
        preserve_text = "\n\n".join(sections_to_preserve) if sections_to_preserve else "None"
        rewrite_list = ", ".join(sections_to_rewrite) if sections_to_rewrite else "None"
        
        return f"""You are {avatar.name}.

{avatar.system_instruction}

MISSION: SURGICAL REWRITE

TOPIC: {topic}

FEEDBACK:
{feedback}

SECTIONS TO PRESERVE (DO NOT CHANGE):
{preserve_text}

SECTIONS TO REWRITE: {rewrite_list}

CRITICAL INSTRUCTIONS:
1. Copy preserved sections EXACTLY as shown
2. ONLY rewrite the flagged sections
3. Ensure new sections integrate smoothly with preserved content
4. Address ALL issues mentioned in feedback

OUTPUT FORMAT:
{f"HOOK:\n[rewrite hook based on feedback]" if targets['hook'] else ""}
{f"BODY:\n[rewrite body based on feedback]" if targets['body'] else ""}

Generate surgical rewrite:"""
    
    @staticmethod
    def build_body_prompt(
        avatar: Any,
        skeleton: Any,
        topic: str,
        hook: str,
        facts: List[str],
        attempt_feedback: str = "",
        examples: str = ""
    ) -> str:
        """Body construction with examples"""
        
        facts_text = "\n".join([f"{i+1}. {fact}" for i, fact in enumerate(facts)])
        rules_text = "\n".join([f"- {k}: {v}" for k, v in skeleton.optimization_rules.items()])
        
        feedback_section = f"""
PREVIOUS ATTEMPT HAD ISSUES:
{attempt_feedback}

YOU MUST ADDRESS ALL ISSUES.
""" if attempt_feedback else ""
        
        return f"""You are {avatar.name}.

{avatar.system_instruction}

TOPIC: {topic}
HOOK: {hook}

STRUCTURE:
{skeleton.structure}{examples}

VERIFIED FACTS:
{facts_text}

OPTIMIZATION RULES:
{rules_text}{feedback_section}

QUALITY CHECKLIST:
✓ Facts woven naturally
✓ Voice consistent
✓ Clear progression
✓ No paragraph > 2-3 lines
✓ No AI words

OUTPUT:
BODY:
[Your content]

Write:"""
    
    @staticmethod
    def build_director_prompt_enhanced(
        avatar: Any,
        content: str,
        topic: str,
        platform: str,
        attempt: int,
        flagged_words: List[Dict[str, str]] = None
    ) -> str:
        """FIX: Enhanced director prompt with word context evaluation"""
        
        flagged_words_section = ""
        if flagged_words:
            flagged_words_section = "\n\nFLAGGED WORDS (EVALUATE CONTEXT):\n"
            for item in flagged_words[:5]:  # Show top 5
                flagged_words_section += f"- '{item['word']}' in context: \"{item['context']}\"\n"
            flagged_words_section += "\nFor each flagged word, determine: Is it used lazily/generically, or is it contextually appropriate?\n"
        
        return f"""You are a Creative Director evaluating {avatar.name}'s content.

ATTEMPT: #{attempt}
PLATFORM: {platform}
TOPIC: {topic}

CONTENT:
{content}{flagged_words_section}

EVALUATION:

1. PERSONA AUTHENTICITY (0-3 points)
   Does this sound like {avatar.name}?
   Score: [0-3]

2. HOOK EFFECTIVENESS (0-2 points)
   Does it stop the scroll?
   Score: [0-2]

3. CONTENT VALUE (0-3 points)
   Does it deliver substance?
   Score: [0-3]

4. READABILITY & FLOW (0-2 points)
   Easy to consume?
   Score: [0-2]

TOTAL SCORE: [Sum]/10

IF SCORE < 9:
SPECIFIC FIXES (be precise about WHICH section):
1. [HOOK/BODY/CTA] - [specific instruction]
2. [HOOK/BODY/CTA] - [specific instruction]
3. [HOOK/BODY/CTA] - [specific instruction]

Evaluate:"""