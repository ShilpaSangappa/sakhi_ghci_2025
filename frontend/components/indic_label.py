"""
Custom Label widget with Indic font support
"""

from kivy.uix.label import Label
from kivy.uix.button import Button

class IndicLabel(Label):
    """Label that supports Indic scripts"""

    def __init__(self, **kwargs):
        # Set font to support Indic languages
        if 'font_name' not in kwargs:
            kwargs['font_name'] = 'Indic'
        super().__init__(**kwargs)

class IndicButton(Button):
    """Button that supports Indic scripts"""

    def __init__(self, **kwargs):
        # Set font to support Indic languages
        if 'font_name' not in kwargs:
            kwargs['font_name'] = 'Indic'
        super().__init__(**kwargs)
