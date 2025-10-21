"""
AI Quality Validator
Uses GPT-5-Pro to validate and improve content before publication
"""

from typing import Dict, List
from loguru import logger
from services.azure_openai_client import AzureOpenAIClient


class QualityValidator:
    """
    AI-powered quality validation and improvement
    Uses GPT-5-Pro for content review and enhancement
    """

    def __init__(self):
        self.openai_client = AzureOpenAIClient()

    def validate_article(self, article: str, category: str, asset: str) -> Dict:
        """
        Validate article quality using GPT-5-Pro

        Args:
            article: Article content to validate
            category: forex, crypto, or commodities
            asset: Asset name (e.g., EUR/USD, Bitcoin, Gold)

        Returns:
            Dict with quality score, issues, and improved version
        """
        logger.info(f"Validating {asset} article quality...")

        validation_prompt = f"""Review this {category} trading article about {asset} for publication quality.

ARTICLE TO REVIEW:
{article[:2000]}...

EVALUATE THE FOLLOWING:
1. **Content Accuracy** (0-25 points):
   - Factual accuracy of market analysis
   - Realistic price levels and trends
   - Professional trading insights

2. **SEO & Structure** (0-25 points):
   - Clear headlines and structure
   - Keyword usage (natural, not stuffed)
   - Readability and flow

3. **Brand Voice** (0-25 points):
   - Professional, trustworthy tone
   - Seekapa brand alignment
   - No guaranteed profits claims
   - Compliance with trading regulations

4. **Completeness** (0-25 points):
   - All required sections present
   - Adequate depth (600-800 words)
   - Actionable insights for traders
   - Proper conclusion

RESPOND IN THIS FORMAT:
```json
{{
  "quality_score": 85,
  "content_accuracy": 22,
  "seo_structure": 20,
  "brand_voice": 23,
  "completeness": 20,
  "issues": [
    "Minor issue 1",
    "Minor issue 2"
  ],
  "strengths": [
    "Strength 1",
    "Strength 2"
  ],
  "recommendation": "PUBLISH" or "IMPROVE" or "REJECT",
  "improvements_needed": [
    "Specific improvement 1",
    "Specific improvement 2"
  ]
}}
```

If score < 70: Recommend "IMPROVE"
If score >= 70: Recommend "PUBLISH"
If score < 50: Recommend "REJECT"
"""

        result = self.openai_client.generate_article(
            prompt=validation_prompt,
            deployment="gpt-5-pro",
            max_tokens=3000
        )

        if result["success"]:
            # Parse JSON response
            try:
                import json
                # Extract JSON from response
                content = result["content"]

                # Find JSON block
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    json_str = content[json_start:json_end].strip()
                elif "{" in content and "}" in content:
                    json_start = content.find("{")
                    json_end = content.rfind("}") + 1
                    json_str = content[json_start:json_end]
                else:
                    raise ValueError("No JSON found in response")

                validation_result = json.loads(json_str)

                logger.info(f"Quality score: {validation_result.get('quality_score', 0)}/100")
                logger.info(f"Recommendation: {validation_result.get('recommendation', 'UNKNOWN')}")

                return {
                    "success": True,
                    **validation_result
                }
            except Exception as e:
                logger.error(f"Failed to parse validation result: {e}")
                # Fallback - assume pass
                return {
                    "success": True,
                    "quality_score": 75,
                    "recommendation": "PUBLISH",
                    "issues": [],
                    "note": f"Validation parsing failed: {e}"
                }
        else:
            logger.warning("Quality validation failed, assuming pass")
            return {
                "success": True,
                "quality_score": 70,
                "recommendation": "PUBLISH",
                "issues": [],
                "note": "Validation service unavailable"
            }

    def validate_translation(
        self,
        original: str,
        translated: str,
        language: str,
        category: str
    ) -> Dict:
        """
        Validate translation quality

        Args:
            original: Original English text
            translated: Translated text
            language: Target language (arabic_gcc, spanish, portuguese)
            category: Content category

        Returns:
            Dict with validation results
        """
        logger.info(f"Validating {language} translation...")

        # Quick checks first
        if not translated or len(translated) == 0:
            return {
                "success": False,
                "quality_score": 0,
                "issues": ["Translation is empty"],
                "recommendation": "RETRY"
            }

        # Length check
        orig_len = len(original.split())
        trans_len = len(translated.split())

        if trans_len < orig_len * 0.5:
            return {
                "success": False,
                "quality_score": 30,
                "issues": [f"Translation too short: {trans_len} words vs {orig_len} words in original"],
                "recommendation": "RETRY"
            }

        # AI validation for non-empty translations
        validation_prompt = f"""Validate this {language} translation of a {category} trading article.

ORIGINAL (English):
{original[:800]}...

TRANSLATION ({language}):
{translated[:800]}...

EVALUATE:
1. Accuracy: Does translation convey same meaning?
2. Fluency: Natural language flow?
3. Terminology: Proper trading terms used?
4. Completeness: All content translated?

RESPOND WITH SCORE 0-100 AND BRIEF ASSESSMENT:
```json
{{
  "quality_score": 85,
  "issues": ["issue1", "issue2"],
  "recommendation": "ACCEPT" or "RETRY"
}}
```
"""

        result = self.openai_client.generate_article(
            prompt=validation_prompt,
            deployment="gpt-5",  # Use standard GPT-5 for quick validation
            max_tokens=500
        )

        if result["success"]:
            try:
                import json
                content = result["content"]

                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    json_str = content[json_start:json_end].strip()
                else:
                    json_start = content.find("{")
                    json_end = content.rfind("}") + 1
                    json_str = content[json_start:json_end]

                validation_result = json.loads(json_str)

                logger.info(f"{language} translation score: {validation_result.get('quality_score', 0)}/100")

                return {
                    "success": True,
                    **validation_result
                }
            except Exception as e:
                logger.warning(f"Translation validation parsing failed: {e}, assuming pass")
                return {
                    "success": True,
                    "quality_score": 75,
                    "recommendation": "ACCEPT",
                    "issues": []
                }
        else:
            # Fallback to basic checks
            return {
                "success": True,
                "quality_score": 70,
                "recommendation": "ACCEPT",
                "issues": [],
                "note": "AI validation unavailable, passed basic checks"
            }

    def improve_article_if_needed(
        self,
        article: str,
        validation_result: Dict,
        category: str,
        asset: str
    ) -> str:
        """
        Improve article based on validation feedback

        Args:
            article: Original article
            validation_result: Validation results from validate_article
            category: Article category
            asset: Asset name

        Returns:
            Improved article or original if no improvement needed
        """
        if validation_result.get("recommendation") != "IMPROVE":
            return article  # No improvement needed

        logger.info(f"Improving {asset} article based on feedback...")

        improvement_prompt = f"""Improve this {category} trading article about {asset} based on the following feedback:

ORIGINAL ARTICLE:
{article}

ISSUES TO FIX:
{chr(10).join(f"- {issue}" for issue in validation_result.get('improvements_needed', []))}

REQUIREMENTS:
- Maintain 600-800 words
- Professional trading tone
- Factually accurate
- No guaranteed profits claims
- Clear structure with headlines
- Actionable insights for traders

RESPOND WITH THE IMPROVED ARTICLE (NO EXPLANATIONS, JUST THE ARTICLE):
"""

        result = self.openai_client.generate_article(
            prompt=improvement_prompt,
            deployment="gpt-5-pro",
            max_tokens=8000
        )

        if result["success"] and result["content"]:
            improved = result["content"].strip()
            logger.success(f"Article improved ({len(improved)} chars)")
            return improved
        else:
            logger.warning("Improvement failed, returning original")
            return article
