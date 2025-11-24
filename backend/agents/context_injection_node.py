# ============================================================================
# FILE: backend/agents/context_injection_node.py
# ============================================================================

from backend.core.state import ContentState
from backend.core.avatars import get_avatar
from backend.core.skeletons import get_skeleton


class ContextInjectionNode:
    """Phase 0: The Context Injection - Prime the State"""
    
    def execute(self, state: ContentState) -> ContentState:
        """Prime the state with Avatar and Platform context"""
        
        print("🎯 [Phase 0] Context Injection: Priming the system...")
        
        # Retrieve Avatar
        avatar = get_avatar(
            state['user_config'].avatar_id,
            state['user_config'].custom_avatar_params
        )
        
        # Retrieve Platform Skeleton
        skeleton = get_skeleton(state['user_config'].platform)
        
        # Inject Avatar Voice
        state['context_layer'].persona_voice = f"""
AVATAR: {avatar.name} ({avatar.icon})
DESCRIPTION: {avatar.description}

SYSTEM INSTRUCTION:
{avatar.system_instruction}
""".strip()
        
        # Inject Platform Rules
        rules_text = "\n".join([f"- {k}: {v}" for k, v in skeleton.optimization_rules.items()])
        state['context_layer'].platform_rules = f"""
PLATFORM: {skeleton.platform.upper()}
SKELETON: {skeleton.name}

OPTIMIZATION RULES:
{rules_text}

ALGORITHMIC TARGETS:
{chr(10).join([f"- {k}: {v}" for k, v in skeleton.algo_targets.items()])}
""".strip()
        
        # Inject Viral DNA
        state['context_layer'].viral_dna = skeleton.structure
        
        print(f"  ✅ Avatar Loaded: {avatar.name}")
        print(f"  ✅ Platform Loaded: {skeleton.name}")
        print(f"  ✅ Context Layer Primed")
        
        return state
