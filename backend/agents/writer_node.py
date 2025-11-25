from backend.core.state import ContentState
from backend.core.avatars import get_avatar
from backend.core.skeletons import get_skeleton
from backend.services.llm_service import llm_service
from backend.utils.prompt_builder import PromptBuilder
from backend.utils.text_processor import TextProcessor
from backend.utils.logger import get_logger
from typing import Any, Dict
import json
import re

logger = get_logger(__name__)

class WriterNode:
    """Phase 3: Content Generation with Surgical Rewrite (ENHANCED)"""
    
    def __init__(self):
        self.prompt_builder = PromptBuilder()
        self.text_processor = TextProcessor()
    
    def execute(self, state: ContentState) -> ContentState:
        """Execute writing with surgical rewrite capability"""
        
        logger.info("âœï¸  [Phase 3] Writer Node: Generating content...")
        logger.debug(f"Input State Keys: {list(state.keys())}")
        
        avatar = get_avatar(
            state['user_config'].avatar_id,
            state['user_config'].custom_avatar_params
        )
        logger.debug(f"Avatar Loaded: {avatar.name}")
        
        skeleton = get_skeleton(state['user_config'].platform)
        logger.debug(f"Skeleton Loaded: {skeleton.name}")
        
        intent = state['draft_artifact'].metadata.get('intent', 'educational')
        logger.debug(f"Intent: {intent}")
        
        # Check if this is a revision
        is_revision = state['diagnostic_vector'].attempt_count > 1
        logger.info(f"Is Revision: {is_revision} (Attempt #{state['diagnostic_vector'].attempt_count})")
        
        if is_revision:
            feedback = state['diagnostic_vector'].reasoning
            logger.info(f"  ðŸ”„ Revision #{state['diagnostic_vector'].attempt_count}")
            logger.debug(f"Feedback received: {feedback}")
            
            # FIX: Analyze which sections need rewriting
            targets = self.prompt_builder.analyze_feedback_target(feedback)
            logger.debug(f"Feedback Analysis Targets: {targets}")
            
            # Check if we can do surgical rewrite
            needs_full_rewrite = targets['structure'] or (targets['hook'] and targets['body'])
            logger.info(f"Needs Full Rewrite: {needs_full_rewrite}")
            
            if not needs_full_rewrite:
                logger.info("  ðŸ”¬ Performing surgical rewrite...")
                return self._surgical_rewrite(state, avatar, targets, feedback)
        
        # Full content generation (first attempt or structural issues)
        logger.info("  ðŸ“ Full content generation...")
        
        state['context_layer'].persona_voice = avatar.system_instruction
        
        # STEP 1: Generate Hooks
        logger.info("  ðŸŽ£ Generating hook variations (JSON mode)...")
        
        hook_prompt = self.prompt_builder.build_hook_prompt_json(
            avatar=avatar,
            topic=state['user_config'].topic,
            platform=state['user_config'].platform,
            intent=intent
        )
        logger.debug(f"Hook Prompt: {hook_prompt[:500]}...")
        
        hook_response = llm_service.generate_architect(
            prompt=hook_prompt,
            system_message=avatar.system_instruction,
            json_mode=True
        )
        logger.debug(f"Hook Response (Raw): {hook_response}")
        
        # Parse hooks
        try:
            hooks_data = json.loads(hook_response)
            hooks = [
                hooks_data.get('hook_1', ''),
                hooks_data.get('hook_2', ''),
                hooks_data.get('hook_3', '')
            ]
            hooks = [h for h in hooks if h]
            
            best_idx = int(hooks_data.get('best', 1)) - 1
            selected_hook = hooks[best_idx] if best_idx < len(hooks) else hooks[0]
            
            logger.info(f"  âœ… Parsed {len(hooks)} hooks via JSON")
            logger.debug(f"Selected Hook: {selected_hook}")
            
        except json.JSONDecodeError:
            logger.warning("  âš ï¸ JSON parse failed, using regex fallback...")
            hooks = []
            for i in range(1, 4):
                match = re.search(rf'HOOK_{i}:\s*(.+?)(?=\n|HOOK_|BEST:|$)', hook_response, re.DOTALL)
                if match:
                    hooks.append(match.group(1).strip())
            
            selected_hook = hooks[0] if hooks else "Default hook needed"
            logger.debug(f"Fallback Selected Hook: {selected_hook}")
        
        # Analyze hook
        if selected_hook:
            hook_analysis = self.text_processor.analyze_hook_strength(selected_hook)
            state['draft_artifact'].metadata['hook_score'] = hook_analysis['score']
            logger.debug(f"Hook Analysis Score: {hook_analysis['score']}")
        
        state['draft_artifact'].hook = selected_hook
        
        # STEP 2: Generate Body
        logger.info("  ðŸ“ Constructing body...")
        
        skeleton_obj = get_skeleton(state['user_config'].platform)
        examples_text = ""
        if skeleton_obj.examples:
            examples_text = "\n\nFEW-SHOT EXAMPLES:\n\n"
            for idx, example in enumerate(skeleton_obj.examples[:2], 1):
                examples_text += f"Example {idx}:\n{example}\n\n"
        
        body_prompt = self.prompt_builder.build_body_prompt(
            avatar=avatar,
            skeleton=skeleton_obj,
            topic=state['user_config'].topic,
            hook=selected_hook,
            facts=state['ground_truth'],
            attempt_feedback="",
            examples=examples_text
        )
        logger.debug(f"Body Prompt: {body_prompt[:500]}...")
        
        body_response = llm_service.generate_architect(
            prompt=body_prompt,
            system_message=avatar.system_instruction
        )
        logger.debug(f"Body Response (Raw): {body_response[:500]}...")
        
        body_match = re.search(r'BODY:\s*(.+?)(?=$)', body_response, re.DOTALL | re.IGNORECASE)
        body_content = body_match.group(1).strip() if body_match else body_response
        
        # FIX: Remove ALL occurrences of hook from body (not just at the start)
        # The LLM sometimes includes the hook multiple times in the body
        if selected_hook:
            hook_pattern = re.escape(selected_hook.strip())
            # Remove hook if it appears at the beginning with optional emoji/formatting
            body_lines = body_content.split('\n')
            cleaned_lines = []
            
            for line in body_lines:
                line_stripped = line.strip()
                # Skip lines that are just the hook (with or without emoji/formatting)
                if line_stripped and not re.match(rf'^[ðŸ’¡ðŸ”¥âš¡ðŸŽ¯ðŸ“Œ]*\s*{hook_pattern}\s*[ðŸ’¡ðŸ”¥âš¡ðŸŽ¯ðŸ“Œ]*$', line_stripped, re.IGNORECASE):
                    cleaned_lines.append(line)
                elif not line_stripped:
                    # Keep empty lines for formatting
                    cleaned_lines.append(line)
            
            body_content = '\n'.join(cleaned_lines).strip()
            logger.info(f"Removed hook duplications from body (if any)")
        
        state['draft_artifact'].body = body_content
        logger.debug(f"Final Body Content: {body_content[:200]}...")
        
        # Assemble and finalize
        self._finalize_content(state)
        
        return state
    
    def _surgical_rewrite(
        self,
        state: ContentState,
        avatar: Any,
        targets: Dict[str, bool],
        feedback: str
    ) -> ContentState:
        """FIX: Perform surgical rewrite of specific sections"""
        
        current_hook = state['draft_artifact'].hook
        current_body = state['draft_artifact'].body
        
        logger.info(f"  ðŸŽ¯ Targets: Hook={targets['hook']}, Body={targets['body']}")
        
        # Generate surgical rewrite prompt
        surgical_prompt = self.prompt_builder.build_surgical_rewrite_prompt(
            avatar=avatar,
            topic=state['user_config'].topic,
            current_hook=current_hook,
            current_body=current_body,
            feedback=feedback,
            targets=targets
        )
        logger.debug(f"Surgical Rewrite Prompt: {surgical_prompt[:500]}...")
        
        rewrite_response = llm_service.generate_architect(
            prompt=surgical_prompt,
            system_message=avatar.system_instruction
        )
        logger.debug(f"Rewrite Response (Raw): {rewrite_response[:500]}...")
        
        # Parse rewritten sections
        if targets['hook']:
            hook_match = re.search(r'HOOK:\s*(.+?)(?=\n\nBODY:|$)', rewrite_response, re.DOTALL | re.IGNORECASE)
            if hook_match:
                state['draft_artifact'].hook = hook_match.group(1).strip()
                logger.info("  âœ… Hook rewritten")
                logger.debug(f"New Hook: {state['draft_artifact'].hook}")
        
        if targets['body']:
            body_match = re.search(r'BODY:\s*(.+?)(?=$)', rewrite_response, re.DOTALL | re.IGNORECASE)
            if body_match:
                body_content = body_match.group(1).strip()
                
                # Apply same hook deduplication logic for surgical rewrites
                current_hook = state['draft_artifact'].hook
                if current_hook:
                    hook_pattern = re.escape(current_hook.strip())
                    body_lines = body_content.split('\n')
                    cleaned_lines = []
                    
                    for line in body_lines:
                        line_stripped = line.strip()
                        if line_stripped and not re.match(rf'^[ðŸ’¡ðŸ”¥âš¡ðŸŽ¯ðŸ“Œ]*\s*{hook_pattern}\s*[ðŸ’¡ðŸ”¥âš¡ðŸŽ¯ðŸ“Œ]*$', line_stripped, re.IGNORECASE):
                            cleaned_lines.append(line)
                        elif not line_stripped:
                            cleaned_lines.append(line)
                    
                    body_content = '\n'.join(cleaned_lines).strip()
                    logger.info("Removed hook duplications from rewritten body (if any)")
                
                state['draft_artifact'].body = body_content
                logger.info("  âœ… Body rewritten")
                logger.debug(f"New Body: {state['draft_artifact'].body[:200]}...")
        
        # Reassemble
        self._finalize_content(state)
        
        return state
    
    def _finalize_content(self, state: ContentState):
        """Assemble final content and detect triggers"""
        
        logger.info("Finalizing content assembly...")
        full_text = self.text_processor.assemble_content(
            hook=state['draft_artifact'].hook,
            re_hook="",
            body=state['draft_artifact'].body,
            twist="",
            cta="",
            platform=state['user_config'].platform
        )
        
        state['draft_artifact'].full_text = full_text
        logger.debug(f"Full Text Assembled: {full_text[:200]}...")
        
        triggers = self.text_processor.detect_engagement_triggers(full_text)
        state['draft_artifact'].metadata['engagement_triggers'] = triggers
        logger.info(f"Engagement Triggers Detected: {triggers}")