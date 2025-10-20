"""
API Credentials Configuration
Loaded from environment variables or GitHub Actions secrets
"""

import os
from typing import Dict

# Azure OpenAI Configuration
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://brn-azai.openai.azure.com/")

# GPT-5 Deployments
GPT5_DEPLOYMENT = os.getenv("GPT5_DEPLOYMENT", "gpt-5")
GPT5_PRO_DEPLOYMENT = os.getenv("GPT5_PRO_DEPLOYMENT", "gpt-5-pro")
GPT5_CODEX_DEPLOYMENT = os.getenv("GPT5_CODEX_DEPLOYMENT", "gpt-5-codex")

# Perplexity API
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_ENDPOINT = os.getenv("PERPLEXITY_ENDPOINT", "https://api.perplexity.ai/chat/completions")

# GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USER = os.getenv("GITHUB_USER", "oded-be-z")
GITHUB_IMAGES_REPO = os.getenv("GITHUB_IMAGES_REPO", "n8n-trading-images")

# Zapier Webhook
ZAPIER_WEBHOOK_URL = os.getenv("ZAPIER_WEBHOOK_URL")

# Trading Images Repository
TRADING_IMAGES_PATH = "/tmp/n8n-trading-images"
TRADING_IMAGES_URL = "https://raw.githubusercontent.com/oded-be-z/n8n-trading-images/main"

def get_api_headers(service: str) -> Dict[str, str]:
    """Get API headers for a specific service"""
    headers = {
        "perplexity": {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        },
        "azure_openai": {
            "api-key": AZURE_OPENAI_KEY,
            "Content-Type": "application/json"
        },
        "github": {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        },
        "zapier": {
            "Content-Type": "application/json"
        }
    }
    return headers.get(service, {})
