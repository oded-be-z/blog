"""
Image Manager
Select relevant images from GitHub repo or web search
"""

import os
import random
from typing import Optional, List
from loguru import logger
from ..config.credentials import TRADING_IMAGES_PATH, TRADING_IMAGES_URL


class ImageManager:
    """Manages trading images from GitHub repository and web fallback"""

    def __init__(self):
        self.images_path = TRADING_IMAGES_PATH
        self.images_url = TRADING_IMAGES_URL

        # Asset to folder mapping
        self.asset_folders = {
            # Forex
            "EUR/USD": "eur-usd",
            "USD/JPY": "usd-jpy",
            "GBP/USD": "gbp-usd",
            "USD/CAD": "usd-cad",
            "AUD/USD": "aud",

            # Crypto
            "Bitcoin": "btc-usd",
            "Ethereum": "ethereum",
            "XRP": "xrp",

            # Commodities
            "Gold": "gold",
            "Silver": "silver",
            "Oil": "oil",
            "Copper": "copper"
        }

    def get_image_for_asset(self, asset: str, category: str) -> dict:
        """
        Get image URL and alt text for an asset

        Args:
            asset: Asset name (EUR/USD, Bitcoin, Gold)
            category: forex, crypto, or commodities

        Returns:
            Dict with image_url and image_alt
        """
        logger.info(f"Selecting image for {asset}")

        # Get folder name for asset
        folder = self.asset_folders.get(asset)

        if folder:
            # Try to get image from GitHub repo
            image_file = self._get_random_image_from_folder(folder)
            if image_file:
                image_url = f"{self.images_url}/{folder}/{image_file}"
                image_alt = self._generate_alt_text(asset, category)

                logger.success(f"Found image: {image_url}")
                return {
                    "image_url": image_url,
                    "image_alt": image_alt,
                    "source": "github_repo"
                }

        # Fallback to web search or default
        logger.warning(f"No image found in repo for {asset}, using fallback")
        return self._get_fallback_image(asset, category)

    def _get_random_image_from_folder(self, folder: str) -> Optional[str]:
        """
        Get random image filename from folder

        Args:
            folder: Folder name (e.g., "eur-usd", "btc-usd")

        Returns:
            Image filename or None
        """
        folder_path = os.path.join(self.images_path, folder)

        if not os.path.exists(folder_path):
            logger.warning(f"Folder not found: {folder_path}")
            return None

        # List all image files
        images = [
            f for f in os.listdir(folder_path)
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
        ]

        if images:
            selected = random.choice(images)
            logger.info(f"Selected random image: {selected}")
            return selected

        return None

    def _get_fallback_image(self, asset: str, category: str) -> dict:
        """
        Get fallback image if not found in repo

        Args:
            asset: Asset name
            category: Category

        Returns:
            Dict with fallback image info
        """
        # Use blog_samples folder as fallback
        fallback_images = {
            "forex": f"{self.images_url}/blog_samples/sample_4_eur_usd_11.jpg",
            "crypto": f"{self.images_url}/blog_samples/sample_1_btc_10.jpg",
            "commodities": f"{self.images_url}/blog_samples/sample_2_gold_5.jpg"
        }

        image_url = fallback_images.get(category, fallback_images["forex"])
        image_alt = self._generate_alt_text(asset, category)

        logger.info(f"Using fallback image: {image_url}")
        return {
            "image_url": image_url,
            "image_alt": image_alt,
            "source": "fallback"
        }

    def _generate_alt_text(self, asset: str, category: str) -> str:
        """
        Generate SEO-friendly alt text for image

        Args:
            asset: Asset name
            category: Category

        Returns:
            Alt text string
        """
        templates = {
            "forex": f"{asset} forex trading chart showing price movement and technical analysis indicators",
            "crypto": f"{asset} cryptocurrency price chart with market trends and trading volume",
            "commodities": f"{asset} commodity price chart showing market analysis and trading signals"
        }

        return templates.get(category, f"{asset} trading chart and market analysis")

    def get_available_assets(self) -> List[str]:
        """Get list of available assets with images"""
        return list(self.asset_folders.keys())

    def validate_image_url(self, url: str) -> bool:
        """
        Validate that image URL is accessible

        Args:
            url: Image URL to validate

        Returns:
            True if accessible
        """
        import requests

        try:
            response = requests.head(url, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
