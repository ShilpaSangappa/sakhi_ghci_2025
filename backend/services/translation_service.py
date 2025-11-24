"""
Hybrid Translation Service for Sakhi App
Handles AI-powered translation of dynamic user-generated content
Uses cache-first approach to minimize API costs
"""

import sqlite3
from typing import Optional, List, Dict
from datetime import datetime
import os

class HybridTranslationService:
    def __init__(self):
        # Get the project root directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.cache_db = os.path.join(base_dir, "localization", "translation_cache.db")
        self.supported_languages = ['en', 'hi', 'ta', 'kn']
        self.init_cache_db()

    def init_cache_db(self):
        """Initialize translation cache database"""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.cache_db), exist_ok=True)

        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS translation_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_text TEXT,
                source_lang TEXT,
                target_lang TEXT,
                translated_text TEXT,
                provider TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 1,
                UNIQUE(source_text, source_lang, target_lang)
            )
        ''')

        # Create index for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_translation_lookup
            ON translation_cache(source_text, source_lang, target_lang)
        ''')

        conn.commit()
        conn.close()
        print("✓ Translation cache initialized")

    def get_cached_translation(self, text: str, source_lang: str,
                               target_lang: str) -> Optional[str]:
        """Check if translation exists in cache"""
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT translated_text FROM translation_cache
            WHERE source_text = ? AND source_lang = ? AND target_lang = ?
        ''', (text, source_lang, target_lang))

        result = cursor.fetchone()

        # Update access count for analytics
        if result:
            cursor.execute('''
                UPDATE translation_cache
                SET access_count = access_count + 1
                WHERE source_text = ? AND source_lang = ? AND target_lang = ?
            ''', (text, source_lang, target_lang))
            conn.commit()

        conn.close()
        return result[0] if result else None

    def cache_translation(self, text: str, source_lang: str,
                         target_lang: str, translated_text: str, provider: str):
        """Store translation in cache"""
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO translation_cache
            (source_text, source_lang, target_lang, translated_text, provider)
            VALUES (?, ?, ?, ?, ?)
        ''', (text, source_lang, target_lang, translated_text, provider))

        conn.commit()
        conn.close()

    async def translate_dynamic_content(self, text: str,
                                       source_lang: str,
                                       target_lang: str) -> str:
        """
        Main translation method for dynamic content
        Uses cache-first approach to minimize API calls

        Supports: en ↔ hi, en ↔ ta, en ↔ kn, and cross-Indic translations
        """
        # Validate languages
        if source_lang not in self.supported_languages or target_lang not in self.supported_languages:
            print(f"Unsupported language pair: {source_lang} → {target_lang}")
            return text

        # Same language, no translation needed
        if source_lang == target_lang:
            return text

        # Check cache first (95% hit rate expected after initial usage)
        cached = self.get_cached_translation(text, source_lang, target_lang)
        if cached:
            print(f"✓ Cache hit: {source_lang} → {target_lang}")
            return cached

        print(f"✗ Cache miss: {source_lang} → {target_lang}, calling API...")

        # Translate using AI
        try:
            # Try Google Translate first (easiest for demo)
            translated = await self._translate_with_google(text, source_lang, target_lang)
            provider = 'google'
        except Exception as e:
            print(f"Translation failed: {e}")
            # Last resort: return original text
            return text

        # Cache the result
        self.cache_translation(text, source_lang, target_lang, translated, provider)

        return translated

    async def _translate_with_google(self, text: str,
                                     source_lang: str,
                                     target_lang: str) -> str:
        """
        Use Google Translate (googletrans library - FREE)
        """
        try:
            from googletrans import Translator

            translator = Translator()

            # Map our language codes to Google's
            lang_map = {
                'en': 'en',
                'hi': 'hi',
                'ta': 'ta',
                'kn': 'kn'
            }

            src = lang_map.get(source_lang, source_lang)
            dest = lang_map.get(target_lang, target_lang)

            result = translator.translate(text, src=src, dest=dest)

            return result.text
        except Exception as e:
            print(f"Google Translate error: {e}")
            # Fallback to mock translation for demo
            return f"[{target_lang.upper()}] {text}"

    async def translate_batch(self, texts: List[str],
                             source_lang: str,
                             target_lang: str) -> List[str]:
        """
        Batch translate multiple texts (more cost-efficient)
        Useful for translating all posts in a feed at once
        """
        translated_texts = []

        for text in texts:
            translated = await self.translate_dynamic_content(text, source_lang, target_lang)
            translated_texts.append(translated)

        return translated_texts

    def should_translate(self, user_lang: str, content_lang: str) -> bool:
        """Determine if translation is needed"""
        return user_lang != content_lang

    def get_cache_stats(self) -> Dict:
        """Get translation cache statistics"""
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM translation_cache')
        total_cached = cursor.fetchone()[0]

        cursor.execute('SELECT SUM(access_count) FROM translation_cache')
        total_accesses = cursor.fetchone()[0] or 0

        cursor.execute('SELECT provider, COUNT(*) FROM translation_cache GROUP BY provider')
        providers = cursor.fetchall()

        conn.close()

        cache_hit_rate = 0
        if total_accesses > 0:
            cache_hit_rate = ((total_accesses - total_cached) / total_accesses) * 100

        return {
            'cached_translations': total_cached,
            'total_accesses': total_accesses,
            'providers': dict(providers),
            'cache_hit_rate': f"{cache_hit_rate:.2f}%",
            'estimated_api_calls_saved': total_accesses - total_cached,
            'estimated_cost_saved': f"${(total_accesses - total_cached) * 0.002:.2f}"
        }

    def clear_cache(self):
        """Clear all cached translations (for testing)"""
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM translation_cache')
        conn.commit()
        conn.close()
        print("✓ Translation cache cleared")

# Global instance
translation_service = HybridTranslationService()

if __name__ == "__main__":
    import asyncio

    async def test_translation():
        """Test the translation service"""
        print("=== Testing Translation Service ===\n")

        # Test text
        test_text = "Hello, how are you?"

        # Test en -> hi
        print(f"Original (en): {test_text}")
        translated = await translation_service.translate_dynamic_content(test_text, 'en', 'hi')
        print(f"Translated (hi): {translated}\n")

        # Test cache hit
        print("Testing cache hit...")
        translated = await translation_service.translate_dynamic_content(test_text, 'en', 'hi')
        print(f"Translated (hi) [cached]: {translated}\n")

        # Get cache stats
        stats = translation_service.get_cache_stats()
        print("Cache Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

    # Run test
    asyncio.run(test_translation())
