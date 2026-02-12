"""
Automation Module for ELIXI AI
Provides custom commands, workflow automation, habit learning, and suggestions.
"""

from .custom_commands import CustomCommandManager
from .workflows import WorkflowManager
from .habit_learning import HabitLearningEngine
from .suggestion_engine import SuggestionEngine

__all__ = [
    'CustomCommandManager',
    'WorkflowManager',
    'HabitLearningEngine', 
    'SuggestionEngine',
]
