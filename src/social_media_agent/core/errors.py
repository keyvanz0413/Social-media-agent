"""Unified error codes for tool/workflow observability."""

from enum import Enum


class ErrorCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    MCP_ERROR = "MCP_ERROR"
    LLM_ERROR = "LLM_ERROR"
    MEMORY_ERROR = "MEMORY_ERROR"
    SCHEDULER_ERROR = "SCHEDULER_ERROR"
    REVIEW_ERROR = "REVIEW_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"

