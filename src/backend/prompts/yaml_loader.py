import yaml
import os
from pathlib import Path
from typing import Dict, Any

class PromptLoader:
    """Load prompts from YAML files"""
    
    def __init__(self):
        self.prompts_path = Path(__file__).parent / "prompts.yaml"
        self._prompts = None
    
    @property
    def prompts(self) -> Dict[str, Any]:
        """Lazy load prompts"""
        if self._prompts is None:
            self._load_prompts()
        return self._prompts
    
    def _load_prompts(self):
        """Load prompts from YAML file"""
        try:
            with open(self.prompts_path, 'r', encoding='utf-8') as file:
                self._prompts = yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompts file not found: {self.prompts_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in prompts file: {str(e)}")
    
    def get_system_prompt(self, key: str) -> str:
        """Get system prompt by key"""
        return self.prompts.get("system_prompts", {}).get(key, "")
    
    def get_chat_prompt(self, key: str) -> str:
        """Get chat prompt by key"""
        return self.prompts.get("chat_prompts", {}).get(key, "")
    
    def format_prompt(self, prompt_type: str, key: str, **kwargs) -> str:
        """Format prompt with variables"""
        if prompt_type == "system":
            template = self.get_system_prompt(key)
        elif prompt_type == "chat":
            template = self.get_chat_prompt(key)
        else:
            raise ValueError(f"Invalid prompt type: {prompt_type}")
        
        return template.format(**kwargs)

# Global instance
prompt_loader = PromptLoader()
