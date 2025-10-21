"""
Content Generation Agent
Orchestrates the complete article creation workflow:
- Market research via Perplexity
- Content generation via GPT-5
- Translation via GPT-5
- SEO optimization
- HTML formatting
"""

import asyncio
from typing import Dict
from datetime import datetime
from loguru import logger

from services.perplexity_client import PerplexityClient
from services.azure_openai_client import AzureOpenAIClient
from services.translation_service import TranslationService
from services.image_manager import ImageManager
from services.html_formatter import HTMLFormatter
from services.quality_validator import QualityValidator
from config.prompts import get_article_generation_prompt


class ContentGenerationAgent:
    """Autonomous agent for generating multilingual trading blog articles"""

    def __init__(self, category: str, worktree_path: str):
        """
        Initialize content generation agent

        Args:
            category: forex, crypto, or commodities
            worktree_path: Path to git worktree for this agent
        """
        self.category = category
        self.worktree_path = worktree_path

        # Initialize service clients
        self.perplexity = PerplexityClient()
        self.openai = AzureOpenAIClient()
        self.translator = TranslationService()
        self.image_manager = ImageManager()
        self.html_formatter = HTMLFormatter()
        self.validator = QualityValidator()

        logger.info(f"Initialized {category} content generation agent")

    async def generate_article(self) -> Dict:
        """
        Execute complete article generation workflow

        Returns:
            Dict with complete article package including all languages
        """
        logger.info(f"🚀 Starting {self.category} article generation...")

        try:
            # Phase 1: Market Research
            logger.info(f"📊 Phase 1: Market Research via Perplexity")
            market_data = await self._research_market()

            if not market_data["success"]:
                logger.error(f"Market research failed: {market_data.get('error')}")
                return {"success": False, "error": "Market research failed"}

            # Select best asset to write about
            asset_data = self.perplexity.select_best_asset(market_data, self.category)
            logger.success(f"Selected asset: {asset_data['asset']}")

            # Phase 2: Generate English Article
            logger.info(f"✍️ Phase 2: Generating English article with GPT-5-Pro")
            english_article = await self._generate_english_article(asset_data)

            if not english_article["success"]:
                logger.error(f"Article generation failed: {english_article.get('error')}")
                return {"success": False, "error": "Article generation failed"}

            # Phase 2.5: Validate and Improve Article Quality
            logger.info(f"🔍 Phase 2.5: Validating article quality with AI")
            validation_result = self.validator.validate_article(
                article=english_article["content"],
                category=self.category,
                asset=asset_data["asset"]
            )

            logger.info(f"Quality score: {validation_result.get('quality_score', 0)}/100")
            logger.info(f"Recommendation: {validation_result.get('recommendation', 'UNKNOWN')}")

            if validation_result.get("recommendation") == "IMPROVE":
                logger.warning(f"Article needs improvement. Issues: {validation_result.get('issues', [])}")
                improved_article = self.validator.improve_article_if_needed(
                    article=english_article["content"],
                    validation_result=validation_result,
                    category=self.category,
                    asset=asset_data["asset"]
                )
                english_article["content"] = improved_article
                logger.success("Article improved based on AI feedback")
            elif validation_result.get("recommendation") == "REJECT":
                logger.error(f"Article quality too low (score: {validation_result.get('quality_score')})")
                return {"success": False, "error": "Article quality below acceptable threshold"}
            else:
                logger.success(f"Article quality validated (score: {validation_result.get('quality_score')})")

            # Phase 3: Generate SEO Metadata
            logger.info(f"🎯 Phase 3: Generating SEO metadata")
            seo_metadata = self._generate_seo_metadata(
                english_article["content"],
                asset_data["asset"]
            )

            # Phase 4: Select Image
            logger.info(f"🖼️ Phase 4: Selecting relevant image")
            image_data = self.image_manager.get_image_for_asset(
                category=self.category,
                asset=asset_data["asset"]
            )

            # Phase 5: Translate to 3 Languages
            logger.info(f"🌍 Phase 5: Translating to 3 languages")
            translations = await self._translate_article(english_article["content"])

            # Phase 6: Create HTML for all languages
            logger.info(f"📄 Phase 6: Creating HTML for 4 languages")
            article_package = self._create_article_package(
                asset_data=asset_data,
                english_article=english_article["content"],
                translations=translations,
                seo_metadata=seo_metadata,
                image_data=image_data
            )

            logger.success(f"✅ {self.category} article generation completed!")
            return {
                "success": True,
                "package": article_package
            }

        except Exception as e:
            logger.error(f"❌ Article generation failed: {e}")
            logger.exception(e)
            return {"success": False, "error": str(e)}

    async def _research_market(self) -> Dict:
        """Research market using Perplexity API"""
        research_methods = {
            "forex": self.perplexity.research_forex_market,
            "crypto": self.perplexity.research_crypto_market,
            "commodities": self.perplexity.research_commodities_market
        }

        research_method = research_methods.get(self.category)
        if not research_method:
            return {"success": False, "error": f"Unknown category: {self.category}"}

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, research_method)

        return result

    async def _generate_english_article(self, asset_data: Dict) -> Dict:
        """Generate English article using GPT-5-Pro"""
        prompt = get_article_generation_prompt(
            category=self.category,
            asset=asset_data["asset"],
            market_data=asset_data
        )

        # Run in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self.openai.generate_article,
            prompt,
            "gpt-5-pro"  # Use GPT-5-Pro for superior content generation
        )

        return result

    def _generate_seo_metadata(self, article: str, asset: str) -> Dict:
        """Generate SEO metadata"""
        result = self.openai.generate_seo_metadata(
            article=article,
            category=self.category,
            asset=asset
        )

        if result["success"]:
            return result["metadata"]
        else:
            # Use fallback
            logger.warning("Using fallback SEO metadata")
            return self.openai._get_fallback_seo(self.category, asset)["metadata"]

    async def _translate_article(self, english_text: str) -> Dict:
        """Translate article to 3 languages concurrently"""
        languages = ["arabic_gcc", "spanish", "portuguese"]

        # Create translation tasks
        tasks = []
        for lang in languages:
            task = asyncio.create_task(
                self._translate_to_language(english_text, lang)
            )
            tasks.append((lang, task))

        # Wait for all translations
        translations = {}
        for lang, task in tasks:
            result = await task
            translations[lang] = result

        return translations

    async def _translate_to_language(self, text: str, language: str) -> Dict:
        """Translate to a specific language with validation and retry"""
        logger.info(f"Translating to {language}...")

        max_retries = 3
        for attempt in range(max_retries):
            if attempt > 0:
                logger.info(f"Retry attempt {attempt + 1}/{max_retries} for {language} translation")

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.openai.translate_content,
                text,
                language,
                self.category
            )

            if result["success"]:
                # Validate translation quality
                validation = self.validator.validate_translation(
                    original=text,
                    translated=result["content"],
                    language=language,
                    category=self.category
                )

                if validation.get("recommendation") == "RETRY":
                    logger.warning(f"{language} translation validation failed: {validation.get('issues', [])}")
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying {language} translation due to quality issues")
                        continue
                    else:
                        logger.error(f"{language} translation failed validation after {max_retries} attempts")
                        return {
                            "success": False,
                            "error": f"Translation validation failed: {validation.get('issues', [])}"
                        }

                logger.success(f"{language} translation completed and validated (score: {validation.get('quality_score', 0)})")
                return {
                    "success": True,
                    "translated_content": result["content"],
                    "word_count": len(result["content"].split()),
                    "quality_score": validation.get("quality_score", 0)
                }
            else:
                logger.warning(f"{language} translation attempt {attempt + 1} failed: {result.get('error')}")
                if attempt < max_retries - 1:
                    continue

        logger.error(f"{language} translation failed after {max_retries} attempts")
        return {
            "success": False,
            "error": f"Translation failed after {max_retries} attempts"
        }

    def _create_article_package(
        self,
        asset_data: Dict,
        english_article: str,
        translations: Dict,
        seo_metadata: Dict,
        image_data: Dict
    ) -> Dict:
        """Create complete article package with all languages"""

        return self.html_formatter.create_article_package(
            category=self.category,
            asset=asset_data["asset"],
            market_data=asset_data,
            english_article=english_article,
            translations=translations,
            seo_metadata=seo_metadata,
            image_data=image_data
        )


# Convenience functions for orchestrator
async def generate_forex_article(worktree_path: str) -> Dict:
    """Generate forex article"""
    agent = ContentGenerationAgent("forex", worktree_path)
    return await agent.generate_article()


async def generate_crypto_article(worktree_path: str) -> Dict:
    """Generate crypto article"""
    agent = ContentGenerationAgent("crypto", worktree_path)
    return await agent.generate_article()


async def generate_commodities_article(worktree_path: str) -> Dict:
    """Generate commodities article"""
    agent = ContentGenerationAgent("commodities", worktree_path)
    return await agent.generate_article()
