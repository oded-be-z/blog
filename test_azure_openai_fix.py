#!/usr/bin/env python3
"""
Test Azure OpenAI GPT-5 fix - verify reasoning models work correctly
"""

import sys
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.services.azure_openai_client import AzureOpenAIClient

def test_article_generation():
    """Test article generation with fixed client"""
    print("="*60)
    print("Testing Azure OpenAI GPT-5 Article Generation (FIXED)")
    print("="*60)

    client = AzureOpenAIClient()

    prompt = """Write a 300-word professional forex trading article about EUR/USD at 1.1750.

Include:
- Market highlights
- Technical analysis (support/resistance)
- Trading opportunities
- Seekapa brand voice (professional, trustworthy)"""

    print("\nGenerating article...")
    print(f"Prompt length: {len(prompt)} chars")
    print(f"Max tokens: 5000 (reasoning + output)")
    print()

    result = client.generate_article(
        prompt=prompt,
        deployment="gpt-5",
        max_tokens=5000,
        temperature=None  # Use default for GPT-5
    )

    if result["success"]:
        content = result["content"]
        usage = result.get("usage", {})

        print("✅ SUCCESS!")
        print(f"Content length: {len(content)} characters")
        print(f"Word count: {len(content.split())} words")
        print()

        print("Usage stats:")
        print(f"  - Total tokens: {usage.get('total_tokens', 0)}")
        print(f"  - Completion tokens: {usage.get('completion_tokens', 0)}")

        completion_details = usage.get('completion_tokens_details', {})
        if completion_details:
            print(f"  - Reasoning tokens: {completion_details.get('reasoning_tokens', 0)}")
            print(f"  - Output tokens: {completion_details.get('completion_tokens', 0) - completion_details.get('reasoning_tokens', 0)}")

        print()
        print("Sample output (first 300 chars):")
        print("-" * 60)
        print(content[:300] + "...")
        print("-" * 60)

        return True
    else:
        print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
        return False


def test_translation():
    """Test translation with fixed client"""
    print("\n" + "="*60)
    print("Testing Translation (GPT-5 with increased tokens)")
    print("="*60)

    client = AzureOpenAIClient()

    english_text = "EUR/USD is trading at 1.1750 with bullish momentum. Key support is at 1.1650."

    print(f"\nEnglish text: {english_text}")
    print("Translating to Arabic (GCC)...")

    result = client.translate_content(
        text=english_text,
        target_language="arabic_gcc",
        context="forex trading"
    )

    if result["success"]:
        content = result["content"]
        print("✅ SUCCESS!")
        print(f"Translation: {content[:200]}")
        return True
    else:
        print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Azure OpenAI GPT-5 Fix Validation")
    print("="*60)
    print()
    print("FIXES APPLIED:")
    print("✅ Increased max_completion_tokens to 5000")
    print("✅ Removed temperature parameter (use default)")
    print("✅ Updated all methods (article, translation, SEO)")
    print()

    results = {
        "Article Generation": test_article_generation(),
        "Translation": test_translation()
    }

    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 All tests passed! Azure OpenAI integration FIXED!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check logs.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
