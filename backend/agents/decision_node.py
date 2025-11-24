# ============================================================================
# FILE: backend/agents/decision_node.py
# ============================================================================

from backend.core.state import ContentState
from backend.core.config import settings


class DecisionNode:
    """Phase 6: The Perfection Loop - Decision Engine"""
    
    def execute(self, state: ContentState) -> ContentState:
        """Execute decision logic"""
        
        print("🎯 [Phase 6] Decision Node: Evaluating quality...")
        
        diagnostic = state['diagnostic_vector']
        
        # Check quality thresholds
        creative_pass = diagnostic.creative_score >= settings.CREATIVE_THRESHOLD
        compliance_pass = diagnostic.compliance_score >= settings.COMPLIANCE_THRESHOLD
        attempts_remaining = diagnostic.attempt_count < settings.MAX_LOOP_ATTEMPTS
        
        print(f"  Creative: {diagnostic.creative_score} (threshold: {settings.CREATIVE_THRESHOLD})")
        print(f"  Compliance: {diagnostic.compliance_score}% (threshold: {settings.COMPLIANCE_THRESHOLD}%)")
        print(f"  Attempts: {diagnostic.attempt_count}/{settings.MAX_LOOP_ATTEMPTS}")
        
        # Decision logic
        if creative_pass and compliance_pass:
            # SUCCESS PATH
            print("  ✅ Quality thresholds met - Publishing!")
            state['loop_continue'] = False
            state['final_output'] = self._polish_content(state)
        
        elif attempts_remaining:
            # LOOP PATH
            print("  🔄 Quality below threshold - Triggering revision...")
            state['loop_continue'] = True
            state['diagnostic_vector'].attempt_count += 1
            
            # Build diagnostic feedback
            state['diagnostic_vector'].reasoning = self._build_diagnostic_feedback(state)
        
        else:
            # MAX ATTEMPTS REACHED
            print("  ⚠️ Max attempts reached - Using best available version")
            state['loop_continue'] = False
            state['final_output'] = state['draft_artifact'].full_text
        
        return state
    
    def _build_diagnostic_feedback(self, state: ContentState) -> str:
        """Construct actionable feedback for revision"""
        feedback_parts = []
        
        diagnostic = state['diagnostic_vector']
        
        # Add compliance issues
        if diagnostic.flags:
            feedback_parts.append("COMPLIANCE ISSUES:")
            for flag in diagnostic.flags:
                feedback_parts.append(f"- {flag}")
        
        # Add creative feedback
        if diagnostic.reasoning:
            feedback_parts.append("\nCREATIVE FEEDBACK:")
            feedback_parts.append(diagnostic.reasoning)
        
        # Add specific instructions
        feedback_parts.append("\nREVISION INSTRUCTIONS:")
        
        if diagnostic.compliance_score < 100:
            feedback_parts.append("- Fix all compliance issues listed above")
        
        if diagnostic.creative_score < settings.CREATIVE_THRESHOLD:
            feedback_parts.append("- Increase creative impact and persona alignment")
            feedback_parts.append("- Make the hook more provocative")
            feedback_parts.append("- Strengthen the unique angle")
        
        return "\n".join(feedback_parts)
    
    def _polish_content(self, state: ContentState) -> str:
        """Final content polish"""
        content = state['draft_artifact'].full_text
        
        # Strip excessive whitespace
        import re
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Ensure double line breaks (platform-specific)
        if state['user_config'].platform == 'linkedin':
            # LinkedIn requires double breaks
            content = content.replace('\n', '\n\n')
            content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content.strip()
