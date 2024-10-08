import logging
import time
import yaml
import os
import ast
from typing import Dict, Any, Optional, List
from .error_handler import ErrorHandler
from anthropic import Anthropic, NotFoundError, APIError, APIConnectionError
from .claude_manager import ClaudeManager
from .exceptions import RateLimitError
from .token_tracker import TokenTracker
from .token_optimizer import TokenOptimizer

class LLMCostOptimizer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.usage_stats = {
            'fast': {'count': 0, 'total_tokens': 0, 'total_cost': 0},
            'balanced': {'count': 0, 'total_tokens': 0, 'total_cost': 0},
            'powerful': {'count': 0, 'total_tokens': 0, 'total_cost': 0}
        }
        self.cost_per_token = {
            'fast': 0.0001,
            'balanced': 0.0005,
            'powerful': 0.001
        }
        self.performance_metrics = {
            'fast': {'avg_response_time': 0, 'success_rate': 1.0},
            'balanced': {'avg_response_time': 0, 'success_rate': 1.0},
            'powerful': {'avg_response_time': 0, 'success_rate': 1.0}
        }

    async def update_usage(self, tier: str, tokens: int, response_time: float, success: bool):
        if tier in self.usage_stats:
            self.usage_stats[tier]['count'] += 1
            self.usage_stats[tier]['total_tokens'] += tokens
            cost = tokens * self.cost_per_token[tier]
            self.usage_stats[tier]['total_cost'] += cost

            # Update performance metrics
            self.performance_metrics[tier]['avg_response_time'] = (
                (self.performance_metrics[tier]['avg_response_time'] * (self.usage_stats[tier]['count'] - 1) + response_time)
                / self.usage_stats[tier]['count']
            )
            if not success:
                self.performance_metrics[tier]['success_rate'] = (
                    (self.performance_metrics[tier]['success_rate'] * (self.usage_stats[tier]['count'] - 1) + 0)
                    / self.usage_stats[tier]['count']
                )
        else:
            self.logger.warning(f"Unknown tier: {tier}")

    async def get_usage_report(self) -> Dict[str, Any]:
        total_cost = sum(self.usage_stats[tier]['total_cost'] for tier in self.usage_stats)
        return {
            'usage_stats': self.usage_stats,
            'performance_metrics': self.performance_metrics,
            'total_cost': total_cost
        }

    async def suggest_optimization(self) -> str:
        total_queries = sum(self.usage_stats[tier]['count'] for tier in self.usage_stats)
        if total_queries == 0:
            return "Not enough data to suggest optimizations."

        powerful_ratio = self.usage_stats['powerful']['count'] / total_queries
        fast_ratio = self.usage_stats['fast']['count'] / total_queries

        suggestions = []

        if powerful_ratio > 0.3:
            suggestions.append("Consider optimizing prompts to reduce reliance on the 'powerful' tier.")
        elif fast_ratio < 0.2:
            suggestions.append("Look for opportunities to use the 'fast' tier more frequently for simple queries.")

        for tier in self.performance_metrics:
            if self.performance_metrics[tier]['success_rate'] < 0.95:
                suggestions.append(f"Investigate and improve reliability of the '{tier}' tier.")
            if self.performance_metrics[tier]['avg_response_time'] > 5:  #  5 seconds threshold
                suggestions.append(f"Consider optimizing response time for the '{tier}' tier.")

        if not suggestions:
            return "Current usage appears to be well-balanced and performing efficiently across tiers."
        
        return " ".join(suggestions)

    async def select_optimal_tier(self, query_complexity: float) -> str:
        if query_complexity < 0.3:
            return 'fast'
        elif query_complexity < 0.7:
            return 'balanced'
        else:
            return 'powerful'

class LLMManager:
    def __init__(self, config_path='src/llm_config.yaml', claude_manager=None):
        self.error_handler = ErrorHandler()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler('llm_manager.log')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Add a stream handler for console output during tests
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        self.cache = {}
        self.cost_optimizer = LLMCostOptimizer()
        self.config = self._load_config(config_path)
        self.tiers = self.config.get('tiers', {
            'fast': {'model': 'claude-3-haiku-20240307', 'max_tokens': 1000},
            'balanced': {'model': 'claude-3-sonnet-20240229', 'max_tokens': 4000},
            'powerful': {'model': 'claude-3-opus-20240229', 'max_tokens': 4000}
        })
        self.logger.info("LLMManager initialized with config: %s", self.config)
        self.prompt_templates = self.config.get('prompt_templates', {})
        self.claude_manager = claude_manager or self._create_claude_manager()
        self.token_tracker = TokenTracker()
        self.token_optimizer = TokenOptimizer(self.token_tracker)
        self.logger.info("LLMManager initialization complete")

    async def count_tokens(self, text: str) -> int:
        words = text.split()
        return max(1, len(words))  # Ensure we always return at least 1 token

    def _create_claude_manager(self):
        return ClaudeManager()

    def _load_config(self, config_path):
        try:
            if isinstance(config_path, str):
                with open(config_path, 'r') as config_file:
                    return yaml.safe_load(config_file)
            else:
                self.logger.warning(f"Invalid config_path type: {type(config_path)}. Using default configuration.")
                return {}
        except Exception as e:
            self.logger.error(f"Error loading LLM configuration: {str(e)}")
            return {}

    async def query(self, prompt: str, context: Optional[Dict[str, Any]] = None, tier: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
        self.logger.debug(f"Querying LLM with prompt: {prompt[:50]}...")
        self.logger.debug(f"Context: {context}")
        self.logger.debug(f"Tier: {tier}")
        self.logger.debug(f"Model: {model}")
        
        start_time = time.time()
        self.logger.debug(f"Query start time: {start_time}")
        
        try:
            if tier is None:
                query_complexity = await self._estimate_query_complexity(prompt)
                tier = await self.cost_optimizer.select_optimal_tier(query_complexity)

            self.logger.debug(f"Selected tier: {tier}, model: {model or 'default'}")
            self.logger.info(f"Query details - Tier: {tier}, Model: {model or 'default'}, Prompt length: {len(prompt)}")

            cache_key = await self._generate_cache_key(prompt, context, tier)
            if cache_key in self.cache:
                self.logger.info(f"Using cached response for prompt: {prompt[:50]}... (tier: {tier})")
                return self.cache[cache_key]

            max_retries = 3
            original_tier = tier

            while max_retries > 0:
                try:
                    enhanced_prompt = await self._enhance_prompt(prompt, context)
                    optimized_prompt = await self.token_optimizer.optimize_prompt(enhanced_prompt)
                    tier_config = self.tiers.get(tier, self.tiers['balanced'])

                    if model is None:
                        model = tier_config['model']

                    input_tokens = await self.claude_manager.count_tokens(optimized_prompt)
                    response = await self.claude_manager.generate_response(optimized_prompt, model=model)
                    output_tokens = await self.claude_manager.count_tokens(response)
                    
                    await self.token_tracker.add_tokens(cache_key, input_tokens, output_tokens)
                    
                    result = await self._process_response(response, tier, start_time)
                    result['raw_response'] = response
                    self.cache[cache_key] = result
                    self.logger.debug(f"Processed response: {result}")
                    
                    await self.token_tracker.add_tokens(prompt, input_tokens, output_tokens)
                    
                    self.logger.debug(f"Token usage for query '{prompt[:30]}...': {await self.token_tracker.get_token_usage(prompt)}")
                    
                    await self.cost_optimizer.update_usage(tier, input_tokens + output_tokens, time.time() - start_time, True)
                    
                    return {
                        "response": result.get('response', ''),
                        "task_progress": result.get('task_progress', 0),
                        "state_updates": result.get('state_updates', {}),
                        "actions": result.get('actions', []),
                        "suggestions": result.get('suggestions', []),
                        "raw_response": result.get('raw_response', ''),
                        "token_usage": {
                            "input": input_tokens,
                            "output": output_tokens,
                            "total": input_tokens + output_tokens
                        }
                    }
                except RateLimitError:
                    self.logger.warning(f"Rate limit reached for tier: {tier}")
                    max_retries -= 1
                    if max_retries == 0:
                        return await self._fallback_response(prompt, context, original_tier)
                    tier = await self._get_fallback_tier(tier)
                    if tier is None:
                        return await self._fallback_response(prompt, context, original_tier)
                    self.logger.info(f"Falling back to a lower-tier LLM: {tier}")
                except Exception as e:
                    self.logger.error(f"Error querying LLM: {str(e)} (tier: {tier})")
                    await self.cost_optimizer.update_usage(tier, 0, time.time() - start_time, False)
                    max_retries -= 1
                    if max_retries == 0:
                        return await self._fallback_response(prompt, context, original_tier)
            
            return await self._fallback_response(prompt, context, original_tier)
        except Exception as e:
            self.logger.exception(f"Unexpected error in query method: {str(e)}")
            return await self._fallback_response(prompt, context, original_tier)

    async def get_optimization_suggestion(self) -> str:
        return await self.cost_optimizer.suggest_optimization()

    async def get_usage_report(self) -> Dict[str, Any]:
        return await self.cost_optimizer.get_usage_report()

    async def calculate_cost(self, model: str, tokens: int) -> float:
        cost_per_token = 0.0001  # Example cost per token
        return tokens * cost_per_token

    async def _process_response(self, response: str, tier: str, start_time: float) -> Dict[str, Any]:
        end_time = time.time()
        response_time = end_time - start_time
        tokens = await self.claude_manager.count_tokens(response)

        self.logger.debug(f"Received response from LLM: {response[:50]}...")
        structured_response = await self._parse_structured_response(response)
        
        response_with_id = await self._add_unique_id(structured_response)
        response_with_id['response_time'] = response_time
        response_with_id['tier'] = tier
        
        if 'response' not in response_with_id or not response_with_id['response']:
            response_with_id['response'] = response or "No response content"
        
        if isinstance(response_with_id['response'], dict):
            response_with_id['response'] = str(response_with_id['response'])

        return response_with_id

    async def _estimate_query_complexity(self, query: str) -> float:
        word_count = len(query.split())
        complexity_keywords = ['analyze', 'compare', 'evaluate', 'synthesize', 'complex']
        keyword_count = sum(1 for word in query.lower().split() if word in complexity_keywords)
        
        complexity = (word_count / 30) + (keyword_count * 0.5)  # Adjusted normalization
        return min(max(complexity, 0), 1)  # Ensure it's between 0 and 1

    async def _get_fallback_tier(self, current_tier: str) -> str:
        tiers = ['powerful', 'balanced', 'fast']
        try:
            current_index = tiers.index(current_tier)
            if current_index < len(tiers) - 1:
                return tiers[current_index + 1]
        except ValueError:
            pass
        return 'fast'

    async def determine_query_tier(self, query: str) -> str:
        complexity = await self._estimate_query_complexity(query)
        return await self.cost_optimizer.select_optimal_tier(complexity)

    async def _enhance_prompt(self, prompt: str, context: Optional[Dict[str, Any]]) -> str:
        if context is None:
            return prompt

        workflow_stage = context.get('workflow_stage', 'Unknown')
        stage_description = context.get('stage_description', 'No description available')
        stage_tasks = context.get('stage_tasks', [])
        project_structure = context.get('project_structure_instructions', '')
        coding_conventions = context.get('coding_conventions', '')
        workflow_config = context.get('workflow_config', {})

        enhanced_prompt = f"""
        <context>
        You are Claude, an AI language model. You are currently being directed by an automated LLM-Workflow Director as part of an AI-assisted software development process. The project is currently in the {workflow_stage} stage. Your task is to assist with the current workflow step. Please process the following information and respond accordingly.
        </context>

        Current Workflow Stage: {workflow_stage}
        Stage Description: {stage_description}
        Stage Tasks:
        {' '.join(f'- {task}' for task in stage_tasks)}

        Project Structure:
        {project_structure}

        Coding Conventions:
        {coding_conventions}

        Workflow Configuration:
        Stages: {', '.join(stage['name'] for stage in workflow_config.get('stages', []))}
        Transitions: {', '.join(f"{t['from']} -> {t['to']}" for t in workflow_config.get('transitions', []))}

        Given the above context, please respond to the following prompt:

        {prompt}

        Please structure your response using the following XML tags:
        <task_progress>
        [Provide a float value between 0 and 1 indicating the progress of the current task]
        </task_progress>

        <state_updates>
        [Provide any updates to the project state as key-value pairs]
        </state_updates>

        <actions>
        [List any actions that should be taken based on your response]
        </actions>

        <suggestions>
        [Provide any suggestions for the user or the workflow director]
        </suggestions>

        <response>
        [Your main response to the prompt]
        </response>
        """
        self.logger.debug(f"Enhanced prompt generated: {enhanced_prompt[:100]}...")
        return enhanced_prompt

    async def _generate_cache_key(self, prompt: str, context: Optional[Dict[str, Any]] = None, tier: str = 'balanced') -> str:
        if context is None:
            context = {}
        context_str = ','.join(f"{k}:{v}" for k, v in sorted(context.items()))
        return f"{prompt}|{context_str}|{tier}"

    async def _add_unique_id(self, response: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(response, dict):
            response = {"response": str(response)}
        current_time = time.time()
        unique_id = str(abs(hash(str(response) + str(current_time))))
        response['id'] = f"(ID: {unique_id})"
        return response

    async def evaluate_sufficiency(self, stage_name: str, stage_data: Dict[str, Any], project_state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Evaluating sufficiency for stage: {stage_name}")
        try:
            context = {
                'stage_name': stage_name,
                'stage_description': stage_data.get('description', 'No description available'),
                'stage_tasks': stage_data.get('tasks', []),
                'project_state': project_state,
                'workflow_history': project_state.get('workflow_history', [])
            }
            prompt = await self.generate_prompt('sufficiency_evaluation', context)
            response = await self.query(prompt, context=context, tier='balanced')
            self.logger.debug(f"Sufficiency evaluation response: {response}")
            evaluation = await self._parse_sufficiency_evaluation(response)
            return evaluation
        except Exception as e:
            self.logger.error(f"Error evaluating sufficiency: {str(e)}")
            return {"is_sufficient": False, "reasoning": f"Error evaluating sufficiency: {str(e)}"}

    async def _parse_sufficiency_evaluation(self, response: Dict[str, Any]) -> Dict[str, Any]:
        result = {'is_sufficient': False, 'reasoning': "No reasoning provided"}
        content = response.get('response', '')
        if isinstance(content, str):
            if '<evaluation>' in content and '</evaluation>' in content:
                evaluation = content.split('<evaluation>')[1].split('</evaluation>')[0].strip()
                result['is_sufficient'] = evaluation.upper() == 'SUFFICIENT'
            if '<reasoning>' in content and '</reasoning>' in content:
                result['reasoning'] = content.split('<reasoning>')[1].split('</reasoning>')[0].strip()
        elif isinstance(content, dict):
            result['is_sufficient'] = content.get('is_sufficient', False)
            result['reasoning'] = content.get('reasoning', "No reasoning provided")
        if not result['is_sufficient'] and result['reasoning'] == "No reasoning provided":
            result['reasoning'] = "Insufficient data provided in the response"
        return result

    async def _parse_structured_response(self, response: str) -> Dict[str, Any]:
        try:
            structured_response = {
                "task_progress": 0,
                "state_updates": {},
                "actions": [],
                "suggestions": [],
                "response": ""
            }
            current_tag = None
            current_content = []

            for line in response.split('\n'):
                line = line.strip()
                if line.startswith('<') and line.endswith('>'):
                    if current_tag:
                        structured_response[current_tag] = await self._process_value(current_tag, current_content)
                        current_content = []
                    current_tag = line[1:-1]
                elif current_tag:
                    current_content.append(line)

            if current_tag:
                structured_response[current_tag] = await self._process_value(current_tag, current_content)

            return structured_response
        except Exception as e:
            self.logger.error(f"Error parsing structured response: {str(e)}")
            return {
                "error": str(e),
                "response": response,
                "task_progress": 0,
                "state_updates": {},
                "actions": [],
                "suggestions": []
            }

    async def _process_value(self, key: str, value: List[str]) -> Any:
        joined_value = ' '.join(value).strip()
        try:
            if key == 'task_progress':
                return float(joined_value)
            elif key == 'state_updates':
                return ast.literal_eval(joined_value)
            elif key in ['actions', 'suggestions']:
                return [item.strip() for item in joined_value.split(',') if item.strip()]
            else:
                return joined_value
        except Exception as e:
            self.logger.error(f"Error processing value for key '{key}': {str(e)}")
            return joined_value

    async def generate_prompt(self, template_name: str, context: Dict[str, Any]) -> str:
        self.logger.debug(f"Generating prompt with template: {template_name}")
        try:
            template = self.prompt_templates.get(template_name, self.prompt_templates['default'])
            enhanced_context = await self._enhance_context(context)
            prompt = template.format(**enhanced_context)
            self.logger.debug(f"Generated prompt: {prompt[:100]}...")
            return prompt
        except KeyError as e:
            self.logger.error(f"Error generating prompt: Missing key {str(e)}", exc_info=True)
            return f"Error generating prompt: Missing key {str(e)}"
        except Exception as e:
            self.logger.error(f"Unexpected error generating prompt: {str(e)}", exc_info=True)
            return f"Unexpected error generating prompt: {str(e)}"

    async def _enhance_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        enhanced_context = context.copy()
        workflow_config = enhanced_context.get('workflow_config', {})
        current_stage = enhanced_context.get('workflow_stage')
        
        if current_stage and 'stages' in workflow_config:
            stage_info = next((s for s in workflow_config['stages'] if s['name'] == current_stage), None)
            if stage_info:
                enhanced_context['stage_description'] = stage_info.get('description', '')
                enhanced_context['stage_tasks'] = stage_info.get('tasks', [])
                enhanced_context['stage_priorities'] = stage_info.get('priorities', [])

        enhanced_context['available_transitions'] = await self._get_available_transitions(workflow_config, current_stage)
        enhanced_context['project_progress'] = await self._calculate_project_progress(workflow_config, context)

        self.logger.debug(f"Enhanced context: {enhanced_context}")
        return enhanced_context

    async def _get_available_transitions(self, workflow_config: Dict[str, Any], current_stage: str) -> List[str]:
        transitions = workflow_config.get('transitions', [])
        return [t['to'] for t in transitions if t['from'] == current_stage]

    async def _calculate_project_progress(self, workflow_config: Dict[str, Any], context: Dict[str, Any]) -> float:
        total_stages = len(workflow_config.get('stages', []))
        completed_stages = len(context.get('completed_stages', []))
        return completed_stages / total_stages if total_stages > 0 else 0

    async def clear_cache(self):
        self.cache.clear()
        self.logger.info("LLM response cache cleared.")

    async def _get_time(self) -> float:
        return time.time()

    async def _handle_error(self, prompt: str, context: Optional[Dict[str, Any]], tier: str, error: Exception) -> Dict[str, Any]:
        self.logger.error(f"Error in LLM query: {str(error)}")
        await self.cost_optimizer.update_usage(tier, 0, 0, False)
        if isinstance(error, NotFoundError):
            tier = await self._get_fallback_tier(tier)
            if tier:
                return await self.query(prompt, context, tier=tier)
        return await self._fallback_response(prompt, context, tier)

    async def _fallback_response(self, prompt: str, context: Optional[Dict[str, Any]], tier: str) -> Dict[str, Any]:
        self.logger.warning(f"Fallback response triggered for tier: {tier}")
        return {
            "response": "I apologize, but I'm unable to process your request at the moment. Please try again later.",
            "error": f"All LLM tiers failed. Using fallback response. (tier: {tier})",
            "tier": tier,
            "task_progress": 0,
            "state_updates": {},
            "actions": [],
            "suggestions": ["Please try rephrasing your query.", "Check your internet connection.", "Contact support if the issue persists."],
            "raw_response": "",
            "token_usage": {"input": 0, "output": 0, "total": 0}
        }
