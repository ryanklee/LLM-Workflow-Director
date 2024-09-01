import logging
from .documentation_health_checker import DocumentationHealthChecker

class ProjectStateReporter:
    def __init__(self, workflow_director):
        self.workflow_director = workflow_director
        self.logger = logging.getLogger(__name__)
        self.doc_health_checker = DocumentationHealthChecker()

    def generate_report(self, format='plain'):
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
            self._generate_quantitative_metrics()
        ]
        
        if format == 'plain':
            return self._format_plain(report_sections)
        elif format == 'markdown':
            return self._format_markdown(report_sections)
        elif format == 'html':
            return self._format_html(report_sections)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_project_summary(self):
        # Use LLM to generate a summary based on the current project state
        project_state = self.workflow_director.state_manager.get_all()
        summary_prompt = f"Generate a brief summary of the project based on the following state: {project_state}"
        summary = self.workflow_director.llm_manager.query(summary_prompt)
        return ("Project Summary", summary)

    def _generate_current_stage_info(self):
        current_stage = self.workflow_director.get_current_stage()
        progress = self.workflow_director.get_stage_progress()
        return ("Current Stage", f"{current_stage['name']} (Progress: {progress:.2%})")

    def _generate_completed_stages_info(self):
        completed_stages = list(self.workflow_director.completed_stages)
        return ("Completed Stages", ", ".join(completed_stages))

    def _generate_requirements_summary(self):
        # Use LLM to generate a summary of the current requirements
        requirements = self.workflow_director.state_manager.get('requirements', 'No requirements defined')
        summary_prompt = f"Summarize the following project requirements: {requirements}"
        summary = self.workflow_director.llm_manager.query(summary_prompt)
        return ("Requirements Summary", summary)

    def _generate_domain_model_summary(self):
        # Use LLM to generate a summary of the current domain model
        domain_model = self.workflow_director.state_manager.get('domain_model', 'No domain model defined')
        summary_prompt = f"Provide a brief overview of the following domain model: {domain_model}"
        summary = self.workflow_director.llm_manager.query(summary_prompt)
        return ("Domain Model Overview", summary)

    def _generate_documentation_health(self):
        doc_health = self.doc_health_checker.assess_documentation_health(self.workflow_director.state_manager)
        return ("Documentation Health", doc_health)

    def _generate_quantitative_metrics(self):
        total_stages = len(self.workflow_director.stages)
        completed_stages = len(self.workflow_director.completed_stages)
        overall_progress = completed_stages / total_stages
        
        metrics = [
            f"Total Stages: {total_stages}",
            f"Completed Stages: {completed_stages}",
            f"Overall Progress: {overall_progress:.2%}"
        ]
        return ("Quantitative Metrics", "\n".join(metrics))

    def _format_plain(self, sections):
        report = ["LLM-Workflow Director Project Report", "======================================"]
        for title, content in sections:
            report.extend([f"\n{title}:", "-" * len(title), content])
        return "\n".join(report)

    def _format_markdown(self, sections):
        report = ["# LLM-Workflow Director Project Report"]
        for title, content in sections:
            report.extend([f"\n## {title}", content])
        return "\n".join(report)

    def _format_html(self, sections):
        report = ["<html><body>", "<h1>LLM-Workflow Director Project Report</h1>"]
        for title, content in sections:
            report.extend([f"<h2>{title}</h2>", f"<p>{content}</p>"])
        report.append("</body></html>")
        return "\n".join(report)
