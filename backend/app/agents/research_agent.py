import json
import anthropic
from typing import Dict, Any
from ..config import Config
from ..models import FactSheet
from .prompts import RESEARCH_AGENT_PROMPT


class ResearchAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model = Config.CLAUDE_MODEL
        
    def analyze(self, content: str) -> FactSheet:
        """
        Analyze source content and extract structured product information
        
        Args:
            content: Raw text content to analyze
            
        Returns:
            FactSheet object with extracted information
        """
        prompt = RESEARCH_AGENT_PROMPT.format(content=content)
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=Config.MAX_TOKENS,
                temperature=Config.TEMPERATURE,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract text response
            response_text = message.content[0].text
            
            # Parse JSON response
            fact_sheet_data = self._parse_json_response(response_text)
            
            # Validate and create FactSheet object
            fact_sheet = FactSheet(**fact_sheet_data)
            
            return fact_sheet
            
        except Exception as e:
            raise Exception(f"Research Agent failed: {str(e)}")
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON from Claude's response, handling potential formatting issues
        """
        # Remove markdown code blocks if present
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        cleaned = cleaned.strip()
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {str(e)}\nResponse: {response}")