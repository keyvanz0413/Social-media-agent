"""
Sub-agents for the social media multi-agent system.
Each agent is implemented as a tool function for the main coordinator agent.
"""

from social_media_agent.tools.langchain_tools import get_structured_tools

__all__ = ["get_structured_tools"]
