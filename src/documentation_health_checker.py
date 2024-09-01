import logging
from typing import Dict, Any

class DocumentationHealthChecker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def assess_documentation_health(self, state_manager) -> Dict[str, Any]:
        """
        Assess the health of the project documentation.
        
        Args:
            state_manager (StateManager): The state manager containing project information
        
        Returns:
            Dict[str, Any]: A dictionary containing detailed documentation health metrics
        """
        self.logger.info("Assessing documentation health")
        
        docs = state_manager.get('documentation', {})
        total_docs = len(docs)
        up_to_date_docs = sum(1 for doc in docs.values() if doc.get('status') == 'up_to_date')
        outdated_docs = sum(1 for doc in docs.values() if doc.get('status') == 'outdated')
        missing_docs = sum(1 for doc in docs.values() if doc.get('status') == 'missing')
        
        coverage = up_to_date_docs / total_docs if total_docs > 0 else 0
        
        # Calculate average document age
        total_age = sum(doc.get('age', 0) for doc in docs.values())
        avg_age = total_age / total_docs if total_docs > 0 else 0
        
        # Calculate documentation completeness
        required_docs = state_manager.get('required_documentation', [])
        completeness = sum(1 for doc in required_docs if doc in docs) / len(required_docs) if required_docs else 1
        
        if coverage >= 0.9 and completeness >= 0.95:
            health = "Excellent"
        elif coverage >= 0.7 and completeness >= 0.8:
            health = "Good"
        elif coverage >= 0.5 and completeness >= 0.6:
            health = "Fair"
        else:
            health = "Poor"
        
        health_metrics = {
            "health": health,
            "total_docs": total_docs,
            "up_to_date_docs": up_to_date_docs,
            "outdated_docs": outdated_docs,
            "missing_docs": missing_docs,
            "coverage": coverage,
            "avg_age": avg_age,
            "completeness": completeness
        }
        
        self.logger.info(f"Documentation health assessment completed: {health}")
        return health_metrics

    def generate_health_summary(self, health_metrics: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary of the documentation health.
        
        Args:
            health_metrics (Dict[str, Any]): The health metrics dictionary
        
        Returns:
            str: A formatted summary of the documentation health
        """
        summary = f"Documentation Health: {health_metrics['health']}\n\n"
        summary += f"Total Documents: {health_metrics['total_docs']}\n"
        summary += f"Up-to-date Documents: {health_metrics['up_to_date_docs']}\n"
        summary += f"Outdated Documents: {health_metrics['outdated_docs']}\n"
        summary += f"Missing Documents: {health_metrics['missing_docs']}\n"
        summary += f"Documentation Coverage: {health_metrics['coverage']:.2%}\n"
        summary += f"Average Document Age: {health_metrics['avg_age']:.1f} days\n"
        summary += f"Documentation Completeness: {health_metrics['completeness']:.2%}\n\n"
        
        if health_metrics['health'] == "Excellent":
            summary += "Great job! Your documentation is in excellent shape. Keep up the good work!"
        elif health_metrics['health'] == "Good":
            summary += "Your documentation is in good shape, but there's room for improvement. Focus on updating outdated documents and completing any missing required documentation."
        elif health_metrics['health'] == "Fair":
            summary += "Your documentation needs attention. Prioritize updating outdated documents, completing missing documentation, and improving overall coverage."
        else:
            summary += "Your documentation requires immediate attention. Create a plan to significantly improve documentation coverage, update outdated documents, and complete all required documentation."
        
        return summary
