from backend.core.state import ContentState
from backend.core.skeletons import get_skeleton_by_intent, UNIVERSAL_MASTER_KEY
from backend.services.llm_service import llm_service
from backend.utils.prompt_builder import PromptBuilder
from backend.utils.text_processor import TextProcessor
from backend.utils.logger import get_logger

logger = get_logger(__name__)

class RouterNode:
    """Phase 2: DNA Router - Intent-Aware Selection (FIXED)"""
    
    def __init__(self):
        self.prompt_builder = PromptBuilder()
        self.text_processor = TextProcessor()
    
    def execute(self, state: ContentState) -> ContentState:
        """Execute intent-aware routing"""
        
        logger.info("🧬 [Phase 2] Router Node: Intent-aware DNA selection...")
        
        # Get intent from previous analysis
        intent = state['draft_artifact'].metadata.get('intent', 'educational')
        platform = state['user_config'].platform
        logger.debug(f"Routing Inputs - Intent: {intent}, Platform: {platform}")
        
        # FIX: Select skeleton based on BOTH platform AND intent
        skeleton = get_skeleton_by_intent(platform, intent)
        logger.debug(f"Skeleton Selected: {skeleton.name}")
        
        # Check if we got a valid DNA or need dynamic synthesis
        if skeleton == UNIVERSAL_MASTER_KEY:
            logger.warning(f"  ⚠️ Intent '{intent}' not compatible with platform '{platform}'")
            logger.info("  🔄 Will trigger dynamic synthesis...")
            state['context_layer'].viral_dna = ""  # Signal to synthesizer
        else:
            logger.info(f"  ✅ DNA Selected: {skeleton.name}")
            logger.info(f"  ✅ Intent '{intent}' compatible with DNA")
            state['context_layer'].viral_dna = skeleton.structure
        
        # Store skeleton info
        state['context_layer'].platform_rules = str(skeleton.optimization_rules)
        state['draft_artifact'].metadata['skeleton_name'] = skeleton.name
        state['draft_artifact'].metadata['needs_synthesis'] = (skeleton == UNIVERSAL_MASTER_KEY)
        
        logger.debug(f"Routing Complete - Needs Synthesis: {state['draft_artifact'].metadata['needs_synthesis']}")
        
        return state