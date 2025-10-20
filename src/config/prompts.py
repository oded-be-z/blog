"""
GPT-5 Prompt Templates for Content Generation
"""

from datetime import date

def get_article_generation_prompt(category: str, asset: str, market_data: dict) -> str:
    """Generate prompt for article creation"""

    prompts = {
        "forex": f"""Generate a professional 500-word forex trading article about {asset}.

MARKET DATA:
- Current Price: {market_data.get('price', 'N/A')}
- 24h Change: {market_data.get('change', 'N/A')}
- Key Drivers: {market_data.get('drivers', 'Economic data')}

ARTICLE STRUCTURE:
1. Headline (compelling, SEO-optimized)
2. Introduction (50-75 words) - Brief overview of current market conditions
3. Market Highlights (150-200 words):
   - Current price movements and percentage changes
   - Trading volume analysis
   - Key support and resistance levels
4. Technical Analysis (150-175 words):
   - RSI, MACD, moving averages
   - Chart patterns and trends
   - Important technical levels
5. Fundamental Drivers (100-125 words):
   - Economic data releases
   - Geopolitical events
   - Central bank policies
6. Trading Opportunities (75-100 words):
   - Actionable insights for traders
   - Entry/exit suggestions
   - Risk management tips

TONE: Professional, informative, trader-focused
BRAND: Seekapa - professional excellence, trustworthy
INCLUDE: Real-time data, concrete numbers, actionable insights
AVOID: Guaranteed profits, gambling language, unrealistic expectations

Write the article now.""",

        "crypto": f"""Generate a professional 500-word cryptocurrency trading article about {asset}.

MARKET DATA:
- Current Price: {market_data.get('price', 'N/A')}
- Market Cap: {market_data.get('market_cap', 'N/A')}
- 24h Change: {market_data.get('change', 'N/A')}
- Key Catalysts: {market_data.get('catalysts', 'Market sentiment')}

ARTICLE STRUCTURE:
1. Headline (compelling, crypto-focused)
2. Introduction (50-75 words) - Current market status
3. Market Highlights (150-200 words):
   - Price movements, market cap, volume
   - Comparison with other major cryptos
   - Market sentiment indicators
4. Technical Analysis (150-175 words):
   - Support/resistance levels
   - Trend analysis (bullish/bearish)
   - Key technical indicators
5. News & Catalysts (100-125 words):
   - Regulatory updates
   - Technology developments
   - Adoption news
   - Institutional activity
6. Trading Insights (75-100 words):
   - Trading opportunities
   - Risk considerations
   - Market outlook

TONE: Professional, tech-savvy, opportunity-focused
BRAND: Seekapa - transparent, educational
INCLUDE: Real prices, market data, factual analysis
AVOID: FOMO language, pump/dump implications, financial advice

Write the article now.""",

        "commodities": f"""Generate a professional 500-word commodities trading article about {asset}.

MARKET DATA:
- Current Price: {market_data.get('price', 'N/A')}
- 24h Change: {market_data.get('change', 'N/A')}
- Key Drivers: {market_data.get('drivers', 'Supply/demand factors')}

ARTICLE STRUCTURE:
1. Headline (commodity-specific, impactful)
2. Introduction (50-75 words) - Market overview
3. Price Movement (150-200 words):
   - Current prices and recent changes
   - Historical context
   - Trading volume insights
4. Technical Analysis (150-175 words):
   - Chart patterns
   - Key support/resistance
   - Momentum indicators
5. Fundamental Factors (100-125 words):
   - Supply and demand dynamics
   - Geopolitical influences
   - Economic indicators
   - Weather/seasonal factors (if applicable)
6. Trading Outlook (75-100 words):
   - Market direction expectations
   - Key levels to watch
   - Risk management considerations

TONE: Professional, analytical, balanced
BRAND: Seekapa - reliable, data-driven
INCLUDE: Real market data, fundamental analysis, technical levels
AVOID: Speculative claims, emotional language

Write the article now."""
    }

    return prompts.get(category, prompts["forex"])


def get_translation_prompt(text: str, target_language: str, category: str) -> str:
    """Generate prompt for professional translation"""

    language_instructions = {
        "arabic_gcc": """Translate to GCC/Gulf Arabic dialect (Khaleeji):

REQUIREMENTS:
- Use Gulf Arabic dialect (not Modern Standard Arabic)
- Professional yet conversational tone
- Include Islamic finance terminology where appropriate:
  - Trading = التداول (at-tadawul)
  - Broker = وسيط (waseet)
  - Profit = ربح (ribh)
  - Margin = الهامش (al-hamish)
  - Leverage = الرافعة المالية (ar-rafi'a al-maliyya)
- Maintain Seekapa brand voice: trustworthy, professional
- Ensure right-to-left (RTL) compatibility
- Avoid gambling references
- Emphasize regulation, transparency, trust

CULTURAL CONSIDERATIONS:
- Respectful tone for GCC audience
- Family security and financial stability messaging
- Islamic finance principles compliance
- Use local currency examples (AED, SAR) when relevant

Translate now:""",

        "spanish": """Translate to Latin American Spanish:

REQUIREMENTS:
- Use neutral Latin American Spanish (not Castilian)
- Energetic, opportunity-focused tone
- Trading terminology:
  - Trading = Operaciones / Trading
  - Broker = Bróker / Corredor
  - Profit = Ganancia
  - Margin = Margen
  - Leverage = Apalancamiento
- Maintain Seekapa brand: professional, accessible
- Address economic challenges in LATAM
- Emphasize forex as opportunity and wealth protection

TONE: Dynamic, supportive, professional
TARGET: Mexican, Colombian, Argentine, Chilean traders

Translate now:""",

        "portuguese": """Translate to Brazilian Portuguese:

REQUIREMENTS:
- Use Brazilian Portuguese (not European)
- Warm, community-oriented tone
- Use "você" (informal you)
- Trading terminology:
  - Trading = Negociação
  - Broker = Corretora
  - Profit = Lucro
  - Margin = Margem
  - Leverage = Alavancagem
- Maintain Seekapa brand: professional, trustworthy
- Localize with Brazilian context (BRL currency)
- Emphasize community and support

TONE: Friendly, motivational, professional
TARGET: Brazilian traders

Translate now:"""
    }

    instruction = language_instructions.get(target_language, "")
    return f"{instruction}\n\n{text}"


def get_seo_metadata_prompt(article: str, category: str, asset: str) -> str:
    """Generate prompt for SEO metadata creation"""

    return f"""Generate SEO metadata for this {category} article about {asset}:

REQUIREMENTS:
1. SEO Title (50-60 characters):
   - Include {asset} and category
   - Include "Seekapa" brand
   - Compelling and click-worthy

2. Meta Description (150-160 characters):
   - Summarize key points
   - Include primary keyword
   - Call-to-action if space permits

3. Keywords (5-7 keywords):
   - Primary: {asset} + {category}
   - Secondary: "trading", "analysis", "market"
   - Long-tail: specific to article content

4. Image Alt Text (descriptive, SEO-friendly):
   - Describe the trading chart/image
   - Include {asset} keyword
   - Accessibility-friendly

ARTICLE:
{article[:500]}...

Generate metadata in JSON format:
{{
  "title": "...",
  "description": "...",
  "keywords": ["...", "...", ...],
  "image_alt": "..."
}}"""
