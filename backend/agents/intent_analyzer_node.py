from backend.core.state import ContentState
from backend.services.llm_service import llm_service
from backend.utils.prompt_builder import PromptBuilder
from backend.utils.text_processor import TextProcessor


class IntentAnalyzerNode:
    """Analyzes intent AND extracts SEO keyword (ENHANCED)"""
    
    def __init__(self):
        self.prompt_builder = PromptBuilder()
        self.text_processor = TextProcessor()
    
    def execute(self, state: ContentState) -> ContentState:
        """Analyze intent and extract primary keyword"""
        
        print("🧠 [Intent Analyzer] Analyzing content intent and keyword...")
        
        # FIX: Enhanced prompt with keyword extraction
        intent_prompt = self.prompt_builder.build_intent_analysis_with_keyword(
            topic=state['user_config'].topic,
            platform=state['user_config'].platform
        )
        
        response = llm_service.generate_research(
            intent_prompt,
            json_mode=True
        )
        
        # Parse JSON response
        try:
            import json
            intent_data = json.loads(response)
            
            primary_intent = intent_data.get('primary_intent', 'educational')
            confidence = intent_data.get('confidence', 'medium')
            reasoning = intent_data.get('reasoning', '')
            primary_keyword = intent_data.get('primary_keyword', '')  # FIX: New field
            secondary_keywords = intent_data.get('secondary_keywords', [])  # FIX: New field
            
            print(f"  📊 Intent: {primary_intent} (confidence: {confidence})")
            print(f"  🔑 Primary Keyword: {primary_keyword}")
            
        except json.JSONDecodeError:
            # Fallback to text parsing
            print("  ⚠️ JSON parse failed, using text fallback")
            intent_data = self.text_processor.extract_intent_from_response(response)
            
            primary_intent = intent_data.get('primary_intent', 'educational')
            confidence = intent_data.get('confidence', 'medium')
            reasoning = intent_data.get('reasoning', '')
            
            # Fallback keyword extraction
            topic_words = state['user_config'].topic.split()
            primary_keyword = max(topic_words, key=len) if topic_words else ''
            secondary_keywords = []
        
        # Store in metadata
        state['draft_artifact'].metadata['intent'] = primary_intent
        state['draft_artifact'].metadata['confidence'] = confidence
        state['draft_artifact'].metadata['reasoning'] = reasoning
        state['draft_artifact'].metadata['primary_keyword'] = primary_keyword  # FIX: Store for Optimizer
        state['draft_artifact'].metadata['secondary_keywords'] = secondary_keywords  # FIX: Store for Optimizer
        
        return state
