from backend.core.state import ContentState
from backend.core.avatars import get_avatar
from backend.services.llm_service import llm_service
from backend.services.metrics_service import metrics_service
from backend.utils.prompt_builder import PromptBuilder
from backend.utils.text_processor import TextProcessor
from backend.utils.logger import get_logger

logger = get_logger(__name__)

class DirectorNode:
    """Phase 5: Creative Review with Context Awareness (ENHANCED)"""
    
    def __init__(self):
        self.prompt_builder = PromptBuilder()
        self.text_processor = TextProcessor()
    
    def execute(self, state: ContentState) -> ContentState:
        """Execute complete creative review with word context evaluation"""
        
        logger.info("🎬 [Phase 5] Director Node: Complete creative review...")
        
        avatar = get_avatar(
            state['user_config'].avatar_id,
            state['user_config'].custom_avatar_params
        )
        logger.debug(f"Avatar Loaded: {avatar.name}")
        
        # FIX: Get flagged words with context
        content = state['draft_artifact'].full_text
        flagged_words = metrics_service.detect_flagged_words_with_context(content)
        
        if flagged_words:
            logger.info(f"Flagged Words Detected: {len(flagged_words)}")
            logger.debug(f"Flagged Words Details: {flagged_words}")
        else:
            logger.debug("No flagged words detected.")
        
        # Build enhanced review prompt with word context
        director_prompt = self.prompt_builder.build_director_prompt_enhanced(
            avatar=avatar,
            content=content,
            topic=state['user_config'].topic,
            platform=state['user_config'].platform,
            attempt=state['diagnostic_vector'].attempt_count,
            flagged_words=flagged_words
        )
        logger.debug(f"Director Prompt: {director_prompt[:500]}...")
        
        review_response = llm_service.generate_director(
            prompt=director_prompt,
            system_message="You are a Creative Director. Evaluate context, not just rules."
        )
        logger.debug(f"Director Review Response (Raw): {review_response}")
        
        # Extract score and feedback
        creative_score = self.text_processor.extract_score_from_review(review_response)
        feedback = self.text_processor.extract_feedback_from_review(review_response)
        
        # Update diagnostic
        state['diagnostic_vector'].creative_score = creative_score
        state['diagnostic_vector'].reasoning = feedback
        state['diagnostic_vector'].metadata['full_review'] = review_response
        
        # FIX: Store word evaluation
        state['diagnostic_vector'].metadata['flagged_words_evaluated'] = True
        
        logger.info(f"  🎯 Creative Score: {creative_score}/10")
        logger.info(f"  💬 Feedback: {feedback[:100]}...")
        
        if flagged_words:
            logger.info(f"  🔍 Reviewed {len(flagged_words)} flagged words in context")
            
        return state