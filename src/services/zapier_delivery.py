"""
Zapier Webhook Delivery Service
Send article packages to Zapier for review and publishing
"""

import requests
import json
from typing import List, Dict
from loguru import logger
from config.credentials import ZAPIER_WEBHOOK_URL


class ZapierDelivery:
    """Delivers article packages to Zapier webhook"""

    def __init__(self):
        self.webhook_url = ZAPIER_WEBHOOK_URL

    def send_articles(
        self,
        articles: List[Dict],
        metadata: Dict = None
    ) -> Dict:
        """
        Send articles to Zapier webhook

        Args:
            articles: List of article packages
            metadata: Additional metadata (execution time, quality scores, etc.)

        Returns:
            Dict with delivery status
        """
        # Restructure articles to new format with clear fields
        restructured_articles = self._restructure_articles(articles)

        payload = {
            "generated_at": articles[0]["generated_at"] if articles else None,
            "articles": restructured_articles,
            "metadata": metadata or self._generate_metadata(articles)
        }

        try:
            logger.info(f"Sending {len(articles)} articles to Zapier webhook...")

            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            response.raise_for_status()

            logger.success(f"Successfully delivered to Zapier (status: {response.status_code})")

            return {
                "success": True,
                "status_code": response.status_code,
                "response": response.text
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Zapier delivery failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def send_with_retry(
        self,
        articles: List[Dict],
        metadata: Dict = None,
        max_retries: int = 3
    ) -> Dict:
        """
        Send articles with retry logic

        Args:
            articles: Article packages
            metadata: Additional metadata
            max_retries: Maximum retry attempts

        Returns:
            Dict with delivery status
        """
        import time

        for attempt in range(1, max_retries + 1):
            logger.info(f"Delivery attempt {attempt}/{max_retries}")

            result = self.send_articles(articles, metadata)

            if result["success"]:
                return result

            if attempt < max_retries:
                wait_time = attempt * 5  # Exponential backoff: 5s, 10s, 15s
                logger.warning(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

        logger.error(f"All {max_retries} delivery attempts failed")
        return result

    def save_failed_delivery(
        self,
        articles: List[Dict],
        date_str: str
    ) -> str:
        """
        Save failed delivery payload for manual retry

        Args:
            articles: Article packages
            date_str: Date string (YYYY-MM-DD)

        Returns:
            Path to saved file
        """
        import os

        # Get project root (3 levels up from this file: src/services/zapier_delivery.py)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        failed_dir = os.path.join(project_root, "output", "failed_deliveries")
        os.makedirs(failed_dir, exist_ok=True)

        filepath = f"{failed_dir}/failed_{date_str}.json"

        payload = {
            "articles": articles,
            "generated_at": articles[0]["generated_at"] if articles else None,
            "note": "This delivery failed. Retry manually by posting to Zapier webhook."
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        logger.warning(f"Saved failed delivery to: {filepath}")
        return filepath

    def _restructure_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Restructure articles to new Zapier format with clear fields

        Args:
            articles: Original article packages

        Returns:
            Restructured articles with: article_type, specific_asset, image_url, languages
        """
        restructured = []

        for article in articles:
            # Extract category/type
            article_type = article.get("category", "unknown")

            # Extract specific asset
            specific_asset = self._extract_asset(article)

            # Get image URL (full URL, not just path)
            image_url = self._get_full_image_url(article)

            # Restructure languages with clear header/content fields
            languages_data = {}
            for lang_code, lang_data in article.get("languages", {}).items():
                languages_data[lang_code] = {
                    "language": self._map_language_name(lang_code),
                    "header": lang_data.get("seo", {}).get("title", ""),
                    "content": self._extract_content_from_html(lang_data.get("html", ""))
                }

            restructured_article = {
                "article_type": article_type,
                "specific_asset": specific_asset,
                "image_url": image_url,
                "languages": languages_data
            }

            restructured.append(restructured_article)

        return restructured

    def _extract_asset(self, article: Dict) -> str:
        """
        Extract specific asset from article

        Args:
            article: Article package

        Returns:
            Asset name (e.g., EUR/USD, Bitcoin, Gold)
        """
        # Try different keys depending on category
        if "currency_pair" in article:
            return article["currency_pair"]
        elif "asset" in article:
            return article["asset"]
        elif "commodity" in article:
            return article["commodity"]
        else:
            return "Unknown"

    def _get_full_image_url(self, article: Dict) -> str:
        """
        Get full image URL from article

        Args:
            article: Article package

        Returns:
            Full image URL (https://...)
        """
        image_data = article.get("image", {})

        # Check if we already have a full URL
        if "url" in image_data:
            return image_data["url"]

        # Build URL from path and filename
        filename = image_data.get("filename", "")
        if not filename:
            return ""

        # Use the GitHub raw URL from credentials
        from config.credentials import TRADING_IMAGES_URL

        # Determine subfolder based on asset type
        category = article.get("category", "forex")

        # Map to image folder structure
        if category == "forex":
            # Extract currency pair (e.g., EUR/USD -> eur-usd)
            asset = self._extract_asset(article)
            folder = asset.lower().replace("/", "-")
        elif category == "crypto":
            # Get crypto name (e.g., Bitcoin -> bitcoin)
            asset = self._extract_asset(article)
            folder = asset.lower()
        elif category == "commodities":
            # Get commodity name (e.g., Gold -> gold)
            asset = self._extract_asset(article)
            folder = asset.lower()
        else:
            folder = "general"

        return f"{TRADING_IMAGES_URL}/{folder}/{filename}"

    def _generate_metadata(self, articles: List[Dict]) -> Dict:
        """
        Generate metadata summary for delivery

        Args:
            articles: List of article packages

        Returns:
            Metadata dict
        """
        total_languages = sum(
            len(article["languages"])
            for article in articles
        )

        # Calculate average quality scores
        quality_scores = []
        for article in articles:
            for lang, data in article["languages"].items():
                if "quality_score" in data:
                    quality_scores.append(data["quality_score"])

        avg_quality = (
            sum(quality_scores) / len(quality_scores)
            if quality_scores else 0
        )

        return {
            "articles_generated": len(articles),
            "total_translations": total_languages - len(articles),  # Minus English originals
            "languages_per_article": 4,  # EN + AR + ES + PT
            "average_quality_score": round(avg_quality, 2),
            "categories": [article["category"] for article in articles],
            "assets": [article["asset"] for article in articles]
        }

    def _map_language_name(self, lang_code: str) -> str:
        """
        Map language code to full language name

        Args:
            lang_code: Language code (e.g., 'en', 'ar', 'es', 'pt-BR')

        Returns:
            Full language name (e.g., 'English', 'Arabic (Gulf)', 'Spanish')
        """
        language_map = {
            "en": "English",
            "ar": "Arabic (Gulf)",
            "es": "Spanish",
            "pt-BR": "Portuguese (Brazil)"
        }

        return language_map.get(lang_code, lang_code.upper())

    def _extract_content_from_html(self, html: str) -> str:
        """
        Extract article content from HTML document

        Args:
            html: Full HTML document string

        Returns:
            Clean article text content (without HTML tags and metadata footer)
        """
        if not html:
            return ""

        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, 'html.parser')

            # Find the article tag
            article_tag = soup.find('article')
            if not article_tag:
                return ""

            # Extract all paragraph text (excluding metadata section)
            paragraphs = []
            for p in article_tag.find_all('p'):
                # Skip if this is inside the metadata div
                if p.find_parent('div', class_='metadata'):
                    continue

                text = p.get_text(strip=True)

                # Skip empty paragraphs
                if not text:
                    continue

                # Remove ### markdown headers from first paragraph
                text = text.replace('###', '').strip()

                paragraphs.append(text)

            # Join all paragraphs with newlines
            content = '\n\n'.join(paragraphs)

            return content

        except Exception as e:
            logger.warning(f"BeautifulSoup not available, using regex fallback: {e}")
            # Fallback: Extract paragraphs using regex
            import re

            # Extract content between <article> and </article>
            article_match = re.search(r'<article>(.*?)</article>', html, re.DOTALL)
            if article_match:
                article_html = article_match.group(1)

                # Extract all paragraph content (text between <p> and </p>)
                paragraphs = re.findall(r'<p>(.*?)</p>', article_html, re.DOTALL)

                # Clean each paragraph
                cleaned_paragraphs = []
                for p in paragraphs:
                    # Remove any remaining HTML tags
                    text = re.sub(r'<[^>]+>', '', p)
                    # Normalize whitespace
                    text = re.sub(r'\s+', ' ', text).strip()
                    # Remove ### markdown headers
                    text = text.replace('###', '').strip()

                    # Skip if it contains "Published by" (metadata footer)
                    if 'Published by' in text or 'Category:' in text:
                        break

                    if text:
                        cleaned_paragraphs.append(text)

                return '\n\n'.join(cleaned_paragraphs)

            # If no article tag found, return empty
            return ""

    def test_webhook(self) -> bool:
        """
        Test Zapier webhook connectivity

        Returns:
            True if webhook is accessible
        """
        test_payload = {
            "test": True,
            "message": "Testing Zapier webhook connectivity",
            "timestamp": "2025-10-20T12:00:00Z"
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=test_payload,
                timeout=10
            )
            response.raise_for_status()

            logger.success("Zapier webhook test successful")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Zapier webhook test failed: {e}")
            return False
