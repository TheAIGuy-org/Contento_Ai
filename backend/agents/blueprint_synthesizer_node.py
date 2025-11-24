# ============================================================================
# FILE: backend/agents/blueprint_synthesizer_node.py
# ============================================================================

from backend.core.state import ContentState
from backend.core.skeletons import get_skeleton, UNIVERSAL_MASTER_KEY
from backend.services.llm_service import llm_service


class BlueprintSynthesizerNode:
    """Dynamic blueprint creation when no DNA match exists"""
    
    def execute(self, state: ContentState) -> ContentState:
        """Synthesize custom blueprint if needed"""
        
        print("📐 [Blueprint Synthesizer] Creating custom structure...")
        
        needs_synthesis = state['draft_artifact'].metadata.get('needs_synthesis', False)
        
        if needs_synthesis:
            print("  🔄 Custom structure required (Intent mismatch). Synthesizing...")
            
            intent = state['draft_artifact'].metadata.get('intent', 'educational')
            
            synthesis_prompt = f"""You are a content structure architect.

TASK: Design a viral content structure for:
- Topic: {state['user_config'].topic}
- Platform: {state['user_config'].platform}
- Intent: {intent}

REQUIREMENTS:
1. Define clear sections (Hook, Body, Closing)
2. Specify formatting rules
3. Include engagement mechanisms
4. Optimize for platform algorithm

OUTPUT FORMAT:
STRUCTURE:
[Your structure template with {{placeholders}}]

RULES:
- [Rule 1]
- [Rule 2]

ALGO_TARGETS:
- [Target 1]
- [Target 2]

Generate the blueprint:"""
            
            blueprint_response = llm_service.generate_architect(
                prompt=synthesis_prompt,
                system_message="You are a viral content architect."
            )
            
            # Inject the synthesized DNA
            state['context_layer'].viral_dna = blueprint_response
            print("  ✅ Custom blueprint synthesized and injected")
            
        else:
            print("  ✨ Using standard Platform DNA")
        
        return state