#!/usr/bin/env python3
"""
Test Zapier webhook delivery with all 3 generated articles
"""

import json
import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def load_article(filepath):
    """Load article JSON"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_delivery_payload(articles):
    """Create Zapier webhook payload"""
    return {
        "generated_at": datetime.now().isoformat(),
        "execution_date": "2025-10-20",
        "article_count": len(articles),
        "articles": articles,
        "metadata": {
            "system": "automated_blog_multi_agent_v1.0",
            "categories": ["forex", "crypto", "commodities"],
            "languages_per_article": 4,
            "total_translations": len(articles) * 3,  # 3 translations per article
            "quality_validated": True,
            "test_delivery": True
        }
    }

def send_to_zapier(payload):
    """Send payload to Zapier webhook"""
    webhook_url = os.getenv('ZAPIER_WEBHOOK_URL')

    print("="*60)
    print("Sending articles to Zapier webhook...")
    print("="*60)
    print(f"Webhook URL: {webhook_url}")
    print(f"Articles: {payload['article_count']}")
    print(f"Total size: {len(json.dumps(payload))} bytes")
    print()

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()

        print("✅ SUCCESS!")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}")

        return {
            "success": True,
            "status_code": response.status_code,
            "response": response.text
        }

    except requests.exceptions.RequestException as e:
        print(f"❌ FAILED: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """Main test function"""
    print("="*60)
    print("Zapier Webhook Delivery Test")
    print("="*60)
    print()

    # Load all 3 articles
    print("Loading articles...")
    forex_article = load_article('/home/odedbe/blog/output/test-forex-article.json')
    crypto_article = load_article('/home/odedbe/blog/output/test-crypto-article.json')
    commodities_article = load_article('/home/odedbe/blog/output/test-commodities-article.json')

    print(f"✅ Loaded Forex article: {forex_article.get('currency_pair', 'N/A')}")
    print(f"✅ Loaded Crypto article: {crypto_article.get('asset', 'N/A')}")
    print(f"✅ Loaded Commodities article: {commodities_article.get('commodity', 'N/A')}")
    print()

    # Create payload
    articles = [
        {
            "category": "forex",
            "asset": forex_article.get('currency_pair', 'EUR/USD'),
            "price": forex_article.get('current_price'),
            "change_24h": forex_article.get('price_change_24h'),
            "languages": forex_article.get('languages', {}),
            "image": forex_article.get('image', {}),
            "generated_at": forex_article.get('generated_at')
        },
        {
            "category": "crypto",
            "asset": crypto_article.get('asset', 'Unknown'),
            "price": crypto_article.get('market_data', {}).get('current_price', 'N/A'),
            "change_24h": crypto_article.get('market_data', {}).get('24h_change', 'N/A'),
            "languages": crypto_article.get('languages', {}),
            "image": {
                "path": crypto_article.get('featured_image', ''),
                "alt_text_en": "Crypto trading chart"
            },
            "generated_at": crypto_article.get('publication_date')
        },
        {
            "category": "commodities",
            "asset": commodities_article.get('commodity', 'Unknown'),
            "price": commodities_article.get('market_data', {}).get('current_price', 'N/A'),
            "change_24h": commodities_article.get('market_data', {}).get('24h_change', 'N/A'),
            "languages": commodities_article.get('languages', {}),
            "image": {
                "path": commodities_article.get('featured_image', ''),
                "alt_text_en": "Commodities trading chart"
            },
            "generated_at": commodities_article.get('publication_date')
        }
    ]

    payload = create_delivery_payload(articles)

    # Send to Zapier
    result = send_to_zapier(payload)

    print()
    print("="*60)
    if result['success']:
        print("✅ Test PASSED - All 3 articles delivered successfully")
        return 0
    else:
        print("❌ Test FAILED - Delivery unsuccessful")
        return 1

if __name__ == "__main__":
    exit(main())
