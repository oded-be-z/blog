#!/usr/bin/env python3
"""
Main Orchestrator - Automated Trading Blog System
Coordinates 3 parallel sub-agents using git worktrees

Architecture:
- Main Orchestrator (this file)
  ├─→ Forex Agent (git worktree: blog-forex/)
  ├─→ Crypto Agent (git worktree: blog-crypto/)
  └─→ Commodities Agent (git worktree: blog-commodities/)

Uses:
- Task tool to launch parallel sub-agents
- Git worktrees for parallel branch work
- SKILL_multilingual_content for translations
- Azure OpenAI MCP for content generation
- Perplexity API for market research
"""

import asyncio
import sys
import os
from datetime import datetime
from loguru import logger

# Get project root directory (parent of src/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add src to path
sys.path.insert(0, PROJECT_ROOT)

from utils.git_worktree_manager import GitWorktreeManager
from services.zapier_delivery import ZapierDelivery
from services.html_formatter import HTMLFormatter


# Configure logging
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logger.add(
    os.path.join(LOG_DIR, "orchestrator_{time:YYYY-MM-DD}.log"),
    rotation="1 day",
    retention="30 days",
    level="INFO"
)


class BlogOrchestrator:
    """Main orchestrator for automated blog generation"""

    def __init__(self):
        self.date_str = datetime.now().strftime("%Y-%m-%d")
        self.categories = ["forex", "crypto", "commodities"]

        self.git_manager = GitWorktreeManager()
        self.zapier = ZapierDelivery()
        self.html_formatter = HTMLFormatter()

        self.articles = []
        self.execution_start = None

    async def run(self):
        """Execute complete blog generation workflow"""
        self.execution_start = datetime.now()
        logger.info(f"=" * 80)
        logger.info(f"Starting Automated Blog Generation - {self.date_str}")
        logger.info(f"=" * 80)

        try:
            # Phase 1: Setup
            logger.info("PHASE 1: Setup and Initialization")
            self._create_output_directories()

            # Phase 2: Create Git Worktrees
            logger.info("PHASE 2: Creating Git Worktrees")
            worktrees = self.git_manager.create_worktrees(
                categories=self.categories,
                date_str=self.date_str
            )

            # Phase 3: Launch Parallel Agents
            logger.info("PHASE 3: Launching 3 Parallel Sub-Agents")
            # NOTE: In actual implementation, this would use the Task tool
            # For now, we'll create the workflow and document how to use Task

            logger.info("⚠️  Manual Agent Launch Required:")
            logger.info("Use Claude Code's Task tool to launch 3 parallel agents:")
            logger.info("1. Task(subagent_type='general-purpose', prompt=FOREX_AGENT_PROMPT)")
            logger.info("2. Task(subagent_type='general-purpose', prompt=CRYPTO_AGENT_PROMPT)")
            logger.info("3. Task(subagent_type='general-purpose', prompt=COMMODITIES_AGENT_PROMPT)")

            # For testing, we'll simulate agent outputs
            logger.warning("Running in simulation mode for testing...")
            articles = await self._simulate_agent_outputs()

            # Phase 4: Merge Branches
            logger.info("PHASE 4: Merging Git Branches")
            branches = [f"daily/{cat}-{self.date_str}" for cat in self.categories]
            merge_success = self.git_manager.merge_branches(branches)

            if not merge_success:
                raise Exception("Failed to merge branches")

            # Phase 5: Quality Validation
            logger.info("PHASE 5: Quality Validation")
            valid_articles = self._validate_articles(articles)

            # Phase 6: Zapier Delivery
            logger.info("PHASE 6: Delivering to Zapier Webhook")
            delivery_result = self.zapier.send_with_retry(
                articles=valid_articles,
                metadata=self._get_execution_metadata()
            )

            if not delivery_result["success"]:
                # Save for manual retry
                self.zapier.save_failed_delivery(valid_articles, self.date_str)

            # Phase 7: Cleanup
            logger.info("PHASE 7: Cleanup")
            self.git_manager.cleanup_worktrees(self.categories)
            self.git_manager.delete_branches(branches)

            # Summary
            execution_time = (datetime.now() - self.execution_start).total_seconds()
            logger.success(f"=" * 80)
            logger.success(f"✅ Blog Generation Completed Successfully!")
            logger.success(f"Articles Generated: {len(valid_articles)}")
            logger.success(f"Execution Time: {execution_time:.0f} seconds ({execution_time/60:.1f} minutes)")
            logger.success(f"Zapier Delivery: {'✅ Success' if delivery_result['success'] else '❌ Failed (saved locally)'}")
            logger.success(f"=" * 80)

            return delivery_result

        except Exception as e:
            logger.error(f"❌ Blog generation failed: {e}")
            logger.exception(e)
            return {"success": False, "error": str(e)}

    async def _simulate_agent_outputs(self):
        """Simulate agent outputs for testing (replace with actual Task tool calls)"""
        logger.info("Simulating parallel agent execution...")

        # In production, this would be:
        # async with asyncio.TaskGroup() as tg:
        #     forex_task = tg.create_task(self._launch_forex_agent())
        #     crypto_task = tg.create_task(self._launch_crypto_agent())
        #     commodities_task = tg.create_task(self._launch_commodities_agent())

        # Simulate processing time
        await asyncio.sleep(2)

        # Return mock articles
        return [
            self._create_mock_article("forex", "EUR/USD"),
            self._create_mock_article("crypto", "Bitcoin"),
            self._create_mock_article("commodities", "Gold")
        ]

    def _create_mock_article(self, category: str, asset: str):
        """Create mock article for testing"""
        return {
            "category": category,
            "asset": asset,
            "generated_at": datetime.now().isoformat(),
            "market_data": {
                "price": "1.0845" if category == "forex" else "$110,818",
                "change": "+0.32%",
                "drivers": "Market analysis"
            },
            "languages": {
                "en": {
                    "html": f"<article><h1>{asset} Analysis</h1><p>Mock content...</p></article>",
                    "seo": {
                        "title": f"{asset} Analysis | {category.title()} | Seekapa",
                        "description": f"Professional {asset} analysis...",
                        "keywords": [asset, category, "trading"],
                        "image_alt": f"{asset} trading chart"
                    }
                },
                "ar": {"html": "..."},
                "es": {"html": "..."},
                "pt-BR": {"html": "..."}
            }
        }

    def _validate_articles(self, articles):
        """Validate article quality"""
        valid = []
        for article in articles:
            if len(article["languages"]) >= 4:  # Must have all 4 languages
                valid.append(article)
                logger.info(f"✅ {article['category']} article validated")
            else:
                logger.warning(f"⚠️  {article['category']} article incomplete")

        return valid

    def _get_execution_metadata(self):
        """Get execution metadata"""
        execution_time = (datetime.now() - self.execution_start).total_seconds()
        return {
            "execution_time_seconds": int(execution_time),
            "date": self.date_str,
            "categories": self.categories,
            "system": "automated_blog_multi_agent_v1.0"
        }

    def _create_output_directories(self):
        """Create necessary output directories"""
        os.makedirs(os.path.join(PROJECT_ROOT, "output"), exist_ok=True)
        os.makedirs(os.path.join(PROJECT_ROOT, "logs"), exist_ok=True)


async def main():
    """Main entry point"""
    orchestrator = BlogOrchestrator()
    result = await orchestrator.run()
    return result


if __name__ == "__main__":
    # Run orchestrator
    result = asyncio.run(main())
    sys.exit(0 if result.get("success") else 1)
