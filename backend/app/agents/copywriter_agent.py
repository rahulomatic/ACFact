import json
import anthropic
from typing import Dict, Any
from ..config import Config
from ..models import FactSheet, CopywriterOutput, EditorFeedback
from .prompts import COPYWRITER_AGENT_PROMPT, COPYWRITER_REVISION_PROMPT


class CopywriterAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model = Config.CLAUDE_MODEL
        
    def create_content(self, fact_sheet: FactSheet) -> CopywriterOutput:
        """
        Generate marketing content based on fact sheet
        
        Args:
            fact_sheet: Structured product information
            
        Returns:
            CopywriterOutput with blog post, social media thread, and email
        """
        # Convert fact sheet to JSON string for the prompt
        fact_sheet_json = fact_sheet.model_dump_json(indent=2)
        
        prompt = COPYWRITER_AGENT_PROMPT.format(fact_sheet=fact_sheet_json)
        
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
            content_data = self._parse_json_response(response_text)
            
            # Validate and create CopywriterOutput object
            output = CopywriterOutput(**content_data)
            
            return output
            
        except Exception as e:
            raise Exception(f"Copywriter Agent failed: {str(e)}")
    
    def revise_content(
        self, 
        fact_sheet: FactSheet, 
        previous_output: CopywriterOutput,
        editor_feedback: EditorFeedback
    ) -> CopywriterOutput:
        """
        Revise content based on editor feedback
        
        Args:
            fact_sheet: Original fact sheet
            previous_output: Previous copywriter output
            editor_feedback: Editor's feedback and corrections
            
        Returns:
            Revised CopywriterOutput
        """
        fact_sheet_json = fact_sheet.model_dump_json(indent=2)
        previous_output_json = previous_output.model_dump_json(indent=2)
        feedback_json = editor_feedback.model_dump_json(indent=2)
        
        prompt = COPYWRITER_REVISION_PROMPT.format(
            fact_sheet=fact_sheet_json,
            previous_output=previous_output_json,
            editor_feedback=feedback_json
        )
        
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
            content_data = self._parse_json_response(response_text)
            
            # Validate and create CopywriterOutput object
            output = CopywriterOutput(**content_data)
            
            return output
            
        except Exception as e:
            raise Exception(f"Copywriter Agent revision failed: {str(e)}")
    
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