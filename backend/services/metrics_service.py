import re
import textstat
from typing import Dict, List, Tuple


class MetricsService:
    """Text analysis with context-aware evaluation (FIXED)"""
    
    # Soft flag words instead of hard ban
    FLAGGED_WORDS = [
        "delve", "unleash", "tapestry", "realm", "leverage",
        "synergy", "paradigm shift", "game-changer", "cutting-edge",
        "innovative", "revolutionize", "next-generation", "robust",
        "disrupt", "transform", "empower", "optimize"  # Extended list
    ]
    
    def calculate_readability(self, text: str) -> float:
        """Calculate Flesch-Kincaid Grade Level"""
        try:
            grade = textstat.flesch_kincaid_grade(text)
            return round(grade, 1)
        except:
            return 0.0
    
    def check_paragraph_length(self, text: str, max_lines: int = 3) -> List[str]:
        """Detect walls of text"""
        paragraphs = text.split('\n\n')
        violations = []
        
        for idx, para in enumerate(paragraphs, 1):
            lines = para.count('\n') + 1
            if lines > max_lines and para.strip():
                violations.append(f"Paragraph {idx} has {lines} lines (max: {max_lines})")
        
        return violations
    
    def detect_flagged_words_with_context(self, text: str) -> List[Dict[str, str]]:
        """FIX: Detect flagged words with surrounding context"""
        flagged = []
        text_lower = text.lower()
        
        for word in self.FLAGGED_WORDS:
            pattern = r'\b' + re.escape(word) + r'\b'
            matches = re.finditer(pattern, text_lower)
            
            for match in matches:
                start = match.start()
                end = match.end()
                
                # Extract context window (50 chars before and after)
                context_start = max(0, start - 50)
                context_end = min(len(text), end + 50)
                context = text[context_start:context_end]
                
                flagged.append({
                    'word': word,
                    'context': context,
                    'position': start
                })
        
        return flagged
    
    def check_hook_visual_length(self, hook: str, chars_per_line: int = 40) -> Tuple[bool, int]:
        """FIX: Check hook by visual lines instead of char count"""
        
        # Calculate approximate lines based on character width
        char_count = len(hook)
        estimated_lines = (char_count / chars_per_line) + 1
        
        # LinkedIn mobile typically shows 2 lines before "...see more"
        max_lines = 2
        is_valid = estimated_lines <= max_lines
        
        return is_valid, int(estimated_lines)
    
    def check_hook_length(self, hook: str, max_chars: int = 60) -> Tuple[bool, int]:
        """Legacy method - kept for backward compatibility"""
        char_count = len(hook)
        is_valid = char_count <= max_chars
        return is_valid, char_count
    
    def calculate_keyword_density(self, text: str, keyword: str) -> float:
        """Calculate keyword density"""
        if not keyword or not text:
            return 0.0
        
        keyword_clean = keyword.lower().strip()
        text_clean = text.lower()
        
        word_count = len(text.split())
        if word_count == 0:
            return 0.0
        
        keyword_count = text_clean.count(keyword_clean)
        density = (keyword_count / word_count) * 100
        return round(density, 2)
    
    def check_keyword_placement(
        self,
        text: str,
        keyword: str,
        title: str = ""
    ) -> Dict[str, bool]:
        """FIX: Check semantic keyword placement instead of just density"""
        
        if not keyword:
            return {'in_title': False, 'in_first_100': False, 'in_headers': False}
        
        keyword_lower = keyword.lower()
        text_lower = text.lower()
        
        # Check title/H1
        in_title = keyword_lower in title.lower() if title else False
        
        # Check first 100 words
        first_100_words = ' '.join(text.split()[:100]).lower()
        in_first_100 = keyword_lower in first_100_words
        
        # Check headers (H2, H3) - look for markdown headers
        headers = re.findall(r'^#{2,3}\s+(.+)$', text, re.MULTILINE)
        in_headers = any(keyword_lower in h.lower() for h in headers) if headers else False
        
        return {
            'in_title': in_title,
            'in_first_100': in_first_100,
            'in_headers': in_headers
        }
    
    def check_seo_compliance_semantic(
        self,
        text: str,
        keyword: str,
        title: str = "",
        min_density: float = 0.5,
        max_density: float = 2.5
    ) -> Tuple[bool, Dict[str, any], List[str]]:
        """FIX: Semantic SEO check - placement over density"""
        
        density = self.calculate_keyword_density(text, keyword)
        placement = self.check_keyword_placement(text, keyword, title)
        
        issues = []
        
        # Priority 1: Natural placement (more important than density)
        if not placement['in_title']:
            issues.append("Keyword missing from title/H1 (critical)")
        
        if not placement['in_first_100']:
            issues.append("Keyword missing from first 100 words (important)")
        
        if not placement['in_headers']:
            issues.append("Keyword missing from subheaders (recommended)")
        
        # Priority 2: Density (soft constraint)
        if density < min_density:
            issues.append(f"Keyword density low: {density}% (guide: {min_density}%+)")
        elif density > max_density:
            issues.append(f"Keyword density high: {density}% (may feel unnatural, guide: <{max_density}%)")
        
        # Pass if critical placements are met, even if density is slightly off
        is_compliant = placement['in_title'] and placement['in_first_100']
        
        return is_compliant, {
            'density': density,
            'placement': placement
        }, issues
    
    def calculate_compliance_score(
        self,
        text: str,
        rules: Dict[str, str],
        keyword: str = None,
        title: str = ""
    ) -> Tuple[float, List[str]]:
        """Calculate compliance with semantic checks (FIXED)"""
        flags = []
        total_checks = 0
        passed_checks = 0
        
        # Readability check
        if 'readability_target' in rules:
            total_checks += 1
            grade = self.calculate_readability(text)
            target = int(rules['readability_target'].replace('grade_', ''))
            
            if grade <= target:
                passed_checks += 1
            else:
                flags.append(f"Readability grade {grade} exceeds target {target}")
        
        # Paragraph length check
        if 'paragraph_max_lines' in rules:
            total_checks += 1
            max_lines = int(rules['paragraph_max_lines'])
            violations = self.check_paragraph_length(text, max_lines)
            
            if not violations:
                passed_checks += 1
            else:
                flags.extend(violations)
        
        # FIX: Flagged words detection (soft - for Director review)
        flagged_words = self.detect_flagged_words_with_context(text)
        if flagged_words:
            # Don't fail compliance, just flag for Director review
            word_list = [f['word'] for f in flagged_words]
            flags.append(f"Flagged words detected (need context review): {', '.join(set(word_list))}")
        
        # FIX: SEO semantic check (if applicable)
        if keyword and ('keyword_density_min' in rules or 'keyword_density_max' in rules):
            total_checks += 1
            
            min_density = float(rules.get('keyword_density_min', 0.5))
            max_density = float(rules.get('keyword_density_max', 2.5))
            
            is_compliant, seo_data, seo_issues = self.check_seo_compliance_semantic(
                text, keyword, title, min_density, max_density
            )
            
            if is_compliant:
                passed_checks += 1
            else:
                flags.extend(seo_issues)
        
        # Calculate score
        score = (passed_checks / total_checks * 100) if total_checks > 0 else 0.0
        
        return round(score, 1), flags


metrics_service = MetricsService()
