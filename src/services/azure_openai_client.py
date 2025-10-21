"""
Azure OpenAI Client
Wrapper for Azure OpenAI MCP tools: consult_gpt5, consult_gpt5_pro, consult_gpt5_codex
"""

import requests
import time
from typing import Dict, Optional
from loguru import logger
from config.credentials import (
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
        max_tokens: int = 16384,
        temperature: float = None
    ) -> Dict:
        """
        Generate article content using GPT-5 or GPT-5-Pro

        Args:
            prompt: Article generation prompt
            deployment: GPT-5 model deployment name (gpt-5 or gpt-5-pro)
            max_tokens: Maximum tokens in response (16384 for GPT-5-Pro)
            temperature: Creativity level (0-1), None for default. Note: GPT-5 only supports default temperature.

        Returns:
            Dict with generated content
        """
        # GPT-5-Pro uses Responses API, GPT-5 uses Chat Completions API
        is_responses_api = deployment == "gpt-5-pro"

        if is_responses_api:
            # Responses API (GPT-5-Pro)
            url = f"{self.endpoint}openai/responses?api-version=2025-04-01-preview"

            # Combine system message and prompt into single input
            full_input = "You are a professional forex/crypto/commodities trading content writer for Seekapa, a regulated forex broker.\n\n" + prompt

            payload = {
                "model": deployment,
                "input": full_input,
                "max_output_tokens": max_tokens
            }

            # Only add temperature if specified
            if temperature is not None:
                payload["temperature"] = temperature
        else:
            # Chat Completions API (GPT-5 standard)
            url = f"{self.endpoint}openai/deployments/{deployment}/chat/completions?api-version=2024-12-01-preview"

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
                "max_completion_tokens": max_tokens
            }

            # Only add temperature if specified
            if temperature is not None:
                payload["temperature"] = temperature

        # Retry logic for transient errors
        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt + 1}/{max_retries} for {deployment}...")
                    time.sleep(retry_delay * attempt)  # Exponential backoff

                logger.info(f"Generating content with {deployment}...")
                # GPT-5-Pro needs much longer timeout for complex reasoning (3-4 minutes typical)
                timeout = 300 if is_responses_api else 90  # 5 minutes for Responses API, 90s for standard
                response = requests.post(url, headers=self.headers, json=payload, timeout=timeout)
                response.raise_for_status()

                data = response.json()

                # Extract content based on API type
                if is_responses_api:
                    # Responses API returns output array
                    if data.get("output") and isinstance(data["output"], list):
                        # Find message object
                        message_obj = next((item for item in data["output"] if item.get("type") == "message"), None)

                        if message_obj and message_obj.get("content") and isinstance(message_obj["content"], list):
                            # Extract text from content items
                            content = "\n\n".join(
                                item.get("text", "")
                                for item in message_obj["content"]
                                if item.get("text")
                            )
                        else:
                            content = str(data["output"])
                    else:
                        content = data.get("output", "")

                    # Map usage tokens (Responses API uses different field names)
                    usage = {
                        "prompt_tokens": data.get("usage", {}).get("input_tokens", 0),
                        "completion_tokens": data.get("usage", {}).get("output_tokens", 0),
                        "total_tokens": data.get("usage", {}).get("total_tokens", 0)
                    }
                else:
                    # Standard Chat Completions format
                    content = data["choices"][0]["message"]["content"]
                    usage = data.get("usage", {})

                # Check if content is empty
                if not content or len(content) == 0:
                    logger.warning(f"Empty content returned from {deployment}, retrying...")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        return {"success": False, "error": "Empty content returned after retries"}

                logger.success(f"Article generated ({len(content)} chars)")
                return {"success": True, "content": content, "usage": usage}

            except requests.exceptions.HTTPError as e:
                # Check if it's a 4xx error (client error) - don't retry these unless it's 429 (rate limit)
                if e.response.status_code == 429:
                    logger.warning(f"Rate limit hit, will retry after backoff...")
                    if attempt < max_retries - 1:
                        continue
                elif 400 <= e.response.status_code < 500:
                    logger.error(f"Client error {e.response.status_code}: {e}")
                    # For 400 errors, try one more time with a delay
                    if attempt < max_retries - 1:
                        logger.info("Retrying 400 error after delay...")
                        continue
                    return {"success": False, "error": str(e)}
                else:
                    # 5xx errors - retry
                    logger.warning(f"Server error, will retry: {e}")
                    if attempt < max_retries - 1:
                        continue
                    return {"success": False, "error": str(e)}
            except requests.exceptions.RequestException as e:
                logger.error(f"Azure OpenAI API error: {e}")
                if attempt < max_retries - 1:
                    logger.info("Retrying after network error...")
                    continue
                return {"success": False, "error": str(e)}

        # If we get here, all retries failed
        return {"success": False, "error": f"All {max_retries} retry attempts failed"}

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
        from config.prompts import get_translation_prompt

        prompt = get_translation_prompt(text, target_language, context)

        return self.generate_article(
            prompt=prompt,
            deployment=GPT5_DEPLOYMENT,
            max_tokens=6000,  # Higher for reasoning + translation
            temperature=None  # Use default for GPT-5 reasoning models
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
        from config.prompts import get_seo_metadata_prompt

        prompt = get_seo_metadata_prompt(article, category, asset)

        result = self.generate_article(
            prompt=prompt,
            deployment=GPT5_DEPLOYMENT,
            max_tokens=2000,  # Increased for reasoning models
            temperature=None  # Use default for GPT-5
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
            max_tokens=3000,  # Increased for reasoning models
            temperature=None  # Use default for GPT-5
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
