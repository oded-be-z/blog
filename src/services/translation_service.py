"""
Translation Service
Implements SKILL_multilingual_content.md best practices
Professional translations for GCC Arabic, Spanish, Portuguese
"""

from typing import Dict, List
from loguru import logger
from services.azure_openai_client import AzureOpenAIClient


class TranslationService:
    """
    Professional translation service following SKILL_multilingual_content.md
    Supports: English, GCC Arabic, Latin American Spanish, Brazilian Portuguese
    """

    def __init__(self):
        self.openai_client = AzureOpenAIClient()

        # Language configurations from SKILL_multilingual_content.md
        self.languages = {
            "arabic_gcc": {
                "name": "Arabic (Gulf/GCC)",
                "code": "ar",
                "tone": "Professional, respectful, trustworthy",
                "special_handling": "Islamic finance terminology"
            },
            "spanish": {
                "name": "Spanish (Latin America)",
                "code": "es",
                "tone": "Energetic, opportunity-focused",
                "special_handling": "Neutral LATAM dialect"
            },
            "portuguese": {
                "name": "Portuguese (Brazilian)",
                "code": "pt-BR",
                "tone": "Warm, community-oriented",
                "special_handling": "Brazilian context"
            }
        }

    def translate_article(
        self,
        english_content: str,
        target_language: str,
        category: str = "trading"
    ) -> Dict:
        """
        Translate article to target language with professional quality

        Args:
            english_content: Source English content
            target_language: arabic_gcc, spanish, or portuguese
            category: Context (forex, crypto, commodities)

        Returns:
            Dict with translated content and quality metadata
        """
        logger.info(f"Translating to {target_language}...")

        result = self.openai_client.translate_content(
            text=english_content,
            target_language=target_language,
            context=f"{category} article"
        )

        if result["success"]:
            translated = result["content"]

            # Quality validation
            quality_score = self._validate_translation_quality(
                source=english_content,
                translated=translated,
                language=target_language
            )

            return {
                "success": True,
                "translated_content": translated,
                "language": target_language,
                "language_code": self.languages[target_language]["code"],
                "quality_score": quality_score,
                "word_count": len(translated.split())
            }
        else:
            logger.error(f"Translation failed for {target_language}: {result.get('error')}")
            return result

    def translate_to_all_languages(
        self,
        english_content: str,
        category: str = "trading"
    ) -> Dict[str, Dict]:
        """
        Translate article to all supported languages

        Args:
            english_content: Source English content
            category: Context for translation

        Returns:
            Dict mapping language to translation result
        """
        translations = {}

        for lang_key in ["arabic_gcc", "spanish", "portuguese"]:
            result = self.translate_article(
                english_content=english_content,
                target_language=lang_key,
                category=category
            )
            translations[lang_key] = result

        logger.success(f"Completed {len(translations)} translations")
        return translations

    def _validate_translation_quality(
        self,
        source: str,
        translated: str,
        language: str
    ) -> int:
        """
        Validate translation quality

        Args:
            source: Original English text
            translated: Translated text
            language: Target language

        Returns:
            Quality score (0-100)
        """
        # Basic quality checks
        score = 100

        # Length check (translation should be similar length ±30%)
        source_len = len(source.split())
        translated_len = len(translated.split())

        if translated_len < source_len * 0.7 or translated_len > source_len * 1.3:
            score -= 20
            logger.warning(f"Translation length mismatch: {translated_len} vs {source_len}")

        # Check for untranslated placeholders
        placeholders = ["[INSERT]", "[TODO]", "{{", "}}"]
        for placeholder in placeholders:
            if placeholder in translated:
                score -= 30
                logger.warning(f"Found placeholder in translation: {placeholder}")

        # Language-specific checks
        if language == "arabic_gcc":
            # Check for Arabic characters
            if not any('\u0600' <= char <= '\u06FF' for char in translated):
                score -= 50
                logger.error("No Arabic characters found in Arabic translation!")

        logger.info(f"Translation quality score: {score}/100")
        return score

    def get_terminology_glossary(self, category: str) -> Dict[str, Dict[str, str]]:
        """
        Get trading terminology glossary from SKILL_multilingual_content.md

        Args:
            category: forex, crypto, or commodities

        Returns:
            Dict mapping English terms to translations
        """
        # From SKILL_multilingual_content.md terminology table
        glossary = {
            "Trading": {
                "arabic": "التداول (at-tadawul)",
                "spanish": "Operaciones / Trading",
                "portuguese": "Negociação"
            },
            "Broker": {
                "arabic": "وسيط (waseet)",
                "spanish": "Bróker / Corredor",
                "portuguese": "Corretora"
            },
            "Profit": {
                "arabic": "ربح (ribh)",
                "spanish": "Ganancia",
                "portuguese": "Lucro"
            },
            "Loss": {
                "arabic": "خسارة (khasara)",
                "spanish": "Pérdida",
                "portuguese": "Prejuízo"
            },
            "Margin": {
                "arabic": "الهامش (al-hamish)",
                "spanish": "Margen",
                "portuguese": "Margem"
            },
            "Leverage": {
                "arabic": "الرافعة المالية (ar-rafi'a al-maliyya)",
                "spanish": "Apalancamiento",
                "portuguese": "Alavancagem"
            }
        }

        return glossary
