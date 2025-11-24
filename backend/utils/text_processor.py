import re
from typing import List, Dict, Tuple


class TextProcessor:
    """Complete text manipulation and extraction"""
    
    @staticmethod
    def extract_queries_from_response(response: str) -> List[str]:
        """Parse queries with multiple fallback patterns"""
        queries = []
        
        # Try multiple patterns
        patterns = [
            r'Query \d+:\s*(.+?)(?=\n|Query|$)',
            r'\d+[\.\)]\s*(.+?)(?=\n|$)',
            r'[-•]\s*(.+?)(?=\n|$)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            if matches:
                for match in matches:
                    query = re.sub(r'[\[\]\*\"]', '', match.strip())
                    if query and len(query) > 3:
                        queries.append(query)
                break
        
        return queries[:3]
    
    @staticmethod
    def extract_facts_from_response(response: str) -> List[str]:
        """Parse facts with source validation"""
        facts = []
        
        pattern = r'Fact:\s*(.+?)(?=\nFact:|\n\n|$)'
        matches = re.findall(pattern, response, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            fact = match.strip()
            if '[Source:' in fact or '[source:' in fact.lower():
                facts.append(fact)
        
        return facts
    
    @staticmethod
    def extract_content_blocks_robust(response: str) -> Dict[str, str]:
        """FIX: Robust content parsing with fallbacks"""
        blocks = {
            'hook': '', 're_hook': '', 'body': '', 'twist': '',
            'cta': '', 'catchphrase': '', 'visuals': ''
        }
        
        # Try standard patterns first
        patterns = {
            'hook': [
                r'HOOK[_\s]*\d*:\s*(.+?)(?=\n\n|\nRE|BODY|$)',
                r'\*\*HOOK\*\*:\s*(.+?)(?=\n\n|$)',
                r'1\.\s*(.+?)(?=\n\n|2\.|$)'  # Numbered list fallback
            ],
            'body': [
                r'BODY:\s*(.+?)(?=\n\n|\nTWIST|\nCTA|$)',
                r'\*\*BODY\*\*:\s*(.+?)(?=\n\n|$)',
                r'(?:Content|Main):\s*(.+?)(?=\n\n|$)'
            ]
        }
        
        for key, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
                if match:
                    blocks[key] = match.group(1).strip()
                    break
        
        # FIX: Ultimate fallback - treat entire response as body if no tags found
        if not blocks['body'] and not blocks['hook']:
            print("  ⚠️ No structured tags found, using fallback parser...")
            
            # Split by double newlines
            parts = response.split('\n\n')
            if len(parts) >= 2:
                blocks['hook'] = parts[0]
                blocks['body'] = '\n\n'.join(parts[1:])
            else:
                blocks['body'] = response
                
        return blocks

    @staticmethod
    def extract_score_from_review(response: str) -> float:
        """Parse score with fallbacks"""
        patterns = [
            r'(?:TOTAL[_\s])?SCORE[:\s]*(\d+(?:\.\d+)?)\s*/?\s*10',
            r'(?:score|rating).*?(\d+(?:\.\d+)?)\s*/\s*10'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        return 0.0
    
    @staticmethod
    def extract_feedback_from_review(response: str) -> str:
        """Parse improvement instructions"""
        patterns = [
            r'SPECIFIC[_\s]+(?:IMPROVEMENT|FIX).*?:\s*(.+?)(?=\n\n|$)',
            r'(?:IMPROVEMENT|TO IMPROVE):\s*(.+?)(?=\n\n|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "No specific feedback."
    
    @staticmethod
    def extract_intent_from_response(response: str) -> Dict[str, str]:
        """Parse intent classification"""
        intent_data = {
            'primary_intent': 'educational',
            'confidence': 'medium',
            'reasoning': ''
        }
        
        # Intent
        intent_patterns = [r'PRIMARY[_\s]INTENT:\s*(\w+)', r'INTENT:\s*(\w+)']
        for pattern in intent_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                intent_data['primary_intent'] = match.group(1).lower()
                break
        
        # Confidence
        conf_match = re.search(r'CONFIDENCE:\s*(\w+)', response, re.IGNORECASE)
        if conf_match:
            intent_data['confidence'] = conf_match.group(1).lower()
        
        # Reasoning
        reason_match = re.search(r'REASONING:\s*(.+?)(?=\n\n|$)', response, re.DOTALL | re.IGNORECASE)
        if reason_match:
            intent_data['reasoning'] = reason_match.group(1).strip()
        
        return intent_data
    
    @staticmethod
    def assemble_content(
        hook: str,
        re_hook: str,
        body: str,
        twist: str,
        cta: str,
        platform: str
    ) -> str:
        """Assemble with platform-specific formatting"""
        
        parts = [hook]
        if re_hook:
            parts.append(re_hook)
        parts.append(body)
        if twist:
            parts.append(twist)
        if cta:
            parts.append(cta)
        
        if platform == 'linkedin':
            full_text = '\n\n'.join([p for p in parts if p])
        elif platform == 'twitter':
            full_text = '\n\n'.join([p for p in parts if p]) + '\n\n🧵'
        else:
            full_text = '\n\n'.join([p for p in parts if p])
        
        # Clean excessive whitespace
        full_text = re.sub(r'\n{3,}', '\n\n', full_text)
        return full_text.strip()
    
    @staticmethod
    def analyze_hook_strength(hook: str) -> Dict[str, any]:
        """Analyze hook effectiveness"""
        analysis = {
            'length': len(hook),
            'word_count': len(hook.split()),
            'has_number': bool(re.search(r'\d+', hook)),
            'has_question': hook.strip().endswith('?'),
            'creates_curiosity': False,
            'score': 5.0
        }
        
        # Curiosity patterns
        curiosity = [
            r'here\'s (what|why|how)',
            r'(secret|truth) about',
            r'\d+ (reasons|ways|things)'
        ]
        analysis['creates_curiosity'] = any(re.search(p, hook.lower()) for p in curiosity)
        
        # Score
        if analysis['length'] <= 60:
            analysis['score'] += 1.0
        if analysis['has_number']:
            analysis['score'] += 1.0
        if analysis['creates_curiosity']:
            analysis['score'] += 2.0
        
        return analysis
    
    @staticmethod
    def detect_engagement_triggers(content: str) -> List[str]:
        """Detect engagement mechanisms"""
        triggers = []
        content_lower = content.lower()
        
        if '?' in content:
            triggers.append('Contains questions')
        if any(w in content_lower for w in ['you', 'your']):
            triggers.append('Direct address')
        if any(w in content_lower for w in ['comment', 'share', 'agree']):
            triggers.append('Clear CTA')
        if re.search(r'\d+\.|\d+\)', content):
            triggers.append('Numbered list')
            
        return triggers