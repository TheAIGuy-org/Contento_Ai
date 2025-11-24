from backend.core.state import ContentState
from backend.core.skeletons import get_skeleton
from backend.services.metrics_service import metrics_service


class OptimizerNode:
    """Phase 4: Optimization with Intelligent Keyword (FIXED)"""
    
    def execute(self, state: ContentState) -> ContentState:
        """Execute complete optimization"""
        
        print("📊 [Phase 4] Optimizer Node: Complete analysis...")
        
        skeleton = get_skeleton(state['user_config'].platform)
        rules = skeleton.optimization_rules
        content = state['draft_artifact'].full_text
        hook = state['draft_artifact'].hook
        
        # FIX: Use keyword from Intent Analyzer (not naive extraction)
        keyword = state['draft_artifact'].metadata.get('primary_keyword', None)
        
        if not keyword and state['user_config'].platform == 'blog':
            # Ultimate fallback (should rarely happen)
            print("  ⚠️ No keyword from Intent Analyzer, using fallback")
            topic_words = state['user_config'].topic.lower().split()
            keyword = max(topic_words, key=len) if topic_words else None
        
        if keyword:
            print(f"  🔍 SEO Keyword: {keyword}")
        
        # Calculate compliance with keyword
        compliance_score, flags = metrics_service.calculate_compliance_score(
            text=content,
            rules=rules,
            keyword=keyword,
            title=hook
        )
        
        # Hook visual check
        if 'hook_max_lines' in rules:
            max_lines = int(rules['hook_max_lines'])
            chars_per_line = int(rules.get('hook_chars_per_line', 40))
            
            is_valid, estimated_lines = metrics_service.check_hook_visual_length(
                hook, chars_per_line
            )
            
            if not is_valid:
                flags.append(f"Hook spans {estimated_lines} lines (max: {max_lines})")
        
        # Fact usage check
        facts = state['ground_truth']
        if facts:
            facts_used = 0
            for fact in facts:
                fact_clean = fact.split('[Source:')[0].lower()
                key_terms = [t.strip() for t in fact_clean.split() if len(t.strip()) > 5]
                if any(term in content.lower() for term in key_terms[:3]):
                    facts_used += 1
            
            usage_rate = (facts_used / len(facts) * 100) if facts else 0
            state['diagnostic_vector'].metadata['facts_usage_rate'] = usage_rate
            
            if usage_rate < 30:
                flags.append(f"Low fact usage: {usage_rate:.0f}%")
        
        # Readability
        import textstat
        grade_level = metrics_service.calculate_readability(content)
        sentences = content.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        # Keyword density
        if keyword:
            keyword_density = metrics_service.calculate_keyword_density(content, keyword)
            state['diagnostic_vector'].metadata['keyword_density'] = keyword_density
        
        state['diagnostic_vector'].metadata.update({
            'grade_level': grade_level,
            'avg_sentence_length': round(avg_sentence_length, 1)
        })
        
        if grade_level > 10:
            flags.append(f"Readability: Grade {grade_level}")
        
        # Engagement prediction
        engagement_triggers = state['draft_artifact'].metadata.get('engagement_triggers', [])
        hook_score = state['draft_artifact'].metadata.get('hook_score', 5.0)
        
        engagement_score = min(10.0, (
            hook_score * 0.4 +
            len(engagement_triggers) * 1.5 +
            (100 - grade_level) * 0.3
        ))
        
        state['diagnostic_vector'].engagement_score = round(engagement_score, 1)
        state['diagnostic_vector'].compliance_score = compliance_score
        state['diagnostic_vector'].flags = flags
        
        print(f"  📊 Compliance: {compliance_score}%")
        print(f"  📊 Engagement: {engagement_score:.1f}/10")
        print(f"  📊 Issues: {len(flags)}")
        
        return state