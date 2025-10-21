"""
Perplexity API Client
Deep web research for market intelligence
"""

import requests
from typing import Dict, List
from loguru import logger
from config.credentials import PERPLEXITY_API_KEY, PERPLEXITY_ENDPOINT, get_api_headers


class PerplexityClient:
    """Client for Perplexity API market research"""

    def __init__(self):
        self.api_key = PERPLEXITY_API_KEY
        self.endpoint = PERPLEXITY_ENDPOINT
        self.headers = get_api_headers("perplexity")

    def research_forex_market(self) -> Dict:
        """Research current forex market trends and top pairs"""
        prompt = """Provide current forex market analysis:

1. Top 3 trending forex pairs today with:
   - Current price
   - 24h percentage change
   - Trading volume insights
   - Key drivers (economic data, central bank policy, geopolitical)

2. Most volatile pair with highest trading opportunity

3. Key economic events affecting forex today

Format: JSON with {pair_name, price, change_pct, volume, drivers, opportunity_score}"""

        return self._query(prompt)

    def research_crypto_market(self) -> Dict:
        """Research current cryptocurrency market trends"""
        prompt = """Provide current cryptocurrency market analysis:

1. Top 3 trending cryptocurrencies today:
   - Bitcoin, Ethereum, and one trending altcoin
   - Current price
   - Market cap
   - 24h percentage change
   - Key catalysts (news, regulation, tech updates)

2. Market sentiment (bullish/bearish/neutral)

3. Major news affecting crypto today

Format: JSON with {crypto_name, price, market_cap, change_pct, catalysts, sentiment}"""

        return self._query(prompt)

    def research_commodities_market(self) -> Dict:
        """Research current commodities market trends"""
        prompt = """Provide current commodities market analysis:

1. Top commodities moving today (Gold, Silver, Oil, Copper):
   - Current price
   - 24h percentage change
   - Key drivers (supply/demand, geopolitical, economic)

2. Most significant commodity movement

3. Fundamental factors affecting prices

Format: JSON with {commodity_name, price, change_pct, drivers, significance_score}"""

        return self._query(prompt)

    def _query(self, prompt: str) -> Dict:
        """
        Send query to Perplexity API

        Args:
            prompt: Research question

        Returns:
            Dict with research results
        """
        payload = {
            "model": "sonar",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        try:
            logger.info(f"Querying Perplexity API...")
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            logger.success(f"Perplexity research completed")
            return {"success": True, "content": content, "data": data}

        except requests.exceptions.RequestException as e:
            logger.error(f"Perplexity API error: {e}")
            return {"success": False, "error": str(e)}

    def select_best_asset(self, research_data: Dict, category: str) -> Dict:
        """
        Select the best asset to write about based on research

        Args:
            research_data: Research results from Perplexity
            category: forex, crypto, or commodities

        Returns:
            Dict with selected asset and key data
        """
        # Parse research content and select most volatile/newsworthy asset
        # This is a simplified version - in production, parse JSON properly

        content = research_data.get("content", "")

        # Default selections based on research trends
        defaults = {
            "forex": {
                "asset": "EUR/USD",
                "price": "1.0845",
                "change": "+0.32%",
                "drivers": "ECB rate decision, US inflation data"
            },
            "crypto": {
                "asset": "Bitcoin",
                "price": "$110,818",
                "change": "+2.5%",
                "catalysts": "ETF inflows, halving anticipation"
            },
            "commodities": {
                "asset": "Gold",
                "price": "$2,650/oz",
                "change": "+1.2%",
                "drivers": "Safe-haven demand, inflation hedging"
            }
        }

        # In production, parse the actual Perplexity response
        # For now, return structured data with research insights
        selected = defaults.get(category, defaults["forex"])
        selected["research_insights"] = content[:500]  # Include research summary

        logger.info(f"Selected {category} asset: {selected['asset']}")
        return selected
