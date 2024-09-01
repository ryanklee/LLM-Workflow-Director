import requests
import logging
from typing import Dict, Any, Optional

class LLMMicroserviceClient:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)

    def query(self, prompt: str, context: Optional[Dict[str, Any]] = None, tier: str = 'balanced') -> str:
        self.logger.info(f"Querying LLM microservice with tier: {tier}")
        endpoint = f"{self.base_url}/query"
        payload = {
            "prompt": prompt,
            "context": context or {},
            "tier": tier
        }
        try:
            response = requests.post(endpoint, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            self.logger.debug(f"LLM microservice response: {result}")
            return result["response"]
        except requests.RequestException as e:
            self.logger.error(f"Error querying LLM microservice: {str(e)}")
            return self._fallback_response(prompt, context, tier)

    def evaluate_sufficiency(self, stage_name: str, stage_data: Dict[str, Any], project_state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Evaluating sufficiency for stage: {stage_name}")
        endpoint = f"{self.base_url}/evaluate_sufficiency"
        payload = {
            "stage_name": stage_name,
            "stage_data": stage_data,
            "project_state": project_state
        }
        try:
            response = requests.post(endpoint, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            self.logger.debug(f"Sufficiency evaluation response: {result}")
            return result
        except requests.RequestException as e:
            self.logger.error(f"Error evaluating sufficiency: {str(e)}")
            return self._fallback_sufficiency_evaluation(stage_name, stage_data, project_state)

    def _fallback_response(self, prompt: str, context: Optional[Dict[str, Any]], tier: str) -> str:
        self.logger.warning("Using fallback response due to LLM microservice unavailability")
        return f"LLM microservice is currently unavailable. Unable to process the query: {prompt[:100]}..."

    def _fallback_sufficiency_evaluation(self, stage_name: str, stage_data: Dict[str, Any], project_state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.warning("Using fallback sufficiency evaluation due to LLM microservice unavailability")
        return {
            "is_sufficient": True,
            "reasoning": "LLM microservice is unavailable. Assuming stage is sufficient to proceed."
        }
