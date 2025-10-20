"""
Azure OpenAI Client
Wrapper for Azure OpenAI MCP tools: consult_gpt5, consult_gpt5_pro, consult_gpt5_codex
"""

import requests
from typing import Dict, Optional
from loguru import logger
from ..config.credentials import (
    AZURE_OPENAI_KEY,
    AZURE_OPENAI_ENDPOINT,
    GPT5_DEPLOYMENT,
    GPT5_PRO_DEPLOYMENT,
    get_api_headers
)


class AzureOpenAIClient:
    """Client for Azure OpenAI GPT-5 models"""

    def __init__(self):
        self.api_key = AZURE_OPENAI_KEY
        self.endpoint = AZURE_OPENAI_ENDPOINT
        self.headers = get_api_headers("azure_openai")

    def generate_article(
        self,
        prompt: str,
        deployment: str = GPT5_DEPLOYMENT,
        max_tokens: int = 1500,
        temperature: float = 0.7
    ) -> Dict:
        """
        Generate article content using GPT-5

        Args:
            prompt: Article generation prompt
            deployment: GPT-5 model deployment name
            max_tokens: Maximum tokens in response
            temperature: Creativity level (0-1)

        Returns:
            Dict with generated content
        """
        url = f"{self.endpoint}openai/deployments/{deployment}/chat/completions?api-version=2025-01-01-preview"

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional forex/crypto/commodities trading content writer for Seekapa, a regulated forex broker."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_completion_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            logger.info(f"Generating content with {deployment}...")
            response = requests.post(url, headers=self.headers, json=payload, timeout=90)
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            logger.success(f"Article generated ({len(content)} chars)")
            return {"success": True, "content": content, "usage": data.get("usage", {})}

        except requests.exceptions.RequestException as e:
            logger.error(f"Azure OpenAI API error: {e}")
            return {"success": False, "error": str(e)}

    def translate_content(
        self,
        text: str,
        target_language: str,
        context: str = "trading article"
    ) -> Dict:
        """
        Translate content to target language using GPT-5

        Args:
            text: English text to translate
            target_language: arabic_gcc, spanish, or portuguese
            context: Content context for better translation

        Returns:
            Dict with translated content
        """
        from ..config.prompts import get_translation_prompt

        prompt = get_translation_prompt(text, target_language, context)

        return self.generate_article(
            prompt=prompt,
            deployment=GPT5_DEPLOYMENT,
            max_tokens=2000,
            temperature=0.3  # Lower temperature for translation accuracy
        )

    def generate_seo_metadata(
        self,
        article: str,
        category: str,
        asset: str
    ) -> Dict:
        """
        Generate SEO metadata using GPT-5

        Args:
            article: Article content
            category: forex, crypto, or commodities
            asset: Asset name (EUR/USD, Bitcoin, Gold)

        Returns:
            Dict with SEO metadata (title, description, keywords, image_alt)
        """
        from ..config.prompts import get_seo_metadata_prompt

        prompt = get_seo_metadata_prompt(article, category, asset)

        result = self.generate_article(
            prompt=prompt,
            deployment=GPT5_DEPLOYMENT,
            max_tokens=500,
            temperature=0.5
        )

        if result["success"]:
            # Parse JSON response
            try:
                import json
                metadata = json.loads(result["content"])
                return {"success": True, "metadata": metadata}
            except json.JSONDecodeError:
                logger.warning("Failed to parse SEO metadata JSON, using fallback")
                return self._get_fallback_seo(category, asset)
        else:
            return result

    def validate_article_quality(self, article: str, category: str) -> Dict:
        """
        Use GPT-5-Pro to validate article quality (optional)

        Args:
            article: Article content to validate
            category: Article category

        Returns:
            Dict with quality score and suggestions
        """
        prompt = f"""Review this {category} trading article for quality:

ARTICLE:
{article[:1000]}...

EVALUATE:
1. Content accuracy and completeness
2. Professional tone and brand voice
3. SEO optimization
4. Actionable insights for traders
5. Compliance (no guaranteed profits claims)

Provide:
- Quality score (0-100)
- Strengths (bullet points)
- Improvements needed (bullet points)
- Overall recommendation (publish/revise)

Format as JSON."""

        return self.generate_article(
            prompt=prompt,
            deployment=GPT5_PRO_DEPLOYMENT,
            max_tokens=800,
            temperature=0.3
        )

    def _get_fallback_seo(self, category: str, asset: str) -> Dict:
        """Generate fallback SEO metadata if GPT-5 fails"""
        return {
            "success": True,
            "metadata": {
                "title": f"{asset} Analysis Today | {category.title()} Trading | Seekapa",
                "description": f"Professional {asset} market analysis for {category} traders. Real-time insights, technical analysis, and trading opportunities from Seekapa.",
                "keywords": [asset, f"{category} trading", "market analysis", "Seekapa", "trading insights"],
                "image_alt": f"{asset} {category} trading chart showing market analysis"
            }
        }
