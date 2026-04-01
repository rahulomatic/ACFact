import json
import anthropic
from typing import Dict, Any
from ..config import Config
from ..models import FactSheet, CopywriterOutput, EditorFeedback
from .prompts import EDITOR_AGENT_PROMPT


class EditorAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model = Config.CLAUDE_MODEL
        
    def review(
        self, 
        fact_sheet: FactSheet, 
        copywriter_output: CopywriterOutput
    ) -> EditorFeedback:
        """
        Review copywriter's output for accuracy, tone, and hallucinations
        
        Args:
            fact_sheet: Original fact sheet
            copywriter_output: Content created by copywriter
            
        Returns:
            EditorFeedback with detailed review results
        """
        fact_sheet_json = fact_sheet.model_dump_json(indent=2)
        copywriter_json = copywriter_output.model_dump_json(indent=2)
        
        prompt = EDITOR_AGENT_PROMPT.format(
            fact_sheet=fact_sheet_json,
            copywriter_output=copywriter_json
        )
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=Config.MAX_TOKENS,
                temperature=0.3,  # Lower temperature for more consistent reviews
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
            feedback_data = self._parse_json_response(response_text)
            
            # Validate and create EditorFeedback object
            feedback = EditorFeedback(**feedback_data)
            
            return feedback
            
        except Exception as e:
            raise Exception(f"Editor Agent failed: {str(e)}")
    
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