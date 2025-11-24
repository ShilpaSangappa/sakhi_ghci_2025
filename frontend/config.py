"""
Configuration for Sakhi App
Sets up fonts for Indic language support
"""

from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.config import Config
import os

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Configure Kivy for better text rendering
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')

def setup_fonts():
    """Register fonts that support Indic scripts"""

    # Try to register system fonts that support Indic languages
    # Windows: Uses Nirmala UI (Hindi), Latha (Tamil), Tunga (Kannada)
    # Linux: Uses Lohit fonts
    # Mac: Uses system fonts

    try:
        # For Windows
        if os.name == 'nt':
            # Try multiple font options for Indic language support
            font_options = [
                'C:/Windows/Fonts/NirmalaUI.ttf',  # Nirmala UI (correct filename)
                'C:/Windows/Fonts/Nirmala.ttc',    # TrueType Collection
                'C:/Windows/Fonts/seguisym.ttf',   # Segoe UI Symbol
                'C:/Windows/Fonts/mangal.ttf',     # Mangal (Devanagari/Hindi)
                'C:/Windows/Fonts/arial.ttf'       # Fallback
            ]

            font_path = None
            for font in font_options:
                if os.path.exists(font):
                    font_path = font
                    print(f"✓ Found font: {font}")
                    break

            if not font_path:
                # If no font found, try to use system default
                print("⚠ No Indic-compatible font found, using Kivy default")
                return

            # Register as default font so all widgets use it
            LabelBase.register(
                DEFAULT_FONT,
                fn_regular=font_path,
                fn_bold=font_path,
                fn_italic=font_path,
                fn_bolditalic=font_path
            )

            print(f"✓ Indic fonts registered successfully using: {font_path}")

        # For Linux (including WSL)
        elif os.name == 'posix':
            # Get the directory where this config file is located
            current_dir = os.path.dirname(os.path.abspath(__file__))

            # Try fonts in priority order - Local fonts first, then Windows fonts
            font_paths = [
                # Local fonts (Hindi, Kannada, Tamil support via Nirmala)
                os.path.join(current_dir, 'fonts', 'Nirmala.ttf'),
                # WSL - Access Windows fonts (best Indic support)
                '/c/Windows/Fonts/Nirmala.ttf',
                '/c/Windows/Fonts/mangal.ttf',
                '/mnt/c/Windows/Fonts/Nirmala.ttc',
                '/mnt/c/Windows/Fonts/mangal.ttf',
                # Linux native fonts
                '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf',
                '/usr/share/fonts/truetype/lohit-devanagari/Lohit-Devanagari.ttf',
                # Fallback (limited Indic support)
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
            ]

            font_registered = False
            for font_path in font_paths:
                if os.path.exists(font_path):
                    # Register with bold variant if available
                    bold_path = font_path.replace('Nirmala.ttf', 'NirmalaB.ttf')
                    if os.path.exists(bold_path):
                        LabelBase.register(
                            DEFAULT_FONT,
                            fn_regular=font_path,
                            fn_bold=bold_path
                        )
                    else:
                        LabelBase.register(
                            DEFAULT_FONT,
                            fn_regular=font_path
                        )
                    print(f"✓ Indic fonts registered using: {font_path}")
                    font_registered = True
                    break

            if not font_registered:
                print("⚠ No suitable font found for Indic languages")

        # For Mac
        else:
            # Mac has good default font support for Indic languages
            print("✓ Using system fonts (Mac)")

    except Exception as e:
        print(f"⚠ Warning: Could not register Indic fonts: {e}")
        print("  Hindi/Tamil/Kannada text may not display correctly")
        print("  The app will still work, but with placeholder boxes")
        print("\n  To fix:")
        print("  - Windows: Make sure Nirmala UI font is installed")
        print("  - Linux: Install fonts-noto package")
        print("  - Mac: System fonts should work by default")

def get_font_name():
    """Get the font name to use for labels"""
    return DEFAULT_FONT
