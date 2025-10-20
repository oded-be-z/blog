#!/usr/bin/env python3
"""
Quick API test script to verify all services are working
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_perplexity():
    """Test Perplexity API"""
    print("Testing Perplexity API...")
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonar",
        "messages": [{
            "role": "user",
            "content": "What is the current EUR/USD price and key drivers today?"
        }]
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        content = data['choices'][0]['message']['content']
        print(f"✅ Perplexity API working! Response length: {len(content)} chars")
        return True
    except Exception as e:
        print(f"❌ Perplexity API failed: {e}")
        return False


def test_azure_openai():
    """Test Azure OpenAI API"""
    print("\nTesting Azure OpenAI API (GPT-5)...")
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    key = os.getenv('AZURE_OPENAI_KEY')
    deployment = os.getenv('GPT5_DEPLOYMENT', 'gpt-5')

    url = f"{endpoint}openai/deployments/{deployment}/chat/completions?api-version=2025-01-01-preview"
    headers = {
        "api-key": key,
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "Write one paragraph about EUR/USD trading."
            }
        ],
        "max_completion_tokens": 200
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()

        # Check if we got content
        if 'choices' in data and len(data['choices']) > 0:
            content = data['choices'][0]['message'].get('content', '')
            if content:
                print(f"✅ Azure OpenAI working! Response length: {len(content)} chars")
                print(f"   Sample: {content[:100]}...")
                return True
            else:
                # Check for reasoning tokens
                usage = data.get('usage', {})
                reasoning_tokens = usage.get('completion_tokens_details', {}).get('reasoning_tokens', 0)
                if reasoning_tokens > 0:
                    print(f"⚠️  GPT-5 returned {reasoning_tokens} reasoning tokens but no content")
                    print("   This might be expected behavior for reasoning models")
                    print("   Let's try a different deployment or approach")
                return False
        else:
            print(f"❌ Unexpected response structure: {data}")
            return False

    except Exception as e:
        print(f"❌ Azure OpenAI failed: {e}")
        return False


def test_zapier_webhook():
    """Test Zapier webhook"""
    print("\nTesting Zapier webhook...")
    webhook_url = os.getenv('ZAPIER_WEBHOOK_URL')

    test_payload = {
        "test": True,
        "message": "Testing webhook connectivity",
        "timestamp": "2025-10-20T12:30:00Z"
    }

    try:
        response = requests.post(webhook_url, json=test_payload, timeout=15)
        response.raise_for_status()
        print(f"✅ Zapier webhook working! Status: {response.status_code}")
        print(f"   Response: {response.text[:100]}")
        return True
    except Exception as e:
        print(f"❌ Zapier webhook failed: {e}")
        return False


def main():
    """Run all API tests"""
    print("="*60)
    print("API Connectivity Tests")
    print("="*60)

    results = {
        "Perplexity": test_perplexity(),
        "Azure OpenAI": test_azure_openai(),
        "Zapier": test_zapier_webhook()
    }

    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    for service, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{service}: {status}")

    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 All API tests passed!")
        return 0
    else:
        print("\n⚠️  Some API tests failed. Check configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
