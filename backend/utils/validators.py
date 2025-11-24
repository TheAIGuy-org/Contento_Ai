# ============================================================================
# FILE: backend/utils/validators.py
# ============================================================================

from typing import Tuple
from backend.core.state import UserConfig


class InputValidator:
    """Validate user inputs"""
    
    VALID_PLATFORMS = ["linkedin", "twitter", "blog"]
    VALID_AVATARS = ["stark", "musk", "jobs", "goggins", "viral_bro", "custom"]
    
    @staticmethod
    def validate_user_config(config: UserConfig) -> Tuple[bool, str]:
        """Validate user configuration"""
        
        # Check topic
        if not config.topic or len(config.topic.strip()) < 3:
            return False, "Topic must be at least 3 characters"
        
        # Check platform
        if config.platform.lower() not in InputValidator.VALID_PLATFORMS:
            return False, f"Platform must be one of: {', '.join(InputValidator.VALID_PLATFORMS)}"
        
        # Check avatar
        if config.avatar_id.lower() not in InputValidator.VALID_AVATARS:
            return False, f"Avatar must be one of: {', '.join(InputValidator.VALID_AVATARS)}"
        
        # Check custom avatar params if custom
        if config.avatar_id.lower() == "custom" and not config.custom_avatar_params:
            return False, "Custom avatar requires custom_avatar_params"
            
        return True, "Configuration valid"