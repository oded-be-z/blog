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
        payload = {
            "generated_at": articles[0]["generated_at"] if articles else None,
            "articles": articles,
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

        failed_dir = "/home/odedbe/blog/output/failed_deliveries"
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
