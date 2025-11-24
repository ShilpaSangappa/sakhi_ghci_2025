"""
Quick script to check which fonts are available for Indic languages
"""

import os

print("Checking for Indic-compatible fonts on Windows...\n")

font_options = [
    ('C:/Windows/Fonts/NirmalaUI.ttf', 'Nirmala UI (Supports Hindi, Tamil, Kannada)'),
    ('C:/Windows/Fonts/Nirmala.ttc', 'Nirmala TTC Collection'),
    ('C:/Windows/Fonts/seguisym.ttf', 'Segoe UI Symbol'),
    ('C:/Windows/Fonts/mangal.ttf', 'Mangal (Hindi/Devanagari)'),
    ('C:/Windows/Fonts/latha.ttf', 'Latha (Tamil)'),
    ('C:/Windows/Fonts/tunga.ttf', 'Tunga (Kannada)'),
    ('C:/Windows/Fonts/arial.ttf', 'Arial (Fallback)'),
]

found_fonts = []
missing_fonts = []

for font_path, description in font_options:
    if os.path.exists(font_path):
        print(f"[FOUND] {font_path}")
        print(f"        {description}\n")
        found_fonts.append(font_path)
    else:
        print(f"[MISSING] {font_path}")
        print(f"          {description}\n")
        missing_fonts.append(font_path)

print(f"\n{'='*60}")
print(f"Summary: {len(found_fonts)} fonts found, {len(missing_fonts)} missing")
print(f"{'='*60}\n")

if found_fonts:
    print(f"Recommended font to use: {found_fonts[0]}")
else:
    print("⚠ WARNING: No Indic-compatible fonts found!")
    print("\nTo fix this:")
    print("1. Go to Windows Settings > Time & Language > Language")
    print("2. Add Hindi, Tamil, or Kannada language")
    print("3. Download the language pack")
    print("4. Restart your computer")
    print("\nOr install fonts manually from:")
    print("https://www.microsoft.com/typography/fonts/family.aspx?FID=343")
