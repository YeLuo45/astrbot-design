"""
Multi-Agent Collaboration System - Configuration
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AgentConfig:
    """Configuration for a single agent"""

    id: str
    name: str
    type: str  # "coordinator", "specialist", "critic"
    domain: Optional[str] = None
    max_retries: int = 3
    timeout: float = 60.0
    metadata: Dict = field(default_factory=dict)


@dataclass
class MultiAgentConfig:
    """Configuration for multi-agent system"""

    enabled: bool = True
    max_parallel: int = 5
    timeout: float = 300.0
    retry: int = 3
    default_team: str = "code-review"
    heartbeat_interval: float = 30.0
    context_ttl: int = 3600

    agent_teams: Dict[str, List[AgentConfig]] = field(default_factory=dict)

    def get_team(self, name: str) -> List[AgentConfig]:
        """Get team configuration by name"""
        return self.agent_teams.get(name, [])

    def add_team(self, name: str, agents: List[AgentConfig]):
        """Add a team configuration"""
        self.agent_teams[name] = agents


# Default team configurations
DEFAULT_CODE_REVIEW_TEAM = "code-review"
DEFAULT_RESEARCH_TEAM = "research"
DEFAULT_DEBATE_TEAM = "debate"


def get_default_code_review_team() -> List[AgentConfig]:
    """Get default code review team configuration"""
    return [
        AgentConfig(id="coordinator", name="Coordinator", type="coordinator"),
        AgentConfig(id="code-generator", name="CodeGenerator", type="specialist", domain="code"),
        AgentConfig(id="code-reviewer", name="CodeReviewer", type="specialist", domain="code-review"),
        AgentConfig(id="code-critic", name="CodeCritic", type="critic", domain="code-quality"),
    ]


def get_default_research_team() -> List[AgentConfig]:
    """Get default research team configuration"""
    return [
        AgentConfig(id="coordinator", name="Coordinator", type="coordinator"),
        AgentConfig(id="web-searcher", name="WebSearcher", type="specialist", domain="web-search"),
        AgentConfig(id="doc-analyzer", name="DocAnalyzer", type="specialist", domain="document-analysis"),
        AgentConfig(id="synthesizer", name="Synthesizer", type="specialist", domain="synthesis"),
    ]


def get_default_debate_team() -> List[AgentConfig]:
    """Get default debate team configuration"""
    return [
        AgentConfig(id="coordinator", name="Coordinator", type="coordinator"),
        AgentConfig(id="pro-arguer", name="ProArguer", type="specialist", domain="pro-argument"),
        AgentConfig(id="con-arguer", name="ConArguer", type="specialist", domain="con-argument"),
        AgentConfig(id="debate-judge", name="DebateJudge", type="critic", domain="debate-judgment"),
    ]


def create_default_config() -> MultiAgentConfig:
    """Create default multi-agent configuration"""
    config = MultiAgentConfig()
    config.add_team(DEFAULT_CODE_REVIEW_TEAM, get_default_code_review_team())
    config.add_team(DEFAULT_RESEARCH_TEAM, get_default_research_team())
    config.add_team(DEFAULT_DEBATE_TEAM, get_default_debate_team())
    return config
