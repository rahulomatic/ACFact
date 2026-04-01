from typing import Tuple
from ..agents import ResearchAgent, CopywriterAgent, EditorAgent
from ..models import FactSheet, CopywriterOutput, EditorFeedback, PipelineResponse
from .logger import AgentLogger
from ..config import Config
import json
import os
from datetime import datetime


class Pipeline:
    """
    Orchestrates the execution of all agents in sequence with feedback loop
    """
    
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.copywriter_agent = CopywriterAgent()
        self.editor_agent = EditorAgent()
        self.logger = AgentLogger()
        
    def execute(self, content: str) -> PipelineResponse:
        """
        Execute the complete pipeline: Research -> Copywriter -> Editor (with feedback loop)
        
        Args:
            content: Source content to process
            
        Returns:
            PipelineResponse with all results and logs
        """
        try:
            # Step 1: Research Agent
            self.logger.log(
                "Research Agent",
                "started",
                "Analyzing source content and extracting product information..."
            )
            
            fact_sheet = self.research_agent.analyze(content)
            
            self.logger.log(
                "Research Agent",
                "completed",
                f"Successfully extracted information for: {fact_sheet.product_name}",
                data={
                    "features_count": len(fact_sheet.features),
                    "ambiguous_count": len(fact_sheet.ambiguous_statements)
                }
            )
            
            # Step 2: Copywriter Agent (with potential revisions)
            copywriter_output, iterations = self._run_copywriter_with_feedback(fact_sheet)
            
            # Step 3: Final Editor Review
            self.logger.log(
                "Editor Agent",
                "started",
                "Performing final review of approved content..."
            )
            
            final_feedback = self.editor_agent.review(fact_sheet, copywriter_output)
            
            self.logger.log(
                "Editor Agent",
                "completed",
                f"Final review complete. Approved: {final_feedback.approved}"
            )
            
            # Save outputs to file
            output_file = self._save_outputs(fact_sheet, copywriter_output, final_feedback)
            
            self.logger.log(
                "Pipeline",
                "completed",
                f"All content generated and saved to: {output_file}",
                data={"iterations": iterations}
            )
            
            return PipelineResponse(
                success=True,
                fact_sheet=fact_sheet,
                copywriter_output=copywriter_output,
                editor_feedback=final_feedback,
                logs=self.logger.get_logs(),
                iterations=iterations,
                final_approved=final_feedback.approved
            )
            
        except Exception as e:
            self.logger.log(
                "Pipeline",
                "error",
                f"Pipeline failed: {str(e)}"
            )
            
            return PipelineResponse(
                success=False,
                logs=self.logger.get_logs(),
                error=str(e)
            )
    
    def _run_copywriter_with_feedback(
        self, 
        fact_sheet: FactSheet
    ) -> Tuple[CopywriterOutput, int]:
        """
        Run copywriter agent with editor feedback loop
        
        Args:
            fact_sheet: Product information
            
        Returns:
            Tuple of (approved_output, number_of_iterations)
        """
        max_iterations = Config.MAX_RETRIES
        iteration = 0
        
        # Initial content generation
        self.logger.log(
            "Copywriter Agent",
            "started",
            "Creating initial marketing content (blog, social media, email)..."
        )
        
        copywriter_output = self.copywriter_agent.create_content(fact_sheet)
        iteration += 1
        
        self.logger.log(
            "Copywriter Agent",
            "completed",
            f"Initial content generated (Iteration {iteration})"
        )
        
        # Editor review loop
        while iteration <= max_iterations:
            self.logger.log(
                "Editor Agent",
                "started",
                f"Reviewing content (Iteration {iteration})..."
            )
            
            editor_feedback = self.editor_agent.review(fact_sheet, copywriter_output)
            
            if editor_feedback.approved and not editor_feedback.has_errors:
                self.logger.log(
                    "Editor Agent",
                    "completed",
                    "✓ Content approved! No errors found."
                )
                break
            
            if iteration >= max_iterations:
                self.logger.log(
                    "Editor Agent",
                    "completed",
                    f"⚠ Max iterations ({max_iterations}) reached. Using best available content."
                )
                break
            
            # Log issues found
            issues = []
            if editor_feedback.hallucinations:
                issues.append(f"{len(editor_feedback.hallucinations)} hallucinations")
            if editor_feedback.tone_issues:
                issues.append(f"{len(editor_feedback.tone_issues)} tone issues")
            if editor_feedback.factual_errors:
                issues.append(f"{len(editor_feedback.factual_errors)} factual errors")
            
            self.logger.log(
                "Editor Agent",
                "revision_needed",
                f"Issues found: {', '.join(issues)}. Requesting revision...",
                data={
                    "hallucinations": editor_feedback.hallucinations,
                    "tone_issues": editor_feedback.tone_issues,
                    "factual_errors": editor_feedback.factual_errors
                }
            )
            
            # Request revision
            self.logger.log(
                "Copywriter Agent",
                "started",
                f"Revising content based on feedback (Iteration {iteration + 1})..."
            )
            
            copywriter_output = self.copywriter_agent.revise_content(
                fact_sheet, 
                copywriter_output, 
                editor_feedback
            )
            iteration += 1
            
            self.logger.log(
                "Copywriter Agent",
                "completed",
                f"Revision complete (Iteration {iteration})"
            )
        
        return copywriter_output, iteration
    
    def _save_outputs(
        self, 
        fact_sheet: FactSheet, 
        copywriter_output: CopywriterOutput,
        editor_feedback: EditorFeedback
    ) -> str:
        """
        Save all outputs to a JSON file
        
        Returns:
            Output file path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"content_factory_output_{timestamp}.json"
        filepath = os.path.join(Config.OUTPUTS_DIR, filename)
        
        os.makedirs(Config.OUTPUTS_DIR, exist_ok=True)
        
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "fact_sheet": fact_sheet.model_dump(),
            "content": {
                "blog_post": copywriter_output.blog_post,
                "social_media_thread": copywriter_output.social_media_thread,
                "email_teaser": copywriter_output.email_teaser
            },
            "editor_review": editor_feedback.model_dump(),
            "logs": [log.model_dump() for log in self.logger.get_logs()]
        }
        
        with open(filepath, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        return filename