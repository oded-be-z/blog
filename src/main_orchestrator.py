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
from agents.content_generation_agent import (
    generate_forex_article,
    generate_crypto_article,
    generate_commodities_article
)


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

            # Phase 3: Launch Parallel Agents (Real AI Content Generation)
            logger.info("PHASE 3: Launching 3 Parallel AI Agents")
            logger.info("🤖 Using GPT-5-Pro + Perplexity for real content generation...")

            articles = await self._generate_articles_parallel(worktrees)

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

            # Return success if articles were generated, even if Zapier delivery failed
            # Articles are saved locally for manual delivery if webhook fails
            return {
                "success": True,
                "articles_generated": len(valid_articles),
                "zapier_delivery": delivery_result,
                "execution_time": execution_time
            }

        except Exception as e:
            logger.error(f"❌ Blog generation failed: {e}")
            logger.exception(e)
            return {"success": False, "error": str(e)}

    async def _generate_articles_parallel(self, worktrees: Dict[str, str]) -> list:
        """
        Generate articles in parallel using real AI agents

        Args:
            worktrees: Dict mapping category to worktree path

        Returns:
            List of article packages
        """
        logger.info("Starting parallel AI content generation...")

        # Create tasks for all 3 agents
        tasks = {
            "forex": asyncio.create_task(
                generate_forex_article(worktrees.get("forex", ""))
            ),
            "crypto": asyncio.create_task(
                generate_crypto_article(worktrees.get("crypto", ""))
            ),
            "commodities": asyncio.create_task(
                generate_commodities_article(worktrees.get("commodities", ""))
            )
        }

        # Wait for all agents to complete
        logger.info("⏳ Waiting for all 3 agents to complete...")
        results = {}
        for category, task in tasks.items():
            try:
                result = await task
                results[category] = result
                if result.get("success"):
                    logger.success(f"✅ {category} agent completed successfully")
                else:
                    logger.error(f"❌ {category} agent failed: {result.get('error')}")
            except Exception as e:
                logger.error(f"❌ {category} agent exception: {e}")
                results[category] = {"success": False, "error": str(e)}

        # Extract article packages from successful results
        articles = []
        for category, result in results.items():
            if result.get("success") and "package" in result:
                articles.append(result["package"])
            else:
                logger.warning(f"⚠️  {category} article not included (failed or incomplete)")

        logger.info(f"Collected {len(articles)} articles from parallel generation")
        return articles

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
