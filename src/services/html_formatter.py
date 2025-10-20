"""
HTML Formatter & SEO Optimizer
Convert article content to clean HTML with embedded images and metadata
"""

from typing import Dict
from datetime import datetime
from loguru import logger


class HTMLFormatter:
    """Formats articles as clean HTML with SEO optimization"""

    def format_article(
        self,
        content: str,
        title: str,
        seo_metadata: Dict,
        image_url: str,
        image_alt: str,
        language_code: str = "en",
        rtl: bool = False
    ) -> str:
        """
        Format article as HTML

        Args:
            content: Article text content
            title: Article title
            seo_metadata: SEO metadata dict
            image_url: Image URL
            image_alt: Image alt text
            language_code: Language code (en, ar, es, pt-BR)
            rtl: Right-to-left text direction (for Arabic)

        Returns:
            HTML string
        """
        # Convert plain text to HTML paragraphs
        paragraphs = content.strip().split('\n\n')
        html_content = '\n'.join(
            f'<p>{para.strip()}</p>'
            for para in paragraphs
            if para.strip()
        )

        # Build HTML
        dir_attr = 'dir="rtl"' if rtl else ''

        html = f"""<!DOCTYPE html>
<html lang="{language_code}" {dir_attr}>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{seo_metadata.get('title', title)}</title>
    <meta name="description" content="{seo_metadata.get('description', '')}">
    <meta name="keywords" content="{', '.join(seo_metadata.get('keywords', []))}">
    <meta name="author" content="Seekapa">
    <meta name="robots" content="index, follow">

    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="article">
    <meta property="og:title" content="{seo_metadata.get('title', title)}">
    <meta property="og:description" content="{seo_metadata.get('description', '')}">
    <meta property="og:image" content="{image_url}">

    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{seo_metadata.get('title', title)}">
    <meta name="twitter:description" content="{seo_metadata.get('description', '')}">
    <meta name="twitter:image" content="{image_url}">

    <style>
        body {{
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #1a1a1a;
            font-size: 2.5em;
            margin-bottom: 0.5em;
        }}
        .featured-image {{
            width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 20px 0;
        }}
        p {{
            margin-bottom: 1em;
            font-size: 1.1em;
        }}
        .metadata {{
            color: #666;
            font-size: 0.9em;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }}
    </style>
</head>
<body>
    <article>
        <h1>{title}</h1>

        <img src="{image_url}"
             alt="{image_alt}"
             class="featured-image"
             loading="lazy">

        {html_content}

        <div class="metadata">
            <p><strong>Published by:</strong> Seekapa</p>
            <p><strong>Category:</strong> {', '.join(seo_metadata.get('keywords', [])[:3])}</p>
            <p><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
        </div>
    </article>
</body>
</html>"""

        logger.success(f"Formatted article as HTML ({len(html)} chars)")
        return html

    def create_article_package(
        self,
        category: str,
        asset: str,
        market_data: Dict,
        english_article: str,
        translations: Dict[str, Dict],
        seo_metadata: Dict,
        image_data: Dict
    ) -> Dict:
        """
        Create complete article package with all languages

        Args:
            category: forex, crypto, or commodities
            asset: Asset name
            market_data: Market data dict
            english_article: English article content
            translations: Dict of translations
            seo_metadata: SEO metadata
            image_data: Image URL and alt text

        Returns:
            Dict with complete article package
        """
        package = {
            "category": category,
            "asset": asset,
            "market_data": market_data,
            "generated_at": datetime.now().isoformat(),
            "languages": {}
        }

        # English version
        package["languages"]["en"] = {
            "html": self.format_article(
                content=english_article,
                title=seo_metadata.get('title', f"{asset} Analysis"),
                seo_metadata=seo_metadata,
                image_url=image_data["image_url"],
                image_alt=image_data["image_alt"],
                language_code="en",
                rtl=False
            ),
            "seo": seo_metadata,
            "word_count": len(english_article.split())
        }

        # Translated versions
        language_map = {
            "arabic_gcc": {"code": "ar", "rtl": True},
            "spanish": {"code": "es", "rtl": False},
            "portuguese": {"code": "pt-BR", "rtl": False}
        }

        for lang_key, lang_config in language_map.items():
            if lang_key in translations and translations[lang_key].get("success"):
                translated_content = translations[lang_key]["translated_content"]

                package["languages"][lang_config["code"]] = {
                    "html": self.format_article(
                        content=translated_content,
                        title=seo_metadata.get('title', f"{asset} Analysis"),
                        seo_metadata=seo_metadata,
                        image_url=image_data["image_url"],
                        image_alt=image_data["image_alt"],
                        language_code=lang_config["code"],
                        rtl=lang_config["rtl"]
                    ),
                    "seo": seo_metadata,
                    "word_count": translations[lang_key].get("word_count", 0),
                    "quality_score": translations[lang_key].get("quality_score", 0)
                }

        logger.success(f"Created article package with {len(package['languages'])} languages")
        return package
