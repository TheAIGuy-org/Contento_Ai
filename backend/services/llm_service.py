from groq import Groq
from typing import Optional
from backend.core.config import settings
import json


class LLMService:
    """Groq LLM integration with JSON mode support (FIXED)"""
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
    
    def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_message: Optional[str] = None,
        json_mode: bool = False  # FIX: Add JSON mode flag
    ) -> str:
        """Generate completion with optional JSON mode"""
        
        messages = []
        
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # FIX: Enable JSON mode if requested
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {str(e)}")
    
    def generate_director(
        self,
        prompt: str,
        system_message: str,
        json_mode: bool = False
    ) -> str:
        """High creativity LLM for Creative Director"""
        return self.generate(
            prompt=prompt,
            model=settings.DIRECTOR_MODEL,
            temperature=settings.DIRECTOR_TEMPERATURE,
            system_message=system_message,
            json_mode=json_mode
        )
    
    def generate_architect(
        self,
        prompt: str,
        system_message: str,
        json_mode: bool = False
    ) -> str:
        """Balanced LLM for Platform Architect"""
        return self.generate(
            prompt=prompt,
            model=settings.ARCHITECT_MODEL,
            temperature=settings.ARCHITECT_TEMPERATURE,
            system_message=system_message,
            json_mode=json_mode
        )
    
    def generate_research(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        json_mode: bool = False
    ) -> str:
        """Factual LLM for Research"""
        return self.generate(
            prompt=prompt,
            model=settings.RESEARCH_MODEL,
            temperature=settings.RESEARCH_TEMPERATURE,
            system_message=system_message,
            json_mode=json_mode
        )


llm_service = LLMService()
