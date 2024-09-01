import logging
from typing import List, Tuple, Dict, Any
from .documentation_health_checker import DocumentationHealthChecker

class ProjectStateReporter:
    def __init__(self, workflow_director):
        self.workflow_director = workflow_director
        self.logger = logging.getLogger(__name__)
        self.doc_health_checker = DocumentationHealthChecker()

    def generate_report(self, format: str = 'plain') -> str:
        """
        Generate a comprehensive project state report.
        
        Args:
            format (str): The output format of the report. Options: 'plain', 'markdown', 'html'
        
        Returns:
            str: The formatted project state report
        """
        self.logger.info(f"Generating project state report in {format} format")
        
        report_sections = [
            self._generate_project_summary(),
            self._generate_current_stage_info(),
            self._generate_completed_stages_info(),
            self._generate_requirements_summary(),
            self._generate_domain_model_summary(),
            self._generate_documentation_health(),
            self._generate_quantitative_metrics(),
            self._generate_next_steps(),
            self._generate_risk_assessment()
        ]
        
        if format == 'plain':
            return self._format_plain(report_sections)
        elif format == 'markdown':
            return self._format_markdown(report_sections)
        elif format == 'html':
            return self._format_html(report_sections)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_project_summary(self) -> Tuple[str, str]:
        project_state = self.workflow_director.state_manager.get_all()
        context = {
            "project_name": project_state.get("project_name", "Unnamed Project"),
            "current_stage": self.workflow_director.current_stage,
            "completed_stages": len(self.workflow_director.completed_stages),
            "total_stages": len(self.workflow_director.stages)
        }
        summary_prompt = "Generate a brief summary of the project based on the provided context. Include the project name, current stage, and overall progress."
        summary = self.workflow_director.llm_manager.query(summary_prompt, context)
        return ("Project Summary", summary)

    def _generate_current_stage_info(self) -> Tuple[str, str]:
        current_stage = self.workflow_director.get_current_stage()
        progress = self.workflow_director.get_stage_progress()
        tasks = current_stage.get('tasks', [])
        tasks_info = "\n".join([f"- {task}" for task in tasks])
        return ("Current Stage", f"{current_stage['name']} (Progress: {progress:.2%})\n\nTasks:\n{tasks_info}")

    def _generate_completed_stages_info(self) -> Tuple[str, str]:
        completed_stages = list(self.workflow_director.completed_stages)
        return ("Completed Stages", ", ".join(completed_stages))

    def _generate_requirements_summary(self) -> Tuple[str, str]:
        requirements = self.workflow_director.state_manager.get('requirements', 'No requirements defined')
        context = {"requirements": requirements}
        summary_prompt = "Summarize the project requirements, highlighting key functional and non-functional requirements. If no requirements are defined, suggest next steps for requirements gathering."
        summary = self.workflow_director.llm_manager.query(summary_prompt, context)
        return ("Requirements Summary", summary)

    def _generate_domain_model_summary(self) -> Tuple[str, str]:
        domain_model = self.workflow_director.state_manager.get('domain_model', 'No domain model defined')
        context = {"domain_model": domain_model}
        summary_prompt = "Provide a brief overview of the domain model, including key entities and their relationships. If no domain model is defined, suggest steps to start creating one."
        summary = self.workflow_director.llm_manager.query(summary_prompt, context)
        return ("Domain Model Overview", summary)

    def _generate_documentation_health(self) -> Tuple[str, str]:
        doc_health = self.doc_health_checker.assess_documentation_health(self.workflow_director.state_manager)
        return ("Documentation Health", doc_health)

    def _generate_quantitative_metrics(self) -> Tuple[str, str]:
        total_stages = len(self.workflow_director.stages)
        completed_stages = len(self.workflow_director.completed_stages)
        overall_progress = completed_stages / total_stages
        
        metrics = [
            f"Total Stages: {total_stages}",
            f"Completed Stages: {completed_stages}",
            f"Overall Progress: {overall_progress:.2%}"
        ]
        return ("Quantitative Metrics", "\n".join(metrics))

    def _generate_next_steps(self) -> Tuple[str, str]:
        context = {
            "current_stage": self.workflow_director.current_stage,
            "completed_stages": list(self.workflow_director.completed_stages),
            "remaining_stages": [stage for stage in self.workflow_director.stages if stage not in self.workflow_director.completed_stages]
        }
        next_steps_prompt = "Based on the current project state, suggest the next 3-5 steps to move the project forward. Consider the current stage, completed stages, and remaining stages."
        next_steps = self.workflow_director.llm_manager.query(next_steps_prompt, context)
        return ("Next Steps", next_steps)

    def _generate_risk_assessment(self) -> Tuple[str, str]:
        context = self.workflow_director.state_manager.get_all()
        risk_prompt = "Based on the current project state, identify potential risks and challenges. Suggest mitigation strategies for each identified risk."
        risk_assessment = self.workflow_director.llm_manager.query(risk_prompt, context)
        return ("Risk Assessment", risk_assessment)

    def _format_plain(self, sections: List[Tuple[str, str]]) -> str:
        report = ["LLM-Workflow Director Project Report", "======================================"]
        for title, content in sections:
            report.extend([f"\n{title}:", "-" * len(title), content])
        return "\n".join(report)

    def _format_markdown(self, sections: List[Tuple[str, str]]) -> str:
        report = ["# LLM-Workflow Director Project Report"]
        for title, content in sections:
            if isinstance(content, str):
                report.extend([f"\n## {title}", content])
            else:
                self.logger.warning(f"Unexpected content type for section '{title}': {type(content)}")
                report.extend([f"\n## {title}", str(content)])
        return "\n".join(report)

    def _format_html(self, sections: List[Tuple[str, str]]) -> str:
        report = ["<html><body>", "<h1>LLM-Workflow Director Project Report</h1>"]
        for title, content in sections:
            report.extend([f"<h2>{title}</h2>", f"<p>{content}</p>"])
        report.append("</body></html>")
        return "\n".join(report)
