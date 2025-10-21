#!/usr/bin/env python3
"""
Quick test to verify GPT-5-Pro integration
Tests Azure OpenAI API with correct configuration
"""

import sys
import os

# Add src to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
sys.path.insert(0, SRC_DIR)

from services.azure_openai_client import AzureOpenAIClient
from loguru import logger

def test_gpt5_pro():
    """Test GPT-5-Pro article generation"""
    logger.info("=" * 60)
    logger.info("Testing GPT-5-Pro Integration")
    logger.info("=" * 60)

    client = AzureOpenAIClient()

    # Simple test prompt
    test_prompt = """Write a brief 200-word trading market analysis about Bitcoin.

Include:
- Current market sentiment
- Key price levels
- Trading outlook

Keep it professional and informative."""

    logger.info("Calling GPT-5-Pro...")
    result = client.generate_article(
        prompt=test_prompt,
        deployment="gpt-5-pro",
        max_tokens=2000
    )

    if result["success"]:
        logger.success("✅ GPT-5-Pro is working!")
        logger.info(f"Generated content length: {len(result['content'])} characters")
        logger.info("=" * 60)
        logger.info("Sample output (first 500 chars):")
        logger.info("-" * 60)
        print(result["content"][:500])
        logger.info("-" * 60)
        logger.info(f"Token usage: {result.get('usage', {})}")
        return True
    else:
        logger.error(f"❌ GPT-5-Pro failed: {result.get('error')}")
        return False

if __name__ == "__main__":
    success = test_gpt5_pro()
    sys.exit(0 if success else 1)
