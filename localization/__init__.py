"""
Localization package for Sakhi App
"""

from .translation_manager import (
    translator,
    get_text,
    get_text_formatted,
    set_language,
    get_current_language
)

__all__ = [
    'translator',
    'get_text',
    'get_text_formatted',
    'set_language',
    'get_current_language'
]
