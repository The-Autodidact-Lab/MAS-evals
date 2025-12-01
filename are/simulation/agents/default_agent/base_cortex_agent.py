import uuid
from typing import Any
from cortex.context_cortex import ContextCortex
from cortex.cortex_agent import CortexAgent
from are.simulation.agents.default_agent.base_agent import (
    BaseAgent,
    ConditionalStep,
)
from are.simulation.agents.llm.types import MessageRole


class BaseCortexAgent(BaseAgent):
    """
    Base agent with cortex integration hooks.
    
    Extends BaseAgent to add conditional pre/post-steps for cortex integration,
    enabling automatic trace ingestion and context sharing.
    
    Subclasses should call super().__init__() with BaseAgent parameters plus
    cortex, cortex_agent, agent_id, and agent_mask.
    """
    
    cortex: ContextCortex
    cortex_agent: CortexAgent
    agent_id: str
    agent_mask: int
    _last_cortex_ingestion_index: int

    def __init__(
        self,
        cortex: ContextCortex,
        cortex_agent: CortexAgent,
        agent_id: str,
        agent_mask: int,
        **kwargs: Any,  # BaseAgent parameters
    ):
        super().__init__(**kwargs)
        
        # set up cortex
        self.cortex = cortex
        self.cortex_agent = cortex_agent
        self.agent_id = agent_id
        self.agent_mask = agent_mask
        self._last_cortex_ingestion_index = -1
        
        # automatically register agent with cortex
        if self.cortex:
            self.cortex.register_agent(
                agent_id=self.agent_id,
                mask=self.agent_mask,
            )

        # register post-step cortex hook
        self._register_cortex_hooks()
    
    def _register_cortex_hooks(self) -> None:
        """Register conditional post-step hook for cortex trace ingestion."""
        self.conditional_post_steps.append(
            ConditionalStep(
                condition=None,  # Always run
                function=self._cortex_post_step,
                name=f"{self.agent_id}_cortex_post",
            )
        )
    
    def build_history_from_logs(
        self, exclude_log_types: list[str] = []
    ) -> list[dict[str, Any]]:
        """
        Override for default history build in order to add cortex episodes.
        """
        # build from history first to prevent overwriting our changes later
        history = super().build_history_from_logs(exclude_log_types)
        
        # inject cortex episodes into system prompt
        if self.cortex:
            cortex_episodes = self.cortex.get_episodes_for_agent(
                self.agent_id, include_raw=False
            )
            if cortex_episodes:
                # build structured text from cortex
                cortex_context_lines = [
                    f"- [{ep.source_agent_id}]: {ep.summary or f'Context from {ep.source_agent_id}'}"
                    for ep in cortex_episodes
                ]
                cortex_context_content = "\n".join(cortex_context_lines)
                cortex_section = f"\n\n<relevant_multiagent_context>\n{cortex_context_content}\n</relevant_multiagent_context>"
                
                for msg in history:
                    role = msg.get("role")
                    # Handle both MessageRole enum and string comparison
                    if role == MessageRole.SYSTEM or (isinstance(role, str) and role == "system"):
                        msg["content"] += cortex_section
                        break
        
        return history

    
    def _cortex_post_step(self, agent: BaseAgent) -> None:
        """
        Post-step hook: Ingest agent's step trace into cortex.
        
        This runs after each step to extract the trace and ingest it into
        the shared cortex with appropriate access masks.
        """
        if self.cortex is None or self.cortex_agent is None:
            return
        
        # Extract step trace since last ingestion
        last_idx = self._last_cortex_ingestion_index
        current_logs = self.logs[last_idx - 4 :] # inject contextual logs
        
        if not current_logs:
            return
        
        # reformat trace from logs
        trace = {
            "agent_id": self.agent_id,
            "logs": [
                {
                    "type": log.get_type(),
                    "content": log.get_content_for_llm() if hasattr(log, "get_content_for_llm") else str(log),
                    "timestamp": log.timestamp,
                }
                for log in current_logs[-1:]
            ],
        }
        
        # ingest trace
        episode_id = f"{self.agent_id}_ep_{uuid.uuid4().hex[:8]}"

        _ = self.cortex_agent.run(
            episode_id=episode_id,
            source_agent_id=self.agent_id,
            raw_trace=trace,
            metadata={"step": self.iterations, "timestamp": self.make_timestamp()},
        )
        
        self._last_cortex_ingestion_index = len(self.logs) - 1